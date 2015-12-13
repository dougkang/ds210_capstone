import ConfigParser
import argparse
import sys
import pickle
import time
import random
from pymongo import MongoClient
from multiprocessing import Process, Pipe

class InstaModel(object):
  '''
  Combines a feature extractor and a cluster model to achieve the following:
  Given a media_feed, return a dictionary of locations and their frequency
  within the cluster
  '''
  def __init__(self, extractor, rm):
    self.extractor = extractor
    self.rm = rm

  def predict(self, uid, access, cache = None):
    print >> sys.stderr, "[%s] predicting location" % uid
    (mf, Y_feat) = self.extractor.transform_uid(uid, access, cache)
    print >> sys.stderr, "[%s] features: %s" % (uid, str(Y_feat.shape))

    Y_loc = self.rm.predict(uid, Y_feat)
    print >> sys.stderr, "[%s] %d locations found" % (uid, len(Y_loc))
    total = sum(Y_loc.values())
    res_loc = dict([(k, float(v) / total) for k,v in Y_loc.items() ])

    return (mf, res_loc)

class Server(object):

  def __init__(self, names, models, weights, caches):
    self._mw = dict(zip(names, zip(models, weights, caches)))

  def cache(self, name):
    return self._mw[name][2]

  def model(self, name):
    return self._mw[name]

  def predict(self, uid, access):
    # TODO it might be better to extract media feed here
    res_loc = {}

    def f(n, m, w, c, conn):
      try:
        mf, Y_loc = m.predict(uid, access, c)
        conn.send((mf, Y_loc))
      except Exception:
        conn.send(([], {}))
      finally:
        conn.close()

    p_conns = []
    for n,(m,w,c) in self._mw.items():
      print >> sys.stderr, "[%s] invoking model %s, w=%f" % (uid, n, w)
      p_conn, c_conn = Pipe()
      p = Process(target=f, args=(n, m, w, c, c_conn))
      p_conns.append((p_conn, p))
      p.start()

    for p_conn,p in p_conns:
      mf, Y_loc = p_conn.recv()
      for k,v in Y_loc.items():
        k = int(k)
        if k not in res_loc:
          res_loc[k] = 0.0
        print >> sys.stderr, "[%s] predicted %s: %s" % (uid,k,v)
        res_loc[k] = res_loc[k] + (float(v)*w)
      print >> sys.stderr, "[%s] processed model results" % uid

      p.join()

    print >> sys.stderr, "[%s] all models returned" % uid
    res_loc = sorted(res_loc.items(), key=lambda x: x[1], reverse = True)

    return (mf, res_loc)

if __name__ == '__main__':

  from bottle import Bottle, request, response, run, route
  app = Bottle()

  # Extract config information from args and supplied config
  parser = argparse.ArgumentParser()
  parser.add_argument('--cfg', type=str, required=True, help="path to config")
  parser.add_argument('--port', type=int, help="port")
  args = parser.parse_args()

  config = ConfigParser.ConfigParser()
  config.read(args.cfg)
  print str(config)

  max_user_posts = config.getint('server', 'max_user_posts')
  max_location_posts = config.getint('server', 'max_location_posts')

  # Connect to mongo
  host = config.get('mongo', 'host')
  port = config.getint('mongo', 'port')
  db = config.get('mongo', 'db')
  print >> sys.stderr, "[server] Connecting to %s:%d/%s" % (host, port, db)
  client = MongoClient(host, port)
  location_collection = client[db][config.get('server', 'location_collection')]
  media_feed_collection = client[db][config.get('server', 'media_feed_collection')]
  # Kinda hacky, but assumes that all image model results have been saved in these
  # caches either previously or during the prediction stage.
  style_cache_collection = client[db][config.get('server', 'style_cache_collection')]
  object_cache_collection = client[db][config.get('server', 'object_cache_collection')]
  place_cache_collection = client[db][config.get('server', 'place_cache_collection')]

  # Initialize models
  models = []
  weights = []
  names = []
  caches = []

  for model_name in config.get('server', 'models').split(','):
    print >> sys.stderr, "[server] Loading %s model" % model_name
    with open(config.get(model_name, 'pickle')) as f_im:
      im = pickle.load(f_im)
      names.append(model_name)
      models.append(im)
      weights.append(config.getfloat(model_name, 'weight'))
      # Hacky way to add caches
      if config.has_option(model_name, 'cache_collection'):
        caches.append(client[db][config.get(model_name, 'cache_collection')])
      else:
        caches.append(None)
      print >> sys.stderr, "[server] Loaded %s model" % model_name

  print >> sys.stderr, "[server] found %d models" % len(models)
  print >> sys.stderr, "[server] found %d weights" % len(weights)

  server = Server(names, models, weights, caches)

  # Enable CORS
  @app.hook('after_request')
  def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

  @route('/')
  def index():
    print >> sys.stderr, "[server] status request"
    return { 'status': 'OK' }

  @route('/location/<lid>')
  def location(lid):
    now = time.time()
    res = location_collection.find_one({ "_id": int(lid) })
    res['id'] = lid
    res['latency'] = (time.time() - now) * 1000
    del res['_id']
    return res

  @route('/user/<uid>')
  def user(uid):
    now = time.time()
    res = media_feed_collection.find_one({ "_id": int(uid) })
    res['id'] = uid
    res['latency'] = (time.time() - now) * 1000
    del res['_id']
    return res

  def build_response(uid, now, mf, res_loc, res_loc_pop = None):
    print >> sys.stderr, "[server] looking up top users"
    top_users = {}
    for k,s,v in res_loc:
      for p in v['posts']:
        x = p['uid']
        if x not in top_users:
          top_users[x] = 0
        top_users[x] = top_users[x] + s
    # TODO hardcoded to 25 top occuring users here
    top_users = sorted(top_users.items(), 
        key=lambda x: x[1], reverse=True)[:25]

    res_usr = []
    for uid,score in top_users:
      x = media_feed_collection.find_one(
          { "_id": uid }, { 'feed': { '$slice': max_user_posts } })
      res_usr.append((uid, score, x))
    res_usr = filter(lambda x: x[2] is not None, res_usr)

    def get_results(m, data):
      score = sum([ x['score'] for x in data ])
      src = m.images['standard_resolution'].url
      return { 'src': src, 'score': score, 'results': data }

    print >> sys.stderr, "[server] looking up places"
    res_place = []
    for m in mf:
      res = place_cache_collection.find_one({ '_id': m.id })
      if res is not None:
        res_place.append(get_results(m, res['result']))
    res_place = sorted(res_place, key = lambda x: x['score'], reverse = True)[:20]

    print >> sys.stderr, "[server] looking up objects"
    res_object = []
    for m in mf:
      res = object_cache_collection.find_one({ '_id': m.id })
      if res is not None:
        res_object.append(get_results(m, res['result']))
    res_object = sorted(res_object, key = lambda x: x['score'], reverse = True)[:20]

    print >> sys.stderr, "[server] finding top tags"
    res_tags = {}
    for m in mf:
      for t in m.tags:
	k = t.name
        if k not in res_tags:
          res_tags[k] = 0
        res_tags[k] = res_tags[k] + 1
    res_tags = sorted(res_tags.items(), key = lambda x: x[1], reverse=True)[:20]

    # XXX BAD BAD BAD, but running out of time
    def unique_posts(posts):
      visited = set()
      res = []
      for p in posts:
        if p['uid'] not in visited:
          visited.add(p['uid'])
          res.append(p)
      return res

    print >> sys.stderr, "[server] returning result"
    return { 
      'id': uid,
      'latency': (time.time() - now) * 1000,
      # This number currently maxes out at our feed limit, which is 50
      'n': len(mf),
      'objects': res_object,
      'places': res_place,
      'tags': [ { 'name': x[0], 'score': x[1] } for x in res_tags ],
      'users': [
        { 'id': k, 
          'name': v['name'] if 'name' in v else 'instagram_user', 
          'score': s, 
          'posts': [ { 
            'id': x['id'],
            'src': x['images']['standard_resolution']
            } for x in v['feed'] ]
          } for k,s,v in res_usr ],
      'locations': [ 
        { 'id': k, 
          'name': "%s, %s" % (v['city'], v['country']), 
          'score': s, 
          'posts': unique_posts(v['posts'])
          } for k,s,v in res_loc ],
      'popular_locations': [ 
        { 'id': k, 
          'name': "%s, %s" % (v['city'], v['country']), 
          'score': s, 
          'posts': unique_posts(v['posts'])
          } for k,s,v in res_loc_pop ] }

  @route('/random/<access>/<uid>')
  def predict(uid, access):
    now = time.time()

    print >> sys.stderr, "[server] random request: %s" % uid
    print >> sys.stderr, "[server] randomly generating locations"
    mf, res_loc = server.predict(uid, access)
    # proceed to discard the results
    res_loc = [ (x['_id'], random.random(), x) for x in location_collection.find() ]
    res_loc = filter(lambda x: 'posts' in x[2] and len(x[2]['posts']) > 0, res_loc)
    res_loc = sorted(res_loc, key = lambda x: x[1], reverse = True)[:20]

    return build_response(uid, now, mf, res_loc)

  @route('/popular/<access>/<uid>')
  def predict(uid, access):
    now = time.time()

    destinations = [ 
      'Marrakech', 'Siem Reap', 'Istanbul', 'Hanoi', 'Prague', 'London', 'Rome', 'Buenos Aires',
      'Paris', 'Cape Town', 'New York', 'Zurich', 'Barcelona', 'Nevsehir', 'Cusco', 'St. Petersburg',
      'Bangkok', 'Kathmandu', 'Athens', 'Budapest' ]

    print >> sys.stderr, "[server] popular request: %s" % uid
    print >> sys.stderr, "[server] generating popular locations"
    mf, res_loc = server.predict(uid, access)
    # proceed to discard the results
    res_loc = []
    for d in destinations:
      x = location_collection.find_one({ 'city': d })
      print x
      res_loc.append((x['_id'], 0, x))

    return build_response(uid, now, mf, res_loc)

  @route('/predict/<access>/<uid>')
  def predict(uid, access):
    now = time.time()
    th = 0.0
    if 'th' in request.query:
      th = float(request.query['th'])

    print >> sys.stderr, "[server] predict request: %s, th=%d" % (uid, th)
    print >> sys.stderr, "[server] predicting locations"
    mf, res_loc = server.predict(uid, access)
    res_loc = filter(lambda x: x[1] > th, res_loc)
    # Augment our result with the location information
    res_loc = map(lambda x: (x[0], x[1], location_collection.find_one(
      { "_id": int(x[0]) }, { 'posts': { '$slice': max_location_posts } })), res_loc)

    destinations = [ 
      'Marrakech', 'Siem Reap', 'Istanbul', 'Hanoi', 'Prague', 'London', 'Rome', 'Buenos Aires',
      'Paris', 'Cape Town', 'New York', 'Zurich', 'Barcelona', 'Nevsehir', 'Cusco', 'St. Petersburg',
      'Bangkok', 'Kathmandu', 'Athens', 'Budapest' ]

    print >> sys.stderr, "[server] generating popular locations"
    # proceed to discard the results
    res_loc_pop = []
    for d in destinations:
      x = location_collection.find_one({ 'city': d })
      res_loc_pop.append((x['_id'], 0, x))

    return build_response(uid, now, mf, res_loc, res_loc_pop)

  port = args.port if args.port is not None else config.getint('server', 'port')
  print >> sys.stderr, "[server] Starting server at port %d" % port
  run(host='0.0.0.0', port=port)

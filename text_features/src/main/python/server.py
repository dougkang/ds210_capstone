import ConfigParser
import argparse
import sys
import pickle
import time
from pymongo import MongoClient

class InstaModel(object):
  '''
  Combines a feature extractor and a cluster model to achieve the following:
  Given a media_feed, return a dictionary of locations and their frequency
  within the cluster
  '''
  def __init__(self, extractor, rm):
    self.extractor = extractor
    self.rm = rm

  def predict(self, uid, access, cache):
    print >> sys.stderr, "[%s] predicting location" % uid
    (mf, Y_feat) = self.extractor.transform_uid(uid, access)
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
    for n,(m,w,c) in self._mw.items():
      print >> sys.stderr, "[%s] invoking model %s, w=%d" % (uid, n, w)
      mf, Y_loc = m.predict(uid, access, c)
      for k,v in Y_loc.items():
        if k not in res_loc:
          res_loc[k] = 0
        res_loc[k] = res_loc[k] + v*w

    total = sum(res_loc.values())
    res_loc = [ (k, (float(v) / total)) for k,v in res_loc.items() ]
    res_loc = sorted(res_loc, key=lambda x: x[1], reverse = True)

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

    print >> sys.stderr, "[server] looking up top users"
    top_users = {}
    for k,s,v in res_loc:
      for p in v['posts']:
        uid = p['uid']
        if uid not in top_users:
          top_users[uid] = 0
        top_users[uid] = top_users[uid] + s
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

    print >> sys.stderr, "[server] looking up styles"
    res_style = []
    for m in mf:
      res = server.cache('style_knn').fine_one({ '_id': m.id })
      if res is not None:
        res_style.append(get_results(m, res['result']))
    res_style = sorted(res_style, key = lambda x: x['score'])[:10]

    print >> sys.stderr, "[server] looking up places"
    res_place = []
    for m in mf:
      res = server.cache('place_knn').fine_one({ '_id': m.id })
      if res is not None:
        res_object.append(get_results(m, res['result']))
    res_place = sorted(res_place, key = lambda x: x['score'])[:10]

    print >> sys.stderr, "[server] looking up objects"
    res_object = []
    for m in mf:
      res = server.cache('object_knn').fine_one({ '_id': m.id })
      if res is not None:
        res_object.append(get_results(m, res['result']))
    res_object = sorted(res_object, key = lambda x: x['score'])[:10]

    return { 
      'id': uid,
      'latency': (time.time() - now) * 1000,
      'objects': res_object,
      'places': res_place,
      'styles': res_style,
      'users': [
        { 'id': k, 
          'name': v['uname'] if 'uname' in v else 'instagram_user', 
          'score': s, 
          'posts': [ { 
            'id': x['id'],
            'src': x['images']['standard_resolution']
            } for x in v['feed'] ]
          } for k,s,v in res_usr ],
      'locations': [ 
        { 'id': k, 
          'name': v['city'], 
          'score': s, 
          'posts': v['posts'] 
          } for k,s,v in res_loc ] }

  port = args.port if args.port is not None else config.getint('server', 'port')
  print >> sys.stderr, "[server] Starting server at port %d" % port
  run(host='0.0.0.0', port=port)

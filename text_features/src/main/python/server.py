import ConfigParser
import argparse
import sys
import pickle
import time
from pymongo import MongoClient
from bottle import route, run, request

class InstaModel(object):
  '''
  Combines a feature extractor and a cluster model to achieve the following:
  Given a media_feed, return a dictionary of locations and their frequency
  within the cluster
  '''
  def __init__(self, extractor, rm):
    self.extractor = extractor
    self.rm = rm

  def predict(self, uid, access):
    print >> sys.stderr, "[%s] predicting cluster" % uid
    Y_feat = self.extractor.transform_uid(uid, access)
    print >> sys.stderr, "[%s] features: %s" % (uid, str(Y_feat.shape))
    Y_loc = self.rm.predict(uid, Y_feat)
    print >> sys.stderr, "[%s] %d locations found" % (uid, len(Y_loc))

    total = sum(Y_loc.values())
    res = dict([(k, float(v) / total) for k,v in Y_loc.items() ])

    return res

class Server(object):

  def __init__(self, models, weights):
    self._mw = zip(models, weights)


  def predict(self, uid, access):
    # TODO it might be better to extract media feed here
    Y = {}
    for m,w in self._mw:
      Y_loc = m.predict(uid, access)
      for k,v in Y_loc.items():
        if k not in Y:
          Y[k] = 0
        Y[k] = Y[k] + v*w

    total = sum(Y.values())
    res = [ (k, (float(v) / total)) for k,v in Y.items() ]

    return sorted(res, key=lambda x: x[1], reverse = True)

if __name__ == '__main__':

  # Extract config information from args and supplied config
  parser = argparse.ArgumentParser()
  parser.add_argument('--cfg', type=str, required=True, help="path to config")
  parser.add_argument('--port', type=int, help="port")
  args = parser.parse_args()

  config = ConfigParser.ConfigParser()
  config.read(args.cfg)
  print config

  # Connect to mongo
  host = config.get('mongo', 'host')
  port = config.getint('mongo', 'port')
  db = config.get('mongo', 'db')
  print >> sys.stderr, "[server] Connecting to %s:%d/%s" % (host, port, db)
  client = MongoClient(host, port)
  location_collection = client[db][config.get('server', 'location_collection')]

  models = []
  weights = []

  for model_name in config.get('server', 'models').split(','):
    print >> sys.stderr, "[server] Loading %s model" % model_name
    with open(config.get(model_name, 'pickle')) as f_im:
      im = pickle.load(f_im)
      models.append(im)
      weights.append(config.getfloat(model_name, 'weight'))
      print >> sys.stderr, "[server] Loaded %s model" % model_name

  print >> sys.stderr, "[server] found %d models" % len(models)
  print >> sys.stderr, "[server] found %d weights" % len(weights)

  server = Server(models, weights)

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

  @route('/predict/<access>/<uid>')
  def predict(uid, access):
    now = time.time()
    th = 0.0
    if 'th' in request.query:
      th = float(request.query['th'])

    print >> sys.stderr, "[server] predict request: %s, th=%d" % (uid, th)
    res = filter(lambda x: x[1] > th, server.predict(uid, access))
    # Augment our result with the location information
    res = map(lambda x: (x[0], x[1], location_collection.find_one({ "_id": int(x[0]) })), res)
    print res
      
    return { 
      'id': uid,
      'latency': (time.time() - now) * 1000,
      'locations': [ 
        { 'id': k, 'name': v['city'], 'score': s, 'posts': v['posts'] } for k,s,v in res ] }

  port = args.port if args.port is not None else config.getint('server', 'port')
  print >> sys.stderr, "[server] Starting server at port %d" % port
  run(host='0.0.0.0', port=port)



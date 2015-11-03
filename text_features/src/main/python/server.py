import ConfigParser
import argparse
import sys
import pickle
import time
from extractor import ImageFeatureExtractor, TextFeatureExtractor
from cluster import KMModel
from pymongo import MongoClient
from bottle import route, run

class InstaModel(object):
  '''
  Combines a feature extractor and a cluster model to achieve the following:
  Given a media_feed, return a dictionary of locations and their frequency
  within the cluster
  '''
  def __init__(self, extractor, cm):
    self.extractor = extractor
    self.cm = cm

  def predict(self, uid, access):
    print >> sys.stderr, "[%s] predicting cluster" % uid
    Y_feat = self.extractor.transform_uid(uid, access)
    print >> sys.stderr, "[%s] features: %s" % (uid, str(Y_feat.shape))
    Y_loc = self.cm.predict(uid, Y_feat)
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
  parser.add_argument('--port', type=int, default=8080, help="port")
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

  models = []
  weights = []

  print >> sys.stderr, "[server] Loading text model"
  # Construct Text InstaModel
  with \
      open(config.get('text', 'tfidf')) as f_tfidf, \
      open(config.get('text', 'kmeans')) as f_km:
    coll = config.get('text', 'coll')
    tfidf = pickle.load(f_tfidf)
    km = pickle.load(f_km)
    extractor = TextFeatureExtractor(tfidf)
    cm = KMModel(km, client[db], coll)
    models.append(InstaModel(extractor, cm))
    weights.append(config.getfloat('text', 'weight'))
    print >> sys.stderr, "[server] Loaded image model"

  # TODO Add Image Model
  # print >> sys.stderr, "[server] Loading image model"
  # Construct Image InstaModel
  # with open(config.get('image', 'vocab')) as f_vocab:
  #   coll = config.get('image', 'coll')
  #   url = config.get('image', 'url')
  #   vocab = pickle.load(f_vocab)
  #   extractor = ImageFeatureExtractor(vocab, url)
  #   cm = KMModel(km, client[db], coll)))
  #   models.append(InstaModel(extractor, cm))
  #   weights.append(config.getfloat('image', 'weight'))
  #   print >> sys.stderr, "[server] Loaded text model"

  print >> sys.stderr, "[server] found %d models" % len(models)
  print >> sys.stderr, "[server] found %d weights" % len(weights)

  server = Server(models, weights)

  @route('/')
  def index():
    print >> sys.stderr, "[server] status request"
    return { 'status': 'OK' }

  @route('/predict/<access>/<uid>')
  def predict(uid, access):
    now = time.time()
    print >> sys.stderr, "[server] predict request: %s" % uid
    res = server.predict(uid, access)
    return { 
        'uid': uid,
        'latency': (time.time() - now) * 1000,
        'locations': [ { 'name': k, 'score': v } for k,v in res ] }

  print >> sys.stderr, "[server] Starting server at port %d" % args.port
  run(host='localhost', port=args.port)



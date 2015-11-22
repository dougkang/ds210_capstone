import sys
import math
import pickle
import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.neighbors import NearestNeighbors
from cluster import LModel

def post_knn(X, y, k = 10, path = "models/userknn_pm.pickle", 
    host = "localhost", port = 27017, 
    db = "instagram", knn_collection = "nn", **kwargs):

  m = NearestNeighbors(k, **kwargs)
  m.fit(X)
 
  print >> sys.stderr, "[post_knn] saving locations to %s:%s/%s/%s" % (host, port, db, knn_collection)
  mongo = MongoClient(host, port = int(port))[db][knn_collection]
  for i,locs in enumerate(y):
    data = {}
    for l,v in locs:
      data[str(int(l))] = int(v)
    mongo.update_one({ '_id': int(i) }, { '$set': { "locations": data } }, upsert = True)

  metrics = {}
  metrics['n'] = X.shape[0]

  print metrics

  lm = LModel(m, host, port, db, knn_collection, k)
  # Save off our model
  with open(path, 'w') as f_m:
    pickle.dump(lm, f_m)
    print "Saved lookup model"

  return (lm, metrics)


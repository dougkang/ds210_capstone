import os
import sys
from pymongo import MongoClient

# TODO Cluster Model is a misnomer.  This is just a model

class RecModel(object):
  '''
  Given a vector of features X, return a dictionary of locations and their
  frequency within the cluster
  '''

  def _predict(self, x):
    raise NotImplemented("Not implemented!")

  def predict(self, uid, x):
    print >> sys.stderr, "[%s] predicting locations" % (uid)
    Y = self._predict(x)
    print >> sys.stderr, "[%s] predicted %d locations" % (uid, len(Y))
    return Y

class LModel(RecModel):
  '''
  A recommendation model whose underlying model returns one or more ids to lookup
  in a database
  '''
  def __init__(self, m, host, port, db, collection, k):
    self._m = m
    self._host = host
    self._port = port
    self._db = db
    self._collection = collection
    self.k = int(k)
    self._client = MongoClient(self._host, port=int(self._port))
    self._mongo = self._client[self._db][self._collection]

  def __getstate__(self):
    return (self._m, self._host, self._port, self._db, self._collection, self.k)

  def __setstate__(self, state):
    self.__init__(*state)

  def _predict(self, X):
    res = {}
    
    # A couple of our models in this group use kneighbors instead of predict
    # If such a function exists, use it, otherwise, stick to predict
    predict = lambda x: self._m.predict(x)
    if hasattr(self._m, "kneighbors"):
      predict = lambda x: self._m.kneighbors(x, self.k, return_distance=False)

    for x in predict(X)[0]:
      for y in self._mongo.find_one({ '_id': x })['locations']:
        if y not in res:
          res[y] = 0
        res[y] = res[y] + 1
    res = sorted(res.items(), key=lambda x: x[1], reverse=True)[:self.k]

    # Normalize the result
    total = sum([ x[1] for x in res ])
    norm = dict([ (x[0], float(x[1])/total) for x in res ])

    return norm


class PModel(RecModel):
  '''
  A recommendation model whose underlying model returns probabilities
  '''
  def __init__(self, pm, location_dict, k):
    self._pm = pm
    self._dict = location_dict
    self.k = k

  def _predict(self, X):
    # For all posts, determine the probability distribution for all locations
    # Accumulate the location information for all posts into a single map
    # Take the top k locations
    res = {}
    for k in self._dict:
      res[k] = 0
    for x in self._pm.predict_proba(X):
      for i,y in enumerate(x):
        loc = self._dict[i]
        res[loc] = res[loc] + y
    res = sorted(res.items(), key=lambda x: x[1], reverse=True)[:self.k]

    # Normalize the result
    total = sum([ x[1] for x in res ])
    norm = dict([ (x[0], float(x[1])/total) for x in res ])

    return norm

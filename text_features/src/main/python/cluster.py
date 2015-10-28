import os
import sys

class ClusterModel(object):
  '''
  Given a vector of features X, return a dictionary of locations and their
  frequency within the cluster
  '''
  def __init__(self, mongo, coll):
    self._coll = coll
    self._db = mongo[coll]

  def predict_cluster(self, x):
    raise Exception("Not implemented")

  def predict(self, uid, x):
    print >> sys.stderr, "[%s] predicting cluster" % (uid)
    Y = self.predict_cluster(x)[0]
    print >> sys.stderr, "[%s] cluster prediction: %s" % (uid, str(Y))
    doc = self._db.find_one(int(Y))
    if doc is None:
      raise Exception("Cluster %d not found in coll %s" % (Y, self._coll))
    print >> sys.stderr, "[%s] cluster has %d locations" % (uid, len(doc['locations']))
    return doc['locations']

class KMModel(ClusterModel):
  def __init__(self, km, mongo, coll):
    ClusterModel.__init__(self, mongo, coll)
    self._km = km

  def predict_cluster(self, x):
    return self._km.predict(x)

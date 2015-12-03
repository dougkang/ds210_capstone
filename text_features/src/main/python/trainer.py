import sys
import os
import math
import pickle
import pandas as pd
import numpy as np
import load_data
from server import InstaModel
from pymongo import MongoClient

def load(dataset_path, force_refresh = False, **kwargs):
  if force_refresh or not os.path.isfile(dataset_path):
    print "[trainer] loading data from scratch"
    df = load_data.load(**kwargs)
    print "[trainer] assigning airport"
    df = load_data.assign_airport(df, **kwargs)
    print "[trainer] saving dataset to %s" % dataset_path
    df.to_csv(dataset_path, encoding='utf-8')
  else:
    print "[trainer] loading existing data at %s" % dataset_path
    # Using python engine, which is slower, but was having memory issues when using
    # the C engine
    df = pd.read_csv(dataset_path, encoding='utf-8', engine="python")
  return df

class Trainer(object):
  '''
  Responsible for training an InstaModel
  '''

  def __init__(self, train_extractor, train_recmodel, cache = None):
    self._train_extractor = train_extractor
    self._train_recmodel = train_recmodel
    self._cache = cache

  def _run(self, df, im_path, df_test = None, **kwargs):
    X, y, ex = self._train_extractor(df, cache = self._cache, **kwargs)
    X_test = None
    y_test = None
    # FIXME this is heavily tied to text extractor
    if df_test is not None:
      X_test = ex._tfidf.transform(df_test['bow'])
      y_test = df_test['airport']
    rm, metrics = self._train_recmodel(X, y, X_test = X_test, y_test = y_test, **kwargs)
    m = InstaModel(ex, rm)

    # Save off our InstaModel
    with open(im_path, 'w') as f_im:
      pickle.dump(m, f_im)

    return (m, metrics)

  def run(self, im_path, dataset_path, \
      force_refresh = False, df_test = None, **kwargs):
    '''
    Run the trainer to train an Instamodel

    Args:
      im_path: the path where we plan to save our instamodel.
      dataset_path: the path from which to load a previously cached dataset.  If None, run will
        try to load the dataset from scratch and save to this location
      force_refresh: whether or not we want to force the refresh of a cached dataset
    Returns:
      a tuple containing the instamodel and some metrics we have calculated
    '''

    df = load(dataset_path, force_refresh, **kwargs)
    return self._run(df, im_path, df_test, **kwargs)

if __name__ == "__main__":
  import ConfigParser
  import argparse
  import train_tfidf
  import train_img
  import train_pmodel
  import train_lmodel

  parser = argparse.ArgumentParser()
  parser.add_argument('models', type=str, nargs='+', help="type of model to train")
  parser.add_argument('--cfg', type=str, required=True, help="path to config")
  parser.add_argument('--output', type=str, required=True, help="path to model output directory")
  parser.add_argument('--clean', action='store_true', help="clean dataset file")
  args = parser.parse_args()

  config = ConfigParser.ConfigParser()
  config.read(args.cfg)

  for i,m in enumerate(args.models):
    print >> sys.stderr, "[trainer] training model %d: %s" % (i, m)

    kwargs = dict(config.items("mongo") + config.items("dataset") + config.items(m))
    if args.clean and i == 0:
      kwargs['force_refresh'] = True
    else:
      kwargs['force_refresh'] = False
    print >> sys.stderr, "[trainer] config: %s" % str(kwargs)

    if m == 'text_knn':
      trainer = Trainer(train_tfidf.post_tfidf, train_pmodel.post_knn)
    elif m == 'text_gmm':
      trainer = Trainer(train_tfidf.post_tfidf, train_pmodel.post_gmm)
    elif m == 'text_svm':
      trainer = Trainer(train_tfidf.post_tfidf, train_pmodel.post_svm)
    elif m == 'text_nb':
      trainer = Trainer(train_tfidf.post_tfidf, train_pmodel.post_nb)
    elif m == 'text_userknn':
      trainer = Trainer(train_tfidf.user_tfidf, train_lmodel.post_knn)
    elif m == 'style_knn' or m == 'object_knn' or m == 'place_knn':
      host = config.get('mongo', 'host')
      port = config.getint('mongo', 'port')
      db = config.get('mongo', 'db')
      print >> sys.stderr, "[trainer] Connecting to %s:%d/%s" % \
         (host, port, db)
      client = MongoClient(host, port)
      cache = client[db][config.get(m, 'cache_collection')]
      trainer = Trainer(train_img.post_img, train_pmodel.post_knn, cache)
    else:
      raise ValueError("Unrecognized model %s" % m)

    trainer.run("%s/%s.pickle" % (args.output, m), **kwargs)


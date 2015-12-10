import sys
import math
import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from extractor import ImageFeatureExtractor

def post_img(df, vocab_path, url, cache = None, **kwargs):
  # Generate a dataset that doesn't group users
  # We are only interested in stuff with locations

  with open(vocab_path) as f_vocab:
    vocab = dict([ (x[1].strip(), x[0]) for x in enumerate(f_vocab.readlines()) ])

  extractor = ImageFeatureExtractor(vocab, url, **kwargs)
  df_img = df.loc[pd.notnull(df['airport'])]
  X = extractor._transform(zip(df_img['mid'], df_img['url']), cache)
  y_loc = df_img['airport']

  print "Post Image Dataset"
  print X.shape
  print y_loc.shape
  print df_img.head()

  print y_loc

  return (X, y_loc, extractor)

def user_img(df, vocab_path, url, cache = None, loc_only = True, **kwargs):
  # Generate a dataset that doesn't group users
  # We are only interested in stuff with locations
  with open(vocab_path) as f_vocab:
    vocab = dict([ (x[1].strip(), x[0]) for x in enumerate(f_vocab.readlines()) ])

  extractor = ImageFeatureExtractor(vocab, url, **kwargs)
  df = df.loc[pd.notnull(df['airport'])]
  X = extractor._transform(zip(df['mid'], df['url']), cache)
  df['feat'] = [ x for x in X ]

  # Group our posts by userid and combine the bow and locations into a single feature
  data = { 'uid': [], 'feat': [], 'loc': [] }
  for k,vs in df.groupby('uid').groups.iteritems():
      locs = dict(df.loc[vs]['airport'].value_counts()).items()
      feats = reduce(lambda x,y: x + y, df.loc[vs]['feat'])
      # We are only interested in users with at least one location
      if len(locs) > 0:
          data['uid'].append(k)
          data['loc'].append(locs)
          data['feat'].append(feats)

  df_user = pd.DataFrame(data)

  if loc_only:
    df_user = df_user.loc[pd.notnull(df_user['loc'])]

  X = np.array([ x for x in df_user['feat'] ])
  y_loc = df_user['loc']
                     
  print "User Dataset: %s, %s" % (str(X.shape), str(y_loc.shape))

  extractor = ImageFeatureExtractor(vocab, url, **kwargs)

  return (X, y_loc, extractor)

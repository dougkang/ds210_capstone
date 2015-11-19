import sys
import math
import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from extractor import TextFeatureExtractor

def post_tfidf(df, **kwargs):
  # Generate a dataset that doesn't group users
  # We are only interested in stuff with locations
  tfidf = TfidfVectorizer(stop_words='english', norm='l2', ngram_range=[1,2])
  df_bow = df.loc[pd.notnull(df['airport'])]
  X_bow = tfidf.fit_transform(df_bow['bow'])
  y_loc = df_bow['airport']

  print "Post BOW Dataset"
  print X_bow.shape
  print y_loc.shape
  print df_bow.head()

  extractor = TextFeatureExtractor(tfidf)

  return (X_bow, y_loc, extractor)

def user_tfidf(df, loc_only = False, **kwargs):
  # Group our posts by userid and combine the bow and locations into a single feature
  data = { 'uid': [], 'bow': [], 'loc': [] }
  for k,vs in df.groupby('uid').groups.iteritems():
      locs = dict(df.loc[vs]['airport'].value_counts()).items()
      # We are only interested in users with at least one location
      if len(locs) > 0:
          data['uid'].append(k)
          data['loc'].append(locs)
          data['bow'].append(' '.join(df.loc[vs]['bow']))

  df_user_bow = pd.DataFrame(data)
  df_user_bow = df_user_bow.loc[[ len(x.strip()) > 0 for x in df_user_bow['bow'] ]]

  if loc_only:
    df_user_bow = df_user_bow.loc[pd.notnull(df_user_bow['loc'])]

  tfidf_user = TfidfVectorizer(stop_words='english', norm='l2', ngram_range=[1,2])
  Y_user_bow = tfidf_user.fit_transform(df_user_bow['bow'])
  Y_user_loc = df_user_bow['loc']
                     
  print "User BOW Dataset"
  print Y_user_bow.shape
  print df_user_bow.head()

  extractor = TextFeatureExtractor(tfidf_user)

  return (Y_user_bow, Y_user_loc, extractor)

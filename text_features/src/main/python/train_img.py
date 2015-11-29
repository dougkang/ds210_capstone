import sys
import math
import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from extractor import ImageFeatureExtractor

def post_img(df, vocab_path, url="http://119.81.249.157:3000/resources/1", **kwargs):
  # Generate a dataset that doesn't group users
  # We are only interested in stuff with locations

  with open(vocab_path) as f_vocab:
    vocab = dict([ (x[1].strip(), x[0]) for x in enumerate(f_vocab.readlines()) ])

  extractor = ImageFeatureExtractor(vocab, url, **kwargs)
  df_img = df.loc[pd.notnull(df['airport'])]
  X = extractor._transform(zip(df_img['mid'], df_img['url']))
  y_loc = df_bow['airport']

  print "Post Image Dataset"
  print X.shape
  print y_loc.shape
  print df_bow.head()

  with open(tfidf_path, 'w') as f_tfidf:
    pickle.dump(extractor, f_tfidf)
    print "Saved text feature extractor to %s" % tfidf_path

  return (X, y_loc, extractor)

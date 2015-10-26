import os
import numpy as np
import pandas as pd
from langdetect import detect_langs
from pymongo import MongoClient
from IPython.display import Image

def load(limit = None):

  # Constants
  host = '192.168.1.131'
  port = 27017
  db = 'instagram'
  collection = 'media_feeds'

  # Connect to mongo
  client = MongoClient(host, port)
  mongo = client[db][collection]

  # Extract the features that we are interested in and put it into a dataframe
  data = {}
  for k in [ 'uid', 'mid', 'date', 'text', 'tags', 'tags_count', 'likes', 'type', 'locid', 'locname', 'lat', 'long', 'url', 'lang', 'lang_prob' ]:
    data[k] = []

  cnt = 0
  for x in mongo.find():
    if limit is not None and cnt >= limit:
      break
    for y in x['feed']:
      cnt = cnt + 1
      if cnt % 100 == 0:
        print "%d documents loaded" % cnt
      data['uid'].append(x['_id'])
      data['mid'].append(y['id'])
      data['date'].append(y['created'])
      data['text'].append(y['caption'])
      data['type'].append(y['type'])
      data['tags'].append(" ".join(sorted(y['tags'], key=lambda x: len(x), reverse=True)))
      data['tags_count'].append(len(y['tags']))
      data['likes'].append(y['like_count'])
      data['locid'].append(y['location']['id'] if y['location'] is not None else None)
      data['locname'].append(y['location']['name'] if y['location'] is not None else None)
      data['lat'].append(y['location']['latitude'] if y['location'] is not None else None)
      data['long'].append(y['location']['longitude'] if y['location'] is not None else None)
      data['url'].append(y['images']['thumbnail'])
      try:
        langs = filter(lambda x: x > 0.2, detect_langs(y['caption'].replace('#', '')))
        data['lang'].append(langs[0].lang)
        data['lang_prob'].append(langs[0].prob)
      except Exception:
        data['lang'].append("??")
        data['lang_prob'].append(0.0)

  df = pd.DataFrame(data)
  if limit is not None:
    df = df[:limit]

  df['text_cleaned'] = [ reduce(lambda y,z: y.replace('#'+z, ''), x['tags'].split(' '), x['text']) \
    for i,x in df.iterrows() ]
  df['text_length'] = [ len(x) for x in df['text_cleaned'] ]
  df['tag_length'] = [ len(x) for x in df['tags'] ] - df['tags_count']
  df['tt_ratio'] = (df['tag_length'].astype(np.float)+1) / (df['text_length']+1)

  print df.describe()
  return df

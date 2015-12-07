import os
import sys
import math
import numpy as np
import pandas as pd
from langdetect import detect_langs
from pymongo import MongoClient
from sklearn.neighbors import NearestNeighbors

def load(limit = None,
    host = "localhost", port = 27017, 
    db = "instagram", media_feed_collection = 'media_feeds', **kwargs):

  # Connect to mongo
  client = MongoClient(host, int(port))
  mongo = client[db][media_feed_collection]

  # Extract the features that we are interested in and put it into a dataframe
  data = {}
  for k in [ 'uid', 'uname', 'mid', 'date', 'text', 'tags', 'tags_count', \
      'likes', 'type', 'locid', 'locname', 'lat', 'long', 'url', 'lang', 'lang_prob' ]:
    data[k] = []

  cnt = 0
  for x in mongo.find():
    if limit is not None and cnt >= int(limit):
      break
    if 'feed' not in x:
      continue

    for y in x['feed']:
      cnt = cnt + 1
      if cnt % 100 == 0:
        print "%d documents loaded" % cnt
      data['uid'].append(x['_id'])
      data['uname'].append(x['name'] if 'name' in x else "instagram_user")
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
      data['url'].append(y['images']['standard_resolution'])
      try:
        langs = filter(lambda x: x > 0.2, detect_langs(y['caption'].replace('#', '')))
        data['lang'].append(langs[0].lang)
        data['lang_prob'].append(langs[0].prob)
      except Exception:
        data['lang'].append("??")
        data['lang_prob'].append(0.0)

  client.close()

  df = pd.DataFrame(data)
  if limit is not None:
    df = df[:int(limit)]

  df['text_cleaned'] = [ reduce(lambda y,z: y.replace('#'+z, ''), x['tags'].split(' '), x['text']) \
    for i,x in df.iterrows() ]
  df['text_length'] = [ len(x) for x in df['text_cleaned'] ]
  df['tag_length'] = [ len(x) for x in df['tags'] ] - df['tags_count']
  df['tt_ratio'] = (df['tag_length'].astype(np.float)+1) / (df['text_length']+1)

  print df.describe()
  return df

def assign_airport(
    df, airport_data = "src/main/resources/airports.dat",
    host = "localhost", port = 27017,
    db = "instagram", location_collection = "location", **kwargs):
  # Find the closest airport
  airports_df = pd.read_csv(airport_data, 
      encoding="utf-8",
      names=[ "name","city","country","x4","x5","lat","long","x6","x7","x8","x9" ])
  airports_df['name'] = [ x.replace('.', '') for x in airports_df['name'] ]
  airports_df['lat'] = airports_df['lat'].astype(np.float)
  airports_df['long'] = airports_df['long'].astype(np.float)
  airports_df['id'] = airports_df.index
  airports_df = airports_df[["id", "name", "city", "country", "lat", "long"]]
  print >> sys.stderr, "[assign_airport] found %d airports" % airports_df.shape[0]

  print >> sys.stderr, "[assign_airport] saving location information"
  client = MongoClient(host, int(port))
  mongo = client[db][location_collection]
  for i,r in airports_df.iterrows():
    data = { 
        'name': r['name'], 'city': r['city'], 'country': r['country'], \
        'lat': r['lat'], 'long': r['long'], 'posts': [] }
    mongo.update_one({ '_id': i }, { '$set': data }, upsert = True)

  print >> sys.stderr, "[assign_airport] finding closest airport"
  nn = NearestNeighbors(1)
  nn.fit(airports_df[["lat", "long"]])

  # We define a city to be a place that has an airport, so do some additional work to attach a location to
  # the nearest airport
  df["airport"] = None
  idxs = pd.notnull(df['lat'])
  ids = nn.kneighbors(
      df.loc[idxs, ['lat', 'long']], return_distance = False)
  df.loc[idxs, "airport"] = [ x[0] for x in ids ]

  print >> sys.stderr, "[assign_airport] cleaning up text"

  # Do some text cleanup
  df['tags_cleaned'] = [ ' '.join([ 'tag:'+y for y in x.split(' ') if len(x.strip()) > 0 ]) for x in df['tags'] ]
  df['bow'] = [ x['text_cleaned'] + ' ' + x['tags_cleaned'] for i,x in df.iterrows() ]

  # Let's play with only english language captions for now
  en_df = df.loc[(df["lang"] == "en") | (df["lang"] == "??")]
  en_df.loc[[ len(x.strip()) > 0 for x in en_df['bow']], [ "uid", "uname", "mid", "bow", "url", "airport"]].head()

  print >> sys.stderr, "[assign_airport] saving posts"
  for i,r in en_df.iterrows():
    data = { 
        'id': r['mid'], 'name': r['uname'], 'uid': r['uid'], 
        'src': r['url'], 'likes': r['likes'] }

    mongo.update_one({ '_id': r['airport'] }, 
      { '$push': { 
        "posts": { 
          '$each': [ data ],
          '$sort': { 'likes': -1 },
          '$slice': -150 } } })

  client.close()

  return en_df

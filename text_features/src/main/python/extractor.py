import json
import os
import sys
import requests
import time
import numpy as np
from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError, InstagramClientError

# Initialize our API
client_id = os.environ.get('INSTAGRAM_CLIENT_ID')
client_secret = os.environ.get('INSTAGRAM_CLIENT_SECRET')
feed_limit = 50

class FeatureExtractor(object):
  '''
  Given a media feed, extract the features (in np.array)
  Given a user, extract the features (in np.array)
  '''

  def name(self):
    raise Exception("Not implemented")

  def transform(self, media_feed, cache = None):
    raise Exception("Not implemented")

  def transform_uid(self, uid, access_token, cache = None):
    print >> sys.stderr, "[%s] extracting posts" % uid
    # Extract the posts for this users
    api = InstagramAPI(
      access_token=access_token, 
      client_id=client_id,
      client_secret=client_secret)
    media_feed, mf_next_ = api.user_recent_media(user_id = uid, count = feed_limit)
    while mf_next_:
      more, mf_next_ = api.user_recent_media(with_next_url=mf_next_)
    print >> sys.stderr, "[%s] found %d posts" % (uid, len(media_feed))

    return (media_feed, self.transform(uid, media_feed, cache))

class TextFeatureExtractor(FeatureExtractor):
  '''
  Given a pretrained tfidf model and a media feed, extract the TFIDF values 
  of the captions
  '''

  def __init__(self, tfidf, **kwargs):
    self._tfidf = tfidf

  def transform(self, uid, media_feed, cache = None):
    print >> sys.stderr, "[%s] transforming posts into text features" % uid
    bow = "" 
    for m in media_feed:
      if hasattr(m.caption, 'text'):
        bow = bow + ' ' + m.caption.text
      if hasattr(m, 'tags'):
        bow = bow + ' ' + ' '.join([ "tags:"+x.name for x in m.tags ])
    print >> sys.stderr, "[%s] text length: %d" % (uid, len(bow))
    # TODO some additional cleanup of text to go here
    return self._tfidf.transform([ bow ])

class TagFeatureExtractor(FeatureExtractor):

  def __init__(self, tfidf, **kwargs):
    self._tfidf = tfidf

  def transform(self, uid, media_feed, cache = None):
    print >> sys.stderr, "[%s] transforming posts into text features" % uid
    bow = "" 
    for m in media_feed:
      if hasattr(m, 'tags'):
        bow = bow + ' ' + ' '.join([ x.name for x in m.tags ])
    print >> sys.stderr, "[%s] text length: %d" % (uid, len(bow))
    # TODO some additional cleanup of text to go here
    return self._tfidf.transform([ bow ])

class FilterFeatureExtractor(FeatureExtractor):

  def __init__(self, tfidf, **kwargs):
    self._tfidf = tfidf

  def transform(self, uid, media_feed, cache = None):
    print >> sys.stderr, "[%s] transforming posts into text features" % uid
    bow = "" 
    for m in media_feed:
      if hasattr(m, 'filter'):
        bow = bow + ' ' + ' '.join(m.filter)
    print >> sys.stderr, "[%s] text length: %d" % (uid, len(bow))
    # TODO some additional cleanup of text to go here
    return self._tfidf.transform([ bow ])

class ImageFeatureExtractor(FeatureExtractor):
  '''
  Given a url to the image model server and a media feed, extract image features
  and their confidences 
  '''

  def __init__(self, vocab, \
      url = "http://119.81.249.157:3000/resources/1",
      batch_size = 100, qps = 1, **kwargs):

    '''
    - vocab: dictionary where key is the name and value is the index
    - url: the endpoint to hit when retrieving image resources
    '''
    self.url = url
    self._vocab = vocab
    self._batch_size = int(batch_size)
    self._qps = int(qps)
 
  def _send_request(self, data):
    r = requests.post(self.url, json=data)
    print >> sys.stderr, "[imgfeat] response: %d %s" % (r.status_code, r.text[:150])
    # Raises exception if NOT OK
    res = r.json() if r.status_code == 200 else {}
    return r.json()
 
  def _transform(self, urls, cache = None):
    res = np.zeros((len(urls), len(self._vocab)))

    data = {}
    curr = 0
    for mid,url in urls:
      doc = cache.find_one({ "_id": mid }) if cache is not None else None

      if doc is not None:
        print >> sys.stderr, "[imgfeat] cached hit: %s: %s" % (self.url, doc)
        idx = [ self._vocab[x['id']] for x in doc['result'] ]
        vs = [ x['score'] for x in doc['result'] ]
        res[curr, idx] = vs
        curr = curr + 1
      else:
        data[mid] = url
        if len(data) % self._batch_size == 0:
          print >> sys.stderr, "[imgfeat] %d/%d" % (curr,len(urls))
          print >> sys.stderr, "[imgfeat] batch threshold reached, hitting image server %s" % self.url
          for k,v in self._send_request(data).iteritems():
            idx = [ self._vocab[x['id'].lower()] for x in v ]
            vs = [ x['score'] for x in v ]
            res[curr, idx] = vs
            if cache is not None:
              cache.update_one({ '_id': k }, { '$set': { "result": v } }, upsert = True)
            curr = curr + 1
          data = {}
          time.sleep(1.0 / self._qps)

    # If there are any leftover stuff in the queue, process it
    if len(data) > 0:
      print >> sys.stderr, "[imgfeat] end of urls reached, hitting image server %s" % self.url
      for k,v in self._send_request(data).iteritems():
        idx = [ self._vocab[x['id'].lower()] for x in v ]
        vs = [ x['score'] for x in v ]
        res[curr, idx] = vs
        if cache is not None:
          cache.update_one({ '_id': k }, { '$set': { "result": v } }, upsert = True)
        curr = curr + 1

    return res

  def transform(self, uid, media_feed, cache = None):
    print >> sys.stderr, "[%s] extracting posts" % uid
    print >> sys.stderr, "[%s] transforming posts into image features" % uid
    urls = []
    print media_feed
    for m in media_feed:
      if 'standard_resolution' in m.images:
        urls.append((m.id, m.images['standard_resolution'].url))
    print urls
    return self._transform(urls, cache) 

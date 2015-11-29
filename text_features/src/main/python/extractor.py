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
feed_limit = 100

class FeatureExtractor(object):
  '''
  Given a media feed, extract the features (in np.array)
  Given a user, extract the features (in np.array)
  '''

  def name(self):
    raise Exception("Not implemented")

  def transform(self, media_feed):
    raise Exception("Not implemented")

  def transform_uid(self, uid, access_token):
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

    return self.transform(uid, media_feed)

class TextFeatureExtractor(FeatureExtractor):
  '''
  Given a pretrained tfidf model and a media feed, extract the TFIDF values 
  of the captions
  '''

  def __init__(self, tfidf, **kwargs):
    self._tfidf = tfidf

  def transform(self, uid, media_feed):
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

class ImageFeatureExtractor(FeatureExtractor):
  '''
  Given a url to the image model server and a media feed, extract image features
  and their confidences 
  '''

  def __init__(self, vocab, \
      url="http://119.81.249.157:3000/resources/1",
      batch_size = 100, qps = 1, **kwargs):

    '''
    - vocab: dictionary where key is the name and value is the index
    - url: the endpoint to hit when retrieving image resources
    '''
    self.url = url
    self._vocab = vocab
    self._batch_size = int(batch_size)
    self._qps = int(qps)
  
  def _transform(self, urls):
    res = np.zeros((len(urls), len(self._vocab)))

    for i in range(0, len(urls), self._batch_size):
      print >> sys.stderr, "[imgfeat] batch: %d" % i
      data = {}
      for mid,url in urls[i:i+self._batch_size]:
          data[mid] = url
      print >> sys.stderr, "[imgfeat] images length: %d" % len(data)
      print >> sys.stderr, "[imgfeat] hitting image server %s" % self.url
      r = requests.post(self.url, json=data)
      print >> sys.stderr, "[imgfeat] response: %d %s" % (r.status_code, r.text[:100])
      # Raises exception if NOT OK
      r.raise_for_status()
      for j,x in enumerate(r.json().itervalues()):
        idx = [ self._vocab[y['id']] for y in x ]
        vs = [ y['score'] for y in x ]
        res[i+j, idx] = vs
      time.sleep(1.0 / self._qps)

    return res

  def transform(self, uid, media_feed):
    print >> sys.stderr, "[%s] extracting posts" % uid
    print >> sys.stderr, "[%s] transforming posts into image features" % uid
    urls = []
    for m in media_feed:
      if hasattr(m.images, 'standard_resolution'):
        urls.append((m.id, m.images['standard_resolution'].url))
    return self._transform(self, urls) 

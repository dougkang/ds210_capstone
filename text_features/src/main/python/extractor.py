import json
import os
import sys
import requests
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

  def __init__(self, tfidf):
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
  Given a url to the iamge model server and a media feed, extract image features
  and their confidences 
  '''

  def __init__(self, vocab, url="http://119.81.249.157:3000/resources/1"):
    self.url = url
    self._vocab

  def transform(self, uid, media_feed):
    print >> sys.stderr, "[%s] extracting posts" % uid
    print >> sys.stderr, "[%s] transforming posts into image features" % uid
    data = {}
    for m in media_feed:
      if hasattr(m.images, 'standard_resolution'):
        data[m.id] = m.images['standard_resolution'].url
    print >> sys.stderr, "[%s] images length: %d" % (uid, len(data))
    print >> sys.stderr, "[%s] hitting image server %s" % (uid, self.url)
    r = requests.post(self.url, json=data)
    print >> sys.stderr, "[%s] response: %d " % (uid, r.status_code, r.text[:100])
    # Raises exception if NOT OK
    # TODO when image server is up and running again, uncomment this code
    # r.raise_for_status()
    # TODO retrieve ids, coerce into a matrix where id = voca
    # run them through tfidf
    # return r.json()
    raise Exception("Not implemented")

import argparse
import json
import pickle
import os
import sys
import time
from bottle import route, request, run, template
from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError, InstagramClientError

# Initialize our API
client_id = os.environ.get('INSTAGRAM_CLIENT_ID')
client_secret = os.environ.get('INSTAGRAM_CLIENT_SECRET')
feed_limit = 100

class TextFeatureExtractor(object):
  def predict(self, uid, access_token):
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
    print >> sys.stderr, "[%s] transforming posts into features" % uid
    bow = "" 
    for m in media_feed:
      if hasattr(m.caption, 'text'):
        bow = bow + ' ' + m.caption.text
      if hasattr(m, 'tags'):
        bow = bow + ' ' + ' '.join([ "tags:"+x.name for x in m.tags ])
    print >> sys.stderr, "[%s] text length: %d" % (uid, len(bow))
    # TODO some additional cleanup of text to go here
    return bow

extractor = TextFeatureExtractor()

if __name__ == '__main__':
  @route('/')
  def index():
    return "OK"

  @route('/predict/<access>/<uid>')
  def predict(access, uid):
    return extractor.predict(uid, access)
 
  print "Starting up server"
  run(host='localhost', port=8080)
  print "Server started, listening on port 8080"

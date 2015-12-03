import os
import sys
import time
from datetime import datetime
from pymongo import MongoClient
from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError

# Initialize our API
client_id = os.environ.get('INSTAGRAM_CLIENT_ID')
client_secret = os.environ.get('INSTAGRAM_CLIENT_SECRET')
redirect_uri = os.environ.get('INSTAGRAM_REDIRECT_URI')
host = 'localhost'
port = 27017
db = 'instagram'
collection = 'media_feeds'
feed_limit = 100
rate_limit = 5000
wait_secs = float(rate_limit) / (60*60)

client = MongoClient(host, port)
mongo = client[db][collection]

redirect_uri = "https://api.instagram.com/oauth/authorize/" + \
    "?client_id=%s&redirect_uri=%s&response_type=token" % (client_id, redirect_uri)

print ("URL: " + redirect_uri)
access_token = str(raw_input("Code: ").strip())

# Recreate the API object with the acess token now
api = InstagramAPI(
  access_token=access_token, 
  client_id=client_id,
  client_secret=client_secret)

print "Waiting %d secs between requests" % wait_secs
count = 0
private_count = 0
for i,line in enumerate(open(sys.argv[1]).readlines()):
  (uid,uname) = line.strip().split(',')
  print >> sys.stderr, "%d: User: %s|%s" % (i, uid, uname)
  try: 
    media_feed, mf_next_ = api.user_recent_media(user_id = uid, count = feed_limit)
    time.sleep(wait_secs)
    while mf_next_:
      print >> sys.stderr, "paging.",
      more, mf_next_ = api.user_recent_media(with_next_url=mf_next_)
      media_feed.extend(more)
      time.sleep(wait_secs)
    print >> sys.stderr
    print >> sys.stderr, "%s|%s has %d entries" % (uid, uname, len(media_feed))
    doc = {
	"name": uname,
        "feed": [ { 
          "id": x.id,
          "created": x.created_time, 
          "updated": datetime.now(),
          "caption": x.caption.text if hasattr(x.caption, "text") else "",
          "like_count": x.like_count if hasattr(x, "like_count") else 0,
          "link": x.link if hasattr(x, "link") else None, 
          "type": x.type if hasattr(x, "type") else "unknown",
          "filter": x.filter if hasattr(x, "filter") else None,
          "tags": [ y.name for y in x.tags ] if hasattr(x, "tags") else [],
          "location": { \
              "id": x.location.id, 
              "name": x.location.name if hasattr(x.location, "name") else None, \
              "latitude": x.location.point.latitude \
		if hasattr(x.location, "point") and hasattr(x.location.point, "latitude") else None, \
              "longitude": x.location.point.longitude \
		if hasattr(x.location, "point") and hasattr(x.location.point, "longitude") else None \
              } if hasattr(x, "location") else None,
          "images": {
            "low_resolution": x.images["low_resolution"].url,
            "standard_resolution": x.images["standard_resolution"].url,
            "thumbnail": x.images["thumbnail"].url
          }
        } for x in media_feed[:feed_limit] ] }
    mongo.update_one({ "_id": uid }, { "$set":  doc }, upsert=True)
    count = count + 1
  except InstagramAPIError as e:
    if e.status_code == 400:
      print >> sys.stderr, "User is private"
      private_count = private_count + 1
    else:
      print >> sys.stderr, "Error: " + str(e)
  except Exception as e:
    print >> sys.stderr, "Error: " + str(e)
    

print "Completed: %d count, %d private" % (count, private_count)

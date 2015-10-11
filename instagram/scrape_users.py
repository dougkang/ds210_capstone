import os
import sys
import time
from pymongo import MongoClient
from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError, InstagramClientError

# Initialize our API
client_id = os.environ.get('INSTAGRAM_CLIENT_ID')
client_secret = os.environ.get('INSTAGRAM_CLIENT_SECRET')
redirect_uri = os.environ.get('INSTAGRAM_REDIRECT_URI')
host = 'localhost'
port = 27017
db = 'instagram'
collection = 'users'
follower_limit = 1000
rate_limit = 5000
wait_secs = float(rate_limit) / (60*60)

client = MongoClient(host, port)
mongo = client[db][collection]

api = InstagramAPI(
  client_id=client_id,
  client_secret=client_secret)

queries = [ "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z" ]

visited = set()

print "Waiting %d secs between requests" % wait_secs
count = 0
private_count = 0
for i,q in enumerate(queries):
  print >> sys.stderr, "%d/%d: Query: %s" % (i, len(queries), q)
  users = api.user_search(q)
  for j,u in enumerate([ x for x in users if x not in visited ]):
    follower_count = 0
    visited.add(u)
    print >> sys.stderr, "%d/%d|%d/%d: Found user: %s:%s" \
        % (i, len(queries), j, len(users), u.id, u.username)
    try: 
      followers, next_ = api.user_followed_by(u.id) 
      time.sleep(wait_secs)
      while next_ and follower_count <= follower_limit:
        print >> sys.stderr
        print >> sys.stderr, "%s:%s has %d entries" % (u.id, u.username, len(followers))
        for k,uid in enumerate(followers):
          count = count + 1
          follower_count = follower_count + 1
          print >> sys.stderr, "%d/%d|%d/%d|%d/%d: %s:%s" \
              % (i, len(queries), j, len(users), follower_count, follower_limit, uid.id, uid.username)
          doc = { "_id": uid.id, "username": uid.username }
          try:
            mongo.insert_one(doc)
          except Exception as e:
            print >> sys.stderr, e
        print >> sys.stderr, "paging.",
        followers, next_ = api.user_followed_by(with_next_url=next_)
        time.sleep(wait_secs)
    except Exception as e:
      print >> sys.stderr, "call failed, skipping" + str(e)


print "Completed: %d count" % count
         

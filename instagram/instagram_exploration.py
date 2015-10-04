# Script built while exploring the Instagram API

from instagram.client import InstagramAPI

# Initialize our API
client_id = ''
access_token = ''
client_secret = ''
api = InstagramAPI(
    access_token=access_token, 
    client_id = client_id, 
    client_secret=client_secret)

# Retrieve a post from popular media
media = api.media_popular(count=1)[0]

for user in media.likes:
  # Grab a sample user from the post like
  uname = user.username
  uid = user.id
  media_feed, _next = api.user_recent_media(user_id = uid, count = 10)

  print "10 Latest Posts for %s:%s" % (uid, uname)
  for i,m in enumerate(media_feed):
    print "#" * 80
    print "%d: %s" % (i, m.id)
    print "#" * 80
    print "created: %s" % m.created_time
    print "caption: %s" % m.caption
    print "location: %s" % (m.location if hasattr(m, 'location') else "Unknown")
    print "tags: %s" % ", ".join([ x.name for x in m.tags ])
    print "%d comments, %d likes" % (m.comment_count, m.like_count)
    print "filter: %s" % m.filter
    print "link: %s" % m.link
    print "img: %s" % m.get_standard_resolution_url()
    print

  # We can also grab a list of users that follow or are followed by our user
  followers, _next = api.user_followed_by(uid)
  print "Followers of %s:%s" % (uid, uname)
  for i,u in enumerate(followers):
    print "%d. %s:%s" % (i+1, u.id, u.username)
  print 

  following, _next = api.user_follows(uid)
  print "Followees of %s:%s" % (uid, uname)
  for i,u in enumerate(following):
    print "%d. %s:%s" % (i+1, u.id, u.username)
  print 

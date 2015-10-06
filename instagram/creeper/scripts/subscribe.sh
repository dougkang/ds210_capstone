#!/bin/bash

. ./credentials.sh

CALLBACK=$1
RES=0

usage=<<EOF
Subscribes creeper to instagram notifications

Usage:
  sh subscribe.sh <callback_url>

Important Note: the callback url should correspond with the callback url that 
you set up for the client.
EOF

# Set up SF geography subscription
curl -v \
  -F "client_id=$INSTAGRAM_CLIENT_ID" \
  -F "client_secret=$INSTAGRAM_CLIENT_SECRET" \
  -F "object=geography" \
  -F "aspect=media" \
  -F "lng=-118.2500" \
  -F "lat=34.0500" \
  -F "radius=10000" \
  -F "verify_token=ds210" \
  -F "callback_url=http://$CALLBACK/notify/geo/sf" \
  https://api.instagram.com/v1/subscriptions/

RES=`expr $RES + $?`

echo
exit $RES

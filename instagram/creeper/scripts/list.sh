#!/bin/bash

. ./credentials.sh

CALLBACK=$1
RES=0

usage=<<EOF
Lists subscriptions for instagram notifications

Usage:
  sh list.sh

EOF

# Set up SF geography subscription
curl -s \
  "https://api.instagram.com/v1/subscriptions?client_id=$INSTAGRAM_CLIENT_ID&client_secret=$INSTAGRAM_CLIENT_SECRET"

RES=`expr $RES + $?`

echo ""
exit $RES

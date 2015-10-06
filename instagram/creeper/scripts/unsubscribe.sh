#!/bin/bash

. ./credentials.sh

CALLBACK=$1
RES=0

usage=<<EOF
Unsubscribes creeper from all instagram notifications

Usage:
  sh unsubscribe.sh
EOF

# Set up SF geography subscription
curl -s -X DELETE \
  "https://api.instagram.com/v1/subscriptions?client_id=$INSTAGRAM_CLIENT_ID&client_secret=$INSTAGRAM_CLIENT_SECRET&object=all"
RES=`expr $RES + $?`

echo
exit $RES

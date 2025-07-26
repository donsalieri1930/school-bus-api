#!/bin/bash

curl -s -X POST http://localhost:8000/sms \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "sms_to=test" \
  -d "sms_from=$1" \
  -d "sms_text=$2" \
  -d "sms_date=1753099200" \
  -d "username=test" \
  -d "MsgId=test"

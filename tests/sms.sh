#!/bin/bash


curl -s -X POST http://localhost:8000/sms \
  -H "Content-Type: application/json" \
  -d '{
    "sms_to": "",
    "sms_from": "'"$1"'",
    "sms_text": "'"$2"'",
    "sms_date": "1753099200",
    "username": "",
    "MsgId": ""
  }'

#!/bin/sh -x 
TOKEN=$(curl -s -H 'Content-type: application/json' -d '{"username":"alibaba", "password":"hi"}' localhost:8282/session/login | jq .auth_token | tr -d '"')")
curl -s -H "Authorization: Bearer ${TOKEN}" -H 'Content-type: application/json' -d '{"new_password":"ho"}' localhost:8282/session/password

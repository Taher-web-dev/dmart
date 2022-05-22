#!/bin/sh

SHORTNAME="alibaba"
DISPLAYNAME="Ali Baba"
EMAIL="ali@baba.com"
PASSWORD="hello"
INVITATION="ABCxyz"

API_URL=http://127.0.0.1:8282
CT="content-type: application/json"

echo "Delete previously created user (if any)"
rm -f ../space/users/.dm/${SHORTNAME}/meta.User.json
[[ -d ../space/users/.dm/${SHORTNAME}/ ]] && rmdir ../space/users/.dm/${SHORTNAME}/

echo "Create user"
CREATE=$(jq -c -n --arg displayname "$DISPLAYNAME" --arg email "$EMAIL" --arg password "$PASSWORD" '{display_name: $displayname, email: $email, password: $password}')
curl -s -H "$CT" -d "$CREATE" "${API_URL}/user/create/${SHORTNAME}?invitation=$INVITATION" | jq

echo "Login"
LOGIN=$(jq -c -n --arg shortname "$SHORTNAME" --arg password "$PASSWORD" '{shortname: $shortname, password: $password}')
curl -s -H "$CT" -d "$LOGIN" ${API_URL}/user/login | jq 

TOKEN=$(curl -s -H "$CT" -d "$LOGIN" ${API_URL}/user/login | jq .auth_token | tr -d '"')

AUTH="Authorization: Bearer ${TOKEN}"

echo "Set profile"
UPDATE='{"display_name": "a new one", "email":"howaboutthis@me.com"}'
curl -s -H "$AUTH" -H "$CT" -d "$UPDATE" $API_URL/user/profile | jq

echo "Get profile"
curl -s -H "$AUTH" -H "$CT" $API_URL/user/profile | jq

echo "Delete"
curl -s -H "$AUTH" -H "$CT" -d '{}' $API_URL/user/delete | jq

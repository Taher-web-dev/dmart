#!/bin/sh 

SHORTNAME="alibaba"
DISPLAYNAME="Ali Baba"
EMAIL="ali@baba.com"
PASSWORD="hello"

API_URL=http://127.0.0.1:8282
CT="content-type: application/json"

echo "Delete previously created user"
rm ../space/users/.dm/alibaba/meta.User.json
rmdir ../space/users/.dm/alibaba/

echo "Create user"
curl -s -H "$CT" -d "{\"password\":\"${PASSWORD}\",\"display_name\":\"${DISPLAYNAME}\",\"email\":\"${EMAIL}\"}" "${API_URL}/user/create/${SHORTNAME}?invitation=ABC" | jq

echo "Login"
curl -s -H "$CT" -d "{\"shortname\":\"${SHORTNAME}\",\"password\":\"${PASSWORD}\"}" ${API_URL}/user/login | jq 

TOKEN=$(curl -s -H "$CT" -d "{\"shortname\":\"${SHORTNAME}\",\"password\":\"${PASSWORD}\"}" ${API_URL}/user/login | jq .auth_token | tr -d '"')

AUTH="Authorization: Bearer ${TOKEN}"

echo "Set profile"


echo "Get profile"
curl -s -H "$AUTH" -H "$CT" $API_URL/user/profile | jq

echo "Delete"
curl -s -H "$AUTH" -H "$CT" $API_URL/user/delete | jq

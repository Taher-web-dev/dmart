#!/bin/sh

SHORTNAME="alibaba"
DISPLAYNAME="Ali Baba"
EMAIL="ali@baba.com"
PASSWORD="hello"
INVITATION="ABCxyz"

API_URL=http://127.0.0.1:8282
CT="content-type: application/json"

echo "Delete previously created user (if any)"
rm -f ../space/users/.dm/${SHORTNAME}/meta.user.json
[[ -d ../space/users/.dm/${SHORTNAME}/ ]] && rmdir ../space/users/.dm/${SHORTNAME}/

echo "Create user"
CREATE=$(jq -c -n --arg shortname "$SHORTNAME" --arg displayname "$DISPLAYNAME" --arg email "$EMAIL" --arg password "$PASSWORD" '{resource_type: "user", subpath: "users", shortname: $shortname, attributes:{display_name: $displayname, email: $email, password: $password}}')
curl -s -H "$CT" -d "$CREATE" "${API_URL}/user/create?invitation=$INVITATION" | jq

echo "Login"
LOGIN=$(jq -c -n --arg shortname "$SHORTNAME" --arg password "$PASSWORD" '{shortname: $shortname, password: $password}')
curl -s -H "$CT" -d "$LOGIN" ${API_URL}/user/login | jq 

TOKEN=$(curl -s -H "$CT" -d "$LOGIN" ${API_URL}/user/login | jq .auth_token | tr -d '"')

AUTH="Authorization: Bearer ${TOKEN}"

echo "Get profile"
curl -s -H "$AUTH" -H "$CT" $API_URL/user/profile | jq

echo "Update profile"
UPDATE=$(jq -c -n --arg shortname "$SHORTNAME" '{resource_type: "user", subpath: "users", shortname: $shortname, attributes:{display_name: "New display name", email: "new@email.coom"}}')
curl -s -H "$AUTH" -H "$CT" -d "$UPDATE" $API_URL/user/profile | jq

echo "Get profile"
curl -s -H "$AUTH" -H "$CT" $API_URL/user/profile | jq

SUBPATH="curl_content"
echo "Create Content Resource"
RECORD=$(jq -c -n --arg subpath "$SUBPATH" --arg shortname "$SHORTNAME"  '{resource_type: "content", subpath: $subpath, shortname: $shortname, attributes:{body: "this content created from curl request for testing"}}')
curl -s -H "$AUTH" -H "$CT" -d "$RECORD" ${API_URL}/managed/create | jq 

echo "Update The Content Resource"
RECORD=$(jq -c -n --arg subpath "$SUBPATH" --arg shortname "$SHORTNAME"  '{resource_type: "content", subpath: $subpath, shortname: $shortname, attributes:{body: "-----UPDATED-------this content created from curl request for testing"}}')
curl -s -H "$AUTH" -H "$CT" -d "$RECORD" ${API_URL}/managed/update | jq 


echo "Create Comment Resource Under The Content Resource"
COMMENT_SHORTNAME="Hello there"
SUBPATH="curl_content/$SHORTNAME"
RECORD=$(jq -c -n --arg subpath "$SUBPATH" --arg shortname "$COMMENT_SHORTNAME"  '{resource_type: "comment", subpath: $subpath, shortname: $shortname, is_attachment: true, attributes:{body: "A comment insdie the content resource"}}')
curl -s -H "$AUTH" -H "$CT" -d "$RECORD" ${API_URL}/managed/create | jq 

# echo "Delete"
# curl -s -H "$AUTH" -H "$CT" -d '{}' $API_URL/user/delete | jq

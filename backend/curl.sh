#!/bin/bash

SHORTNAME="alibaba"
DISPLAYNAME="Ali Baba"
EMAIL="ali@baba.com"
PASSWORD="hello"
INVITATION="ABCxyz"

API_URL=http://127.0.0.1:8282
CT="content-type: application/json"

echo "Delete previously created user (if any)"
rm -f ../space/users/.dm/${SHORTNAME}/meta.*.json
[[ -d ../space/users/.dm/${SHORTNAME}/ ]] && rmdir ../space/users/.dm/${SHORTNAME}/

echo "Delete previously created attachment (if any)"
[[ -d ../space/cool ]] && rm -r ../space/cool

echo -n "Create user: "
CREATE=$(jq -c -n --arg shortname "$SHORTNAME" --arg displayname "$DISPLAYNAME" --arg email "$EMAIL" --arg password "$PASSWORD" '{resource_type: "user", subpath: "users", shortname: $shortname, attributes:{display_name: $displayname, email: $email, password: $password}}')
curl -s -H "$CT" -d "$CREATE" "${API_URL}/user/create?invitation=$INVITATION" | jq .status

echo -n "Login: "
LOGIN=$(jq -c -n --arg shortname "$SHORTNAME" --arg password "$PASSWORD" '{shortname: $shortname, password: $password}')
curl -s -H "$CT" -d "$LOGIN" ${API_URL}/user/login | jq .status 

TOKEN=$(curl -s -H "$CT" -d "$LOGIN" ${API_URL}/user/login | jq .auth_token | tr -d '"')

AUTH="Authorization: Bearer ${TOKEN}"

echo -n "Get profile: "
curl -s -H "$AUTH" -H "$CT" $API_URL/user/profile | jq .status

echo -n "Update profile: "
UPDATE=$(jq -c -n --arg shortname "$SHORTNAME" '{resource_type: "user", subpath: "users", shortname: $shortname, attributes:{display_name: "New display name", email: "new@email.coom"}}')
curl -s -H "$AUTH" -H "$CT" -d "$UPDATE" $API_URL/user/profile | jq .status

echo -n "Get profile: "
curl -s -H "$AUTH" -H "$CT" $API_URL/user/profile | jq .status

SUBPATH="myposts"
echo -n "Create Content: " 
RECORD=$(jq -c -n --arg subpath "$SUBPATH" --arg shortname "$SHORTNAME"  '{resource_type: "content", subpath: $subpath, shortname: $shortname, attributes:{payload: {body: "this content created from curl request for testing", content_type: "text"}, tags: ["one","two"], content_type: "text", display_name: "This is a nice one", description: "Furhter description could help"}}')
curl -s -H "$AUTH" -H "$CT" -d "$RECORD" ${API_URL}/managed/create | jq .status 

#echo -n "Update Content: "
#RECORD=$(jq -c -n --arg subpath "$SUBPATH" --arg shortname "$SHORTNAME"  '{resource_type: "content", subpath: $subpath, shortname: $shortname, attributes:{body: "-----UPDATED-------this content created from curl request for testing"}}')
#curl -s -H "$AUTH" -H "$CT" -d "$RECORD" ${API_URL}/managed/update | jq .status 


echo -n "Comment on content: "
COMMENT_SHORTNAME="greatcomment"
COMMENT_SUBPATH="$SUBPATH/$SHORTNAME"
RECORD=$(jq -c -n --arg subpath "$COMMENT_SUBPATH" --arg shortname "$COMMENT_SHORTNAME"  '{resource_type: "comment", subpath: $subpath, shortname: $shortname, attributes:{body: "A comment insdie the content resource"}}')
curl -s -H "$AUTH" -H "$CT" -d "$RECORD" ${API_URL}/managed/create | jq .status 

echo -n "Create Schema: "
curl -s -H "$AUTH" -F 'request_record=@"../space/test/createschema.json"' -F 'payload_file=@"../space/test/schema.json"' ${API_URL}/managed/create_with_payload | jq .status

echo -n "Create content: "
curl -s -H "$AUTH" -F 'request_record=@"../space/test/createcontent.json"' -F 'payload_file=@"../space/test/data.json"' ${API_URL}/managed/create_with_payload  | jq  .status

echo -n "Upload attachment: "
curl -s -H "$AUTH" -F 'request_record=@"../space/test/createmedia.json"' -F 'payload_file=@"../space/test/logo.jpeg"' ${API_URL}/managed/create_with_payload  | jq .status

echo -n "Query content"
RECORD=$(jq -c -n --arg subpath "$SUBPATH" '{type: "subpath", subpath: $subpath}')
curl -s -H "$AUTH" -H "$CT" -d "$RECORD" ${API_URL}/managed/query | jq .status

echo -n "Delete user: "
curl -s -H "$AUTH" -H "$CT" -d '{}' $API_URL/user/delete | jq .status


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

echo -n -e "Create user: \t\t"
CREATE=$(jq -c -n --arg shortname "$SHORTNAME" --arg displayname "$DISPLAYNAME" --arg email "$EMAIL" --arg password "$PASSWORD" '{resource_type: "user", subpath: "users", shortname: $shortname, attributes:{display_name: $displayname, email: $email, password: $password}}')
curl -s -H "$CT" -d "$CREATE" "${API_URL}/user/create?invitation=$INVITATION" | jq .status

echo -n -e "Login: \t\t\t"
LOGIN=$(jq -c -n --arg shortname "$SHORTNAME" --arg password "$PASSWORD" '{shortname: $shortname, password: $password}')
curl -s -H "$CT" -d "$LOGIN" ${API_URL}/user/login | jq .status 

TOKEN=$(curl -s -H "$CT" -d "$LOGIN" ${API_URL}/user/login | jq .auth_token | tr -d '"')

AUTH="Authorization: Bearer ${TOKEN}"

echo -n -e "Get profile: \t\t"
curl -s -H "$AUTH" -H "$CT" $API_URL/user/profile | jq .status

echo -n -e "Update profile: \t"
UPDATE=$(jq -c -n --arg shortname "$SHORTNAME" '{resource_type: "user", subpath: "users", shortname: $shortname, attributes:{display_name: "New display name", email: "new@email.coom"}}')
curl -s -H "$AUTH" -H "$CT" -d "$UPDATE" $API_URL/user/profile | jq .status

echo -n -e "Get profile: \t\t"
curl -s -H "$AUTH" -H "$CT" $API_URL/user/profile | jq .status

SUBPATH="myposts"

echo -n -e "Create folder: \t\t"
RECORD=$(jq -c -n --arg subpath "$SUBPATH" --arg shortname "$SUBPATH"  '{resource_type: "folder", subpath: "content", shortname: $subpath, attributes:{tags: ["one","two"], display_name: "This is a nice one", description: "Furhter description could help"}}')
curl -s -H "$AUTH" -H "$CT" -d "$RECORD" ${API_URL}/managed/create | jq .status 


echo -n -e "Create Content: \t" 
RECORD=$(jq -c -n --arg subpath "$SUBPATH" --arg shortname "$SHORTNAME"  '{resource_type: "content", subpath: $subpath, shortname: $shortname, attributes:{payload: {body: "this content created from curl request for testing", content_type: "text"}, tags: ["one","two"], display_name: "This is a nice one", description: "Furhter description could help"}}')
curl -s -H "$AUTH" -H "$CT" -d "$RECORD" ${API_URL}/managed/create | jq .status 

#echo -n -e "Update Content: \t\t"
#RECORD=$(jq -c -n --arg subpath "$SUBPATH" --arg shortname "$SHORTNAME"  '{resource_type: "content", subpath: $subpath, shortname: $shortname, attributes:{body: "-----UPDATED-------this content created from curl request for testing"}}')
#curl -s -H "$AUTH" -H "$CT" -d "$RECORD" ${API_URL}/managed/update | jq .status 


echo -n -e "Comment on content: \t"
COMMENT_SHORTNAME="greatcomment"
COMMENT_SUBPATH="$SUBPATH/$SHORTNAME"
RECORD=$(jq -c -n --arg subpath "$COMMENT_SUBPATH" --arg shortname "$COMMENT_SHORTNAME"  '{resource_type: "comment", subpath: $subpath, shortname: $shortname, attributes:{body: "A comment insdie the content resource"}}')
curl -s -H "$AUTH" -H "$CT" -d "$RECORD" ${API_URL}/managed/create | jq .status 

echo -n -e "Create Schema: \t\t"
curl -s -H "$AUTH" -F 'request_record=@"../space/test/createschema.json"' -F 'payload_file=@"../space/test/schema.json"' ${API_URL}/managed/create_with_payload | jq .status

echo -n -e "Create content: \t"
curl -s -H "$AUTH" -F 'request_record=@"../space/test/createcontent.json"' -F 'payload_file=@"../space/test/data.json"' ${API_URL}/managed/create_with_payload  | jq  .status

echo -n -e "Upload attachment: \t"
curl -s -H "$AUTH" -F 'request_record=@"../space/test/createmedia.json"' -F 'payload_file=@"../space/test/logo.jpeg"' ${API_URL}/managed/create_with_payload  | jq .status

echo -n -e "Query content: \t\t"
RECORD=$(jq -c -n --arg subpath "$SUBPATH" '{type: "subpath", subpath: $subpath}')
curl -s -H "$AUTH" -H "$CT" -d "$RECORD" ${API_URL}/managed/query | jq .status

echo -n -e "Delete user: \t\t"
curl -s -H "$AUTH" -H "$CT" -d '{}' $API_URL/user/delete | jq .status


import json
import shutil
from fastapi.testclient import TestClient
from fastapi import status
from utils.settings import settings
import os

from main import app

client = TestClient(app)

user_shortname: str = "alibaba"
password: str = "hello"
token: str = ""

subpath: str = "cars"
shortname: str = "BMW"
attachment_shortname: str = "doors"

dirpath = f"{settings.space_root}/{subpath}/.dm/{shortname}"

attachment_record_path = "../space/test/createmedia.json"
attachment_media_path = "../space/test/logo.jpeg"
# attachment = {
#     "file": {
#         "logo.jpeg",
#         attachment_media_path,
#         # open(, "rb"),
#         "application/octet-stream",
#     },
#     "request": {
#         "createmedia.json",
#         attachment_record_path,
#         # open(attachment_record_path, "rb"),
#         "application/json",
#     },
# }

if os.path.exists(dirpath):
    shutil.rmtree(dirpath)


def test_login():
    headers = {"Content-Type": "application/json"}
    endpoint = "/user/login"
    request_data = {"shortname": user_shortname, "password": password}

    response = client.post(endpoint, json=request_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"] == "success"
    global token
    token = json_response["auth_token"]


def test_create_content_resource():
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/managed/create"
    request_data = {
        "resource_type": "content",
        "subpath": subpath,
        "shortname": shortname,
        "attributes": {"body": "2 door only"},
    }

    assert_code_and_status_success(
        client.post(endpoint, json=request_data, headers=headers)
    )


def test_create_user_resource():
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/managed/create"
    request_data = {
        "resource_type": "user",
        "subpath": subpath,
        "shortname": shortname,
        "attributes": {"email": "info@bmw.com", "password": "password"},
    }

    assert_code_and_status_success(
        client.post(endpoint, json=request_data, headers=headers)
    )


def test_update_user_resource():
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/managed/update"
    request_data = {
        "resource_type": "user",
        "subpath": subpath,
        "shortname": shortname,
        "attributes": {"email": "info@bmw.com", "password": "UPDATED"},
    }

    assert_code_and_status_success(
        client.post(endpoint, json=request_data, headers=headers)
    )


def test_create_folder_resource():
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/managed/create"
    request_data = {
        "resource_type": "folder",
        "subpath": subpath,
        "shortname": shortname,
        "attributes": {"body": "2 door only"},
    }

    assert_code_and_status_success(
        client.post(endpoint, json=request_data, headers=headers)
    )


def test_create_comment_resource():
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/managed/create"
    request_data = {
        "resource_type": "comment",
        "subpath": f"{subpath}/{shortname}",
        "shortname": attachment_shortname,
        "attributes": {"body": "A very speed car"},
    }

    assert_code_and_status_success(
        client.post(endpoint, json=request_data, headers=headers)
    )


def test_query_subpath():
    limit = 3
    filter_types = ["content", "comment", "user", "folder"]
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/managed/query"
    request_data = {
        "type": "subpath",
        "subpath": subpath,
        "filter_types": filter_types,
        "filter_shortnames": [shortname],
        "limit": limit,
        "offset": 0,
    }

    response = client.post(endpoint, json=request_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"] == "success"
    assert json_response["attributes"]["returned"] == limit
    for record in json_response["records"]:
        assert record["resource_type"] in filter_types


def test_delete_all():
    # DELETE USER
    response = delete_user()
    assert_code_and_status_success(response=response)

    # DELETE CONTENT RESOURCE
    response = delete_resource(
        resource="content", del_subpath=subpath, del_shortname=shortname
    )
    assert_code_and_status_success(response=response)

    # DELETE USER RESOURCE
    response = delete_resource(
        resource="user", del_subpath=subpath, del_shortname=shortname
    )
    assert_code_and_status_success(response=response)

    # DELETE FOLDER RESOURCE
    response = delete_resource(
        resource="folder", del_subpath=subpath, del_shortname=shortname
    )
    assert_code_and_status_success(response=response)

    # DELETE COMMENT RESOURCE
    response = delete_resource(
        resource="comment",
        del_subpath=f"{subpath}/{shortname}",
        del_shortname=attachment_shortname,
    )
    assert_code_and_status_success(response=response)

    shutil.rmtree(f"{settings.space_root}/{subpath}")


def delete_user():
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/user/delete"
    return client.post(endpoint, json={}, headers=headers)


def delete_resource(resource: str, del_subpath: str, del_shortname: str):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/managed/delete"
    request_data = {
        "resource_type": resource,
        "subpath": del_subpath,
        "shortname": del_shortname,
        "attributes": {},
    }

    return client.post(endpoint, json=request_data, headers=headers)


def test_upload_attachment_with_payload():
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = "managed/media"
    request_file = open(attachment_record_path, "rb")
    media_file = open(attachment_media_path, "rb")

    data = [
        ("request_record", ("createmedia.json", request_file, "application/json")),
        ("file", ("logo.jpeg", media_file, "application/octet-stream")),
    ]

    assert_code_and_status_success(client.post(endpoint, files=data, headers=headers))
    request_file.close()
    media_file.close()


def test_retrieve_attachment():
    headers = {"Authorization": f"Bearer {token}"}
    request_file = open(attachment_record_path, "rb")
    request_file_data = json.loads(request_file.read())

    subpath = request_file_data["subpath"]
    file_name = (
        request_file_data["shortname"] + "." + attachment_media_path.split(".")[-1]
    )
    endpoint = f"managed/media/{subpath}/{file_name}"

    response = client.get(endpoint, headers=headers)
    assert response.status_code == status.HTTP_200_OK

    request_file.close()


def assert_code_and_status_success(response):
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"] == "success"

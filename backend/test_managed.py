import json
import shutil
from fastapi.testclient import TestClient
from fastapi import status
from test_utils import check_validation, assert_code_and_status_success, check_not_found
from utils.settings import settings
import os

from main import app

client = TestClient(app)

PRODUCTS_SPACE: str = "products"
DEMO_SPACE: str = "demo"
USERS_SUBPATH: str = "users"

user_shortname: str = "alibaba"
password: str = "hello"

subpath: str = "cool"
shortname: str = "stuff"
attachment_shortname: str = "doors"

dirpath = f"{settings.spaces_folder}/{PRODUCTS_SPACE}/{subpath}/.dm/{shortname}"

attachment_record_path = f"{settings.spaces_folder}/{DEMO_SPACE}/test/createmedia.json"
attachment_payload_path = f"{settings.spaces_folder}/{DEMO_SPACE}/test/logo.jpeg"

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

    check_not_found(
        client.post(
            endpoint, json={**request_data, "shortname": "shortname"}, headers=headers
        )
    )

    response = client.post(
        endpoint, json={**request_data, "password": "password"}, headers=headers
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json().get("status") == "failed"
    assert response.json().get("error").get("type") == "auth"


def test_create_content_resource():
    headers = {"Content-Type": "application/json"}
    endpoint = "/managed/request"
    request_data = {
        "space_name": PRODUCTS_SPACE,
        "request_type": "create",
        "records": [
            {
                "resource_type": "content",
                "subpath": subpath,
                "shortname": shortname,
                "attributes": {"body": "2 door only"},
            }
        ],
    }

    assert_code_and_status_success(
        client.post(endpoint, json=request_data, headers=headers)
    )

    check_validation(
        client.post(
            endpoint,
            json={**request_data, "request_type": "request_type"},
            headers=headers,
        )
    )


def test_create_folder_resource():
    headers = {"Content-Type": "application/json"}
    endpoint = "/managed/request"
    request_data = {
        "space_name": PRODUCTS_SPACE,
        "request_type": "create",
        "records": [
            {
                "resource_type": "folder",
                "subpath": subpath,
                "shortname": shortname,
                "attributes": {},
            }
        ],
    }

    assert_code_and_status_success(
        client.post(endpoint, json=request_data, headers=headers)
    )

    check_validation(
        client.post(
            endpoint,
            json={**request_data, "request_type": "request_type"},
            headers=headers,
        )
    )


def test_create_comment_resource():
    headers = {"Content-Type": "application/json"}
    endpoint = "/managed/request"
    request_data = {
        "space_name": PRODUCTS_SPACE,
        "request_type": "create",
        "records": [
            {
                "resource_type": "comment",
                "subpath": f"{subpath}/{shortname}",
                "shortname": attachment_shortname,
                "attributes": {"body": "A very speed car"},
            }
        ],
    }

    assert_code_and_status_success(
        client.post(endpoint, json=request_data, headers=headers)
    )

    check_validation(
        client.post(
            endpoint,
            json={**request_data, "request_type": "request_type"},
            headers=headers,
        )
    )


def test_upload_attachment_with_payload():
    endpoint = "managed/resource_with_payload"
    with open(attachment_record_path, "rb") as request_file:
        media_file = open(attachment_payload_path, "rb")

        data = [
            ("request_record", ("createmedia.json", request_file, "application/json")),
            ("payload_file", ("logo.jpeg", media_file, "image/jpeg")),
        ]

        assert_code_and_status_success(
            client.post(endpoint, data={"space_name": PRODUCTS_SPACE}, files=data)
        )

    media_file.close()


def test_retrieve_attachment():

    with open(attachment_record_path, "rb") as request_file:
        request_file_data = json.loads(request_file.read())

        subpath = request_file_data["subpath"]
        file_name = (
            request_file_data["shortname"]
            + "."
            + attachment_payload_path.split(".")[-1]
        )
        print("\n\n SUBPATH: ", subpath, "\n FILENAME: ", file_name)
        endpoint = f"managed/payload/media/{PRODUCTS_SPACE}/{subpath}/{file_name}"
        response = client.get(endpoint)
        assert response.status_code == status.HTTP_200_OK


def test_query_subpath():
    limit = 2
    filter_types = ["content", "comment", "folder", "media"]
    headers = {"Content-Type": "application/json"}
    endpoint = "/managed/query"
    request_data = {
        "type": "subpath",
        "space_name": PRODUCTS_SPACE,
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
    assert "comment" in json_response["records"][0]["attachments"]
    assert "media" in json_response["records"][0]["attachments"]
    for record in json_response["records"]:
        assert record["resource_type"] in filter_types

    check_validation(
        client.post(
            endpoint,
            json={**request_data, "type": "request_type"},
            headers=headers,
        )
    )


def test_delete_all():
    # DELETE USER
    response = delete_user()
    assert_code_and_status_success(response=response)

    # DELETE CONTENT RESOURCE
    response = delete_resource(
        resource="content", del_subpath=subpath, del_shortname=shortname
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

    path = settings.spaces_folder / PRODUCTS_SPACE / subpath
    if path.is_dir():
        shutil.rmtree(path)


def delete_user():
    headers = {"Content-Type": "application/json"}
    endpoint = "/user/delete"
    return client.post(endpoint, json={}, headers=headers)


def delete_resource(resource: str, del_subpath: str, del_shortname: str):
    headers = {"Content-Type": "application/json"}
    endpoint = "/managed/request"
    request_data = {
        "space_name": PRODUCTS_SPACE,
        "request_type": "delete",
        "records": [
            {
                "resource_type": resource,
                "subpath": del_subpath,
                "shortname": del_shortname,
                "attributes": {},
            }
        ],
    }

    return client.post(endpoint, json=request_data, headers=headers)

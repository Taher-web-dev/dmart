from fastapi.testclient import TestClient
from fastapi import status
import os

from main import app

client = TestClient(app)

shortname: str = "alibaba"
display_name: str = "Ali Baba"
email: str = "ali@baba.com"
password: str = "hello"
invitation: str = "A1B2C3"
token: str = ""
subpath="nicepost"

dirpath = f"../space/users/.dm/{shortname}"
filepath = f"{dirpath}/meta.User.json"
if os.path.exists(filepath):
    os.remove(filepath)

if os.path.exists(dirpath):
    os.rmdir(dirpath)


def test_card():
    response = client.get("/")
    assert response.status_code == 200


def test_create_user():
    headers = {"Content-Type": "application/json"}
    endpoint = f"/user/create?invitation={invitation}"
    request_data = {
        "resource_type": "user",
        "subpath": "users",
        "shortname": shortname,
        "attributes": {
            "display_name": display_name,
            "email": email,
            "password": password,
        },
    }

    response = client.post(endpoint, json=request_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"] == "success"


def test_login():
    headers = {"Content-Type": "application/json"}
    endpoint = "/user/login"
    request_data = {"shortname": shortname, "password": password}

    response = client.post(endpoint, json=request_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"] == "success"
    global token
    token = json_response["auth_token"]


def test_get_profile():
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/user/profile"
    response = client.get(endpoint, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"] == "success"

def test_update_profile():
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/user/profile"
    request_data = {
        "resource_type": "user",
        "subpath": "users",
        "shortname": shortname,
        "attributes": {
            "display_name": display_name,
            "email": email,
        },
    }

    response = client.post(endpoint, json=request_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"] == "success"


def test_create_content_resource():
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/managed/create"
    request_data = {
        "resource_type": "content",
        "subpath": subpath,
        "shortname": shortname,
        "attributes": {
            "body": "this content created for testing"
        },
    }

    response = client.post(endpoint, json=request_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"] == "success"


def test_update_content_resource():
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/managed/update"
    request_data = {
        "resource_type": "content",
        "subpath": subpath,
        "shortname": shortname,
        "attributes": {
            "body": "UPDATED_OF(this content created for testing)"
        },
    }

    response = client.post(endpoint, json=request_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"] == "success"


def test_query_subpath():
    limit = 2
    filter_types = [
        "content",
        "comment",
        "user"
    ]
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/managed/query"
    request_data = {
        "type": "subpath",
        "subpath": subpath,
        "filter_types": filter_types,
        "filter_shortnames": [
            shortname
        ],
        "search": "string",
        "from_date": "2022-05-25T09:03:25.560Z",
        "to_date": "2022-05-25T09:03:25.560Z",
        "exclude_fields": [
            "string"
        ],
        "include_fields": [
            
        ],
        "sort_by": "string",
        "limit": limit,
        "offset": 0,
        "tags": [
            "string"
        ]
    }

    response = client.post(endpoint, json=request_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"] == "success"
    assert json_response["attributes"]["returned"] <= limit
    for record in json_response["records"]:
        assert record["resource_type"] in filter_types
        

def test_delete_resource():
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/managed/delete"
    request_data = {
        "resource_type": "content",
        "subpath": subpath,
        "shortname": shortname,
        "attributes": {
        },
    }

    response = client.post(endpoint, json=request_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"] == "success"


def test_delete_user():
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/user/delete"
    response = client.post(endpoint, json={}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"] == "success"


if __name__ == "__main__":
    test_create_user()
    test_login()
    test_get_profile()
    test_update_profile()
    test_create_content_resource()
    test_update_content_resource()
    test_query_subpath()
    test_delete_resource()
    test_delete_user()

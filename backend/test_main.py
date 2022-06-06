from fastapi.testclient import TestClient
from fastapi import status
import os
import test_managed as managed
from utils.settings import settings

from main import app

client = TestClient(app)

MANAGEMENT_SPACE : str ="management"
USERS_SUBPATH : str ="users"

shortname: str = "alibaba"
displayname: str = "Ali Baba"
email: str = "ali@baba.com"
password: str = "hello"
invitation: str = "A1B2C3"
token: str = ""
subpath = "nicepost"

dirpath = f"{settings.spaces_folder}/{MANAGEMENT_SPACE}/{USERS_SUBPATH}/.dm/{shortname}"
filepath = f"{dirpath}/meta.user.json"
if os.path.exists(filepath):
    os.remove(filepath)

if os.path.exists(dirpath):
    os.rmdir(dirpath)


def test_card():
    response = client.get("/")
    assert response.status_code == 200


def test_create_user():
    headers = {"Content-Type": "application/json"}
    endpoint = f"/user/create"
    request_data = {
        "resource_type": "user",
        "subpath": "users",
        "shortname": shortname,
        "attributes": {
            "displayname": displayname,
            "email": email,
            "password": password,
            "invitation": invitation
        },
    }
    response = client.post(endpoint, json=request_data, headers=headers)
    # print("\n\n\n RESPONSE: ", response.json())
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


def test_get_profile():
    headers = {"Content-Type": "application/json"}
    endpoint = "/user/profile"
    response = client.get(endpoint, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"] == "success"


def test_update_profile():
    headers = {"Content-Type": "application/json"}
    endpoint = "/user/profile"
    request_data = {
        "resource_type": "user",
        "subpath": "users",
        "shortname": shortname,
        "attributes": {
            "displayname": displayname,
            "email": email,
        },
    }

    response = client.post(endpoint, json=request_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"] == "success"


if __name__ == "__main__":
    test_create_user()
    test_login()
    test_get_profile()
    test_update_profile()
    managed.test_create_content_resource()
    managed.test_create_comment_resource()
    managed.test_create_folder_resource()
    managed.test_upload_attachment_with_payload()
    managed.test_query_subpath()
    managed.test_delete_all()

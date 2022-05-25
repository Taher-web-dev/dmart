from pathlib import Path
import shutil
from urllib import response
from fastapi.testclient import TestClient
from fastapi import status
import os

from main import app

client = TestClient(app)

user_shortname: str = "alibaba"
password: str = "hello"
token: str = ""

subpath:str = "cars"
shortname: str = "BMW"
attachment_shortname: str = "doors"

dirpath = f"../space/{subpath}/.dm/{shortname}"        

if os.path.exists(dirpath):
    shutil.rmtree(dirpath)

def test_login():
    headers = {"Content-Type": "application/json"}
    endpoint = "/user/login"
    request_data = {"shortname": user_shortname, "password": password}

    response = client.post(endpoint, json=request_data, headers=headers)
    print("\n\n\nresponse.json()", response.json())
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
        "attributes": {
            "body": "2 door only"
        },
    }

    assert_code_and_status_success(client.post(endpoint, json=request_data, headers=headers))


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
    print("\n\n\n\nresponse.json()", response.json())
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"] == "success"


def test_create_user_resource():
    print("\n\n\nTOKEN: ", token)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/managed/create"
    request_data = {
        "resource_type": "user",
        "subpath": subpath,
        "shortname": shortname,
        "attributes": {
            "email":"info@bmw.com",
            "password":"password"
        },
    }

    assert_code_and_status_success(client.post(endpoint, json=request_data, headers=headers))

def test_update_user_resource():
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/managed/update"
    request_data = {
        "resource_type": "user",
        "subpath": subpath,
        "shortname": shortname,
        "attributes": {
            "email":"info@bmw.com",
            "password":"UPDATED"
        },
    }

    assert_code_and_status_success(client.post(endpoint, json=request_data, headers=headers))

def test_create_folder_resource():
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/managed/create"
    request_data = {
        "resource_type": "folder",
        "subpath": subpath,
        "shortname": shortname,
        "attributes": {
            "body": "2 door only"
        },
    }

    assert_code_and_status_success(client.post(endpoint, json=request_data, headers=headers))


def test_create_comment_resource():
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    endpoint = "/managed/create"
    request_data = {
        "resource_type": "comment",
        "subpath": f"{subpath}/{shortname}",
        "shortname": attachment_shortname,
        "attributes": {
            "body": "A very speed car"
        },
    }

    assert_code_and_status_success(client.post(endpoint, json=request_data, headers=headers))


def test_query_subpath():
    limit = 3
    filter_types = [
        "content",
        "comment",
        "user",
        "folder"
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



def assert_code_and_status_success(response):
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

import csv
from io import StringIO
import json

import requests
from models.enums import RequestType
from utils import db
import models.core as core
import models.api as api

url = "http://127.0.0.1:8000"

shortname = "string"
password = "string"

file_path = "../spaces/demo/test/subaccounts.csv"
resource_type = "content"
schema_shortname = "subaccount"

request_session = requests.Session()

def login(shortname: str, password: str):
    response = request_session.post(url=f"{url}/user/login", json={"shortname": shortname, "password": password})
    return response.json()


def import_resources_from_csv(url, file_path, resource_type, schema_shortname):

    space_name = "products"
    subpath = "content"

    with open(file_path, 'rb') as csv_file:
        contents = csv_file.read()

    decoded = contents.decode()
    buffer = StringIO(decoded)
    csv_reader = csv.DictReader(buffer)

    schema_path = db.payload_path(
        space_name, "schema", core.Schema) / f"{schema_shortname}.json"
    with open(schema_path) as schema_file:
        schema_content = json.load(schema_file)

    schema_properties = schema_content["properties"]
    data_types_mapper = {
        'integer': int,
        "string": str
    }

    records: list = []
    for row in csv_reader:
        shortname: str = ""
        payload_object: dict = {}
        for key, value in row.items():
            if not value:
                continue

            keys_list = key.split(".")
            current_schema_property = schema_properties
            for item in keys_list:
                current_schema_property = current_schema_property[item.strip()]
            value = data_types_mapper[current_schema_property["type"]](value)

            match len(keys_list):
                case 1:
                    payload_object[keys_list[0].strip()] = value
                case 2:
                    if keys_list[0].strip() not in payload_object:
                        payload_object[keys_list[0].strip()] = {}
                    payload_object[keys_list[0].strip(
                    )][keys_list[1].strip()] = value
                case 3:
                    if keys_list[0].strip() not in payload_object:
                        payload_object[keys_list[0].strip()] = {}
                    if keys_list[1].strip() not in payload_object[keys_list[0].strip()]:
                        payload_object[keys_list[0].strip(
                        )][keys_list[1].strip()] = {}
                    payload_object[keys_list[0].strip(
                    )][keys_list[1].strip()][keys_list[2].strip()] = value
                case _:
                    continue

            if key == "id":
                shortname = value

        if shortname:
            payload_object["schema_shortname"] = schema_shortname
            records.append(core.Record(
                resource_type=resource_type,
                shortname=shortname,
                subpath=subpath,
                attributes=payload_object
            ))

    request_data = api.Request(
        space_name=space_name,
        request_type=RequestType.create,
        records=records
    )
    response = request_session.post(url=f"{url}/managed/request", json=request_data.dict())
    return response.json()


if __name__ == "__main__":
    login_response = login(shortname, password)

    result = import_resources_from_csv(url, file_path, resource_type, schema_shortname)

    if result["status"] == 'success':
        print("Data Imported successfully")
    else:
        print("Failed to load data, errors: \n", result.error)

import csv
import hashlib
from io import StringIO
from fastapi import APIRouter, Depends, UploadFile, Path, Form, status
from fastapi.responses import FileResponse
import models.api as api
import models.core as core
from models.enums import ContentType, RequestType
import utils.db as db
import utils.regex as regex
import sys
from jsonschema import validate
import json
from pathlib import Path as FSPath
from utils.settings import settings
from utils.jwt import JWTBearer

router = APIRouter()


@router.post("/query", response_model=api.Response, response_model_exclude_none=True)
async def query_entries(query: api.Query,
    _=Depends(JWTBearer())) -> api.Response:
    total, records = await db.serve_query(query)
    return api.Response(
        status=api.Status.success,
        records=records,
        attributes={"total": total, "returned": len(records)},
    )


@router.post("/request", response_model=api.Response, response_model_exclude_none=True)
async def serve_request( request: api.Request, owner_shortname=Depends(JWTBearer())) -> api.Response:
    if request.space_name not in settings.space_names:
        raise api.Exception(
            status.HTTP_400_BAD_REQUEST,
            api.Error(
                type="reqeust",
                code=202,
                message="Space name provided is empty or invalid",
            ),
        )
    if not request.records:
        raise api.Exception(
            status.HTTP_400_BAD_REQUEST,
            api.Error(
                type="reqeust",
                code=202,
                message="Request records cannot be empty",
            ),
        )

    match request.request_type:
        case api.RequestType.create:
            for record in request.records:
                resource_obj = core.Meta.from_record(record=record, shortname=owner_shortname)
                # Check if the payload should goes in the meta file or in a separate file
                # if record.payload_location:
                #    db.save(request.space_name, record.subpath, resource_obj)
                # else :

                # Validate schema if present
                if "schema_shortname" in record.attributes:
                    schema_shortname = record.attributes["schema_shortname"]
                    resource_obj.payload.schema_shortname = schema_shortname
                    record.attributes.pop("schema_shortname")

                    schema_payload_path = db.payload_path(
                        request.space_name, "schema", core.Schema
                    )
                    validate_payload_with_schema(
                        schema_path=schema_payload_path / f"{schema_shortname}.json",
                        payload_data=record.attributes,
                    )

                separate_payload_data = {}
                if resource_obj.payload:
                    separate_payload_data = resource_obj.payload.body
                    resource_obj.payload.body = record.shortname + ".json"

                await db.save(request.space_name, record.subpath, resource_obj)

                if separate_payload_data:
                    await db.save_payload_from_json(
                        request.space_name,
                        record.subpath,
                        resource_obj,
                        separate_payload_data,
                    )

        case api.RequestType.update:
            for record in request.records:
                resource_obj = core.Meta.from_record(record=record, shortname=owner_shortname)
                await db.update(request.space_name, record.subpath, resource_obj)
        case api.RequestType.delete:
            for record in request.records:
                cls = getattr(
                    sys.modules["models.core"], record.resource_type.capitalize()
                )
                item = db.load(
                    request.space_name, record.subpath, record.shortname, cls
                )
                db.delete(request.space_name, record.subpath, item)
        case api.RequestType.move:
            for record in request.records:
                if (
                    "dest_subpath" not in record.attributes
                    and not record.attributes["dest_subpath"]
                ) and (
                    "dest_shortname" not in record.attributes
                    and not record.attributes["dest_shortname"]
                ):
                    raise api.Exception(
                        status.HTTP_400_BAD_REQUEST,
                        api.Error(
                            type="move",
                            code=202,
                            message="Please provide a new path or a new shortname",
                        ),
                    )

                if (
                    "src_subpath" not in record.attributes
                    and not record.attributes["src_subpath"]
                ) and (
                    "src_shortname" not in record.attributes
                    and not record.attributes["src_shortname"]
                ):
                    raise api.Exception(
                        status.HTTP_400_BAD_REQUEST,
                        api.Error(
                            type="move",
                            code=202,
                            message="Please provide a new path or a new shortname",
                        ),
                    )
                cls = getattr(
                    sys.modules["models.core"], record.resource_type.capitalize()
                )
                item = db.load(
                    request.space_name,
                    record.attributes["src_subpath"],
                    record.attributes["src_shortname"],
                    cls,
                )
                await db.move(
                    request.space_name,
                    record.attributes["src_subpath"],
                    record.attributes["src_shortname"],
                    record.attributes["dest_subpath"],
                    record.attributes["dest_shortname"],
                    item,
                )
    return api.Response(status=api.Status.success)


@router.get(
    "/payload/{resource_type}/{space_name}/{subpath:path}/{shortname}.{ext}",
    response_model_exclude_none=True,
)
async def retrieve_entry_or_attachment_payload(
    resource_type: api.ResourceType,
    space_name: str = Path(..., regex=regex.SPACENAME),
    subpath: str = Path(..., regex=regex.SUBPATH),
    shortname: str = Path(..., regex=regex.SHORTNAME),
    ext: str = Path(..., regex=regex.EXT),
    _=Depends(JWTBearer())
) -> FileResponse:

    cls = getattr(sys.modules["models.core"], resource_type.capitalize())
    meta = db.load(space_name, subpath, shortname, cls)
    if (
        meta.payload is None
        or meta.payload.body is None
        or meta.payload.body != f"{shortname}.{ext}"
    ):
        raise api.Exception(
            status.HTTP_400_BAD_REQUEST,
            error=api.Error(
                type="media", code=220, message="Request object is not available"
            ),
        )

    # TODO check security labels for pubblic access
    payload_path = db.payload_path(space_name, subpath, cls)
    return FileResponse(payload_path / str(meta.payload.body))


@router.post(
    "/resource_with_payload",
    response_model=api.Response,
    response_model_exclude_none=True,
)
async def create_or_update_resource_with_payload(
    payload_file: UploadFile,
    request_record: UploadFile,
    space_name: str = Form(...),
    owner_shortname=Depends(JWTBearer())
):
    # NOTE We currently make no distinction between create and update. in such case update should contain all the data every time.
    if space_name not in settings.space_names:
        raise api.Exception(
            status.HTTP_400_BAD_REQUEST,
            api.Error(
                type="reqeust",
                code=202,
                message="Space name provided is empty or invalid",
            ),
        )
    if payload_file.filename.endswith(".json"):
        resource_content_type = ContentType.json
    elif payload_file.content_type == "text/markdown":
        resource_content_type = ContentType.markdown
    elif "image/" in payload_file.content_type:
        resource_content_type = ContentType.image
    else:
        raise api.Exception(
            status.HTTP_406_NOT_ACCEPTABLE,
            api.Error(
                type="attachment",
                code=217,
                message="The file type is not supported",
            ),
        )

    record = core.Record.parse_raw(request_record.file.read())
    sha1 = hashlib.sha1()
    sha1.update(payload_file.file.read())
    checksum = sha1.hexdigest()
    await payload_file.seek(0)
    resource_obj = core.Meta.from_record(record=record, shortname=owner_shortname)
    resource_obj.payload = core.Payload(
        content_type=resource_content_type,
        checksum=checksum,
        body=f"{record.shortname}." + payload_file.filename.split(".")[1],
    )

    if (
        not isinstance(resource_obj, core.Attachment)
        and not isinstance(resource_obj, core.Content)
        and not isinstance(resource_obj, core.Schema)
    ):
        raise api.Exception(
            status.HTTP_400_BAD_REQUEST,
            api.Error(
                type="attachment",
                code=217,
                message="Only resources of type 'attachment' or 'content' are allowed",
            ),
        )

    if (
        resource_content_type == ContentType.json
        and "schema_shortname" in record.attributes
    ):
        resource_obj.payload.schema_shortname = record.attributes["schema_shortname"]
        schema_payload_path = db.payload_path(space_name, "schema", core.Schema)
        validate_payload_with_schema(
            schema_path=schema_payload_path
            / f"{resource_obj.payload.schema_shortname}.json",
            payload_data=payload_file,
        )

    await db.save(space_name, record.subpath, resource_obj)
    await db.save_payload(space_name, record.subpath, resource_obj, payload_file)
    return api.Response(status=api.Status.success)


def validate_payload_with_schema(schema_path: FSPath, payload_data: UploadFile | dict):
    schema = json.loads(FSPath(schema_path).read_text())
    if not isinstance(payload_data, dict):
        data = json.load(payload_data.file)
        payload_data.file.seek(0)
    else:
        data = payload_data

    validate(instance=data, schema=schema)


@router.post(
    "/resources_from_csv/{resource_type}/{space_name}/{subpath:path}/{schema_shortname}",
    response_model=api.Response,
    response_model_exclude_none=True,
)
async def import_resources_from_csv(
    resources_file: UploadFile,
    resource_type: api.ResourceType,
    space_name: str = Path(..., regex=regex.SPACENAME),
    subpath: str = Path(..., regex=regex.SUBPATH),
    schema_shortname: str = Path(..., regex=regex.SHORTNAME),
    owner_shortname=Depends(JWTBearer()),
):

    contents = await resources_file.read()
    decoded = contents.decode()
    buffer = StringIO(decoded)
    csv_reader = csv.DictReader(buffer)

    schema_path = (
        db.payload_path(space_name, "schema", core.Schema) / f"{schema_shortname}.json"
    )
    with open(schema_path) as schema_file:
        schema_content = json.load(schema_file)

    data_types_mapper = {"integer": int, "number": float, "string": str}

    records: list = []
    for row in csv_reader:
        shortname: str = ""
        payload_object: dict = {}
        for key, value in row.items():
            if not key:
                continue

            if key == "shortname":
                shortname = value
                continue

            keys_list = key.split(".")
            current_schema_property = schema_content
            for item in keys_list:
                current_schema_property = current_schema_property["properties"][
                    item.strip()
                ]

            if not value:
                value = "null" if current_schema_property["type"] == "string" else "0"

            value = data_types_mapper[current_schema_property["type"]](
                value
                if current_schema_property["type"] == "string"
                else value.replace(",", "")
            )

            match len(keys_list):
                case 1:
                    payload_object[keys_list[0].strip()] = value
                case 2:
                    if keys_list[0].strip() not in payload_object:
                        payload_object[keys_list[0].strip()] = {}
                    payload_object[keys_list[0].strip()][keys_list[1].strip()] = value
                case 3:
                    if keys_list[0].strip() not in payload_object:
                        payload_object[keys_list[0].strip()] = {}
                    if keys_list[1].strip() not in payload_object[keys_list[0].strip()]:
                        payload_object[keys_list[0].strip()][keys_list[1].strip()] = {}
                    payload_object[keys_list[0].strip()][keys_list[1].strip()][
                        keys_list[2].strip()
                    ] = value
                case _:
                    continue

        if shortname:
            payload_object["schema_shortname"] = schema_shortname
            records.append(
                core.Record(
                    resource_type=resource_type,
                    shortname=shortname,
                    subpath=subpath,
                    attributes=payload_object,
                )
            )

    return await serve_request(
        request=api.Request(
            space_name=space_name, request_type=RequestType.create, records=records
        ),
        owner_shortname=owner_shortname,
    )

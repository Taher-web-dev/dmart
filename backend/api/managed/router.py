import re
from fastapi import APIRouter, Depends, UploadFile, Path
from fastapi.responses import FileResponse

import models.api as api
import models.core as core
from models.enums import ContentType
import utils.db as db
import utils.regex as regex
from utils.jwt import JWTBearer
import sys
from jsonschema import validate
import json
from pathlib import Path as FSPath

router = APIRouter()


@router.post("/query", response_model=api.Response, response_model_exclude_none=True)
async def query_entries(query: api.Query) -> api.Response:
    total, records = db.serve_query(query)
    return api.Response(
        status=api.Status.success,
        records=records,
        attributes={"total": total, "returned": len(records)},
    )


@router.post("/create", response_model=api.Response, response_model_exclude_none=True)
async def create_entry_or_attachment(
    record: core.Record, shortname=Depends(JWTBearer())
) -> api.Response:
    resource_obj = core.Meta.from_record(record=record, shortname=shortname)
    db.save(record.subpath, resource_obj)
    return api.Response(status=api.Status.success)


@router.post("/update", response_model=api.Response, response_model_exclude_none=True)
async def update_entry_or_attachment(
    record: core.Record, shortname=Depends(JWTBearer())
) -> api.Response:
    resource_obj = core.Meta.from_record(record=record, shortname=shortname)
    db.update(record.subpath, resource_obj)
    return api.Response(status=api.Status.success)


@router.post("/delete", response_model=api.Response, response_model_exclude_none=True)
async def delete_entry(record: core.Record) -> api.Response:
    cls = getattr(sys.modules["models.core"], record.resource_type.capitalize())
    item = db.load(record.subpath, record.shortname, cls)
    db.delete(record.subpath, item)
    return api.Response(status=api.Status.success)


@router.post("/move", response_model=api.Response, response_model_exclude_none=True)
async def move_entry(
    src_subpath: str,
    src_shortname: str,
    dest_subpath,
    dest_shortname: str,
    resource_type: api.ResourceType,
) -> api.Response:
    cls = getattr(sys.modules["models.core"], resource_type.capitalize())
    item = db.load(src_subpath, src_shortname, cls)
    if not dest_subpath and not dest_shortname:
        raise api.Exception(
            404,
            api.Error(
                type="move",
                code=202,
                message="Please provide a new path or a new shortname",
            ),
        )

    db.move(src_subpath, src_shortname, dest_subpath, dest_shortname, item)
    return api.Response(status=api.Status.success)


@router.get(
    "/payload/{subpath:path}/{shortname}.{ext}", response_model_exclude_none=True
)
async def retrieve_entry_or_attachment_payload(
    subpath: str = Path(..., regex=regex.SUBPATH),
    shortname: str = Path(..., regex=regex.SHORTNAME),
    ext: str = Path(..., regex=regex.EXT),
) -> FileResponse:

    if re.match(regex.IMG_EXT, ext):
        meta_class_type = core.Media
    elif ext in ["json", "md"]:
        meta_class_type = core.Content
    else:
        raise api.Exception(
            404,
            error=api.Error(
                type="media", code=220, message="Request object is not available"
            ),
        )

    meta = db.load(subpath, shortname, meta_class_type)
    if (
        meta.payload is None
        or meta.payload.body is None
        or meta.payload.body != f"{shortname}.{ext}"
    ):
        raise api.Exception(
            404,
            error=api.Error(
                type="media", code=220, message="Request object is not available"
            ),
        )

    # TODO check security labels for pubblic access
    payload_path = db.payload_path(subpath, meta_class_type)
    return FileResponse(payload_path / str(meta.payload.body))


@router.post(
    "/create_with_payload",
    response_model=api.Response,
    response_model_exclude_none=True,
)
async def create_entry_or_attachment_with_payload(
    payload_file: UploadFile, request_record: UploadFile, shortname=Depends(JWTBearer())
):
    if payload_file.filename.endswith(".json"):
        resource_content_type = ContentType.json
    elif payload_file.content_type == "text/markdown":
        resource_content_type = ContentType.markdown
    elif "image/" in payload_file.content_type:
        resource_content_type = ContentType.image
    else:
        raise api.Exception(
            406,
            api.Error(
                type="attachment",
                code=217,
                message="The file type is not supported",
            ),
        )

    record = core.Record.parse_raw(request_record.file.read())
    resource_obj = core.Meta.from_record(record=record, shortname=shortname)
    resource_obj.payload = core.Payload(  # detect the resource type
        content_type=resource_content_type,
        body=record.shortname + "." + payload_file.filename.split(".")[1],
    )

    if (
        not isinstance(resource_obj, core.Attachment)
        and not isinstance(resource_obj, core.Content)
        and not isinstance(resource_obj, core.Schema)
    ):
        raise api.Exception(
            406,
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
        schema_payload_path = db.payload_path("schema", core.Schema)
        schema = json.loads(
            FSPath(
                schema_payload_path / f"{resource_obj.payload.schema_shortname}.json"
            ).read_text()
        )
        data = json.load(payload_file.file)
        validate(instance=data, schema=schema)
        await payload_file.seek(0)

    db.save(record.subpath, resource_obj)
    await db.save_payload(
        record.subpath, resource_obj, payload_file
    )  # save any type of entries
    return api.Response(status=api.Status.success)

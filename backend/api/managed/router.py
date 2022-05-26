from fastapi import APIRouter, Depends, UploadFile, Path
from fastapi.responses import FileResponse
import json
import models.api as api
import models.core as core
import utils.db as db
import utils.regex as regex
from utils.jwt import JWTBearer
import sys

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
async def move_entry(record: core.Record) -> api.Response:
    cls = getattr(sys.modules["models.core"], record.resource_type.capitalize())
    item = db.load(record.subpath, record.shortname, cls)
    if "new_path" not in record.attributes or not record.attributes["new_path"]:
        raise api.Exception(
            404, api.Error(type="move", code=202, message="error moving")
        )
    newpath = record.attributes["new_path"]
    db.move(record.subpath, newpath, item)
    return api.Response(status=api.Status.success)


@router.get("/media/{subpath:path}/{shortname}.{ext}")
async def get_media(
    subpath: str = Path(..., regex=regex.SUBPATH),
    shortname: str = Path(..., regex=regex.SHORTNAME),
    ext: str = Path(..., regex=regex.EXT),
) -> FileResponse:
    path, filename = db.metapath(subpath, shortname, core.Media)
    meta = db.load(subpath, shortname, core.Media)
    if (
        meta.payload is None
        or meta.payload.body is None
        or meta.payload.body != f"{shortname}.{ext}"
        or shortname != filename.replace(".json", "")
    ):
        raise api.Exception(
            404,
            error=api.Error(
                type="media", code=220, message="Request object is not available"
            ),
        )

    # TODO check security labels for pubblic access

    media_file = path / str(meta.payload.body)
    return FileResponse(media_file)


@router.post("/media", response_model=api.Response, response_model_exclude_none=True)
async def upload_attachment_with_payload(
    file: UploadFile, request: UploadFile, shortname=Depends(JWTBearer())
):
    record = core.Record.parse_raw(request.file.read())
    resource_obj = core.Meta.from_record(record=record, shortname=shortname)

    if not isinstance(resource_obj, core.Attachment):
        raise api.Exception(
            406,
            api.Error(
                type="attachment",
                code=217,
                message="Only resources of type 'attachment' are allowed",
            ),
        )

    db.save(record.subpath, resource_obj)
    await db.save_payload(record.subpath, resource_obj, file)
    return api.Response(status=api.Status.success)

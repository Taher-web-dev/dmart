from uuid import uuid5
from fastapi import APIRouter, Depends

import models.api as api
import models.core as core
import utils.db as db
from utils.jwt import JWTBearer
import sys

router = APIRouter()


@router.post("/query", response_model=api.Response, response_model_exclude_none=True)
async def query_request(query: api.Query) -> api.Response:
    return db.serve_query(query)


@router.post("/create", response_model=api.Response, response_model_exclude_none=True)
async def change(record: api.Record, shortname=Depends(JWTBearer())) -> api.Response:
    resource_obj = core.Meta.from_record(record=record, shortname=shortname)
    db.save(record.subpath, resource_obj)
    return api.Response(status=api.Status.success)
    


@router.post("/update", response_model=api.Response, response_model_exclude_none=True)
async def update(record: api.Record, shortname=Depends(JWTBearer())) -> api.Response:
    resource_obj = core.Meta.from_record(record=record, shortname=shortname)
    db.update(record.subpath, resource_obj)
    return api.Response(status=api.Status.success)


@router.post("/delete", response_model=api.Response, response_model_exclude_none=True)
async def delete(record: api.Record) -> api.Response:
    cls = getattr(sys.modules["models.core"], record.resource_type.capitalize())
    item = db.load(record.subpath, record.shortname, cls)
    db.delete(record.subpath, item)
    return api.Response(status=api.Status.success)


@router.post("/move", response_model=api.Response, response_model_exclude_none=True)
async def move(record: api.Record) -> api.Response:
    cls = getattr(sys.modules["models.core"], record.resource_type.capitalize())
    item = db.load(record.subpath, record.shortname, cls)
    if "new_path" not in record.attributes or not record.attributes["new_path"]:
        raise api.Exception(404, api.Error(type="move", code=202, message="error moving"))
    newpath = record.attributes["new_path"]
    db.move(record.subpath, newpath, item)
    return api.Response(status=api.Status.success)


@router.get("/media/{pathname}")
async def get_media():
    return {}


# Upload media attachment
@router.post("/media")
async def upload_media():
    return {}

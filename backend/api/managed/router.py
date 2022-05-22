
from fastapi import APIRouter, Depends

import models.api as api
import models.core as core
import utils.db as db
from utils.jwt import JWTBearer

router = APIRouter()


@router.post("/query", response_model=api.Response, response_model_exclude_none=True)
async def query_request(query: api.Query) -> api.Response:
    return db.serve_query(query)


@router.post("/create", response_model=api.Response, response_model_exclude_none=True)
async def change(record: api.Record, shortname=Depends(JWTBearer())) -> api.Response:
    match record.resource_type:
        case core.ResourceType.comment:
            comment = core.Comment(owner_shortname=shortname, shortname=record.shortname, payload=None)
            db.save(record.subpath, comment)
            return api.Response(status=api.Status.success)

        case core.ResourceType.content:
            if "body" in record.attributes:
                content = core.Content(owner_shortname=shortname, shortname=record.shortname, payload=core.Payload(content_type=core.ContentType.text, body=record.attributes["body"]))
                db.save(record.subpath, content)
                return api.Response(status=api.Status.success)
            raise api.Exception(status_code=404, error=api.Error(type="content", code=111, message="empty body"))


@router.post("/update", response_model=api.Response, response_model_exclude_none=True)
async def update(record: api.Record) -> api.Response:
    return api.Response(status=api.Status.success)


@router.post("/delete", response_model=api.Response, response_model_exclude_none=True)
async def delete(record: api.Record) -> api.Response:
    return api.Response(status=api.Status.success)


@router.post("/move", response_model=api.Response, response_model_exclude_none=True)
async def move(record: api.Record) -> api.Response:
    return api.Response(status=api.Status.success)


@router.get('/media/{pathname}')
async def get_media():
    return {}


# Upload media attachment
@router.post('/media')
async def upload_media():
    return {}


from fastapi import APIRouter

import models.api as api 
import models.core as core
import utils.db as db
from utils.settings import settings

router = APIRouter()

@router.post("/query", response_model=api.Response, response_model_exclude_none=True)
async def query_request(query : api.Query) -> api.Response:
    return db.serve_query(query)

@router.post("/create", response_model=api.Response, response_model_exclude_none=True)
async def change(record : api.Record) -> api.Response:
    return api.Response(status=api.Status.success)

@router.post("/update", response_model=api.Response, response_model_exclude_none=True)
async def update(record : api.Record) -> api.Response:
    return api.Response(status=api.Status.success)

@router.post("/delete", response_model=api.Response, response_model_exclude_none=True)
async def delete(record : api.Record) -> api.Response:
    return api.Response(status=api.Status.success)

@router.post("/move", response_model=api.Response, response_model_exclude_none=True)
async def move(record : api.Record) -> api.Response:
    return api.Response(status=api.Status.success)

@router.get('/media/{pathname}')
async def get_media():
    return {}


# Upload media attachment 
@router.post('/media')
async def upload_media():
    return {}


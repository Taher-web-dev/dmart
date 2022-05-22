
from fastapi import APIRouter, Body
import utils.db as db
import models.api as api

router = APIRouter()

# Retrieve publically-available content

@router.post("/query", response_model=api.Response, response_model_exclude_none=True)
async def query_request(query : api.Query) -> api.Response:
    return db.serve_query(query)


# Public media retrieval; can be used in "src=" in html pages
@router.get('/media/{subpath}')
async def get_media():
    return {}

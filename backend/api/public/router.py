from fastapi import APIRouter, Path
import re
import utils.db as db
import models.api as api
import utils.regex as regex
import models.core as core
from fastapi.responses import FileResponse
from typing import Any
import sys

router = APIRouter()

# Retrieve publically-available content


@router.post("/query", response_model=api.Response, response_model_exclude_none=True)
async def query_entries(query: api.Query) -> api.Response:
    total, records = db.serve_query(query)
    return api.Response(
        status=api.Status.success,
        records=records,
        attributes={"total": total, "returned": len(records)},
    )


@router.get("/meta/{resource_type}/{subpath:path}/{shortname}")
async def get_body(
    resource_name : core.ResourceType, 
    subpath: str = Path(..., regex=regex.SUBPATH),
    shortname: str = Path(..., regex=regex.SHORTNAME),
) -> dict[str, Any]:
    resource_class = getattr(sys.modules["models.core"], resource_name.title())
    meta = db.load(subpath, shortname, resource_class)
    if meta is None :
        raise api.Exception(
            404,
            error=api.Error(
                type="media", code=221, message="Request object is not available"
            ),
        )

    # TODO check security labels for pubblic access
    # assert meta.is_active
    return meta.dict(exclude_none=True)


# Public payload retrieval; can be used in "src=" in html pages
@router.get("/payload/{resource_type}/{subpath:path}/{shortname}.{ext}")
async def get_payload(
    resource_name : core.ResourceType, 
    subpath: str = Path(..., regex=regex.SUBPATH),
    shortname: str = Path(..., regex=regex.SHORTNAME),
    ext: str = Path(..., regex=regex.EXT),
) -> FileResponse:
    resource_class = getattr(sys.modules["models.core"], resource_name.title())
    meta = db.load(subpath, shortname, resource_class)
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
    # assert meta.is_active
    payload_path = db.payload_path(subpath, resource_class)
    media_file = payload_path / str(meta.payload.body)
    return FileResponse(media_file)


@router.post("/submit")
async def submit() -> api.Response:
    return api.Response(status=api.Status.success)

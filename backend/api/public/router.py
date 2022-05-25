from fastapi import APIRouter
import utils.db as db
import models.api as api

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


# Public media retrieval; can be used in "src=" in html pages
@router.get("/payload/{subpath}")
async def get_payload():
    return {}


@router.post("/submit")
async def submit() -> api.Response:
    return api.Response(status=api.Status.success)

""" Main module """

import time
import traceback
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve


# import uvicorn

import json_logging
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import JSONResponse
import models.api as api
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from api.managed.router import router as managed
from api.user.router import router as user
from api.public.router import router as public
from utils.logger import logger
from starlette.concurrency import iterate_in_threadpool
import json
from typing import Any
from fastapi.middleware.cors import CORSMiddleware
from utils.settings import settings
from urllib.parse import urlparse

app = FastAPI(
    title="Datamart API",
    description="Structured Content Management System",
    version="0.0.1",
    redoc_url=None,
    contact={
        "name": "Kefah T. Issa",
        "url": "https://dmart.cc",
        "email": "kefah.issa@gmail.com",
    },
    license_info={
        "name": "GNU Affero General Public License v3+",
        "url": "https://www.gnu.org/licenses/agpl-3.0.en.html",
    },
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    openapi_tags=[
        {"name": "user", "description": "User registration, login, profile and delete"},
        {
            "name": "managed",
            "description": "Login-only content management api and media upload",
        },
        {
            "name": "public",
            "description": "Public api for query and GET access to media",
        },
    ],
)


json_logging.init_fastapi(enable_json=True)
# json_logging.init_request_instrument(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def capture_body(request: Request):
    request.state.request_body = {}
    if (
        request.method == "POST"
        and request.headers.get("content-type") == "application/json"
    ):
        request.state.request_body = await request.json()


@app.exception_handler(StarletteHTTPException)
async def my_exception_handler(_, exception):
    return JSONResponse(content=exception.detail, status_code=exception.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    err = jsonable_encoder({"detail": exc.errors()})["detail"]
    raise api.Exception(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error=api.Error(code=422, type="validation", message=err),
    )


@app.on_event("startup")
async def app_startup():
    logger.info("Starting")
    openapi_schema = app.openapi()
    paths = openapi_schema["paths"]
    for path in paths:
        for method in paths[path]:
            responses = paths[path][method]["responses"]
            if responses.get("422"):
                responses.pop("422")
    app.openapi_schema = openapi_schema


@app.on_event("shutdown")
async def app_shutdown():
    logger.info("Application shutdown")


@app.middleware("http")
async def middle(request: Request, call_next):
    """Wrapper function to manage errors and logging"""
    if request.url._url.endswith("/docs") or request.url._url.endswith("/openapi.json"):
        return await call_next(request)

    start_time = time.time()
    response_body: str | dict = ""
    exception_data: dict[str, Any] | None = None
    try:
        response = await call_next(request)
        raw_response = [section async for section in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(raw_response))
        raw_data = b"".join(raw_response)
        if raw_data:
            try:
                response_body = json.loads(raw_data)
            except:
                response_body = ""
    except api.Exception as ex:
        response = JSONResponse(
            status_code=ex.status_code,
            content=jsonable_encoder(
                api.Response(status=api.Status.failed, error=ex.error)
            ),
        )
        stack = [
            {
                "file": frame.f_code.co_filename,
                "function": frame.f_code.co_name,
                "line": lineno,
            }
            for frame, lineno in traceback.walk_tb(ex.__traceback__)
            if "site-packages" not in frame.f_code.co_filename
        ]
        exception_data = {"props": {"exception": str(ex), "stack": stack}}
        response_body = json.loads(response.body.decode())
    except Exception as ex:
        if ex:
            stack = [
                {
                    "file": frame.f_code.co_filename,
                    "function": frame.f_code.co_name,
                    "line": lineno,
                }
                for frame, lineno in traceback.walk_tb(ex.__traceback__)
                if "site-packages" not in frame.f_code.co_filename
            ]
            exception_data = {"props": {"exception": str(ex), "stack": stack}}
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                api.Response(
                    status=api.Status.failed,
                    error=api.Error(type="internal", code=99, message=str(ex)),
                )
            ),
        )
        response_body = json.loads(response.body.decode())

    referer = request.headers.get(
        "referer",
        request.headers.get("x-forwarded-proto", "http")
        + "://"
        + request.headers.get(
            "x-forwarded-host", f"{settings.listening_host}:{settings.listening_port}"
        ),
    )
    origin = urlparse(referer)
    response.headers[
        "Access-Control-Allow-Origin"
    ] = f"{origin.scheme}://{origin.netloc}"
    response.headers["Access-Control-Allow-Credentials"] = "true"

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    extra = {
        "props": {
            "timestamp": start_time,
            "duration": 1000 * (time.time() - start_time),
            "request": {
                "url": request.url._url,
                "verb": request.method,
                "path": str(request.url.path),
                "query_params": dict(request.query_params.items()),
                "headers": dict(request.headers.items()),
            },
            "response": {
                "headers": dict(response.headers.items()),
                "http_status": response.status_code,
            },
        }
    }

    if exception_data:
        extra["props"]["exception"] = exception_data
    if hasattr(request.state, "request_body"):
        extra["props"]["request"]["body"] = request.state.request_body
    if response_body:
        extra["props"]["response"]["body"] = response_body

    logger.info("Served request", extra=extra)

    return response


@app.get("/", include_in_schema=False)
async def root():
    """Micro-service card identifier"""
    return {
        "name": "DMART",
        "type": "microservice",
        "decription": "Structured CMS",
        "status": "Up and running",
        "date": datetime.now(),
        "status": "success",
    }


app.include_router(
    user, prefix="/user", tags=["user"], dependencies=[Depends(capture_body)]
)
app.include_router(
    managed, prefix="/managed", tags=["managed"], dependencies=[Depends(capture_body)]
)
app.include_router(
    public, prefix="/public", tags=["public"], dependencies=[Depends(capture_body)]
)


@app.get("/{x:path}", include_in_schema=False)
@app.post("/{x:path}", include_in_schema=False)
@app.put("/{x:path}", include_in_schema=False)
@app.patch("/{x:path}", include_in_schema=False)
@app.delete("/{x:path}", include_in_schema=False)
async def catchall():
    raise api.Exception(
        status_code=status.HTTP_404_NOT_FOUND,
        error=api.Error(
            type="catchall", code=230, message="Requested method or path is invalid"
        ),
    )


if __name__ == "__main__":
    #    uvicorn.run(app, host=settings.listening_host, port=settings.listening_port)  # type: ignore
    asyncio.run(serve(app, Config()))  # type: ignore

""" Main module """

import time
import traceback
import logging
import logging.handlers
import uvicorn

# from settings import settings
import json_logging
from utils.settings import settings
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import models.api as api
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from api.managed.router import router as managed
from api.user.router import router as user
from api.public.router import router as public
from urllib.parse import urlparse
from utils.logger import logger


app = FastAPI(
    title="Datamart API",
    description="Structured Content Management System",
    version="0.0.1",
    redoc_url=None,
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
json_logging.init_request_instrument(app)


@app.exception_handler(StarletteHTTPException)
async def my_exception_handler(_, exception):
    return JSONResponse(content=exception.detail, status_code=exception.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
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
    try:
        response = await call_next(request)
    except api.Exception as ex:
        response = JSONResponse(
            status_code=ex.status_code,
            content=jsonable_encoder(
                api.Response(status=api.Status.failed, error=ex.error)
            ),
        )
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
            logger.error(str(ex), extra={"props": {"stack": stack}})
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                api.Response(
                    status=api.Status.failed,
                    error=api.Error(type="internal", code=99, message=str(ex)),
                )
            ),
        )

    response.headers["Access-Control-Allow-Origin"] = (
        request.headers.get("x-forwarded-proto", "http")
        + "://"
        + request.headers.get(
            "x-forwarded-host", f"{settings.listening_host}:{settings.listening_port}"
        )
    )
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers[
        "Access-Control-Allow-Methods"
    ] = "GET, HEAD, POST, PUT, DELETE, OPTIONS"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    logger.info(
        "Processed",
        extra={
            "props": {
                "duration": 1000 * (time.time() - start_time),
                "verb": request.method,
                "path": str(request.url.path),
                "request": {
                    "headers": dict(request.headers.items()),
                    "query_params": dict(request.query_params.items()),
                },
                "response": {
                    "headers": dict(response.headers.items()),
                },
                "http_status": response.status_code,
            }
        },
    )
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
    }


app.include_router(user, prefix="/user", tags=["user"])
app.include_router(managed, prefix="/managed", tags=["managed"])
app.include_router(public, prefix="/public", tags=["public"])

# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: Optional[str] = None):
#    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    uvicorn.run(app, host=settings.listening_host, port=settings.listening_port)  # type: ignore

""" Main module """

import traceback
import logging
import logging.handlers
import uvicorn

# from settings import settings
import json_logging
from utils.settings import settings

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import models.api as api 
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from api.managed.router import router as managed
from api.session.router import router as session
from api.public.router import router as public


app = FastAPI(
    title="Datamart API",
    description="Structured-content Content Management System",
    version="0.0.1",
    redoc_url=None,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_handler = logging.handlers.RotatingFileHandler(
    filename=settings.log_path / 'x-ljson.log', maxBytes=5000000, backupCount=10
)
logger.addHandler(log_handler)
json_logging.init_fastapi(enable_json=True)
json_logging.init_request_instrument(app)


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
    """ Wrapper function to manage errors and logging """
    try:
        response = await call_next(request)
    except api.Exception as ex:
        response = JSONResponse(
            status_code=ex.status_code,
            content=jsonable_encoder(api.Response(status=api.Status.failed, error=ex.error)),
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

    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response


@app.get("/", include_in_schema=False)
async def root():
    """Micro-service card identifier"""
    return {
        "name": "CMS",
        "type": "microservice",
        "decription": "Structured CMS",
        "status": "Up and running",
        "date": datetime.now(),
    }


app.include_router(session, prefix='/session')
app.include_router(managed, prefix='/managed')
app.include_router(public, prefix='/public')

# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: Optional[str] = None):
#    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    uvicorn.run(app, host=settings.listening_host, port=settings.listening_port) # type: ignore

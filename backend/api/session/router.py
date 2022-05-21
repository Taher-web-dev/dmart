""" Session Apis """

from fastapi import APIRouter, Body, status, Depends

import models.api as api 
import models.core as core
import utils.regex as regex
import utils.db as db
from utils.jwt import JWTBearer, sign_jwt


router = APIRouter()


@router.post("/create", response_model=api.Response, response_model_exclude_none=True)
async def create_user() -> api.Response:
    # Register a new user by invitation
    raise api.Exception(status.HTTP_401_UNAUTHORIZED, api.Error(type="x", code=0, message="y"))


@router.post("/password", response_model=api.Response, response_model_exclude_none=True)
async def change_password( new_password: str = Body(..., embed=True), username=Depends(JWTBearer())
) -> api.Response:
    """Update user profile"""
    user = db.load("users", username, core.User)
    user.password = new_password
    db.save("users", user)
    return api.Response(status=api.Status.success)


@router.post( "/login", response_model=api.Response, response_model_exclude_none=True,)
async def login(
    username: str = Body(...), #, regex=regex.USERNAME),
    password: str = Body(...), #, regex=regex.PASSWORD),
) -> api.Response:
    """Login and generate refresh token"""
    user = db.load("users", username, core.User)
    if user and user.password == password: 
        access_token = sign_jwt({"username": username})
        return api.Response(status=api.Status.success, auth_token = access_token )
    raise api.Exception(status.HTTP_401_UNAUTHORIZED, api.Error(type="auth", code=10, message="Bad creds"))


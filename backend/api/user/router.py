""" Session Apis """

from fastapi import APIRouter, Body, status, Depends

import models.api as api
import models.core as core
import utils.db as db
from utils.jwt import JWTBearer, sign_jwt
from typing import Any


router = APIRouter()


@router.post("/create", response_model=api.Response, response_model_exclude_none=True)
async def create_user(record: api.Record, invitation: str) -> api.Response:
    """Register a new user by invitation"""
    if not invitation:
        # TBD validate invitation.
        # jwt-signed shortname, email and expiration time
        raise api.Exception(
            status_code=400,
            error=api.Error(type="create", code=50, message="bad invitation"),
        )
    if not record.attributes or "password" not in record.attributes:
        raise api.Exception(
            status_code=400,
            error=api.Error(type="create", code=50, message="empty password"),
        )

    user = core.User(
        owner_shortname=record.shortname,
        shortname=record.shortname,
        password=record.attributes["password"],
    )

    if "display_name" in record.attributes:
        user.display_name = record.attributes["display_name"]

    if "email" in record.attributes:
        user.email = record.attributes["email"]

    db.create("users", user)
    return api.Response(status=api.Status.success)


@router.get("/profile", response_model=api.Response, response_model_exclude_none=True)
async def get_profile(shortname=Depends(JWTBearer())) -> api.Response:
    user = db.load("users", shortname, core.User)
    attributes: dict[str, Any] = {}
    if user.email:
        attributes["email"] = user.email
    if user.display_name:
        attributes["display_name"] = user.display_name
    record = api.Record(
        subpath="users",
        shortname=user.shortname,
        resource_type=core.ResourceType.user,
        attributes=attributes,
    )
    return api.Response(status=api.Status.success, records=[record])


@router.post("/profile", response_model=api.Response, response_model_exclude_none=True)
async def update_profile(
    profile: api.Record, shortname=Depends(JWTBearer())
) -> api.Response:
    """Update user profile"""
    user = db.load("users", shortname, core.User)

    if "password" in profile.attributes:
        user.password = profile.attributes["password"]

    if "display_name" in profile.attributes:
        user.display_name = profile.attributes["display_name"]

    if "email" in profile.attributes:
        user.email = profile.attributes["email"]

    db.update("users", user)
    return api.Response(status=api.Status.success)


@router.post(
    "/login",
    response_model=api.Response,
    response_model_exclude_none=True,
)
async def login(
    shortname: str = Body(...),  # , regex=regex.USERNAME),
    password: str = Body(...),  # , regex=regex.PASSWORD),
) -> api.Response:
    """Login and generate refresh token"""
    user = db.load("users", shortname, core.User)
    if user and user.password == password:
        access_token = sign_jwt({"username": shortname})
        return api.Response(status=api.Status.success, auth_token=access_token)
    raise api.Exception(
        status.HTTP_401_UNAUTHORIZED,
        api.Error(type="auth", code=10, message="Bad creds"),
    )


@router.post("/delete", response_model=api.Response, response_model_exclude_none=True)
async def delete(shortname=Depends(JWTBearer())) -> api.Response:
    """Delete own user"""
    user = db.load("users", shortname, core.User)
    db.delete("users", user)
    return api.Response(status=api.Status.success)

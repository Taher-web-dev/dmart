""" Session Apis """

from fastapi import APIRouter, Body, status, Depends, Response

import models.api as api
import models.core as core
import utils.db as db
from utils.jwt import JWTBearer, sign_jwt
from typing import Any
import utils.regex as regex
from utils.settings import settings

router = APIRouter()

MANAGEMENT_SPACE: str = "management"
USERS_SUBPATH: str = "users"


@router.post("/create", response_model=api.Response, response_model_exclude_none=True)
async def create_user(record: core.Record) -> api.Response:
    """Register a new user by invitation"""
    if not record.attributes:
        raise api.Exception(
            status_code=400,
            error=api.Error(type="create", code=50, message="Empty attributes"),
        )

    if "invitation" not in record.attributes:
        # TBD validate invitation (simply it is a jwt signed token )
        # jwt-signed shortname, email and expiration time
        raise api.Exception(
            status_code=400,
            error=api.Error(
                type="create", code=50, message="bad or missign invitation token"
            ),
        )

    # TBD : Raise error if user already eists.

    if "password" not in record.attributes:
        raise api.Exception(
            status_code=400,
            error=api.Error(type="create", code=50, message="empty password"),
        )

    user = core.User.from_record(record=record, shortname="Guest register")

    if "displayname" in record.attributes:
        user.displayname = record.attributes["displayname"]

    if "email" in record.attributes:
        user.email = record.attributes["email"]

    db.create(MANAGEMENT_SPACE, USERS_SUBPATH, user)
    return api.Response(status=api.Status.success)


@router.get("/profile", response_model=api.Response, response_model_exclude_none=True)
async def get_profile(shortname=Depends(JWTBearer())) -> api.Response:
    user = db.load(MANAGEMENT_SPACE, USERS_SUBPATH, shortname, core.User)
    attributes: dict[str, Any] = {}
    if user.email:
        attributes["email"] = user.email
    if user.displayname:
        attributes["displayname"] = user.displayname
    record = core.Record(
        subpath=USERS_SUBPATH,
        shortname=user.shortname,
        resource_type=core.ResourceType.user,
        attributes=attributes,
    )
    return api.Response(status=api.Status.success, records=[record])


@router.post("/profile", response_model=api.Response, response_model_exclude_none=True)
async def update_profile(
    profile: core.Record, shortname=Depends(JWTBearer())
) -> api.Response:
    """Update user profile"""
    user = db.load(MANAGEMENT_SPACE, USERS_SUBPATH, shortname, core.User)

    if "password" in profile.attributes:
        user.password = profile.attributes["password"]

    if "displayname" in profile.attributes:
        user.displayname = profile.attributes["displayname"]

    if "email" in profile.attributes:
        user.email = profile.attributes["email"]

    db.update(MANAGEMENT_SPACE, USERS_SUBPATH, user)
    return api.Response(status=api.Status.success)


@router.post(
    "/login",
    response_model=api.Response,
    response_model_exclude_none=True,
)
async def login(
    response: Response,
    shortname: str = Body(..., regex=regex.SHORTNAME),
    password: str = Body(..., regex=regex.PASSWORD),
) -> api.Response:
    """Login and generate refresh token"""
    user = db.load(MANAGEMENT_SPACE, USERS_SUBPATH, shortname, core.User)
    if user and user.password == password:
        access_token = sign_jwt({"username": shortname})
        response.set_cookie(
            key="auth_token",
            value=access_token,
            expires=settings.jwt_access_expires,
            httponly=True,
            #samesite="none",
            #secure=True,
            secure=False,
            samesite="lax",
        )
        return api.Response(
            status=api.Status.success,
            records=[
                core.Record(
                    resource_type=core.ResourceType.user,
                    subpath="users",
                    shortname=shortname,
                    attributes={},
                )
            ],
        )
    raise api.Exception(
        status.HTTP_401_UNAUTHORIZED,
        api.Error(type="auth", code=10, message="Bad creds"),
    )


@router.post("/delete", response_model=api.Response, response_model_exclude_none=True)
async def delete_account(shortname=Depends(JWTBearer())) -> api.Response:
    """Delete own user"""
    user = db.load(MANAGEMENT_SPACE, USERS_SUBPATH, shortname, core.User)
    db.delete(MANAGEMENT_SPACE, USERS_SUBPATH, user)
    return api.Response(status=api.Status.success)

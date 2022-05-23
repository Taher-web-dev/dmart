import jwt
from time import time
from typing import Optional, Any
from fastapi import Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from utils.settings import settings
import models.api as api


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict[str, Any]:
        try:
            credentials: Optional[HTTPAuthorizationCredentials] = await super(
                JWTBearer, self
            ).__call__(request)
            if credentials and credentials.scheme == "Bearer":
                decoded = decode_jwt(credentials.credentials)
                if decoded and "username" in decoded:
                    return decoded["username"]
        except:
            raise api.Exception(
                status.HTTP_401_UNAUTHORIZED,
                api.Error(type="jwtauth", code=10, message="Not authenticated"),
            )
        raise api.Exception(
            status.HTTP_401_UNAUTHORIZED,
            api.Error(type="jwtauth", code=11, message="Not authenticated"),
        )


def sign_jwt(data: dict, expires: int = 600) -> str:
    payload = {"data": data, "expires": time() + expires}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_jwt(token: str) -> dict[str, Any]:
    try:
        decoded_token = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return decoded_token["data"] if decoded_token["expires"] >= time() else None
    except Exception:
        return {}


if __name__ == "__main__":
    import os
    import binascii

    # Generate secret
    print(binascii.hexlify(os.urandom(24)))

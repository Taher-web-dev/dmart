from models.enums import ResourceType
import models.core as core
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any
from builtins import Exception as PyException
from models.enums import RequestType
import utils.regex as regex


class Request(BaseModel):
    space_name: str = Field(..., regex=regex.SPACENAME)
    request_type: RequestType
    records: list[core.Record]


class QueryType(str, Enum):
    search = "search"
    subpath = "subpath"
    events = "events"
    history = "history"
    tags = "tags"
    spaces = "spaces"


class Query(BaseModel):
    type: QueryType
    space_name: str = Field(..., regex=regex.SPACENAME)
    subpath: str = Field(..., regex=regex.SUBPATH)
    filter_types: list[ResourceType] | None = None
    filter_shortnames: list[str] | None = Field(
        regex=regex.SHORTNAME, default_factory=list
    )
    filter_tags: list[str] | None = None
    search: str | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    exclude_fields: list[str] | None = None
    include_fields: list[str] | None = None
    sort_by: str | None = None
    retrieve_json_payload: bool = False
    limit: int = 10
    offset: int = 0


class Status(str, Enum):
    success = "success"
    failed = "failed"


class Error(BaseModel):
    type: str
    code: int
    message: str | list[dict]


class Response(BaseModel):
    status: Status
    error: Error | None = None
    auth_token: str | None = None
    records: list[core.Record] | None = None
    attributes: dict[str, Any] | None = None


class Exception(PyException):
    status_code: int
    error: Error

    def __init__(self, status_code: int, error: Error):
        super().__init__(status_code)
        self.status_code = status_code
        self.error = error

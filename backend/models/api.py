from models.enums import ResourceType
import models.core as core
from enum import Enum
from pydantic import BaseModel, Field
from pydantic.types import UUID4 as UUID
from datetime import datetime
from typing import Any, Dict, List
from builtins import Exception as PyException
from utils.regex import FILE_NAME, SUBPATH


class QueryType(str, Enum):
    search = "search"
    subpath = "subpath"
    events = "events"
    history = "history"


class Query(BaseModel):
    type: QueryType
    subpath: str = Field(regex=SUBPATH)
    filter_types: list[ResourceType]
    filter_shortnames: list[str] = Field(regex=FILE_NAME)
    search: str
    from_date: datetime
    to_date: datetime
    exclude_fields: list[str]
    include_fields: list[str]
    sort_by: str
    limit: int
    offset: int
    tags: list[str]


class Status(str, Enum):
    success = "success"
    failed = "failed"


class Error(BaseModel):
    type: str
    code: int
    message: str | List[Dict]


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

from models.enums import ResourceType
from enum import Enum
from pydantic import BaseModel
from pydantic.types import UUID4 as UUID
from datetime import datetime
from typing import Any
from builtins import Exception as PyException


class Record(BaseModel):
    resource_type: ResourceType
    is_attachment: bool | None = None
    uuid: UUID | None = None
    shortname: str
    subpath: str
    attributes: dict[str, Any]


class QueryType(str, Enum):
    search = "search"
    subpath = "subpath"
    folders = "folders"
    events = "events"
    history = "history"


class Query(BaseModel):
    type: QueryType
    subpath: str
    resource_uuids: list[UUID]
    resource_types: list[ResourceType]
    resource_shortnames: list[str]
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
    message: str


class Response(BaseModel):
    status: Status = Status.success
    error: Error | None = None
    auth_token: str | None = None
    records: list[Record] | None = None
    supplement: list[Record] | None = None
    attributes: dict[str, Any] | None = None


class Exception(PyException):
    status_code: int
    error: Error

    def __init__(self, status_code: int, error: Error):
        super().__init__(status_code)
        self.status_code = status_code
        self.error = error

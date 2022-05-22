
from enum import Enum
from pydantic import BaseModel, Field
from pydantic.types import UUID4 as UUID
from uuid import uuid4
from typing import Any
from datetime import datetime
from pathlib import Path


class Resource(BaseModel):
    class Config:
        use_enum_values = True


class RequestType(str, Enum):
    login = 'login'
    logout = 'logout'
    query = 'query'
    create = 'create'
    update = 'update'
    delete = 'delete'
    copy = 'copy'
    move = 'move'


class Language(str, Enum):
    ar = 'arabic'
    en = 'english'
    ku = 'kurdish'
    fr = 'french'
    tr = 'trukish'


class ResourceType(str, Enum):
    relationship = 'Relationship'
    actor = 'Actor'
    user = 'User'
    group = 'Group'
    comment = 'comment'
    meta = 'meta'
    media = 'Media'
    folder = 'Folder'
    acl = 'acl'
    query = 'query'
    locator = 'locator'
    record = 'record'
    content = 'content'


class ContentType(str, Enum):
    text = 'text'
    markdown = 'markdown'
    json = 'json'
    image = 'image'


class Payload(Resource):
    content_type: ContentType
    body: str | dict[str, Any]  # | Path in the future.


class Meta(Resource):
    uuid: UUID = Field(default_factory=uuid4)
    shortname: str
    is_active: bool = False
    display_name: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    attributes: dict[str, Any] | None = None
    owner_shortname: str
    payload: Payload | None = None


class Locator(Resource):
    uuid: UUID | None = None
    type: ResourceType
    subpath: str
    shortname: str
    parent_shortname: str | None  # Reuired for Attachments only
    display_name: str | None
    description: str | None
    tags: list[str] | None = None


class Actor(Meta):
    pass


class User(Actor):
    password: str
    email: str | None = None


class Group(Actor):
    pass


class Attachment(Meta):
    pass


class Comment(Attachment):
    pass


class Media(Attachment):
    pass


class Relationship(Attachment):
    related_to: Locator


class Event(Resource):
    resource: Locator
    user: Locator
    request: RequestType
    timestamp: datetime
    attributes: dict[str, Any]


class Alteration(Attachment):
    uuid: UUID
    user: Locator
    previous_alteration: UUID
    timestamp: datetime
    diff: dict[str, Any]


class Schema(Meta):
    pass


class Content(Meta):
    scheme: Locator | None = None


class Folder(Meta):
    pass

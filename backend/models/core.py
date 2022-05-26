from pydantic import BaseModel
from pathlib import Path

from typing import Any
from pydantic.types import UUID4 as UUID
from uuid import uuid4
from pydantic import Field
from datetime import datetime
import sys

from models.enums import ContentType, RequestType, ResourceType
import utils.regex as regex


class Resource(BaseModel):
    class Config:
        use_enum_values = True


class Payload(Resource):
    content_type: ContentType
    body: str | dict[str, Any] | Path


class Record(BaseModel):
    resource_type: ResourceType
    uuid: UUID | None = None
    shortname: str = Field(regex=regex.SHORTNAME)
    subpath: str = Field(regex=regex.SUBPATH)
    attributes: dict[str, Any]


class Meta(Resource):
    uuid: UUID = Field(default_factory=uuid4)
    shortname: str
    is_active: bool = False
    display_name: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    owner_shortname: str
    payload: Payload | None = None

    @staticmethod
    def from_record(record: Record, shortname: str):
        child_resource_cls = getattr(
            sys.modules["models.core"], record.resource_type.title()
        )
        child_resource_obj = child_resource_cls(
            owner_shortname=shortname, shortname=record.shortname, **record.attributes
        )
        child_resource_obj.parse_record(record)  # PAYLOAD
        return child_resource_obj

    def parse_record(self, record: Record):
        pass

    def to_record(self, subpath: str, shortname: str, include: list[str]):
        # Sanity check
        assert self.shortname == shortname
        fields = {
            "resource_type": type(self).__name__.lower(),
            "uuid": self.uuid,
            "shortname": self.shortname,
            "subpath": subpath,
        }

        fields["attributes"] = self.get_record_attributes(include=include)
        return Record(**fields)

    def get_record_attributes(self, include: list[str]):
        meta_fields = list(Meta.__fields__.keys())
        attributes = {}
        for key, value in self.__dict__.items():
            if (not include or key in include) and key not in meta_fields:
                attributes[key] = value
        return attributes


class Locator(Resource):
    uuid: UUID | None = None
    type: ResourceType
    subpath: str
    shortname: str
    display_name: str | None = None
    description: str | None = None
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
    body: str


class Media(Attachment):
    filename: str

    def parse_record(self, record: Record):
        self.payload = Payload(content_type=ContentType.image, body=record.attributes["filename"])


class Relationship(Attachment):
    related_to: Locator
    attributes: dict[str, Any]


class Event(Resource):
    resource: Locator
    user_shortname: str
    request: RequestType
    timestamp: datetime
    attributes: dict[str, Any]


class Alteration(Attachment):
    uuid: UUID
    user_shortname: str
    previous_alteration: UUID
    timestamp: datetime
    diff: dict[str, Any]


class Schema(Meta):
    pass


class Content(Meta):
    schema_shortname: str | None = None
    body: str

    def parse_record(self, record: Record):
        if "body" in record.attributes:
            self.payload = Payload(
                content_type=ContentType.json, body=record.attributes["body"]
            )
        self.payload = None


class Folder(Meta):
    pass

from pydantic import BaseModel
from pathlib import Path

from typing import Any
from pydantic.types import UUID4 as UUID
from uuid import uuid4
from pydantic import Field
from datetime import datetime
import sys
import json

from models.enums import ContentType, Language, RequestType, ResourceType
import utils.regex as regex


# class MoveModel(BaseModel):
#    resource_type: ResourceType
#    src_shortname: str = Field(regex=regex.SHORTNAME)
#    src_subpath: str = Field(regex=regex.SUBPATH)
#    dist_shortname: str = Field(default=None, regex=regex.SHORTNAME)
#    dist_subpath: str = Field(default=None, regex=regex.SUBPATH)


class Resource(BaseModel):
    class Config:
        use_enum_values = True


class Payload(Resource):
    content_type: ContentType
    content_sub_type: str | None = (
        None  # FIXME change to proper content type static hashmap
    )
    schema_shortname: str | None = None
    checksum: str | None = None
    body: str | dict[str, Any] | Path


class Record(BaseModel):
    resource_type: ResourceType
    uuid: UUID | None = None
    shortname: str = Field(regex=regex.SHORTNAME)
    subpath: str = Field(regex=regex.SUBPATH)
    attributes: dict[str, Any]
    attachments: dict[ResourceType, list[Any]] | None = None


class Meta(Resource):
    uuid: UUID = Field(default_factory=uuid4)
    shortname: str
    is_active: bool = False
    displayname: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    owner_shortname: str
    payload: Payload | None = None

    @staticmethod
    def from_record(record: Record, shortname: str):
        meta_class = getattr(sys.modules["models.core"], record.resource_type.title())
        meta_obj = meta_class(
            owner_shortname=shortname, shortname=record.shortname, **record.attributes
        )
        """
        if "payload.body" in record.attributes and record.attributes["payload.body"]:
            content_type = ContentType.text
            if "payload.content_type" in record.attributes and record.attributes["payload.content_type"]:
                content_type = record.attributes["payload.content"]
            meta_obj.payload = Payload(
                content_type=content_type, body=record.attributes["payload.body"]
            )
        """
        meta_obj.parse_resource_payload(record)
        return meta_obj

    def parse_resource_payload(self, record: Record):
        """
        get record.attributes items that is not defined in the resource class,
        and add them to a Payload object body with content_type = text
        """
        meta_fields = list(self.__fields__.keys())
        payload_body = {}
        for key, value in record.attributes.items():
            if key not in meta_fields:
                payload_body[key] = value

        if len(payload_body) > 0:
            self.payload = Payload(content_type=ContentType.json, body=payload_body)

    def to_record(self, subpath: str, shortname: str, include: list[str]):
        # Sanity check
        assert self.shortname == shortname
        fields = {
            "resource_type": type(self).__name__.lower(),
            "uuid": self.uuid,
            "shortname": self.shortname,
            "subpath": subpath,
        }

        meta_fields = list(Meta.__fields__.keys())
        attributes = {}
        for key, value in self.__dict__.items():
            if (not include or key in include) and key not in meta_fields:
                attributes[key] = value

        if self.displayname:
            attributes["displayname"] = self.displayname

        if self.description:
            attributes["description"] = self.description

        if self.payload:
            attributes["payload"] = self.payload.body
            if self.payload.schema_shortname:
                attributes["schema_shortname"] = self.payload.schema_shortname
            attributes["checksum"] = self.payload.checksum
        if self.tags:
            attributes["tags"] = self.tags

        fields["attributes"] = attributes

        return Record(**fields)


class Locator(Resource):
    uuid: UUID | None = None
    type: ResourceType
    space_name: str
    subpath: str
    shortname: str
    displayname: str | None = None
    description: str | None = None
    tags: list[str] | None = None


class Space(Meta):
    root_registration_signature: str = ""
    primary_website: str = ""
    indexing_enabled: bool = False
    languages: list[Language] = [Language.en]
    mirrors: list[str] = []


class Actor(Meta):
    pass


class User(Actor):
    password: str
    email: str | None = None


class Group(Actor):
    members: list[str] = []  # list of actor_shortnames


class Attachment(Meta):
    pass


class Comment(Attachment):
    body: str


class Media(Attachment):
    pass


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
    user_shortname: str
    previous_alteration: UUID
    timestamp: datetime
    diff: dict[str, Any]


class Schema(Meta):
    pass


class Content(Meta):
    pass


class Folder(Meta):
    pass

from enum import Enum

class ActionType(str, Enum):
    query = "query"
    update = "update"
    create = "create"
    delete = "delete"
    attach = "attach"

class ConditionType(str, Enum):
    is_active = "is_active"
    own = "own"

class Permission (Meta):
    subpaths : dict[str, list[str]] # {"space_name": ["subpath_one", "subpath_two"]}
    resource_types : list[ResourceType]
    actions : list[ActionType]
    conditions : list[ConditionType] = []

class Role(Meta):
    permissions : list[str] # list of permissions_shortnames
    entitled_actors : list[str] # list of actor_shortnames

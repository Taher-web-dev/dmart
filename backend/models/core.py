from pydantic import BaseModel
from pathlib import Path

from typing import Any
from models.api import Error, Record, Exception
from pydantic.types import UUID4 as UUID
from uuid import uuid4
from pydantic import Field
from datetime import datetime
import sys

from models.enums import ContentType, RequestType, ResourceType

class Resource(BaseModel):
    class Config:
        use_enum_values = True





class Payload(Resource):
    content_type: ContentType
    body: str | dict[str, Any] | Path


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
        child_resource_cls = getattr(sys.modules["models.core"], record.resource_type.title())
        child_resource_obj = child_resource_cls(owner_shortname=shortname, shortname=record.shortname, **record.attributes)
        child_resource_obj.parse_record(record) # PAYLOAD
        return child_resource_obj

    def parse_record(self, record: Record):
        return None

    def to_record(self, subpath: str, include: list[str], exclude: list[str]):
        # fields = self.get_record_fields(include=include, exclude=exclude, subpath=subpath)
        fields = {
            "resource_type": type(self).__name__.lower(),
            "subpath": subpath,
            "shortname": self.shortname,
            "uuid": self.uuid,
        }
        # print(self.__dict__.items())
        # for key, value in self.__dict__.items():
        #     if((not include or key in include) and (not exclude or key not in exclude)):
        #         fields[key] = value

        fields["attributes"] = self.get_record_attributes(include=include, exclude=exclude)
        return Record(**fields)
        
    def get_record_attributes(self, include: list[str], exclude: list[str]):
        return {}

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
    body : str



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
                content_type=ContentType.json,
                body = record.attributes["body"]
            )
        self.payload = None

    def get_record_attributes(self, include: list[str], exclude: list[str]):
        meta_fields = list(Meta.__fields__.keys())
        attributes = {}
        for key, value in self.__dict__.items():
            if((not include or key in include) and (not exclude or key not in exclude) and key not in meta_fields):
                attributes[key] = value
        return attributes
        

class Folder(Meta):
    pass


if __name__ == '__main__':
    content = Content(shortname="test", owner_shortname="SAAD", body="TEST BODY")
    record = content.to_record("subpath_test", [], [])
    # parent_class = getattr(content.__class__)

    print("\n Record:",record.__dict__)
    # for attr, val in cls_dict.iteritems():
    #     print("%s = %s", attr, val)
    # for key, value in Meta.__fields__.keys():
    #     print(key, " => ", value)
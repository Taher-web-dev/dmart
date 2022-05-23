from enum import Enum



class RequestType(str, Enum):
    login = "login"
    logout = "logout"
    query = "query"
    create = "create"
    update = "update"
    delete = "delete"
    copy = "copy"
    move = "move"



class Language(str, Enum):
    ar = "arabic"
    en = "english"
    ku = "kurdish"
    fr = "french"
    tr = "trukish"


class ResourceType(str, Enum):
    user = "user"
    group = "group"
    folder = "folder"
    schema = "schema"
    content = "content"
    acl = "acl"
    comment = "comment"
    media = "media"
    relationship = "relationship"
    alteration = "alteration"



class ContentType(str, Enum):
    text = "text"
    markdown = "markdown"
    json = "json"
    image = "image"

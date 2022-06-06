import json
import redis
import models.core as core
from redis.commands.json.path import Path
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import NumericFilter, Query
from typing import Any


from utils.settings import settings


client = redis.Redis(host=settings.redis_host, port=6379)
index: dict[str, Any] = {}
for space_name in settings.space_names:
    index[space_name] = client.ft(space_name)

META_SCHEMA = (
    TextField("$.uuid", no_stem=True, as_name="uuid"),
    TextField("$.shortname", sortable=True, no_stem=True, as_name="shortname"),
    TextField("$.subpath", sortable=True, no_stem=True, as_name="subpath"),
    TextField("$.resource_type", sortable=True, no_stem=True, as_name="resource_type"),
    TextField("$.displayname", sortable=True, as_name="displayname"),
    TextField("$.description", sortable=True, as_name="description"),
    TextField("$.payload.content_type", no_stem=True, as_name="payload_content_type"),
    TextField("$.payload.schema_shortname", no_stem=True, as_name="schema_shortname"),
    NumericField("$.created_at", sortable=True, as_name="created_at"),
    NumericField("$.updated_at", sortable=True, as_name="updated_at"),
    TextField(
        "$.owner_shortname", sortable=True, no_stem=True, as_name="owner_shortname"
    ),
    # NumericField("$.is_active", sortable=True, as_name="is_active"),
    TagField("$.tags", as_name="tags"),
    # TextField("$.payload.body", as_name="payload_body"),
)


def create_index(space_name: str):
    try:
        index[space_name].dropindex(delete_documents=True)
    except:
        pass

    ret = index[space_name].create_index(
        META_SCHEMA,
        definition=IndexDefinition(
            prefix=[f"{space_name}:meta:"], index_type=IndexType.JSON
        ),
    )
    print("Creat index ret: ", ret)

    # TBD : Create schema indexes. i.e. for each space name, there should be schema indexes for all available schema_shortnames


def save_entry(space_name: str, subpath: str, meta: core.Meta):
    resource_type = meta.__class__.__name__.lower()
    docid = f"{space_name}:meta:{subpath}/{meta.shortname}/{meta.uuid}/{resource_type}"
    meta_json = json.loads(meta.json(exclude_none=True))

    # Inject resource_type
    meta_json["resource_type"] = resource_type
    meta_json["created_at"] = meta.created_at.timestamp()
    meta_json["updated_at"] = meta.created_at.timestamp()
    meta_json["tags"] = "none" if not meta.tags else "|".join(meta.tags)
    client.json().set(docid, Path.root_path(), meta_json)

    # TBD : If entry of type content and json payload, save the json document under the respective schema index


"""
def convert(d : dict[str,Any]|list[Any]) -> dict[str,Any]|list[Any]:
    if isinstance(d, dict):
        y = {}
        for k,v in d.items():
            if isinstance(v, str) or isinstance(v, bool) or isinstance(v, int):
                y[k] = v
            elif isinstance(v, bytes):
                y[k] = v.decode()
            elif isinstance(v, dict) or isinstance(v, list):
                y[k] = convert(v)
        return y
    elif isinstance(d, list):
        y = []
        for v in d:
            if isinstance(v, str):
                y.append(v)
            elif isinstance(v, bytes):
                y.append(v.decode())
            elif isinstance(v, dict) or isinstance(v, list):
                y.append(convert(v))
        return y
            
        
"""

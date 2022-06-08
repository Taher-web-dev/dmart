import json
import redis
import models.core as core
from redis.commands.json.path import Path
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search import Search
from redis.commands.search.query import Query
from utils.settings import settings


client = redis.Redis(host=settings.redis_host, port=6379)

def save_meta_doc(space_name: str, schema_shortname: str, subpath: str, meta: core.Meta):
    resource_type = meta.__class__.__name__.lower()
    docid = f"{space_name}:{schema_shortname}:{subpath}/{meta.shortname}/{meta.uuid}/{resource_type}"
    meta_json = json.loads(meta.json(exclude_none=True))

    # Inject resource_type
    meta_json["subpath"] = subpath
    meta_json["resource_type"] = resource_type
    meta_json["created_at"] = meta.created_at.timestamp()
    meta_json["updated_at"] = meta.updated_at.timestamp()
    meta_json["tags"] = "none" if not meta.tags else "|".join(meta.tags)
    client.json().set(docid, Path.root_path(), meta_json)

def save_payload_doc(space_name: str, schema_shortname: str, payload_shortname, payload: dict):
    docid = f"{space_name}:{schema_shortname}/{payload_shortname}"
    
    client.json().set(docid, Path.root_path(), payload)

    # TBD : If entry of type content and json payload, save the json document under the respective schema index


def search(
    space_name: str, 
    search: str, 
    filters: dict[str : list], 
    limit: int,
    offset: int,
    sort_by: str | None = None,
    schema_name: str = "meta",
):
    ft_index = client.ft(f"{space_name}:{schema_name}")
    try:
        ft_index.info()
    except :
        raise Exception("Invalid space name or schema name")

    query_string = search

    for item in filters.items():
        if item[0] == "tags" and item[1]:
            query_string += " @tags:{" + "|".join(item[1]) + "}"
        elif item[1]:
            query_string += " @" + item[0]+ ":(" + "|".join(item[1]) + ")"
        
    search_query = Query(query_string=query_string)

    if sort_by:
        search_query = search_query.sort_by(sort_by)

    search_query = search_query.paging(offset, limit)

    return ft_index.search(query=search_query).docs
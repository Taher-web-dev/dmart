from http import HTTPStatus
import re
import json
import redis
import models.api as api
import models.core as core
from redis.commands.json.path import Path
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search import Search
from redis.commands.search.query import Query
from utils.settings import settings


client = redis.Redis(host=settings.redis_host, port=6379)
redis_indices: dict[str, dict[str, Search]] = {}

REDIS_SCHEMA_DATA_TYPES_MAPPER = {
    "string": TextField,
    "boolean": TextField,
    "integer": NumericField,
    "number": NumericField,
}

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
)

def create_index(space_name: str, schema_name: str, redis_schema: tuple):
    """
    create redis schema index, drop it if exist first
    """
    try:
        redis_indices[space_name][schema_name].dropindex(delete_documents=True)
    except:
        pass

    redis_indices[space_name][schema_name].create_index(
        redis_schema,
        definition=IndexDefinition(
            prefix=[f"{space_name}:{schema_name}"], index_type=IndexType.JSON
        ),
    )
    #print(f"Created new index named {space_name}:{schema_name}\n")


def get_redis_index_fields(key_chain, property, redis_schema_definition):
    """
    takes a key and a value of a schema definition, and return the redis schema index appropriate field class/es
    """
    if "type" in property and property["type"] != "object":
        redis_schema_definition.append(REDIS_SCHEMA_DATA_TYPES_MAPPER[property["type"]](f"$.{key_chain}", sortable=True, as_name=key_chain.replace(".", "_")))
        return redis_schema_definition

    for property_key, property_value in property["properties"].items():
        redis_schema_definition = get_redis_index_fields(f"{key_chain}.{property_key}", property_value, redis_schema_definition)

    return redis_schema_definition
    
def create_indices_for_all_spaces_meta_and_schemas():
    """
    Loop over all spaces, and for each one we create: (only if indexing_enabled is true for the space)
    1-index for meta file called space_name:meta
    2-indices for schema files called space_name:schema_shortname
    """
    for space_name in settings.space_names:
        space_meta_file = settings.spaces_folder / space_name / ".dm/meta.space.json"
        if not space_meta_file.is_file():
            continue

        space_meta_data = json.loads(space_meta_file.read_text())
        if "indexing_enabled" not in space_meta_data or not space_meta_data["indexing_enabled"]:
            continue
        
        # CREATE REDIS INDEX FOR THE META FILES INSIDE THE SPACE
        redis_indices[space_name] = {}
        redis_indices[space_name]["meta"] = client.ft(f"{space_name}:meta")
        create_index(space_name, "meta", META_SCHEMA)

        # CREATE REDIS INDEX FOR EACH SCHEMA DEFINITION INSIDE THE SPACE
        schemas_file_pattern = re.compile(r"(\w*).json")
        schemas_glob = "*.json"
        path = settings.spaces_folder / space_name / "schema"
        for schema_path in path.glob(schemas_glob):
            # GET SCHEMA SHORTNAME
            match = schemas_file_pattern.search(str(schema_path))
            if not match or not schema_path.is_file():
                continue
            schema_shortname = match.group(1)

            # GET SCHEMA PROPERTIES AND 
            # GENERATE REDIS INDEX DEFINITION BY MAPPIN SCHEMA PROPERTIES TO REDIS INDEX FIELDS
            schema_content = json.loads(schema_path.read_text())
            redis_schema_definition = []
            for key, property in schema_content["properties"].items():
                redis_schema_definition.extend(get_redis_index_fields(key, property, []))

            if redis_schema_definition:
                redis_indices[space_name][schema_shortname] = client.ft(f"{space_name}:{schema_shortname}")
                redis_schema_definition.extend([
                    TextField("$.subpath", as_name="subpath"),
                    TextField("$.resource_type", as_name="resource_type"),
                    TextField("$.shortname", as_name="shortname"),
                    TextField("$.meta_doc_id", as_name="meta_doc_id"),
                ])
                create_index(space_name, schema_shortname, tuple(redis_schema_definition))


def generate_doc_id(
    space_name:str,
    schema_shortname: str,
    shortname: str,
    subpath: str
):
    return f"{space_name}:{schema_shortname}:{subpath}/{shortname}"


def save_meta_doc(space_name: str, schema_shortname: str, subpath: str, meta: core.Meta):
    resource_type = meta.__class__.__name__.lower()
    docid = generate_doc_id(space_name, schema_shortname, meta.shortname, subpath)
    meta_json = json.loads(meta.json(exclude_none=True))

    # Inject resource_type
    meta_json["subpath"] = subpath
    meta_json["resource_type"] = resource_type
    meta_json["created_at"] = meta.created_at.timestamp()
    meta_json["updated_at"] = meta.updated_at.timestamp()
    meta_json["tags"] = "none" if not meta.tags else "|".join(meta.tags)
    client.json().set(docid, Path.root_path(), meta_json)

def save_payload_doc(space_name: str, schema_shortname: str, subpath: str, payload_shortname, payload: dict):
    meta_doc_id = generate_doc_id(space_name, "meta", payload_shortname, subpath)
    docid = generate_doc_id(space_name, schema_shortname, payload_shortname, subpath)
    
    payload["subpath"] = subpath
    payload["resource_type"] = "content"
    payload["shortname"] = payload_shortname
    payload["meta_doc_id"] = meta_doc_id
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
        search_query.sort_by(sort_by)

    search_query.paging(offset, limit)

    try:
        return ft_index.search(query=search_query).docs
    except :
        return []

def get_doc_by_id(doc_id: str):
    return client.json().get(name=doc_id)
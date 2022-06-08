from models.enums import ContentType
import utils.redis_services as redis_services
import models.core as core
import models.api as api
import utils.db as db
import sys
import json
import re
import redis
from utils.settings import settings
from redis.commands.search.field import TextField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search import Search


client = redis.Redis(host=settings.redis_host, port=6379)
redis_indices: dict[str, dict[str, Search]] = {}

REDIS_SCHEMA_DATA_TYPES_MAPPER = {
    "string": TextField,
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
    print(f"Created new index named {space_name}:{schema_name}\n")


def get_redis_index_fields(key_chain, property, redis_schema_definition):
    """
    takes a key and a value of a schema definition, and return the redis schema index appropriate field class/es
    """
    if "type" in property:
        redis_schema_definition.append(REDIS_SCHEMA_DATA_TYPES_MAPPER[property["type"]](f"$.{key_chain}", as_name=key_chain.replace(".", "_")))
        return redis_schema_definition

    for property_key, property_value in property.items():
        redis_schema_definition = get_redis_index_fields(f"{key_chain}.{property_key}", property_value, redis_schema_definition)

    return redis_schema_definition
    
def create_index_for_all_spaces_meta_and_schemas():
    """
    Loop over all spaces, and for each one we create
    1-index for meta file called space_name:meta
    2-indices for schema files called space_name:schema_shortname
    """
    for space_name in settings.space_names:
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
                create_index(space_name, schema_shortname, tuple(redis_schema_definition))


def load_data_to_redis(space_name, subpath):
    """
    Load meta files inside subpath then store them to redis as :space_name:meta prefixed doc,
    and if the meta file has a separate payload file follwing a schema we loads the payload content and store it to redis as :space_name:schema_name prefixed doc
    """
    total, locators = db.locators_query(
        api.Query(space_name=space_name, subpath=subpath, type=api.QueryType.subpath, limit=10000)
    )
    loaded_to_redis = 0
    for one in locators:
        # myclass = db.resource_class(core.ResourceType(one.__class__.__name__.lower()))
        try:
            myclass = getattr(sys.modules["models.core"], core.ResourceType("content").title())
            # print("\n\n\n\n space_name: ", space_name, "\n subpath: ", one.subpath, "\nshortname: ", one.shortname)
            meta = db.load(space_name=space_name, subpath=one.subpath, shortname=one.shortname, class_type=myclass)
            redis_services.save_meta_doc(space_name=space_name, schema_shortname="meta", subpath=subpath, meta=meta)
            if meta.payload and meta.payload.content_type == ContentType.json and meta.payload.schema_shortname:
                payload_path = db.payload_path(space_name, one.subpath, myclass) / str(meta.payload.body)
                payload_data = json.loads(payload_path.read_text())
                redis_services.save_payload_doc(
                    space_name=space_name, 
                    schema_shortname=meta.payload.schema_shortname, 
                    payload_shortname=meta.payload.body.split(".")[0], 
                    payload=payload_data
                )
            loaded_to_redis += 1
        except:
            pass
    print(f"Added {loaded_to_redis} document to redis from {space_name}/{subpath}")

def load_all_spaces_data_to_redis():
    """
    Loop over spaces and subpaths inside it and load the data to redis
    """
    for space_name in settings.space_names:
        path = settings.spaces_folder / space_name
        # print("\n\n\n path: ", path, path.is_dir())
        if path.is_dir():
            for subpath in path.iterdir():
                if subpath.is_dir():
                    print("\n\n\n subpath: ", subpath.name)
                    load_data_to_redis(space_name, subpath.name)

if __name__ == "__main__":
    load_all_spaces_data_to_redis()
    create_index_for_all_spaces_meta_and_schemas()

    # print(redis_services.search(
    #     space_name="products",
    #     schema_name="offer",
    #     search="*",
    #     filters={},
    #     limit=5,
    #     offset=0
    # ))

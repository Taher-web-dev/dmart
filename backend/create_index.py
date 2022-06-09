import json
import re
import models.api as api
import utils.db as db
import models.core as core
import sys
from models.enums import ContentType
import utils.redis_services as redis_services
from utils.settings import settings
import utils.regex as regex

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
            # print("\n\n\n", "\n space_name: ", space_name, "\n subpath: ", one.subpath, "\n shortname: ", one.shortname, "\n class_type: ", myclass)
            meta = db.load(space_name=space_name, subpath=one.subpath, shortname=one.shortname, class_type=myclass)
            redis_services.save_meta_doc(space_name=space_name, schema_shortname="meta", subpath=subpath, meta=meta)
            if meta.payload and meta.payload.content_type == ContentType.json and meta.payload.schema_shortname:
                payload_path = db.payload_path(space_name, one.subpath, myclass) / str(meta.payload.body)
                payload_data = json.loads(payload_path.read_text())
                redis_services.save_payload_doc(
                    space_name=space_name, 
                    schema_shortname=meta.payload.schema_shortname, 
                    payload_shortname=meta.payload.body.split(".")[0], 
                    subpath=subpath,
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
        if path.is_dir():
            for subpath in path.iterdir():
                if subpath.is_dir() and re.match(regex.SUBPATH, subpath.name):
                    load_data_to_redis(space_name, subpath.name)

if __name__ == "__main__":
    load_all_spaces_data_to_redis()
    redis_services.create_indices_for_all_spaces_meta_and_schemas()

    # test_search = redis_services.search(
    #     space_name="products",
    #     schema_name="offer",
    #     search="@cbs_name:DB_ATLDaily_600MB",
    #     filters={"subpath": ["offers"], "shortname": ["2140692"]},
    #     limit=10,
    #     offset=0,
    #     sort_by="cbs_id"
    # )
    # print("\n\n\nresult count: ", len(test_search), "\n\nresult: ", test_search)
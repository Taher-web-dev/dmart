import utils.redisearch as search
import models.core as core
import models.api as api
import utils.db as db
import sys

import json

space_name = "products"
search.create_index("products")
subpath = "content"
total, locators = db.locators_query(
    api.Query(space_name=space_name, subpath=subpath, type=api.QueryType.subpath, limit=10000)
)

for one in locators:
    myclass = getattr(sys.modules["models.core"], core.ResourceType("content").title())
    # myclass = db.resource_class(core.ResourceType(one.__class__.__name__.lower()))
    meta = db.load(space_name=space_name, subpath=one.subpath, shortname=one.shortname, class_type=myclass)
    search.save_entry(space_name=space_name, subpath=subpath, meta=meta)

# TEST SEARCH FUNCTION
# ret = search.search(
#     space_name=space_name, 
#     search="", 
#     filters={"filter_shortnames": ["5028", "5067", "5071"], "filter_types": ["content", "media"]},
#     limit=15, 
#     offset=0,
#     include=["uuid", "shortname"],
#     sort_by="shortname"
# )
# print("Number of stored documents : ", len(ret))
# for item in ret:
#     print("\nRET: ", ret)




# ret = search.index.search(Query("curl")) # .return_field("$.meta.is_active", as_field="is_active")).docs
# print(ret.total)
# print(ret)

# print(search.index.info())
# print(one.json())
# print(one.json())
# info()
import utils.redisearch as search
import models.core as core
import models.api as api
import utils.db as db
import sys

import json

search.create_index()
subpath = "myposts"
total, locators = db.locators_query(
    api.Query(subpath=subpath, type=api.QueryType.subpath)
)

for one in locators:
    myclass = getattr(sys.modules["models.core"], core.ResourceType("content").title())
    # myclass = db.resource_class(core.ResourceType(one.__class__.__name__.lower()))
    meta = db.load(one.subpath, one.shortname, myclass)
    search.save_meta(subpath, meta)

ret = search.index.search("alibaba")
print("Returned : ", len(ret.docs))
if ret.docs:
    for one in ret.docs:
        # print(json.dumps(json.loads(json.loads(one.json)), indent=4))
        print(json.dumps(json.loads(one.json), indent=4))


# ret = search.index.search(Query("curl")) # .return_field("$.meta.is_active", as_field="is_active")).docs
# print(ret.total)
# print(ret)

# print(search.index.info())
# print(one.json())
# print(one.json())
# info()

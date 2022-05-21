#import json
#from jsonschema import validate
#from pathlib import Path
#from utils.settings import settings
import models.core as core 
from utils.db import load, save

# print(settings.space_root)

#users = core.Folder(shortname="users")
user = core.User(shortname="alibaba", password="hi")
save("users", user)

#myjson = user.json(exclude_none=True)

#user2 = core.User.parse_raw(myjson)
user2 = load("users", "alibaba", core.User)
print(user2.json(exclude_none=True))

#data = json.loads(Path("./data.json").read_text())
#schema = json.loads(Path("./schema.json").read_text())
#validate(instance=data, schema=schema)

import json
from jsonschema import validate
from pathlib import Path

data = json.loads(Path("./data.json").read_text())
schema = json.loads(Path("./schema.json").read_text())
print("data", data)
print("schema", schema)
print(validate(instance=data, schema=schema))

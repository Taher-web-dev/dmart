from utils.settings import settings
import models.core as core
from typing import TypeVar,Type
import json
import os

Meta = TypeVar("Meta", bound=core.Meta)


def load(subpath:str, shortname:str, class_type: Type[Meta] ) -> Meta:
    path = settings.space_root 
    if type == core.Folder:
        path = path / subpath / shortname / ".dm" / f"meta.{class_type.__name__}.json"
    elif issubclass(class_type, core.Attachment):
        [parent_subpath, parent_name] = subpath.rsplit('/',1)
        path = path / parent_subpath / ".dm" / f"{parent_name}/attachments.{class_type.__name__}/meta.{shortname}.json"
    else:
        path = path / subpath / ".dm" / shortname / f"meta.{class_type.__name__}.json"
    return class_type.parse_raw(path.read_text())

def save(subpath : str, meta : core.Meta):
    path = settings.space_root 
    filename : str
    if isinstance(meta, core.Folder):
        path = path / subpath / meta.shortname / ".dm" 
        filename = f"meta.{type(meta).__name__}.json"
    elif isinstance(meta, core.Attachment):
        [parent_subpath, parent_name] = subpath.rsplit('/',1)
        path = path / parent_subpath / ".dm" / f"{parent_name}/attachments.{type(meta).__name__}"
        filename = f"meta.{meta.shortname}.json"
    else:
        path = path / subpath / ".dm" / meta.shortname
        filename = f"meta.{type(meta).__name__}.json"
    
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path / filename, "w") as file:
        file.write(meta.json(exclude_none=True))

    
    

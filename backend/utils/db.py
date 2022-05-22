from utils.settings import settings
import models.core as core
from typing import TypeVar,Type
import json
import models.api as api
import os
from pathlib import Path

Meta = TypeVar("Meta", bound=core.Meta)

def serve_query(query: api.Query) -> api.Response:
    """ Return requested information """
    if query.type == api.QueryType.subpath:
        folder_metapath = settings.space_root / query.subpath / ".dm/meta.folder.json"  
        if not folder_metapath.is_file():
            raise api.Exception(status_code=404, error=api.Error(type="db", code=12, message="requested object not found"))



    return api.Response(status=api.Status.success)
    

def metapath(subpath:str, shortname:str, class_type: Type[Meta] ) -> tuple[Path, str]:
    """ Construct the full path of the meta file """
    path = settings.space_root 
    filename = ""
    if type == core.Folder:
        path = path / subpath / shortname / ".dm" 
        filename = f"meta.{class_type.__name__}.json"
    elif issubclass(class_type, core.Attachment):
        [parent_subpath, parent_name] = subpath.rsplit('/',1)
        path = path / parent_subpath / ".dm" / f"{parent_name}/attachments.{class_type.__name__}"
        filename = f"meta.{shortname}.json"
    else:
        path = path / subpath / ".dm" / shortname 
        filename = f"meta.{class_type.__name__}.json"
    return path, filename
    
def load(subpath:str, shortname:str, class_type: Type[Meta] ) -> Meta:
    """ Load a Meta Json according to the reuqested Class type """
    path, filename = metapath(subpath, shortname, class_type)
    path /= filename
    if not path.is_file():
        raise api.Exception(status_code=404, error=api.Error(type="db", code=12, message="requested object not found"))
    return class_type.parse_raw(path.read_text())

def save(subpath : str, meta : core.Meta):
    """ Save Meta Json to respectiv file """
    path, filename = metapath(subpath, meta.shortname, meta.__class__)
    """

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
    """
    
    if not path.is_dir():
        os.makedirs(path)

    with open(path / filename, "w") as file:
        file.write(meta.json(exclude_none=True))

    
def create(subpath : str, meta : core.Meta):
    path, filename = metapath(subpath, meta.shortname, meta.__class__)
    if (path/filename).is_file():
        raise api.Exception(status_code=401, error=api.Error(type="create", code=30, message = "already exists"))

    if not path.is_dir():
        os.makedirs(path)

    with open(path / filename, "w") as file:
        file.write(meta.json(exclude_none=True))

def update(subpath : str, meta : core.Meta):
    path, filename = metapath(subpath, meta.shortname, meta.__class__)
    if not (path/filename).is_file():
        raise api.Exception(status_code=404, error=api.Error(type="update", code=30, message = "does not exist"))
    
    with open(path / filename, "w") as file:
        file.write(meta.json(exclude_none=True))

def delete(subpath : str, meta : core.Meta):
    path, filename = metapath(subpath, meta.shortname, meta.__class__)
    if not path.is_dir() or not (path/filename).is_file():
        raise api.Exception(status_code=404, error=api.Error(type="delete", code=30, message = "does not exist"))
    pathname=path/filename
    if pathname.is_file():
        pathname.unlink
    # Remove folder if empty
    os.rmdir(path)

import sys
from models.enums import ResourceType
from utils.settings import settings
import models.core as core
from typing import TypeVar, Type
import models.api as api
import os
import re
from pathlib import Path
from utils.logger import logger

Meta = TypeVar("Meta", bound=core.Meta)

FILE_PATTERN = re.compile("\\.dm\\/([a-zA-Z0-9_]*)\\/meta\\.([a-zA-z]*)\\.json$")
FOLDER_PATTERN = re.compile("\\/([a-zA-Z0-9_]*)\\/.dm\\/meta.folder.json$")


def serve_query(query: api.Query) -> tuple[int, list[core.Record]]:
    records: list[core.Record] = []
    total: int = 0
    if query.type == api.QueryType.subpath:
        path = settings.space_root / query.subpath
        if query.include_fields is None:
            query.include_fields = []

        # Gel all matching entries
        entries_glob = ".dm/*/meta.*.json"
        for one in path.glob(entries_glob):
            match = FILE_PATTERN.search(str(one))
            if not match or not one.is_file:
                logger.error("Invalid file pattern")
                continue
            shortname = match.group(1)
            resource_name = match.group(2).lower()
            if (
                query.filter_types
                and not ResourceType(resource_name) in query.filter_types
            ):
                logger.info(resource_name + " resource is not listed in filter types")
                continue

            if query.filter_shortnames and shortname not in query.filter_shortnames:
                continue

            total += 1
            if len(records) >= query.limit or total < query.offset:
                continue
            resource_class = getattr(sys.modules["models.core"], resource_name.title())
            records.append(
                resource_class.parse_raw(one.read_text()).to_record(
                    query.subpath, shortname, query.include_fields
                )
            )
        # Get all matching sub folders
        subfolders_glob = "*/.dm/meta.folder.json"
        for one in path.glob(subfolders_glob):
            match = FOLDER_PATTERN.search(str(one))

            if not match or not one.is_file:
                logger.error("Invalid file pattern")
                continue
            shortname = match.group(1)
            if query.filter_shortnames and shortname not in query.filter_shortnames:
                continue
            total += 1
            if len(records) >= query.limit or total < query.offset:
                continue
            records.append(
                core.Folder.parse_raw(one.read_text()).to_record(
                    query.subpath, shortname, query.include_fields
                )
            )
    return total, records


def metapath(subpath: str, shortname: str, class_type: Type[Meta]) -> tuple[Path, str]:
    """Construct the full path of the meta file"""
    path = settings.space_root
    filename = ""
    if issubclass(class_type, core.Folder):
        path = path / subpath / shortname / ".dm"
        filename = "meta." + class_type.__name__.lower() + ".json"
    elif issubclass(class_type, core.Attachment):
        [parent_subpath, parent_name] = subpath.rsplit("/", 1)
        attachment_folder = parent_name + "/attachments." + class_type.__name__.lower()
        path = path / parent_subpath / ".dm" / attachment_folder
        filename = f"meta.{shortname}.json"
    else:
        path = path / subpath / ".dm" / shortname
        filename = "meta." + class_type.__name__.lower() + ".json"
    return path, filename


def load(subpath: str, shortname: str, class_type: Type[Meta]) -> Meta:
    """Load a Meta Json according to the reuqested Class type"""
    path, filename = metapath(subpath, shortname, class_type)
    path /= filename
    if not path.is_file():
        raise api.Exception(
            status_code=404,
            error=api.Error(type="db", code=12, message="requested object not found"),
        )
    return class_type.parse_raw(path.read_text())


def save(subpath: str, meta: core.Meta):
    """Save Meta Json to respectiv file"""
    path, filename = metapath(subpath, meta.shortname, meta.__class__)

    if not path.is_dir():
        os.makedirs(path)

    with open(path / filename, "w") as file:
        file.write(meta.json(exclude_none=True))


def create(subpath: str, meta: core.Meta):
    path, filename = metapath(subpath, meta.shortname, meta.__class__)
    if (path / filename).is_file():
        raise api.Exception(
            status_code=401,
            error=api.Error(type="create", code=30, message="already exists"),
        )

    if not path.is_dir():
        os.makedirs(path)

    with open(path / filename, "w") as file:
        file.write(meta.json(exclude_none=True))


async def save_payload(subpath: str, meta: core.Meta, attachment):
    path, filename = metapath(subpath, meta.shortname, meta.__class__)

    if not (path / filename).is_file():
        raise api.Exception(
            status_code=401,
            error=api.Error(type="create", code=30, message="missing metadata"),
        )

    payload_filename = filename.replace(".json", Path(attachment.filename).suffix)
    payload_filename = payload_filename.replace("meta.", "")

    with open(path / payload_filename, "wb") as file:
        while content := await attachment.read(1024):
            file.write(content)


def update(subpath: str, meta: core.Meta):
    path, filename = metapath(subpath, meta.shortname, meta.__class__)
    if not (path / filename).is_file():
        raise api.Exception(
            status_code=404,
            error=api.Error(type="update", code=30, message="does not exist"),
        )

    with open(path / filename, "w") as file:
        file.write(meta.json(exclude_none=True))


def move(subpath: str, newpath: str, meta: core.Meta):
    path, filename = metapath(subpath, meta.shortname, meta.__class__)
    # Fixme ... decide what to move depending on the type
    os.rename(src=path / filename, dst=newpath)


def delete(subpath: str, meta: core.Meta):
    path, filename = metapath(subpath, meta.shortname, meta.__class__)
    if not path.is_dir() or not (path / filename).is_file():
        raise api.Exception(
            status_code=404,
            error=api.Error(type="delete", code=30, message="does not exist"),
        )

    pathname = path / filename
    if pathname.is_file():
        os.remove(pathname)
        media_name = filename.split(".")[1]
        files = os.listdir(path)
        for file in files:
            if media_name in file:
                os.remove(path / file)
                break

    # Remove folder if empty
    if len(os.listdir(path)) == 0:
        os.rmdir(path)

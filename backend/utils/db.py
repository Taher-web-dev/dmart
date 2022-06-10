import sys
from models.enums import ContentType, ResourceType
from utils.settings import settings
import models.core as core
from typing import Any, TypeVar, Type
import models.api as api
import utils.regex as regex
import os
import re
import json
from pathlib import Path
from utils.logger import logger
from utils.redis_services import search as redis_search, get_doc_by_id
from fastapi import status
import aiofiles

MetaChild = TypeVar("MetaChild", bound=core.Meta)

FILE_PATTERN = re.compile("\\.dm\\/([a-zA-Z0-9_]*)\\/meta\\.([a-zA-z]*)\\.json$")
ATTACHMENT_PATTERN = re.compile(r"attachments.(\w*)\/meta\.(\w*)\.json$")
FOLDER_PATTERN = re.compile("\\/([a-zA-Z0-9_]*)\\/.dm\\/meta.folder.json$")
SPACES_PATTERN = re.compile("\\/([a-zA-Z0-9_]*)\\/.dm\\/meta.space.json$")


def locators_query(query: api.Query) -> tuple[int, list[core.Locator]]:
    """Given a query return the total and the locators
    Parameters
    ----------
    query: api.Query
        Query of type subpath

    Returns
    -------
    Total, Locators

    """

    locators: list[core.Locator] = []
    total: int = 0
    match query.type:
        case api.QueryType.subpath:
            path = settings.spaces_folder / query.space_name / query.subpath
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
                    logger.info(
                        resource_name + " resource is not listed in filter types"
                    )
                    continue

                if query.filter_shortnames and shortname not in query.filter_shortnames:
                    continue

                total += 1
                if len(locators) >= query.limit or total < query.offset:
                    continue
                resource_class = getattr(
                    sys.modules["models.core"], resource_name.title()
                )
                meta = resource_class.parse_raw(one.read_text())
                locators.append(
                    core.Locator(
                        uuid=meta.uuid,
                        space_name=query.space_name,
                        subpath=query.subpath,
                        shortname=shortname,
                        type=ResourceType(resource_name),
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
                if len(locators) >= query.limit or total < query.offset:
                    continue
                meta = core.Folder.parse_raw(one.read_text())
                locators.append(
                    core.Locator(
                        uuid=meta.uuid,
                        space_name=query.space_name,
                        subpath=query.subpath,
                        shortname=shortname,
                        type=core.ResourceType.locator,
                    )
                )
    return total, locators


async def serve_query(query: api.Query) -> tuple[int, list[core.Record]]:
    """Given a query return the total and the records

    Parameters
    ----------
    query: api.Query
        query of type [spaces, search, subpath]

    Returns
    -------
    Total, Records

    """
    records: list[core.Record] = []
    total: int = 0
    match query.type:
        case api.QueryType.spaces:
            path = settings.spaces_folder
            spaces_glob = "*/.dm/meta.space.json"
            for one in path.glob(spaces_glob):
                total += 1
                match = SPACES_PATTERN.search(str(one))
                if match:
                    records.append(
                        core.Space.parse_raw(one.read_text()).to_record(
                            query.subpath,
                            match.group(1),
                            query.include_fields if query.include_fields else [],
                        )
                    )

        case api.QueryType.search:
            search_res: list = []
            for schema_name in query.filter_schema_names:
                search_res.extend(
                    redis_search(
                        space_name=query.space_name, 
                        schema_name=schema_name,
                        search=query.search,
                        filters={
                            "resource_type": query.filter_types,
                            "shortname": query.filter_shortnames,
                            "tags": query.filter_tags,
                            "subpath": [query.subpath] if query.subpath != "/" else []
                        },
                        limit=query.limit,
                        offset=query.offset,
                        sort_by=query.sort_by
                    )
                )
            for one in search_res:
                doc_content = json.loads(one.json)

                # This means redis returned content payload object not meta object
                payload_doc_content = None
                if not re.match(regex.META_DOC_ID, one.id):
                    payload_doc_content = doc_content
                    doc_content = get_doc_by_id(payload_doc_content["meta_doc_id"])

                if "tags" not in doc_content or doc_content["tags"] == "none":
                    doc_content["tags"] = []

                resource_class = getattr(sys.modules["models.core"], doc_content["resource_type"].title())
                resource_obj = resource_class.parse_obj(doc_content)
                resource_base_record = resource_obj.to_record(doc_content["subpath"], doc_content["shortname"], query.include_fields)
                if payload_doc_content and query.retrieve_json_payload:
                    payload_doc_content.pop("subpath", None)
                    payload_doc_content.pop("resource_type", None)
                    payload_doc_content.pop("shortname", None)
                    payload_doc_content.pop("meta_doc_id", None)
                    resource_base_record.attributes["payload"] = payload_doc_content
                records.append(resource_base_record)

        case api.QueryType.subpath:
            subpath = query.subpath
            if subpath[0] == "/":
                subpath = "." + subpath
            path = settings.spaces_folder / query.space_name / subpath
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
                    logger.info(
                        resource_name + " resource is not listed in filter types"
                    )
                    continue

                if query.filter_shortnames and shortname not in query.filter_shortnames:
                    continue

                resource_class = getattr(
                    sys.modules["models.core"], resource_name.title()
                )
                resource_obj = resource_class.parse_raw(one.read_text())
                if query.filter_tags and (
                    not resource_obj.tags
                    or not any(item in resource_obj.tags for item in query.filter_tags)
                ):
                    continue
                total += 1
                if len(records) >= query.limit or total < query.offset:
                    continue

                resource_base_record = resource_obj.to_record(
                    query.subpath, shortname, query.include_fields
                )
                if (
                    query.retrieve_json_payload
                    and resource_obj.payload
                    and resource_obj.payload.content_type
                    and resource_obj.payload.content_type == ContentType.json
                    and (path / resource_obj.payload.body).is_file()
                ):
                    async with aiofiles.open(
                        path / resource_obj.payload.body, "r"
                    ) as payload_file_content:
                        resource_base_record.attributes["payload"] = json.loads(
                            await payload_file_content.read()
                        )

                # Get all matching attachments
                attachments_path = path / ".dm" / shortname
                attachments_glob = "attachments.*/meta.*.json"
                attachments_dict: dict[ResourceType, list[Any]] = {}
                for one in attachments_path.glob(attachments_glob):
                    match = ATTACHMENT_PATTERN.search(str(one))
                    if not match or not one.is_file:
                        logger.error("Invalid file pattern")
                        continue
                    attach_shortname = match.group(2)
                    attach_resource_name = match.group(1).lower()
                    if (
                        query.filter_types
                        and not ResourceType(attach_resource_name) in query.filter_types
                    ):
                        logger.info(
                            attach_resource_name
                            + " resource is not listed in filter types"
                        )
                        continue
                    resource_class = getattr(
                        sys.modules["models.core"], attach_resource_name.title()
                    )
                    resource_record_obj = resource_class.parse_raw(
                        one.read_text()
                    ).to_record(
                        query.subpath + "/" + shortname,
                        attach_shortname,
                        query.include_fields,
                    )
                    if attach_resource_name in attachments_dict:
                        attachments_dict[attach_resource_name].append(
                            resource_record_obj
                        )
                    else:
                        attachments_dict[attach_resource_name] = [resource_record_obj]

                resource_base_record.attachments = attachments_dict
                records.append(resource_base_record)

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


def metapath(
    space_name: str, subpath: str, shortname: str, class_type: Type[MetaChild]
) -> tuple[Path, str]:
    """Construct the full path of the meta file"""
    path = settings.spaces_folder / space_name
    filename = ""
    if subpath[0] == "/":
        subpath = f".{subpath}"
    if issubclass(class_type, core.Folder):
        path = path / subpath / shortname / ".dm"
        filename = f"meta.{class_type.__name__.lower()}.json"
    elif issubclass(class_type, core.Attachment):
        [parent_subpath, parent_name] = subpath.rsplit("/", 1)
        attachment_folder = f"{parent_name}/attachments.{class_type.__name__.lower()}"
        path = path / parent_subpath / ".dm" / attachment_folder
        filename = f"meta.{shortname}.json"
    else:
        path = path / subpath / ".dm" / shortname
        filename = f"meta.{class_type.__name__.lower()}.json"
    return path, filename


def payload_path(space_name: str, subpath: str, class_type: Type[MetaChild]) -> Path:
    """Construct the full path of the meta file"""
    path = settings.spaces_folder
    if subpath[0] == "/":
        subpath = f".{subpath}"
    if issubclass(class_type, core.Attachment):
        [parent_subpath, parent_name] = subpath.rsplit("/", 1)
        attachment_folder = f"{parent_name}/attachments.{class_type.__name__.lower()}"
        path = path / space_name / parent_subpath / ".dm" / attachment_folder
    else:
        path = path / space_name / subpath
    return path


def load(
    space_name: str, subpath: str, shortname: str, class_type: Type[MetaChild]
) -> MetaChild:
    """Load a Meta Json according to the reuqested Class type"""
    path, filename = metapath(space_name, subpath, shortname, class_type)
    path /= filename
    if not path.is_file():
        raise api.Exception(
            status_code=status.HTTP_404_NOT_FOUND,
            error=api.Error(type="db", code=12, message="requested object not found"),
        )
    return class_type.parse_raw(path.read_text())


async def save(space_name: str, subpath: str, meta: core.Meta):
    """Save Meta Json to respectiv file"""
    path, filename = metapath(space_name, subpath, meta.shortname, meta.__class__)

    if not path.is_dir():
        os.makedirs(path)

    async with aiofiles.open(path / filename, "w") as file:
        await file.write(meta.json(exclude_none=True))


async def create(space_name: str, subpath: str, meta: core.Meta):
    path, filename = metapath(space_name, subpath, meta.shortname, meta.__class__)
    if (path / filename).is_file():
        raise api.Exception(
            status_code=status.HTTP_400_BAD_REQUEST,
            error=api.Error(type="create", code=30, message="already exists"),
        )

    if not path.is_dir():
        os.makedirs(path)

    async with aiofiles.open(path / filename, "w") as file:
        await file.write(meta.json(exclude_none=True))


async def save_payload(space_name: str, subpath: str, meta: core.Meta, attachment):
    path, filename = metapath(space_name, subpath, meta.shortname, meta.__class__)
    payload_file_path = payload_path(space_name, subpath, meta.__class__)
    payload_filename = meta.shortname + Path(attachment.filename).suffix

    if not (path / filename).is_file():
        raise api.Exception(
            status_code=status.HTTP_400_BAD_REQUEST,
            error=api.Error(type="create", code=30, message="metadata is missing"),
        )

    async with aiofiles.open(payload_file_path / payload_filename, "wb") as file:
        while content := await attachment.read(1024):
            await file.write(content)


async def save_payload_from_json(
    space_name: str, subpath: str, meta: core.Meta, payload_data: dict
):
    path, filename = metapath(space_name, subpath, meta.shortname, meta.__class__)
    payload_file_path = payload_path(space_name, subpath, meta.__class__)
    payload_filename = f"{meta.shortname}.json"

    if not (path / filename).is_file():
        raise api.Exception(
            status_code=status.HTTP_400_BAD_REQUEST,
            error=api.Error(type="create", code=30, message="metadata is missing"),
        )

    async with aiofiles.open(payload_file_path / payload_filename, "w") as file:
        await file.write(json.dumps(payload_data))


async def update(space_name: str, subpath: str, meta: core.Meta):
    path, filename = metapath(space_name, subpath, meta.shortname, meta.__class__)
    if not (path / filename).is_file():
        raise api.Exception(
            status_code=status.HTTP_404_NOT_FOUND,
            error=api.Error(type="update", code=30, message="does not exist"),
        )

    async with aiofiles.open(path / filename, "w") as file:
        await file.write(meta.json(exclude_none=True))


async def move(
    space_name: str,
    src_subpath: str,
    src_shortname: str,
    dest_subpath: str | None,
    dest_shortname: str | None,
    meta: core.Meta,
):
    """Move the file that match the criteria given, remove source folder if empty

    Parameters
    ----------
    space_name: str,
    src_subpath: str,
    src_shortname: str,
    dest_subpath: str | None,
    dest_shortname: str | None,
    meta: core.Meta
    """

    src_path, src_filename = metapath(
        space_name, src_subpath, src_shortname, meta.__class__
    )
    dest_path, dest_filename = metapath(
        space_name,
        dest_subpath or src_subpath,
        dest_shortname or src_shortname,
        meta.__class__,
    )

    # Create dest dir if not exist
    if not os.path.isdir(dest_path):
        os.makedirs(dest_path)

    meta_updated = False
    # Incase of attachment, the shortname is a file so it should be moved
    # use is instance instead
    if isinstance(meta, core.Attachment):
        # Move file
        os.rename(src=src_path / src_filename, dst=dest_path / dest_filename)

        # Move media files with the meta file
        if isinstance(meta, core.Media):
            media_name = src_filename.split(".")[-2]
            files = os.listdir(src_path)
            for file in files:
                if media_name in file:
                    file_name = dest_filename.split(".")[-2]
                    file_ext = file.split(".")[-1]
                    renamed_file = f"{file_name}.{file_ext}"
                    os.rename(src=src_path / file, dst=dest_path / renamed_file)

                    # Don't handle if payload doesn't exist
                    if not meta.payload or not meta.payload.body:
                        break
                    # Update file name inside meta file
                    meta.payload.body = renamed_file
                    meta_updated = True
                    break

    # Rename folder only if meta not Attachment type
    else:
        os.rename(src=src_path, dst=dest_path)

    # Update meta shortname
    if dest_shortname:
        meta.shortname = dest_shortname
        meta_updated = True

    # Store meta updates in the file
    if meta_updated:
        async with aiofiles.open(dest_path / dest_filename, "w") as opened_file:
            await opened_file.write(meta.json(exclude_none=True))

    # Delete Src path if empty
    if src_path.is_dir() and len(os.listdir(src_path)) == 0:
        os.removedirs(src_path)


def delete(space_name: str, subpath: str, meta: core.Meta):
    """Delete the file that match the criteria given, remove folder if empty

    Parameters
    ----------
    space_name: str
    subpath: str
    shortname: str
    meta: Meta

    Exception
    ----------
    api.Exception:
        HTTP_404_NOT_FOUND
    """

    path, filename = metapath(space_name, subpath, meta.shortname, meta.__class__)
    if not path.is_dir() or not (path / filename).is_file():
        raise api.Exception(
            status_code=status.HTTP_404_NOT_FOUND,
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
        os.removedirs(path)

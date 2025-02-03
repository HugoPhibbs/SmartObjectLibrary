from typing import List

import ifcopenshell

from core.opensearch_client import client
from src.core.FileStore import FileStore
from src.core.LibraryObject import LibraryObject

file_store = FileStore()


def get_by_id(object_id: str, format="ifc") -> LibraryObject | str:
    if format == "json":
        response = client.get(index="objects", id=object_id)
        return response["_source"]

    elif format == "ifc":
        ifc_file_path = file_store.object_ifc_path(object_id)
        return ifc_file_path


def get_all_objects(format="ifc") -> List[LibraryObject] | str:
    if format == "json":
        response = client.search(index="objects", body={"query": {"match_all": {}}})
        return response["hits"]["hits"]

    elif format == "ifc":
        objects = []
        for hit in get_all_objects("json"):
            object_id = hit["_id"]
            ifc_file_path = file_store.object_ifc_path(object_id)
            objects.append(ifc_file_path)

        return objects


def get_by_filter(query_filter: dict) -> List[LibraryObject]:
    response = client.search(index="objects", body={"query": query_filter})
    return response["hits"]["hits"]


def get_by_nlp(nlp_query) -> List[LibraryObject]:
    pass


def delete_by_id(object_id: str) -> None:
    response = client.delete(index="objects", id=object_id)
    file_store.delete_object_ifc(object_id)
    return response


def update_by_id(object_id: str, ifc_file: ifcopenshell.file):
    object, _ = LibraryObject.from_ifc_file(ifc_file)
    response = client.update(index="objects", id=object_id, body={"doc": object})
    return response


def create_object(object_ifc_file: ifcopenshell.file, ifc_type="IfcBeam"):
    """
    Handles creating a new object in the OpenSearch index

    Assumes that the new object data is an ifc file

    :param object_ifc_file: ifc file
    :return:
    """
    object, _ = LibraryObject.from_ifc_file(object_ifc_file, ifc_type)
    response = client.index(index="objects", body=object, id=object.id)
    file_store.add_object_ifc(object.id, object_ifc_file)

    return response

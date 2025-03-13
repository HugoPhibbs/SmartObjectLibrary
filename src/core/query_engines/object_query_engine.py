from typing import List

import ifcopenshell

from src.core.QueryBuilder import OpenSearchQueryBuilder
from src.core.opensearch_client import client
from src.core.utils import opensearch_hits_to_dicts
from src.core.FileStore import FileStore
from src.core.LibraryObject import LibraryObject

from werkzeug.datastructures import FileStorage

from PIL import Image

# Query engine for objects

file_store = FileStore()


def get_file_by_object_id(object_id: str, file_type="ifc") -> dict | str:
    if file_type == "json":
        response = client.get(index="objects", id=object_id)
        return LibraryObject.from_opensearch_hit(response).to_dict()

    elif file_type == "ifc":
        return file_store.object_file_path(object_id, "ifc")

    elif file_type == "png":
        return file_store.object_file_path(object_id, "png")

    return "File type not supported"


def get_all_objects(format="ifc") -> List[LibraryObject] | str:
    if format == "json":
        response = client.search(index="objects", body={"query": {"match_all": {}}})
        results = opensearch_hits_to_dicts(response["hits"]["hits"])
        return results

    elif format == "ifc":
        objects = []
        for hit in get_all_objects("json"):
            object_id = hit["_id"]
            ifc_file_path = file_store.object_file_path(object_id, "ifc")
            objects.append(ifc_file_path)

        return objects


def get_by_filter(query_params: dict) -> List[LibraryObject]:
    query_filter = OpenSearchQueryBuilder("object").from_query_params_dict(query_params).build()

    response = client.search(index="objects", body=query_filter)
    results = opensearch_hits_to_dicts(response["hits"]["hits"])

    return results


def get_by_nlp(nlp_query) -> List[LibraryObject]:
    pass


def delete_by_id(object_id: str) -> None:
    response = client.delete(index="objects", id=object_id)
    file_store.delete_all_object_files(object_id)
    return response


def update_by_id(object_id: str, ifc_file: ifcopenshell.file):
    object, _ = LibraryObject.from_ifc_file(ifc_file)
    response = client.update(index="objects", id=object_id, body={"doc": object})
    return response


def create_object(object_ifc_file: ifcopenshell.file, ifc_type="IfcBeam", customID: str = None):
    """
    Handles creating a new object in the OpenSearch index from an IFC file

    :param object_ifc_file: ifc file
    :return: response from OpenSearch
    """
    object, _ = LibraryObject.from_ifc_file(object_ifc_file, ifc_type, customID)

    response = client.index(index="objects", body=object.to_dict(), id=object.id)
    file_store.add_object_file(object.id, object_ifc_file, "ifc")

    return response


def add_object_photo(object_id: str, photo: Image.Image):
    file_store.add_object_file(object_id, photo, "png")
    return "File added"


def get_manufacturers_booklet(object_id: str):
    return file_store.object_file_path(object_id, "manufacturers-booklet")


def get_environment_impact_assessment(object_id: str):
    return file_store.object_file_path(object_id, "environment")


def add_environmental_impact_assessment(file: FileStorage, object_id: str):
    file_store.add_object_file(object_id, file, "environment")
    return "File added"

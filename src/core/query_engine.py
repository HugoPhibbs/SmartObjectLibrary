from typing import List

import ifcopenshell

from core.opensearch_client import client
from src.core.FileStore import FileStore
from src.core.LibraryObject import LibraryObject

file_store = FileStore()


def get_file_by_object_id(object_id: str, file_type="ifc") -> LibraryObject | str:
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
        results = convert_hits_to_objects_with_score(response["hits"]["hits"])
        return results

    elif format == "ifc":
        objects = []
        for hit in get_all_objects("json"):
            object_id = hit["_id"]
            ifc_file_path = file_store.object_file_path(object_id, "ifc")
            objects.append(ifc_file_path)

        return objects

def convert_hits_to_objects_with_score(hits):
    results = []

    for hit in hits:
        results.append({'score': hit["_score"], "object": LibraryObject.from_opensearch_hit(hit).to_dict()})

    return results


def get_by_filter(query_filter: dict) -> List[LibraryObject]:
    response = client.search(index="objects", body=query_filter)
    results = convert_hits_to_objects_with_score(response["hits"]["hits"])
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


def create_object(object_ifc_file: ifcopenshell.file, ifc_type="IfcBeam"):
    """
    Handles creating a new object in the OpenSearch index

    Assumes that the new object data is an ifc file

    :param object_ifc_file: ifc file
    :return:
    """
    object, _ = LibraryObject.from_ifc_file(object_ifc_file, ifc_type)
    response = client.index(index="objects", body=object, id=object.id)
    file_store.add_object_file(object.id, object_ifc_file, "ifc")

    return response

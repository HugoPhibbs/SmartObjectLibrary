from typing import List

import ifcopenshell

from src.site.core.InspectionRecordStore import InspectionRecordStore
from src.site.core.QueryBuilder import QueryBuilder
from src.site.core.utils import opensearch_hits_to_dicts
from src.site.core.FileStore import FileStore
from src.site.core.LibraryObject import LibraryObject

from src.site.core.opensearch_client import get_client

client = get_client()

from werkzeug.datastructures import FileStorage

from PIL import Image

# Query engine for objects

file_store = FileStore()
inspection_record_store = InspectionRecordStore()


def get_file_by_object_id(object_id: str, file_type="ifc") -> dict | str:
    if file_type == "json":
        response = client.get(index="objects", id=object_id)
        return response["_source"]

    elif file_type == "ifc":
        return file_store.object_file_path(object_id, "ifc")

    elif file_type == "png":
        return file_store.object_file_path(object_id, "png")

    return "File type not supported"


def get_all_objects(format="ifc") -> List[LibraryObject] | str:
    if format == "json":
        response = client.search(index="objects", body={"query": {"match_all": {}}, "size": 10000})
        results = opensearch_hits_to_dicts(response["hits"]["hits"])
        print(results[0] if len(results) > 0 else "No results found")
        return results

    elif format == "ifc":
        objects = []
        for hit in get_all_objects("json"):
            object_id = hit["_id"]
            ifc_file_path = file_store.object_file_path(object_id, "ifc")
            objects.append(ifc_file_path)

        return objects


def get_by_filter(query_params: dict) -> List[LibraryObject]:
    print(query_params)

    query_filter = QueryBuilder().from_query_params_dict(query_params).build()

    print(query_filter)

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


def add_manufacturers_booklet(file: FileStorage, object_id: str):
    file_store.add_object_file(object_id, file, "manufacturers-booklet")
    return "File added"


def get_environment_impact_assessment(object_id: str):
    return file_store.object_file_path(object_id, "environment")


def add_environmental_impact_assessment(file: FileStorage, object_id: str):
    file_store.add_object_file(object_id, file, "environment")
    return "File added"


def get_inspection_record(object_id: str, date: str):
    return inspection_record_store.inspection_record_path(object_id, date)


def add_inspection_record(file: FileStorage, object_id: str, date: str):
    inspection_record_store.add_inspection_record(object_id, file, date)
    return "File added"


def get_inspection_record_dates(object_id: str):
    return inspection_record_store.get_inspection_record_dates(object_id)

def get_manufacturers():
    response = client.search(
        index="objects",
        body={
            "size": 0,
            "aggs": {
                "manufacturers": {
                    "terms": {
                        "field": "identity_data.manufacturer.name.keyword",
                        "size": 1000
                    }
                }
            }
        }
    )

    unique_vals = [bucket["key"] for bucket in response["aggregations"]["manufacturers"]["buckets"]]

    return unique_vals

if __name__ == "__main__":
    manufacturer = get_manufacturers()

    mapping = client.indices.get_mapping(index="objects")
    print(mapping)
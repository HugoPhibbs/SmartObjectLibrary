from typing import List

from src.utils.opensearch_client import client


def get_by_id(object_id, format="ifc") -> dict:
    response = client.get(index="objects", id=object_id)
    return response["_source"]


def get_by_filter(query_filter) -> List[dict]:
    response = client.search(index="objects", body={"query": query_filter})
    return response["hits"]["hits"]


def get_by_nlp(nlp_query) -> List[dict]:
    pass


def delete_by_id(object_id) -> None:
    pass


def update_by_id(object_id, new_object_data):
    return None


def create_object(new_object_data):
    return None

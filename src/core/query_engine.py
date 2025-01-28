from typing import List

from src.opensearch_setup import client

def get_by_id(object_id, format="ifc") -> dict:
    pass


def get_by_filter(filter) -> List[dict]:
    pass


def get_by_nlp(nlp_query) -> List[dict]:
    pass


def delete_by_id(object_id) -> None:
    pass


def update_by_id(object_id, new_object_data):
    return None


def create_object(new_object_data):
    return None

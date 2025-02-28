import re

from src.core.QueryBuilder import OpenSearchQueryBuilder
from src.core.utils import opensearch_hits_to_dicts
from src.core.opensearch_client import client

from src.core.query_engines.object_query_engine import get_file_by_object_id


# Query engine for connections

def get_connection_by_id(connection_id):
    response = client.get(index="connections", id=connection_id)
    if response["found"]:
        return response["_source"]
    return None


def get_all_connections():
    response = client.search(index="connections", body={"query": {"match_all": {}}})
    return response["hits"]["hits"]


def get_connections_by_filter(query_params):
    connections_filter = OpenSearchQueryBuilder("connection").from_query_params_dict(query_params).build()

    response = client.search(index="connections", body=connections_filter)

    results = opensearch_hits_to_dicts(response["hits"]["hits"])

    return results

def get_unique_values(field):
    response = client.search(index="connections",
                             body={"size": 0, "aggs": {"unique_values": {"terms": {"field": field}}}})
    unique_values = [bucket["key"] for bucket in response["aggregations"]["unique_values"]["buckets"]]

    return unique_values

def match_connection(connection_type, beam_id, moment, shear):
    object = get_file_by_object_id(beam_id, "json")

    # First get the model
    model = object["property_sets"]["Identity Data"]["Model"]["value"]
    pattern = r"(\d+LL)(\d+\.\d+)"
    match = re.match(pattern, model)
    if match:
        model_dict = {"section_type": match.group(1), "mass_per_length": match.group(2)}
    else:
        return None

    query_params = {
        "match_connection_type": connection_type,
        "moment": moment,
        "shear": shear,
        "section_type": model_dict["section_type"],
        "mass_per_length": model_dict["mass_per_length"]
    }

    connections = get_connections_by_filter(query_params)

    if connections:
        return connections[0]


if __name__ == "__main__":
    print(match_connection("MEP-8", "1MqlONWM9DPguUA1H$xl0k", 50, 25))
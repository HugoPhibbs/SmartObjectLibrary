from core.QueryBuilder import OpenSearchQueryBuilder
from core.utils import opensearch_hits_to_dicts
from src.core.opensearch_client import client


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

    print(connections_filter)

    response = client.search(index="connections", body=connections_filter)

    results = opensearch_hits_to_dicts(response["hits"]["hits"])

    return results


def get_section_types():
    response = client.search(index="connections",
                             body={"size": 0, "aggs": {"unique_values": {"terms": {"field": "section"}}}})
    unique_values = [bucket["key"] for bucket in response["aggregations"]["unique_values"]["buckets"]]

    return unique_values


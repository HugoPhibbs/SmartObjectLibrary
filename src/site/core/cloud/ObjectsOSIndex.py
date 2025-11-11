from opensearchpy import NotFoundError

from src.site.core.cloud.opensearch import get_os_client


class ObjectsOSIndex:

    def __init__(self, index_name="objects", client=None):
        self.index_name = index_name
        self.client = get_os_client() if client is None else client

    def get_object(self, object_id: str):
        try:
            response = self.client.get(index=self.index_name, id=object_id)
            return response["_source"]
        except NotFoundError as nfe:
            print(f"Object with ID {object_id} not found: {nfe}")
            return None

    def delete_object(self, object_id: str):
        return self.client.delete(index=self.index_name, id=object_id)

    def delete_objects_by_query(self, os_query: dict):
        return self.client.delete_by_query(index=self.index_name, body=os_query)

    def put_object(self, object_id: str, object_data: dict):
        return self.client.index(index=self.index_name, id=object_id, body=object_data)

    @staticmethod
    def opensearch_hits_to_results(hits: list):
        results = []

        for hit in hits:
            results.append({"data": hit["_source"], "score": hit["_score"]})

        return results

    def get_all_objects(self, size=10000):
        return self.get_objects_by_query({"query": {"match_all": {}}, "size": size}, size=size)

    def get_objects_by_query(self, os_query: dict, size=10000):
        response = self.client.search(index=self.index_name, body=os_query, size=size)
        return self.opensearch_hits_to_results(response["hits"]["hits"])
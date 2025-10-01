from src.site.core.opensearch_client import get_client

client = get_client("prod")

response = client.search(
    index="objects",
    body={
        "query": {"match_all": {}},
        "size": 10
    }
)
for hit in response["hits"]["hits"]:
    print(hit["_source"])

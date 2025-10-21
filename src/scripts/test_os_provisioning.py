from src.site.core.cloud.opensearch import get_os_client

client = get_os_client("prod")

response = client.search(
    index="objects",
    body={
        "query": {"match_all": {}},
        "size": 10
    }
)
for hit in response["hits"]["hits"]:
    print(hit["_source"])

from src.site.core.InspectionRecordStore import InspectionRecordStore
from src.site.core.FileStore import FileStore

from src.site.core.cloud.opensearch import get_os_client

client = get_os_client()

file_store = FileStore()
inspection_record_store = InspectionRecordStore()

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

import json
import os

import genson

from src.core.opensearch_client import client
from scripts.utils import convert_schema

# Script to upload all beam objects to OpenSearch

JSON_DIR = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\json"
SCHEMA_PATH = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\schema\beams_schema.json"


def add_json_file(file_path):
    object_id = os.path.basename(file_path).split(".")[0]

    with open(file_path, "r") as json_file:
        object_data = json.load(json_file)

    response = client.index(index="objects", body=object_data, id=object_id)
    return response


def add_all_files():
    for file in os.listdir(JSON_DIR):
        file_path = os.path.join(JSON_DIR, file)
        if os.path.isfile(file_path) and file.endswith(".json"):
            add_json_file(file_path)


def create_index(schema, delete_if_exists=True):
    index_exists = client.indices.exists(index="objects")

    if delete_if_exists and index_exists:
        if client.indices.exists(index="objects"):
            client.indices.delete(index="objects")

    elif index_exists:
        return

    client.indices.create(index="objects", body={
        "mappings": {
            "properties": schema
        }
    })


def write_schema():
    # Choose the first object to generate the schema, assume all objects have the same schema
    id = r"1MqlONWM9DPguUA1H$xl0k"

    with open(rf"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\json\{id}.json", "r") as json_file:
        object_data = json.load(json_file)

    builder = genson.SchemaBuilder()
    builder.add_object(object_data)
    schema = builder.to_schema()
    schema = convert_schema(schema)

    # Adjust some fields to be keywords
    schema["id"]["type"] = "keyword"

    with open(SCHEMA_PATH, "w") as schema_file:
        json.dump(schema, schema_file)

    return schema


def main():
    schema = write_schema()
    create_index(schema)
    add_all_files()


if __name__ == "__main__":
    main()

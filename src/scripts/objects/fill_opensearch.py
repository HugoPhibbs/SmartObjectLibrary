import json
import os
from pprint import pprint
import argparse

import genson

from src.site.core.LibraryObject import LibraryObject
from src.scripts.utils import convert_schema

from src.site.core.opensearch_client import get_client

# Script to upload all beam objects to OpenSearch

JSON_DIR = r"data\objects\json"
SCHEMA_PATH = r"data\schema\beams_schema.json"


def add_json_file(os_client, file_path):
    object_id = os.path.basename(file_path).split(".")[0]

    with open(file_path, "r") as json_file:
        object_data = json.load(json_file)

    try:
        response = os_client.index(index="objects", body=object_data, id=object_id)
    except Exception as e:
        print(f"Error uploading {file_path}: {e}")
        pprint(object_data)
        return None

    return response


def add_all_files(os_client):
    for file in os.listdir(JSON_DIR):
        file_path = os.path.join(JSON_DIR, file)
        if os.path.isfile(file_path) and file.endswith(".json"):
            add_json_file(os_client, file_path)


def create_index(os_client, schema=None, delete_if_exists=True):
    index_exists = os_client.indices.exists(index="objects")

    if delete_if_exists and index_exists:
        if os_client.indices.exists(index="objects"):
            os_client.indices.delete(index="objects")

    elif index_exists:
        return

    if schema is None:
        body = None
    else:
        body = {
            "mappings": {
                "properties": schema
            }
        }

    os_client.indices.create(index="objects", body=body)


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


def main(stage):
    schema = LibraryObject.get_opensearch_schema()
    os_client = get_client(stage)

    delete_index_if_exits = stage != "prod"

    create_index(os_client, schema=schema, delete_if_exists=delete_index_if_exits)
    add_all_files(os_client)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill the OpenSearch index with objects")
    parser.add_argument("--prod", action="store_true",
                        help="Fill the production OS domain, instead of the default dev domain")
    args = parser.parse_args()

    stage = "prod" if args.prod else "dev"

    main(stage)

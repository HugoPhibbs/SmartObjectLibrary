import json
import os
import time
from pprint import pprint
import argparse
from dotenv import load_dotenv

import genson
from tqdm import tqdm

from src.site.core.LibraryObject import LibraryObject
from src.scripts.utils import convert_schema
import src.scripts.add_category_data as add_category_data
from src.site.core.cloud.opensearch import get_os_client

# Script to upload all beam objects to OpenSearch

load_dotenv()
BASE_DIR = os.getenv("PROJECT_BASE_DIR")

JSON_DIR = os.path.join(BASE_DIR, r"data\objects\json")
SCHEMA_PATH = os.path.join(BASE_DIR, r"data\schema\beams_schema.json")


def add_json_file(os_client, file_path):
    object_id = os.path.basename(file_path).split(".")[0]

    with open(file_path, "r") as json_file:
        object_data = json.load(json_file)

    try:
        response = os_client.index(index="objects", body=object_data, id=object_id)
    except Exception as e:
        print(f"Error uploading {file_path}: {e}")
        # pprint(object_data)
        return None

    return response


def add_all_files(os_client, json_dir=JSON_DIR, sleep_interval=0):
    print("Adding files...")
    for file in tqdm(os.listdir(json_dir)):
        file_path = os.path.join(json_dir, file)
        if os.path.isfile(file_path) and file.endswith(".json"):
            add_json_file(os_client, file_path)
            time.sleep(sleep_interval)


def create_index(os_client, schema=None, delete_if_exists=True):
    index_exists = os_client.indices.exists(index="objects")

    if delete_if_exists and index_exists:
        print("Deleting existing index 'objects'")
        os_client.indices.delete(index="objects")

    elif index_exists:
        return

    print("Creating index 'objects'")

    settings = {
        "settings": {
            "index": {
                "mapping": {
                    "total_fields": { "limit": 1500 }
                }
            }
        },
    }

    body = settings | schema # merge into one dict
    os_client.indices.create(index="objects", body=body) # if schema is None, creates with no schema


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


def upload_json_to_os(stage, json_dir=JSON_DIR, sleep_interval=0, delete_index_if_exists=None):
    schema = LibraryObject.get_opensearch_schema()
    os_client = get_os_client(stage)

    if delete_index_if_exists is None:
        delete_index_if_exists = stage != "prod"

    create_index(os_client, schema=schema, delete_if_exists=delete_index_if_exists)
    add_all_files(os_client, json_dir=json_dir, sleep_interval=sleep_interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill the OpenSearch index with objects")
    parser.add_argument("--prod", action="store_true",
                        help="Fill the production OS domain, instead of the default dev domain")
    args = parser.parse_args()

    stage = "prod" if args.prod else "dev"

    upload_json_to_os(stage, delete_index_if_exists=True)
    add_category_data.main()
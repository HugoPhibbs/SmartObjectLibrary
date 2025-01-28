import json
import os
import re

import genson

from src.opensearch_setup import client

BEAMS_DIR = r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\beams-json"
SCHEMA_PATH = r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\beams_schema.json"


def convert_schema(schema):
    """
    Convert json schema to opensearch schema

    Should turn all values of "string" to "text", and "number" to "float"

    :param schema:
    :return:
    """
    schema_string = json.dumps(schema)
    schema_string = schema_string.replace('"string"', '"text"')
    schema_string = schema_string.replace('"number"', '"float"')
    schema_string = re.sub(r',\s*"required":\s*\[[^\]]*\]', '', schema_string)

    schema_json = json.loads(schema_string)

    return schema_json["properties"]


def ifcC4NZ_to_opensearch_schema(json_data):
    """
    Creates an opensearch index schema from custom IFC Construction 4.0 NZ data json

    :param json_data: json data as a dict
    :return: opensearch properties schema as a dict
    """
    builder = genson.SchemaBuilder()
    builder.add_object(json_data)
    schema = builder.to_schema()

    return convert_schema(schema)


def add_file(file_path):
    with open(file_path, "r") as json_file:
        beam_data = json.load(json_file)

    response = client.index(index="beams", body=beam_data)

    return response


def add_all_files():
    for file in os.listdir(BEAMS_DIR):
        file_path = os.path.join(BEAMS_DIR, file)
        if os.path.isfile(file_path) and file.endswith(".json"):
            add_file(file_path)


def create_index(schema, delete_if_exists=True):
    index_exists = client.indices.exists(index="beams")

    if delete_if_exists and index_exists:
        if client.indices.exists(index="beams"):
            client.indices.delete(index="beams")

    elif index_exists:
        return

    client.indices.create(index="beams", body={
        "mappings": {
            "properties": schema
        }
    })


def write_schema():
    with open(r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\beams-json\beams_0.json", "r") as json_file:
        beam_data = json.load(json_file)

    builder = genson.SchemaBuilder()
    builder.add_object(beam_data)
    schema = builder.to_schema()

    with open(SCHEMA_PATH, "w") as schema_file:
        json.dump(schema, schema_file)

    schema = convert_schema(schema)

    return schema


def main():
    schema = write_schema()
    create_index(schema)
    add_all_files()


if __name__ == "__main__":
    main()

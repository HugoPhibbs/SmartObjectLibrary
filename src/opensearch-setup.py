import os

from opensearchpy import OpenSearch
import json
from dotenv import load_dotenv
import genson
import re

load_dotenv()

HOST = "http://localhost"
PORT = 9200
auth = ("admin", os.getenv("OPENSEARCH_INITIAL_ADMIN_PASSWORD"))

client = OpenSearch(
    "http://localhost:9200",
    http_auth=auth,
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
    ssl_assert_hostname=False
)

with open(r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\beams-json\beams_0.json", "r") as json_file:
    beam_data = json.load(json_file)

builder = genson.SchemaBuilder()
builder.add_object(beam_data)
schema = builder.to_schema()


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

schema = convert_schema(schema)

# Delete index if it exists
if client.indices.exists(index="beams"):
    client.indices.delete(index="beams")

client.indices.create(index="beams", body={
    "mappings": {
        "properties": schema
    }
})

id = beam_data["id"]
response = client.index(index="beams", body=beam_data)

response = client.search(index="beams", body={
    "query": {
        "match": {
            "id": id
        }
    }
})

print(response["hits"]["hits"][0]["_source"]) # TODO, figure out why nothing is here

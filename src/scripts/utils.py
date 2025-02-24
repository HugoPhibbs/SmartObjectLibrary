import json
import re


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

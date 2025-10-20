# Using the Product Library API

- The API is deployed using an HTTP endpoint - this is how you query data

---

## Authorization

- All API requests must have an attached Authorization header, using a Bearer token
- Please ask, and a token will be provided to you.
- To add an Authorization header use the following format:

```json
{
  "Authorization": "Bearer <your_token_here>"
}
```

---

## Endpoints

### GET /object/query

- This is used to query all matching objects based on the query criteria you provide
- Query parameters are passed as HTTP GET query parameters. While the filters can be relatively complex (e.g. using
  range
  queries, fuzzy logic etc), we will focus on simple equality matches for now.
- Currently, any returned objects are represented in a _full_ json format - there is currently no capability to
  selectively choose which attributes to return.
- Query Parameters should have the following format:
    - For matching on a single value: `<attribute_name>=<value>`, e.g. `object_id=2Dqkuqrwv2jwq8BtWz10gA`
    - For matching on multiple values: `list_<attribute_name>=<value1>,<value2>,<value3>`,
      e.g. `list_category=steel,framing` will return all objects that are **both** in the steel and framing categories.
      You can use `list_should_<attribute_name>>=<value1>,<value2>,<value3>` to return all objects that have attributes
      equal to **any** of the provided values.
- Some key object attributes you may be interested in:
    - `object_id`: the unique identifier for an object
    - `name`: the name of the object
    - `category`: the category/categories the object belongs to
    - `cost.price`: the price of the object

- The response format is a JSON list containing the objects in json format, along with a score (between 0 and 1)
  indicating how well the object matched the query criteria. This score is only relevant when a query involves fuzzy
  logic (which isn't available with this route). An example response could be:

```json5
[
  {
    "data": {
      //... full object data here ...
    },
    "score": 1
  },
  {
    "data": {
      //... full object data here ...
    },
    "score": 0.9
  },
  //... more results here ...
]
```

#### Python Example

```python
import requests

api_endpoint = "..."  # Provided, something like: https://123456789.lambda-url.ap-southeast-2.on.aws/
api_token = ""  # Provided, a string of random characters

headers = {
    "Authorization": f"Bearer {api_token}"
}

filter_objects_url = f"{api_endpoint}/api/object"

filter_query_params = {
    "object_id": "2Dqkuqrwv2jwq8BtWz10gA",
    "list_category": "steel,framing",
    "cost.price": 100
}

response = requests.get(filter_objects_url, headers=headers, params=filter_query_params)
```

### GET /object/os-query

- A more advanced query endpoint using the OpenSearch Query DSL. We recommend using this endpoint for more complex
  queries, e.g. range queries, fuzzy logic etc. It is much more capable than the GET `/object/query` endpoint.
- To use this endpoint, you must send a JSON body containing the query according to the OpenSearch
  Query DSL. See the OpenSearch DSL query docs [here](https://docs.opensearch.org/latest/query-dsl/).
- While the regular GET /object/query supports some aliases for key attributes, this one doesn't. For example
  e.g. `category` is short for
  the exact attribute path `identity_data.primary_info.categories`. Consequently, you will have to
  use the _exact_ attribute path within queries.
- The response format is identical to the GET `/object/query` endpoint.
- An example query body could be (note that you don't need the top level "query" key from the OpenSearch docs):

```json
{
  "bool": {
    "must": [
      {
        "should": {
          "term": {
            "category": "steel"
          }
        }
      },
      {
        "range": {
          "cost.price": {
            "gte": 50,
            "lte": 150
          }
        }
      }
    ]
  }
}
```

#### Python Example

```python
import requests
import json

api_endpoint = "..."  # Provided, something like: https://123456789.lambda-url.ap-southeast-2.on.aws/
api_token = ""  # Provided, a string of random characters

headers = {
    "Authorization": f"Bearer {api_token}"
}

filter_objects_url = f"{api_endpoint}/api/object"

filter_query_body = {
    "bool": {
        "must": [
            {
                "should": {
                    "term": {
                        "category": "steel"
                    }
                }
            },
            {
                "range": {
                    "cost.price": {
                        "gte": 50,
                        "lte": 150
                    }
                }
            }
        ]
    }
}

response = requests.get(filter_objects_url, headers=headers, data=json.dumps(filter_query_body))
```

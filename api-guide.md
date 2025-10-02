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

### /object/filter

- This is used to query all _matching_ objects based on the filter criteria you provide
- Filter parameters are passed as query parameters. While the filters can be relatively complex (e.g. using range
  queries, fuzzy logic etc), we will focus on simple equality matches for now.
- Currently, any returned objects are represented in a _full_ json format - there is no capability to select which
  attributes you would like only. 

#### Examples

```python
import requests

api_endpoint = "..."  # Provided, something like: https://123456789.lambda-url.ap-southeast-2.on.aws/
api_token = ""  # Provided, a string of random characters

headers = {
    "Authorization": f"Bearer {api_token}"
}

filter_objects_url = f"{api_endpoint}/object"

query_params = {
    "object_id": "2Dqkuqrwv2jwq8BtWz10gA",
}

response = requests.get(filter_objects_url, headers=headers, params=query_params)
```
from src.core.opensearch_client import client


class OpenSearchQueryBuilder:
    def __init__(self):
        self.query = {
            "query": {
                "bool": {
                    "filter": []
                }
            }
        }

    def __parse_value(self, value):
        if value == "true" or value == "True":
            return True
        elif value == "false" or value == "False":
            return False
        return value

    def add_filter(self, field, value, operator="term", append_value_to_field=True):
        if append_value_to_field:
            field = f"{field}.value"

        value = self.__parse_value(value)

        self.query["query"]["bool"]["filter"].append({operator: {field: value}})
        return self

    def add_range_filter(self, field, gte, lte):
        raise NotImplementedError
        # self.query["query"]["bool"]["filter"].append({
        #     "range": {
        #         field: {"gte": gte, "lte": lte}
        #     }
        # })
        # return self

    def build(self):
        return self.query

    def from_query_params_dict(self, query_params_dict: dict):
        for key, value in query_params_dict.items():
            self.add_filter(key, value)
        return self

if __name__ == "__main__":
    # Example usage:
    query_builder = OpenSearchQueryBuilder()

    query = (query_builder
             .add_filter("property_sets.Pset_BeamCommon.LoadBearing", "True")
             # .add_filter("colour", "red")
             # .add_range_filter("price", 100, 500)
             .build())

    import json

    print(json.dumps(query, indent=2))

    # response = client.search(index="objects", body=query)

    # print(response)
    # Output:

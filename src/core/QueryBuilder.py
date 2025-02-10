from src.core.opensearch_client import client


class OpenSearchQueryBuilder:
    def __init__(self):
        self.query = {
            "query": {
                "bool": {
                    "filter": []
                },
                "range": {}
            }
        }

    def __parse_query_params(self, query_params_dict: dict):
        """
        Parses query parameters from the request into a dictionary

        :param query_params: query parameters
        :return: dictionary of query parameters
        """

        parsed_params = {"bool": {}, "range": {}}

        for key, value in query_params_dict.items():
            if value == "NaN" or value == "" or not value:
                continue

            if key.startswith("range_"):
                value_split = value.split("-")
                if len(value_split) == 2:
                    field = key.replace("range_", "")
                    field_path = OpenSearchQueryBuilder.fieldToObjectPath(field)
                    parsed_params["range"][field_path] = {"gte": float(value_split[0]), "lte": float(value_split[1])}

            else:
                field_path = OpenSearchQueryBuilder.fieldToObjectPath(key)
                parsed_params["bool"][field_path] = self.__parse_bool_value(value)

        return parsed_params

    def __parse_bool_value(self, value):
        if value in ["true", "True"]:
            return True
        elif value in ["false", "False"]:
            return False
        return value

    def add_filters(self, query_params_dict, bool_operator="term"):
        for field_path, value in query_params_dict["bool"].items():
            self.query["query"]["bool"]["filter"].append({bool_operator: {field_path: value}})

        for field_path, value in query_params_dict["range"].items():
            self.query["query"]["range"][field_path] = value

        return self

    def build(self):
        return self.query

    def from_query_params_dict(self, query_params_dict: dict):

        parsed_query_params = self.__parse_query_params(query_params_dict)

        self.add_filters(parsed_query_params)

        return self

    @staticmethod
    def fieldToObjectPath(field):
        if field in ["ifc_file_path", "ifc_type", "material", "name", "object_placement", "object_type"]:
            return field

        return f"property_sets.{field}.value"


if __name__ == "__main__":
    # Example usage:
    query_builder = OpenSearchQueryBuilder()

    query = (query_builder
             .from_query_params_dict(
        {"Pset_BeamCommon.LoadBearing": "True", "range_price": "100-500"})
             # .add_filter("colour", "red")
             # .add_range_filter("price", 100, 500)
             .build())

    print(query)

    # import json
    #
    # print(json.dumps(query, indent=2))
    #
    # response = client.search(index="objects", body=query)
    #
    # print(response)
    # Output:

import re


class OpenSearchQueryBuilder:
    """
    Class to build an OpenSearch query from query parameters

    Intended to convert query params received from an API request

    Example usage:
    query_builder = OpenSearchQueryBuilder("object")

    query = (query_builder
             .from_query_params_dict(
        {"Pset_BeamCommon.LoadBearing": "True", "range_price": "100to500", "match_material": "steel"})
             # .add_filter("colour", "red")
             # .add_range_filter("price", 100, 500)
             .build())

    print(query)
    """

    def __init__(self, object_type: str):
        self.query = {
            "query": {
                "bool": {
                    "filter": [],
                    "should": [],
                    "must": []
                }
            }
        }
        self.object_type = object_type

    def from_query_params_dict(self, query_params_dict: dict):
        """
        Builds a query from a dictionary of query parameters

        :param query_params_dict: dictionary of query parameters
        :return: self
        """

        parsed_query_params = self.__parse_query_params(query_params_dict)

        self.__add_filters(parsed_query_params)

        return self

    def build(self):
        """
        Builds the query

        :return: query as a dictionary
        """
        return self.query

    @staticmethod
    def __parse_range_string(range_string: str):
        """
        Parses a range string into a dictionary

        Example: "100to500" -> {"min": 100, "max": 500}, "-100to" -> {"min": -100, "max": None}

        :param range_string: range string
        :return: dictionary with min and max values
        """
        match = re.match(r'^(?P<min>-?\d+(?:\.\d+)?)?to(?P<max>-?\d+(?:\.\d+)?)?$', range_string)
        if match:
            return {k: float(v) if v is not None else None for k, v in match.groupdict().items()}
        return None

    def __parse_query_params(self, query_params_dict: dict):
        """
        Parses query parameters from the request into a dictionary

        :param query_params: query parameters
        :return: dictionary of query parameters
        """

        parsed_params = {"term": {}, "range": {}, "should_match": {}, "must_match": {}}

        for key, value in query_params_dict.items():
            if value == "NaN" or value == "" or not value:
                continue

            elif key.startswith("range_"):
                print(f"value {value}")
                min_max = OpenSearchQueryBuilder.__parse_range_string(value)
                print("min_max ", min_max)
                if min_max is not None:
                    field = key.replace("range_", "")
                    field_path = self.fieldToObjectPath(field)
                    parsed_params["range"][field_path] = {}
                    if min_max["min"] is not None:
                        parsed_params["range"][field_path]["gte"] = min_max["min"]
                    if min_max["max"] is not None:
                        parsed_params["range"][field_path]["lte"] = min_max["max"]

            elif key.startswith("bool_"):
                field = key.replace("bool_", "")
                field_path = self.fieldToObjectPath(field)
                if value.isdigit(): value = int(value)
                parsed_params["term"][field_path] = True if value == 1 else False
                print(value)

            elif key.startswith("match_"): # Assume match by itself is "should"
                field = key.replace("match_", "")
                field_path = self.fieldToObjectPath(field)
                parsed_params["should_match"][field_path] = value

            elif key.startswith("must_match_"):
                field = key.replace("must_match_", "")
                field_path = self.fieldToObjectPath(field)
                parsed_params["must_match"][field_path] = value

            else:
                field_path = self.fieldToObjectPath(key)
                parsed_params["term"][field_path] = OpenSearchQueryBuilder.__parse_term_value(value)

        print("parsed_params ", parsed_params)

        return parsed_params

    @staticmethod
    def __parse_term_value(value):
        try:
            return float(value)
        except ValueError:
            return value

    def __add_filters(self, query_params_dict, bool_operator="term"):
        for field_path, value in query_params_dict["term"].items():
            self.query["query"]["bool"]["filter"].append({bool_operator: {field_path: value}})

        for field_path, value in query_params_dict["range"].items():
            self.query["query"]["bool"]["filter"].append({"range": {field_path: value}})

        create_match_query = lambda path, val: {
            "match": {
                path: {
                    "query": val,
                    "fuzziness": "AUTO"
                }
            }
        }

        for field_path, value in query_params_dict["should_match"].items():
            self.query["query"]["bool"]["should"].append(create_match_query(field_path, value))

        for field_path, value in query_params_dict["must_match"].items():
            self.query["query"]["bool"]["must"].append(create_match_query(field_path, value))

        return self

    def fieldToObjectPath(self, field):
        """
        Maps a field to the object path in a OpenSearch index

        :param field: field name
        :return: the object path
        """
        if field.startswith("property_sets."):
            field += ".value"

        return field


if __name__ == "__main__":
    # Example usage:
    query_builder = OpenSearchQueryBuilder("object")

    query = (query_builder
             .from_query_params_dict(
        {"Pset_BeamCommon.LoadBearing": "True", "range_price": "100to500", "match_material": "steel"})
             # .add_filter("colour", "red")
             # .add_range_filter("price", 100, 500)
             .build())

    print(query)

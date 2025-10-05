import re


class QueryBuilder:
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

    def __init__(self):
        self.query = {
            "query": {
                "bool": {
                    "filter": [],
                    "should": [],
                    "must": []
                }
            }
        }

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

        parsed_params = {"term": [], "range": [], "should_match": [], "must_match": []}

        for key, value in query_params_dict.items():
            if value == "NaN" or value == "" or not value:
                continue

            elif key.startswith("range_"):
                print(f"value {value}")
                min_max = QueryBuilder.__parse_range_string(value)
                print("min_max ", min_max)
                if min_max is not None:
                    field = key.replace("range_", "")
                    field_path = self.fieldToObjectPath(field)
                    parsed_params["range"][field_path] = {}
                    range_obj = {}
                    if min_max["min"] is not None:
                        range_obj["gte"] = min_max["min"]
                    if min_max["max"] is not None:
                        range_obj["lte"] = min_max["max"]
                    parsed_params["range"].append(range_obj)

            elif key.startswith("bool_"):
                field = key.replace("bool_", "")
                field_path = self.fieldToObjectPath(field)
                if value.isdigit(): value = int(value)
                parsed_params["term"].append({field_path: True if value == 1 else False})

            elif key.startswith("match_"):  # Assume match by itself is "should"
                field = key.replace("match_", "")
                field_path = self.fieldToObjectPath(field)
                parsed_params["should_match"].append({field_path: value})

            elif key.startswith("must_match_"):
                field = key.replace("must_match_", "")
                field_path = self.fieldToObjectPath(field)
                parsed_params["must_match"].append({field_path: value})

            elif key.startswith("list_"):
                # Assume a term match for all values in a comma-separated list
                field = key.replace("list_", "")
                field_path = self.fieldToObjectPath(field)

                values = value.split(',')
                values = [v for v in values if v]

                for val in values:
                    parsed_params["term"].append({field_path: QueryBuilder.__parse_term_value(val)})

            else:
                field_path = self.fieldToObjectPath(key)
                parsed_params["term"].append({field_path: QueryBuilder.__parse_term_value(value)})

        print("parsed_params ", parsed_params)

        return parsed_params

    @staticmethod
    def __parse_term_value(value):
        try:
            return float(value)
        except ValueError:
            return value

    def __add_filters(self, query_params_dict, bool_operator="term"):
        for obj in query_params_dict["term"]:
            self.query["query"]["bool"]["filter"].append({bool_operator: obj})

        for obj in query_params_dict["range"]:
            self.query["query"]["bool"]["filter"].append({"range": obj})

        create_match_query = lambda obj: {
            "match": {
                obj.keys()[0]: {
                    "query": obj.values()[0],
                    "fuzziness": "AUTO"
                }
            }
        }

        for obj in query_params_dict["should_match"]:
            self.query["query"]["bool"]["should"].append(create_match_query(obj))

        for obj in query_params_dict["must_match"]:
            self.query["query"]["bool"]["must"].append(create_match_query(obj))

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
    query_builder = QueryBuilder()

    query = (query_builder
             .from_query_params_dict(
        {"Pset_BeamCommon.LoadBearing": "True", "range_price": "100to500", "match_material": "steel"})
             # .add_filter("colour", "red")
             # .add_range_filter("price", 100, 500)
             .build())

    print(query)

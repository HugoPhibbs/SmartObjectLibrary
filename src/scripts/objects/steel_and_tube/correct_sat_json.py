import re

__all__ = ["main"]


def correct_mass_per_metre(object_dict):
    # S&T has mass per metre in kg/ft, convert to kg/m
    value_ref = object_dict["property_sets"]["Structural"]["MassPerUnitLength_ANZRS"]  # A reference
    value_ref["value"] *= 3.28084
    value_ref["value"] = round(value_ref["value"], 1)

    return object_dict


def add_section_type(object_dict):
    model = object_dict["property_sets"]["Identity Data"]["Model"]["value"]
    pattern = r"(?P<section_type>\d{3,}[A-Z]{2})(?P<mass_per_length>\d+\.\d+)"
    match = re.match(pattern, model)
    if match:
        # TODO integrate this line of code into LibraryObject.from_ifc_file
        object_dict["property_sets"]["Identity Data"]["section_type"] = {"value": match.group("section_type"),
                                                                         "unit": "NO_UNIT"}
    else:
        raise Exception(f"Model: {model} does not match pattern")

    return object_dict


def main(object_dict):
    object_dict = correct_mass_per_metre(object_dict)
    object_dict = add_section_type(object_dict)

    return object_dict

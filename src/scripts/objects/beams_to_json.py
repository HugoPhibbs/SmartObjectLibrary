import math
import re
import os
import json
from random import random

import ifcopenshell.file
from src.core.LibraryObject import LibraryObject

# Script to convert all IFC files in the single objects directory to JSON files

OBJECTS_DIR = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects"


def correct_mass_per_metre(object_dict):
    # S&T has mass per metre in kg/ft, convert to kg/m
    value_ref = object_dict["property_sets"]["Structural"]["MassPerUnitLength_ANZRS"]  # A reference
    value_ref["value"] *= 3.28084
    value_ref["value"] = round(value_ref["value"], 1)

    return object_dict


def add_recycle_information(object_dict):
    is_recycled = random() > 0.7
    object_dict["is_recycled"] = is_recycled
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


def add_manufacturer_link(object_dict, link="https://www.steelandtube.co.nz"):
    object_dict["manufacturer_link"] = link


def main():
    object_ifc_dir = os.path.join(OBJECTS_DIR, "ifc")

    json_dir = os.path.join(OBJECTS_DIR, "json")

    if not os.path.exists(json_dir):
        os.makedirs(json_dir)

    for i, file in enumerate(os.listdir(object_ifc_dir)):
        file_path = os.path.join(object_ifc_dir, file)
        ifc_file = ifcopenshell.open(file_path)
        object, _ = LibraryObject.from_ifc_file(ifc_file)

        object_dict = object.to_dict()

        add_recycle_information(object_dict)

        correct_mass_per_metre(object_dict)

        add_section_type(object_dict)

        add_manufacturer_link(object_dict)

        with open(os.path.join(json_dir, f"{object.id}.json"), "w") as json_file:
            json.dump(object_dict, json_file, indent=4)


if __name__ == "__main__":
    main()

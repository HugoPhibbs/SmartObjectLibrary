import re
import os
import json
import ifcopenshell.file
from src.core.LibraryObject import LibraryObject

# Script to convert all IFC files in the single beams directory to JSON files

OBJECTS_DIR = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects"


def correct_mass_per_metre(object_dict):
    # S&T has mass per metre in kg/ft, convert to kg/m
    value_ref = object_dict["property_sets"]["Structural"]["MassPerUnitLength_ANZRS"]  # A reference
    value_ref["value"] *= 3.28084
    value_ref["value"] = round(value_ref["value"], 1)

    return object_dict

def add_section_type(object_dict):
    model = object_dict["property_sets"]["Identity Data"]["Model"]["value"]
    pattern = r"(?P<section>\d{3,}[A-Z]{2})(?P<mass_per_length>\d+\.\d+)"
    match = re.match(pattern, model)
    if match:
        # TODO integrate this line of code into LibraryObject.from_ifc_file
        object_dict["property_sets"]["Identity Data"]["section_type"] = {"value": match.group("section"), "unit": "NO_UNIT"}
    else:
        raise Exception(f"Model: {model} does not match pattern")

    return object_dict

def main():
    single_beams_ifc_dir = os.path.join(OBJECTS_DIR, "ifc")

    json_dir = os.path.join(OBJECTS_DIR, "json")

    if not os.path.exists(json_dir):
        os.makedirs(json_dir)

    for i, file in enumerate(os.listdir(single_beams_ifc_dir)):
        file_path = os.path.join(single_beams_ifc_dir, file)
        ifc_file = ifcopenshell.open(file_path)
        object, _ = LibraryObject.from_ifc_file(ifc_file)

        object_dict = object.to_dict()

        correct_mass_per_metre(object_dict)

        add_section_type(object_dict)

        with open(os.path.join(json_dir, f"{object.id}.json"), "w") as json_file:
            json.dump(object_dict, json_file, indent=4)

if __name__ == "__main__":
    main()
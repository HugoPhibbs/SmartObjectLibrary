import math
import re
import os
import json
from random import random

import ifcopenshell.file
from src.core.LibraryObject import LibraryObject
import src.scripts.objects.steel_and_tube.correct_sat_json as correct_json

# Script to convert all IFC files in the single objects directory to JSON files

OBJECTS_DIR = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects"


def add_recycle_information(object_dict):
    is_recycled = random() > 0.7
    object_dict["is_recycled"] = is_recycled
    return object_dict


def add_manufacturer_link(object_dict, link="https://github.com/HugoPhibbs/SmartObjectLibrary"):
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
        add_manufacturer_link(object_dict)

        # Comment out the below for S&T objects
        # object_dict = correct_json.main(object_dict)

        with open(os.path.join(json_dir, f"{object.id}.json"), "w") as json_file:
            json.dump(object_dict, json_file, indent=4)


if __name__ == "__main__":
    main()

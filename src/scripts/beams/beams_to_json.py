import os
import json
import ifcopenshell.file
from src.core.LibraryObject import LibraryObject

OBJECTS_DIR = r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\objects"

if __name__ == "__main__":

    single_beams_ifc_dir = os.path.join(OBJECTS_DIR, "ifc")

    json_dir = os.path.join(OBJECTS_DIR, "json")

    if not os.path.exists(json_dir):
        os.makedirs(json_dir)

    for i, file in enumerate(os.listdir(single_beams_ifc_dir)):
        file_path = os.path.join(single_beams_ifc_dir, file)
        ifc_file = ifcopenshell.open(file_path)
        object, _ = LibraryObject.from_ifc_file(ifc_file)

        with open(os.path.join(json_dir, f"{object.id}.json"), "w") as json_file:
            json.dump(object, json_file, indent=4)
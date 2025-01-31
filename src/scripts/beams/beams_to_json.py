import os
import json
import ifcopenshell.file
from src.core.ifc_to_json import ifc_file_to_object_dict

OBJECTS_DIR = r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\objects"

if __name__ == "__main__":

    single_beams_ifc_dir = os.path.join(OBJECTS_DIR, "ifc")

    json_dir = os.path.join(OBJECTS_DIR, "json")

    if not os.path.exists(json_dir):
        os.makedirs(json_dir)

    for i, file in enumerate(os.listdir(single_beams_ifc_dir)):
        file_path = os.path.join(single_beams_ifc_dir, file)
        ifc_file = ifcopenshell.open(file_path)
        object_dict, id, _ = ifc_file_to_object_dict(ifc_file)

        with open(os.path.join(json_dir, f"{id}.json"), "w") as json_file:
            json.dump(object_dict, json_file, indent=4)
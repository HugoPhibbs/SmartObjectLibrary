import json

from src.scripts.objects.wsp_building.wsp_objects_to_json import clean_wsp_json
from src.site.core import LibraryObject

import os
import ifcopenshell as ifc
from tqdm import tqdm
import ifcopenshell.util.element as util
from src.scripts.objects.parse_building_ifc_to_single_ifc import write_object_to_single_ifc

OBJECTS_DIR = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects"

def parse_exterior_data(ifc_file: ifc.file):
    object_names = ["Curtain Panels : System Panel : Glazed DG",
                    "Generic Models : 3d_Dead Load Brackets (OCF) : 3d_Dead Load Brackets (OCF)"]

    object_types = [
        "IfcPlate",
        "IfcBuildingElementProxy"
    ]
    unique_names = set()
    library_objects = []
    ifc_file_names = []

    for type in object_types:

        objects = ifc_file.by_type(type)

        for ifc_object in objects:
            name = ifc_object.Name
            if name in object_names and name not in unique_names:
                print(f"Found object: {ifc_object.Name}")
                file_name = write_object_to_single_ifc(ifc_file, ifc_object, OBJECTS_DIR)

                library_objects.append(LibraryObject.from_ifc_object(ifc_file, ifc_object))
                ifc_file_names.append(file_name)

                unique_names.add(name)

    return library_objects, ifc_file_names


def parse_room_data(ifc_file: ifc.file):
    included_families_types = [
        "Rectangular Mullion: 45 x 100 Mullion ( no offset)",
        "Rectangular Mullion: 45 x 100 Mullion",
        "System Panel: Glazed - Low Reflectance 6mm ( Offset 19 )",
        "45_Interiordoor_Active,Inactive_Glazedpanel: 910 active, 450 inactive x 2250 Leaf",
    ]

    object_types = [
        "IfcPlate",
        "IfcMember",
        "IfcDoor"
    ]

    unique_families = set()
    library_objects = []
    ifc_file_names = []

    for type in object_types:
        objects = ifc_file.by_type(type)

        for ifc_object in objects:
            psets = util.get_psets(ifc_object)
            object_family_and_type = psets.get("Other", {}).get("Family and Type")

            if object_family_and_type in included_families_types and object_family_and_type not in unique_families:
                library_object = LibraryObject.from_ifc_object(ifc_file, ifc_object)

                print(f"Found object: {object_family_and_type}")

                file_name = write_object_to_single_ifc(ifc_file, ifc_object, OBJECTS_DIR)

                library_objects.append(library_object)
                ifc_file_names.append(file_name)

                unique_families.add(object_family_and_type)

    return library_objects, ifc_file_names


def parse_furnishing_data(ifc_file: ifc.file):
    objects = ifc_file.by_type("IfcFurnishingElement")

    not_included_families = [
        "Furniture_Keyboard_Office",
        "Furniture_Brewer_Coffee_K1552",
        "Furniture_Monitor_Office",
        "Furniture-Artificial-banana-plant-1500mm",
        "Furniture_Printer_M1840"
    ]

    unique_families = set()
    library_objects = []
    ifc_file_names = []

    for ifc_object in tqdm(objects):
        psets = util.get_psets(ifc_object)
        object_family = psets.get("07-Furniture_Material_Takeoff-WSP-FUR-20250725", {}).get("Family")

        if object_family not in unique_families and object_family not in not_included_families:
            library_object = LibraryObject.from_ifc_object(ifc_file, ifc_object)

            print(f"Found object: {object_family}")

            file_name = write_object_to_single_ifc(ifc_file, ifc_object, OBJECTS_DIR)

            library_objects.append(library_object)
            ifc_file_names.append(file_name)
            unique_families.add(object_family)

    print(f"Number of unique objects found: {len(library_objects)}")

    return library_objects, ifc_file_names


if __name__ == "__main__":
    library_objects = []
    ifc_file_names = []

    ifc_file_furnishing = ifc.open(
        r"C:\Users\hugop\Downloads\OneDrive_2_8-11-2025\CHCH-WSP-00-FUR-M3D-001-V2-25072025.ifc")
    lib_objs, file_names = parse_furnishing_data(ifc_file_furnishing)
    library_objects += lib_objs
    ifc_file_names += file_names

    ifc_file_room = ifc.open(r"C:\Users\hugop\Downloads\OneDrive_2_8-11-2025\CHCH-WSP-00-ROOM-UPDATED-V2-25072025.ifc")
    lib_objs, file_names = parse_room_data(ifc_file_room)
    library_objects += lib_objs
    ifc_file_names += file_names

    ifc_file_exterior = ifc.open(r"C:\Users\hugop\Downloads\OneDrive_2_8-11-2025\CHCH-WSP-00-FCD-M3D-001.ifc")
    lib_objs, file_names = parse_exterior_data(ifc_file_exterior)
    library_objects += lib_objs
    ifc_file_names += file_names

    print(f"Total unique objects found: {len(library_objects)}")

    JSON_DIR = os.path.join(OBJECTS_DIR, "json")

    os.makedirs(JSON_DIR, exist_ok=True)

    for lib_object, ifc_file_name in zip(library_objects, ifc_file_names):
        object_dict = lib_object.to_dict()

        clean_wsp_json(object_dict)

        file_name = ifc_file_name.replace(".ifc", ".json")

        json_file_path = os.path.join(JSON_DIR, file_name)

        with open(json_file_path, "w") as f:
            json.dump(object_dict, f, indent=4)



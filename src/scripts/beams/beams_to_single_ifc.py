import os
import re

from tqdm import trange

import ifcopenshell.api.spatial
import ifcopenshell.file
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import ifcopenshell.api.geometry
import ifcopenshell.api.spatial

def write_objects_to_single_ifc(ifc_file_path, objects_dir, object_type="IfcBeam"):
    ifc_file = ifcopenshell.open(ifc_file_path)

    objects = ifc_file.by_type(object_type)

    num_objects = len(objects)

    unique_objects = {}

    for i in trange(num_objects):
        
        if not keep_ifc_column(objects[i], unique_objects):
            continue

        ifc_file_copy = ifcopenshell.open(ifc_file_path)\

        while len(ifc_file_copy.by_type("IfcBuilding")) > 0:
            ifc_file_copy.remove(ifc_file_copy.by_type("IfcBuilding")[0])

        # while len(ifc_file_copy.by_type("IfcBuildingStorey")) > 0:
        #     ifc_file_copy.remove(ifc_file_copy.by_type("IfcBuildingStorey")[0])

        site = ifc_file_copy.by_type("IfcSite")[0]

        new_building = ifcopenshell.api.root.create_entity(ifc_file_copy, "IfcBuilding")
        ifcopenshell.api.aggregate.assign_object(ifc_file_copy, relating_object=site, products=[new_building])

        new_storey = ifcopenshell.api.root.create_entity(ifc_file_copy, "IfcBuildingStorey")
        ifcopenshell.api.aggregate.assign_object(ifc_file_copy, relating_object=new_building, products=[new_storey])

        ifcopenshell.api.geometry.edit_object_placement(ifc_file_copy, product=objects[i])

        ifcopenshell.api.spatial.assign_container(ifc_file_copy, relating_structure=new_storey, products=[objects[i]])

        object_dir = os.path.join(objects_dir, "ifc")

        os.makedirs(object_dir, exist_ok=True)

        curr_id = objects[i].GlobalId

        ifc_file_copy.write(os.path.join(object_dir, f"{curr_id}.ifc"))

def keep_ifc_column(ifc_column, unique_columns):
    pattern = r"^Structural Columns [1-5]:Structural Columns [1-5]$"

    if "steel" in ifc_column.Name.lower() or "column" in ifc_column.Name.lower():
        name_parsed = ":".join(ifc_column.Name.split(":")[:2])

        if re.match(pattern, name_parsed):
            return False

        if name_parsed not in unique_columns.keys():
            unique_columns[name_parsed] = ifc_column
            return True

    return False


if __name__ == "__main__":

    # For beams
    # IFC_FILE_PATH = r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\ifc\Steel-UB Universal Beam-Steel & Tube-300.ifc"
    # OBJECTS_DIR = r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\objects"

    IFC_FILE_PATH = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\ifc\JX-B405-REVIT - Mar18_hphi344-structuralifc.ifc"
    OBJECTS_DIR = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\eng-building"

    write_objects_to_single_ifc(IFC_FILE_PATH, OBJECTS_DIR, object_type="IfcBeam")
import os

import ifcopenshell.file
import shutil

# Write each beam in the S&T file into separate IFC files. For proof of concept of library

IFC_FILE_PATH = r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\ifc\Steel-UB Universal Beam-Steel & Tube-300.ifc"

OBJECTS_DIR = r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\objects"

ifc_file = ifcopenshell.open(IFC_FILE_PATH)

beams = ifc_file.by_type("IfcBeam")

num_beams = len(beams)

for i in range(num_beams):
    ifc_file_copy = ifcopenshell.open(IFC_FILE_PATH)
    beams = list(ifc_file_copy.by_type("IfcBeam"))

    curr_id = 0

    for j in range(num_beams):
        if j != i:
            ifc_file_copy.remove(beams[j])
        else:
            curr_id = beams[j].GlobalId

    object_dir = os.path.join(OBJECTS_DIR, "ifc")

    os.makedirs(object_dir, exist_ok=True)

    ifc_file_copy.write(os.path.join(object_dir, f"{curr_id}.ifc"))

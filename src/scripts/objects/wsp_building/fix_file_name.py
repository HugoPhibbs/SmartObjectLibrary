import os
import ifcopenshell
from src.scripts.objects.parse_building_ifc_to_single_ifc import get_family_and_type
import shutil

if __name__ == "__main__":

    png_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\png"
    fixed_png_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\wsp-building\png-fixed"
    old_ifc_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\wsp-building\ifc"
    new_ifc_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\ifc"

    for old_file in os.listdir(old_ifc_dir):
        old_ifc = ifcopenshell.open(os.path.join(old_ifc_dir, old_file))
        old_id = old_file.split(".")[0]
        old_object = old_ifc.by_type("IfcBeam")[0]
        family_and_type = get_family_and_type(old_object)

        for new_file in os.listdir(new_ifc_dir):
            new_ifc = ifcopenshell.open(os.path.join(new_ifc_dir, new_file))
            new_id = new_file.split(".")[0]
            new_object = new_ifc.by_type("IfcBeam")[0]
            new_family_and_type = get_family_and_type(new_object)

            if family_and_type == new_family_and_type:
                old_png_path = os.path.join(png_dir, f"{old_id}.png")
                fixed_png_path = os.path.join(fixed_png_dir, f"{new_id}.png")

                if os.path.exists(old_png_path):
                    if not os.path.exists(fixed_png_path):
                        shutil.copy(old_png_path, fixed_png_path)
                else:
                    print(f"PNG file not found for old_id:{old_id}, new_id:{new_id}")




import os
import shutil

ifc_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\ifc"
environment_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\environment"

pdf_path = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\Steel & Tube 2024 Climate-related Disclosure.pdf"

object_ids = []

for file in os.listdir(ifc_dir):
    object_ids.append(file.split(".")[0])

for object_id in object_ids:
    shutil.copyfile(pdf_path, os.path.join(environment_dir, f"{object_id}.pdf"))
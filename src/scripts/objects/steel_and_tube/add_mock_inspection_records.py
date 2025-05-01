import os
import shutil

ifc_dir = r"/objects/ifc"
records_dir = r"/objects/inspection-record"

pdf_path = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\Steeldoc-checklists-final-March-22.pdf"

object_ids = []

dates = ["Nov-24", "Nov-23", "Nov-22"]

for file in os.listdir(ifc_dir):
    object_ids.append(file.split(".")[0])

for object_id in object_ids:
    for date in dates:
        shutil.copyfile(pdf_path, os.path.join(records_dir, f"{object_id}_{date}.pdf"))
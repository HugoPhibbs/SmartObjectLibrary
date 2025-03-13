import os
import shutil

ifc_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\ifc"
booklet_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\manufacturers-booklet"

pdf_path = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\S&T_Steel_Product_Guide_Feb2017-01_0.pdf"

object_ids = []

for file in os.listdir(ifc_dir):
    object_ids.append(file.split(".")[0])

for object_id in object_ids:
    shutil.copyfile(pdf_path, os.path.join(booklet_dir, f"{object_id}.pdf"))
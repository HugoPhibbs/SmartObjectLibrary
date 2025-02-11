import os
from PIL import Image

img = Image.open(r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\img.png")

img_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\png"
ifc_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\ifc"

for ifc_file in os.listdir(ifc_dir):
    ifc_file_path = os.path.join(ifc_dir, ifc_file)
    object_id = ifc_file.split(".")[0]

    img_file_path = os.path.join(img_dir, f"{object_id}.png")
    img.save(img_file_path)



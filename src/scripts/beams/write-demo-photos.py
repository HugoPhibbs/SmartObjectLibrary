import os
from PIL import Image

img = Image.open(r"/img.png")

img_dir = r"/objects/png"
ifc_dir = r"/objects/ifc"

for ifc_file in os.listdir(ifc_dir):
    ifc_file_path = os.path.join(ifc_dir, ifc_file)
    object_id = ifc_file.split(".")[0]

    img_file_path = os.path.join(img_dir, f"{object_id}.png")
    img.save(img_file_path)



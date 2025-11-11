from io import BytesIO
from typing import Callable

from PIL import Image

from src.site.core.cloud.ObjectLibraryBucket import ObjectLibraryBucket
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.getenv("PROJECT_BASE_DIR")
OBJECTS_DIR = os.path.join(BASE_DIR, "data", "objects")

files_bucket = ObjectLibraryBucket("object-library-files")


def add_files_from_dir(directory, put_function: Callable[[str, BytesIO, bool], None], file_extension):
    for file_name in os.listdir(directory):
        if file_name.endswith(file_extension):
            object_id = file_name.split(".")[0]
            file_path = os.path.join(directory, file_name)
            print(f"Uploading {file_name} to S3 bucket...")
            with open(file_path, "rb") as f:
                buffer = BytesIO(f.read())
                put_function(object_id, buffer, False)
    print("Upload complete.")


def add_env_files():
    ENV_DIR = os.path.join(OBJECTS_DIR, "environment")
    add_files_from_dir(ENV_DIR, files_bucket.put_environmental_impact_assessment, ".pdf")


def add_inspection_files():
    INSPECTION_DIR = os.path.join(OBJECTS_DIR, "inspection-record")

    for file_name in os.listdir(INSPECTION_DIR):
        if file_name.endswith(".pdf"):
            stripped_file_name = file_name.split(".")[0]

            split_file_name = stripped_file_name.split("_")
            object_id = "_".join(split_file_name[:-1]) # ID may contain underscores
            date = split_file_name[-1]

            file_path = os.path.join(INSPECTION_DIR, file_name)
            print(f"Uploading {file_name} to S3 bucket...")
            with open(file_path, "rb") as f:
                buffer = BytesIO(f.read())
                files_bucket.put_inspection_record(object_id, date, buffer, False)\

    print("Upload complete.")


def add_png_files():
    PNG_DIR = os.path.join(OBJECTS_DIR, "png")
    add_files_from_dir(PNG_DIR, files_bucket.put_object_photo, ".png")


def add_ifc_files():
    IFC_DIR = os.path.join(OBJECTS_DIR, "ifc")
    add_files_from_dir(IFC_DIR, files_bucket.put_object_ifc, ".ifc")


if __name__ == "__main__":
    add_inspection_files()
    # add_env_files()

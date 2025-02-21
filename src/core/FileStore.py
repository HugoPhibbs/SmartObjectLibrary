from PIL import Image
import ifcopenshell
import ifcopenshell.file
import json
import os

OBJECTS_DIR_DEFAULT = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects"


class FileStore:

    def __init__(self, objects_dir=OBJECTS_DIR_DEFAULT):
        self.objects_dir = objects_dir
        self.json_dir = os.path.join(objects_dir, "json")
        self.ifc_dir = os.path.join(objects_dir, "ifc")
        self.photo_dir = os.path.join(objects_dir, "png")

    def object_file_path(self, object_id, file_type):
        if file_type == "ifc":
            return os.path.join(self.ifc_dir, f"{object_id}.ifc")
        elif file_type == "json":
            return os.path.join(self.json_dir, f"{object_id}.json")
        elif file_type == "png":
            return os.path.join(self.photo_dir, f"{object_id}.png")

    def get_object_file(self, object_id: str, file_type: str):
        file_path = self.object_file_path(object_id, file_type)

        if file_type == "ifc":
            return ifcopenshell.open(file_path)
        elif file_type == "json":
            with open(file_path, "r") as json_file:
                return json.load(json_file)
        elif file_type == "png":
            image = Image.open(file_path)
            return image

        raise ValueError(f"File type {file_type} not supported")

    def add_object_file(self, object_id: str, file_data: any, file_type: str):
        file_path = self.object_file_path(object_id, file_type)

        if file_type == "ifc" and isinstance(file_data, ifcopenshell.file):
            file_data.write(file_path)
        elif file_type == "json" and isinstance(file_data, dict):
            with open(file_path, "w") as json_file:
                json.dump(file_data, json_file)
        elif file_type == "png" and isinstance(file_data, Image.Image):
            file_data.save(file_path)
        else:
            raise ValueError(f"File type {file_type} not supported for the given file data")

    def delete_all_object_files(self, object_id):
        for file_type in ["ifc", "json", "png"]:
            self.delete_object_file(object_id, file_type)

    def delete_object_file(self, object_id: str, file_type: str):
        file_path = self.object_file_path(object_id, file_type)

        os.remove(file_path)
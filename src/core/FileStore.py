import ifcopenshell
import json
import os

OBJECTS_DIR_DEFAULT = r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\objects"


class FileStore:

    def __init__(self, objects_dir=OBJECTS_DIR_DEFAULT):
        self.objects_dir = objects_dir
        self.json_dir = os.path.join(objects_dir, "json")
        self.ifc_dir = os.path.join(objects_dir, "ifc")

    def object_json_path(self, object_id):
        return os.path.join(self.json_dir, f"{object_id}.json")

    def object_ifc_path(self, object_id):
        return os.path.join(self.ifc_dir, f"{object_id}.ifc")

    def get_object_json(self, object_id):
        json_path = self.object_json_path(object_id)

        with open(json_path, "r") as json_file:
            return json.load(json_file)

    def get_object_ifc(self, object_id):
        ifc_path = self.object_ifc_path(object_id)

        return ifcopenshell.open(ifc_path)

    def delete_object_ifc(self, object_id):
        ifc_path = self.object_ifc_path(object_id)

        os.remove(ifc_path)

    def delete_object_json(self, object_id):
        json_path = self.object_json_path(object_id)

        os.remove(json_path)

    def add_object_json(self, object_id, object_json):
        json_path = self.object_json_path(object_id)

        with open(json_path, "w") as json_file:
            json.dump(object_json, json_file)

        return json_path

    def add_object_ifc(self, object_id, object_ifc: ifcopenshell.file):
        ifc_path = self.object_ifc_path(object_id)

        object_ifc.write(ifc_path)

        return ifc_path

from dotenv import load_dotenv
from werkzeug.datastructures import FileStorage

load_dotenv()
import os


class InspectionRecordStore:

    def __init__(self, objects_dir=os.getenv("OBJECTS_DIR_DEFAULT")):
        self.objects_dir = objects_dir
        self.inspection_record_dir = os.path.join(objects_dir, "inspection-record")

    def inspection_record_path(self, object_id: str, date: str):
        return os.path.join(self.inspection_record_dir, f"{object_id}_{date}.pdf")

    def add_inspection_record(self, object_id: str, file: FileStorage, date: str):
        file_path = self.inspection_record_path(object_id, date)
        file.save(file_path)
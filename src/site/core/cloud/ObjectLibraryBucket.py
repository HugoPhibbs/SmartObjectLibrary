import tempfile
from io import BytesIO

import botocore
import botocore.exceptions

from src.site.core.cloud.aws import get_s3_client


class ObjectLibraryBucket:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.s3 = get_s3_client()

    def delete_objects_files(self, object_id):
        prefixes = [f"ifc/{object_id}.ifc", f"photos/{object_id}.png"]
        for prefix in prefixes:
            try:
                self.s3.delete_object(Bucket=self.bucket_name, Key=prefix)
            except self.s3.exceptions.NoSuchKey:
                print(f"File with key {prefix} does not exist. Skipping deletion.")

    def key_exists(self, key: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except botocore.exceptions.ClientError as e:
            if e.response.get("Error", {}).get("Code") == "404":
                return False
            raise e

    def put(self, key, buffer: BytesIO, content_type: str, overwrite_existing=True):
        if not overwrite_existing and self.key_exists(key):
            print(f"File with key {key} already exists. Skipping upload.")
            return

        buffer.seek(0)
        self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=buffer, ContentType=content_type)

    def get_file_data_as_buffer(self, key: str):
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            data = response['Body'].read()
            return BytesIO(data)
        except self.s3.exceptions.NoSuchKey:
            print(f"File with key {key} does not exist.")
            return None

    def get_object_ifc(self, object_id: str) -> BytesIO | None:
        return self.get_file_data_as_buffer(f"ifc/{object_id}.ifc")

    def put_object_ifc(self, object_id: str, buffer: BytesIO, overwrite_existing=True):
        self.put(f"ifc/{object_id}.ifc", buffer, 'application/octet-stream', overwrite_existing)

    def get_object_photo(self, object_id: str) -> BytesIO | None:
        return self.get_file_data_as_buffer(f"photos/{object_id}.png")

    def put_object_photo(self, object_id: str, buffer: BytesIO, overwrite_existing=True):
        self.put(f"photos/{object_id}.png", buffer, 'image/png', overwrite_existing)

    @staticmethod
    def inspection_record_key(object_id: str, date: str) -> str:
        return f"inspection-records/{object_id}_{date}.pdf"

    def get_inspection_record(self, object_id: str, date: str) -> BytesIO | None:
        return self.get_file_data_as_buffer(self.inspection_record_key(object_id, date))

    def put_inspection_record(self, object_id: str, date: str, buffer: BytesIO, overwrite_existing=True):
        self.put(self.inspection_record_key(object_id, date), buffer, 'application/pdf', overwrite_existing)

    def get_inspection_record_dates(self, object_id: str) -> list[str]:
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"inspection-records/{object_id}_"
            )
            dates = []
            for obj in response.get('Contents', []):
                key = obj['Key']
                date_part = key.split('_')[-1].replace('.pdf', '')
                dates.append(date_part)
            return dates
        except Exception as e:
            print(f"Error retrieving inspection record dates for object ID {object_id}: {e}")
            return []

    @staticmethod
    def environment_impact_key(object_id: str) -> str:
        return f"environmental-impact-assessments/{object_id}.pdf"

    def get_environmental_impact_assessment(self, object_id: str) -> BytesIO | None:
        return self.get_file_data_as_buffer(self.environment_impact_key(object_id))

    def put_environmental_impact_assessment(self, object_id: str, buffer: BytesIO, overwrite_existing=True):
        self.put(self.environment_impact_key(object_id), buffer, 'application/pdf', overwrite_existing)

    @staticmethod
    def manufacturers_booklet_key(object_id: str) -> str:
        return f"manufacturers-booklets/{object_id}.pdf"

    def get_manufacturers_booklet(self, object_id: str) -> BytesIO | None:
        return self.get_file_data_as_buffer(self.manufacturers_booklet_key(object_id))

    def put_manufacturers_booklet(self, object_id: str, buffer: BytesIO, overwrite_existing=True):
        self.put(self.manufacturers_booklet_key(object_id), buffer, 'application/pdf', overwrite_existing)

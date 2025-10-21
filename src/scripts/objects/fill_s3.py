from io import BytesIO

from PIL import Image

from site.core.cloud.ObjectLibraryBucket import ObjectLibraryBucket
import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.getenv("PROJECT_BASE_DIR")
PNG_DIR = os.path.join(BASE_DIR, "data", "objects", "png")
files_bucket = ObjectLibraryBucket("object-library-files")

if __name__ == "__main__":
    for file_name in os.listdir(PNG_DIR):
        if file_name.endswith(".png"):
            object_id = file_name.split(".")[0]
            file_path = os.path.join(PNG_DIR, file_name)
            image = Image.open(file_path)
            print(f"Uploading {file_name} to S3 bucket...")
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            files_bucket.put_object_photo(object_id, buffer, False)
    print("Upload complete.")

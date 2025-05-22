import os
import json

MOCK_DOCUMENTS_DIR = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\wsp-building\mock-documents"
JSON_DIR = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\json"

MANUFACTURERS_BOOKLET_DIR = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\manufacturers-booklet"
ENVIRONMENTAL_CERTIFICATES_DIR = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\environment"
INSPECTION_RECORDS_DIR = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\inspection-record"

mock_files_dict = {
    "steel": {
        "booklet": "steel_guide.pdf",
        "environment": "steel_environment.pdf",
        "inspection": "steel_inspection.pdf",
    },
    "timber": {
        "booklet": "timber_guide.pdf",
        "environment": "timber_environment.pdf",
        "inspection": "timber_inspection.pdf",
    },
    "damper": {
        "booklet": "dampener_guide.pdf",
        "environment": "steel_environment.pdf",
        "inspection": "steel_inspection.pdf",
    },
}


def write_copy_file(input_file, object_id, output_dir, output_file_name=None):
    """
    Write a copy of the input file to the output directory with the object ID as the filename.
    """
    if not output_file_name:
        output_file_name = f"{object_id}.pdf"

    output_file = os.path.join(output_dir, output_file_name)

    with open(input_file, "rb") as f_in:
        with open(output_file, "wb") as f_out:
            f_out.write(f_in.read())

def main():
    for json_file in os.listdir(JSON_DIR):

        object_id = json_file.split(".")[0]

        with open(os.path.join(JSON_DIR, json_file), "r") as f:
            data = json.load(f)

            product_name = data["identity_data"]["primary_info"]["name"]

            product_name = product_name.lower()

            print(f"{product_name}, id {object_id}")

            if "timber" in product_name:
                product_type = "timber"

            elif "damper" in product_name:
                product_type = "damper"

            else:
                product_type = "steel"

            inspection_record_dates = ["Nov-22", "Nov-23", "Nov-24"]

            write_copy_file(os.path.join(MOCK_DOCUMENTS_DIR, mock_files_dict[product_type]["booklet"]), object_id, MANUFACTURERS_BOOKLET_DIR)
            write_copy_file(os.path.join(MOCK_DOCUMENTS_DIR, mock_files_dict[product_type]["environment"]), object_id, ENVIRONMENTAL_CERTIFICATES_DIR)

            for date in inspection_record_dates:
                    write_copy_file(os.path.join(MOCK_DOCUMENTS_DIR, mock_files_dict[product_type]["inspection"]), object_id, INSPECTION_RECORDS_DIR, f"{object_id}_{date}.pdf")

if __name__ == "__main__":
    main()


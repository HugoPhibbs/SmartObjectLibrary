import os
from src.site.core import LibraryObject as LibraryObjectV2
import ifcopenshell


s_t_prefix = "1Mq"
ifc_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\ifc"


if __name__ == "__main__":
    unique_dim_dicts = {}

    for file in os.listdir(ifc_dir):
        if file.startswith(s_t_prefix):
            continue

        file_path = os.path.join(ifc_dir, file)

        file = ifcopenshell.open(file_path)

        this_object, file_name = LibraryObjectV2.from_ifc_file(file)

        this_dimensions_keys = list(this_object.property_sets["Dimensions"].keys())

        this_dimensions_keys.sort()

        this_dimensions_keys = tuple(this_dimensions_keys)

        name_parsed = ":".join(this_object.identity_data.primary_info.name.split(":")[:-1]) # Remove ID

        if this_dimensions_keys not in unique_dim_dicts:
            unique_dim_dicts[this_dimensions_keys] = (name_parsed, file_name)

    unique_dim_dicts_list = [(k, v) for k, v in unique_dim_dicts.items()]

    print("Unique dimension types:")
    for dim in unique_dim_dicts_list:
        print(f"{dim[1]}: Dims: {dim[0]}")



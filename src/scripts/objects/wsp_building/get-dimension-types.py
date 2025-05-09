import os
from src.core.LibraryObject import LibraryObject
import ifcopenshell


s_t_prefix = "1Mq"
ifc_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\ifc"


if __name__ == "__main__":
    unique_dim_dicts = set()

    for file in os.listdir(ifc_dir):
        if file.startswith(s_t_prefix):
            continue

        file_path = os.path.join(ifc_dir, file)

        file = ifcopenshell.open(file_path)

        this_object, file_name = LibraryObject.from_ifc_file(file)

        this_dimensions_keys = list(this_object.property_sets["Dimensions"].keys())

        this_dimensions_keys.sort()

        this_dimensions_keys = tuple(this_dimensions_keys)

        if this_dimensions_keys not in unique_dim_dicts:
            unique_dim_dicts.add(this_dimensions_keys)

    print("Unique dimension types:")
    for dim in unique_dim_dicts:
        print(dim)



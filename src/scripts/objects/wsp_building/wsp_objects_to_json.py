from src.core.LibraryObject import LibraryObject as LibraryObjectV2
from src.scripts.objects.add_mock_property_sets import add_mock_property_sets
import ifcopenshell
import os
import json

dimension_name_map = {
    # Universal
    "Elevation at Bottom": "elevation_bottom",
    "Elevation at Top": "elevation_top",
    "Length": "length",
    "Volume": "volume",

    # Generic section geometry
    "b": "width",
    "d": "height", # Chosen as height to simplify things
    "h": "height",
    "Ht": "height",
    "D": "height", # Chosen as height to simplify things
    "r": "radius",
    "t": "wall_thickness",
    "tr": "corner_radius",

    # Angle-, channel- & UB-specific
    "b1": "leg_length_long",
    "b2": "leg_length_short",
    "bf": "flange_width",
    "tf": "flange_thickness",
    "tw": "web_thickness",
    "k": "fillet_radius",
    "kr": "root_radius",
    "Cy": "centroid_y",

    # CHS / RHS extras
    "do": "outer_diameter",
    "B": "outer_diameter",

    # Mechanical-connector items
    "Bolt Centreline Radius": "bolt_ctr_radius",
    "Clevis Depth": "clevis_depth",
    "Clevis Thickness": "clevis_thickness",
    "Clevis Width": "clevis_width",
    "End Plate Brace OD": "end_plate_brace_od",
    "End Plate Thickness": "end_plate_thickness",
    "End Plate Top OD": "end_plate_top_od",
    "Mid-stroke Length": "mid_stroke_length",
    "Shank Length": "shank_length",
    "Spherical Bearing Bore Dia.": "spherical_bearing_bore_dia",

    # Misc.
    "Thk": "thickness",
    "s": "spacing",
    "x": "centroid_x",
    "y": "centroid_y",
    "vpy": "shear_vpy",
    "vpz": "shear_vpz",
    "vy": "shear_vy",
    "vz": "shear_vz",
    "Change of Size": "size_change",
    "Change Of Size": "size_change"
}


def clean(obj: LibraryObjectV2):
    dimensions = obj.property_sets["Dimensions"]

    new_dimensions = {}

    for (key, value) in dimensions.items():
        if key in dimension_name_map:
            if key in dimension_name_map:
                new_key = dimension_name_map[key]
                new_dimensions[new_key] = value

    obj.property_sets["Dimensions"] = new_dimensions

    if "Materials and Finishes" in obj.property_sets:
        obj.material.name = obj.property_sets["Materials and Finishes"]["Structural Material"]["value"]
        del obj.property_sets["Materials and Finishes"]

    name = obj.identity_data.primary_info.name
    name_clean = ":".join(name.split(":")[:-1]) # Remove ID
    obj.identity_data.primary_info.name = name_clean



if __name__ == "__main__":
    ifc_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\ifc"
    json_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\json"

    for file_name in os.listdir(ifc_dir):

        file_path = os.path.join(ifc_dir, file_name)

        add_mock_property_sets(file_path)

        file = ifcopenshell.open(file_path)

        obj, _ = LibraryObjectV2.from_ifc_file(file)

        # Clean the object
        clean(obj)

        obj_dict = obj.to_dict()

        file_path_json = os.path.join(json_dir, file_name.replace(".ifc", ".json"))
        with open(file_path_json, "w") as f:
            json.dump(obj_dict, f, indent=4)


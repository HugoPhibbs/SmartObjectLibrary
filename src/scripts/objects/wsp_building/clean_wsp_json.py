import json
import pydash

unit_to_ifc_unit = {
    "length": "LENGTHUNIT",
    "area": "AREAUNIT",
    "volume": "VOLUMEUNIT",
}


def remove_psets(object_dict):
    psets_to_remove = [
        "Geometric Position",
        "Construction",
        "Constraints",
        "Identity Data",
        "Pset_EnvironmentalImpactIndicators",
        "Pset_ReinforcementBarPitchOfBeam"
    ]

    for pset in psets_to_remove:
        if pset in object_dict["property_sets"]:
            del object_dict["property_sets"][pset]


def remove_pset_ids(object_dict):
    for pset_name in object_dict["property_sets"]:
        if "id" in object_dict["property_sets"][pset_name]:
            del object_dict["property_sets"][pset_name]["id"]


def rename_timber_dims(object_dict):
    if object_dict["property_sets"]["Dimensions"]["b"] is not None:
        # Assume timber, rename breadth and depth
        breadth = object_dict["property_sets"]["Dimensions"]["b"]
        depth = object_dict["property_sets"]["Dimensions"]["d"]

        object_dict["property_sets"]["Dimensions"]["Breadth"] = breadth
        object_dict["property_sets"]["Dimensions"]["Depth"] = depth
        del object_dict["property_sets"]["Dimensions"]["b"]
        del object_dict["property_sets"]["Dimensions"]["d"]


def add_dimensions(object_dict):
    new_attribute_dimensions = {
        "Dimensions.Length": unit_to_ifc_unit["length"],
        "Dimensions.Breath": unit_to_ifc_unit["length"],
        "Dimensions.Depth": unit_to_ifc_unit["length"],
        "Dimensions.Volume": unit_to_ifc_unit["volume"],
        "Structural.Cut Length": unit_to_ifc_unit["length"],
        "Pset_BeamCommon.Span": unit_to_ifc_unit["length"],
    }

    psets = object_dict["property_sets"]

    for attribute, unit in new_attribute_dimensions.items():
        if pydash.has(psets, attribute):
            pydash.set_(psets, f"{attribute}.unit", unit)


def remove_pset_attributes(object_dict):
    attributes_to_remove = [
        "Dimensions.Elevation at Bottom",
        "Dimensions.Elevation at Top",
        "Structural.Stick Symbol Location",
        "Structural.Structural Usage",
        "Structural.Angle",
        "Other.Family",
    ]

    for attribute in attributes_to_remove:
        pydash.unset(object_dict["property_sets"], attribute)


def rename_psets(object_dict):
    pset_renames = {
        "Other": "Identity Data"
    }

    for old_name, new_name in pset_renames.items():
        if old_name in object_dict["property_sets"]:
            object_dict["property_sets"][new_name] = object_dict["property_sets"][old_name]
            del object_dict["property_sets"][old_name]


def clean_wsp_json(object_dict):
    """
    Clean the WSP JSON object by removing unnecessary attributes and renaming property sets.
    """
    remove_psets(object_dict)
    remove_pset_ids(object_dict)
    remove_pset_attributes(object_dict)
    rename_psets(object_dict)
    rename_timber_dims(object_dict)
    add_dimensions(object_dict)

    return object_dict


if __name__ == "__main__":
    demo_json_path = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\json\0fGzJV025FtBzI3gApQ6kJ.json"

    with open(demo_json_path, "r") as json_file:
        object_dict = json.load(json_file)
        cleaned_object_dict = clean_wsp_json(object_dict)
        print(json.dumps(cleaned_object_dict, indent=4))

from dataclasses import asdict, is_dataclass
from enum import Enum

from src.site.core import LibraryObject as LibraryObjectV2, CostMetric, Currency
from src.site.core import Cost
from src.scripts.objects.add_mock_property_sets import add_mock_property_sets
import ifcopenshell
import os
import json
import pydash

dimension_name_map = {
    # Universal
    "Elevation at Bottom": "elevation_bottom",
    "Elevation at Top": "elevation_top",
    "Length": "length",
    "Volume": "volume",
    "Height": "height",
    "Width": "width",
    "Area": "area",


    # Generic section geometry
    "b": "width",
    "d": "height",  # Chosen as height to simplify things
    "h": "height",
    "Ht": "height",
    "D": "height",  # Chosen as height to simplify things
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

unit_to_ifc_unit = {
    "length": "LENGTHUNIT",
    "area": "AREAUNIT",
    "volume": "VOLUMEUNIT",
}

SALVAGE_METHODS = [
    "Demolition",
    "Manual Disassembly",
    "Mechanical Disassembly",
]

import random


def add_mock_material_mechanical_properties(object_dict):
    options = {
        "dynamic_viscosity": [0.001, 0.01, 0.1, 1.0, 10.0],  # Pa·s (typically left in Pa·s)
        "young_modulus": [1, 7, 30, 70, 210],  # GPa
        "shear_modulus": [0.5, 2.5, 10, 30, 80],  # GPa
        "poisson_ratio": [0.15, 0.25, 0.30, 0.35, 0.49],  # Unitless
        "thermal_expansion_coefficient": [5, 10, 12, 15, 24],  # µm/m·K (i.e., microstrain per Kelvin)
    }
    units = {
        "dynamic_viscosity": "DYNAMICVISCOSITYUNIT",
        "young_modulus": "PRESSUREUNIT",
        "shear_modulus": "PRESSUREUNIT",
        "poisson_ratio": "NO-UNIT",
        "thermal_expansion_coefficient": "THERMALEXPANSIONCOEFFICIENTUNIT"
    }

    properties = {
        key: {"value": random.choice(values), "unit": units[key]}
        for key, values in options.items()
    }

    object_dict["property_sets"]["Pset_MaterialMechanical"] = properties


def add_mock_recycle_info(object_dict):
    name = object_dict["identity_data"]["primary_info"]["name"]

    is_recycled = random.random() > 0.3

    recycle_dict = {"is_recycled": is_recycled}

    if is_recycled:
        if "timber" in name:
            connection_types = ["Bolted", "Bracketed", "Nailed/Screwed"]
        elif "damper" in name:
            connection_types = ["Bolted", "Welded"]
        else:
            # Assume steel
            connection_types = ["Bolted", "Welded", "Nailed/Screwed", "Riveted", "Bracketed"]

        recycle_dict["previous_connection_type"] = random.choice(connection_types)
        recycle_dict["salvage_method"] = random.choice(SALVAGE_METHODS)

    object_dict["identity_data"]["recycle_info"] = recycle_dict


def remove_psets(object_dict):
    psets_to_remove = [
        "Geometric Position",
        "Construction",
        "Constraints",
        "Identity Data",
        "Pset_EnvironmentalImpactIndicators",
        "Pset_ReinforcementBarPitchOfBeam",
        "Phasing"
    ]

    for pset in psets_to_remove:
        if pset in object_dict["property_sets"]:
            del object_dict["property_sets"][pset]


def remove_pset_ids(object_dict):
    for pset_name in object_dict["property_sets"]:
        if "id" in object_dict["property_sets"][pset_name]:
            del object_dict["property_sets"][pset_name]["id"]


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


def rename_dimensions(object_dict):
    dimensions = object_dict["property_sets"]["Dimensions"]

    new_dimensions = {}

    for (key, value) in dimensions.items():
        if key in dimension_name_map:
            new_key = dimension_name_map[key]
            new_dimensions[new_key] = value
        else:
            new_dimensions[key] = value

    object_dict["property_sets"]["Dimensions"] = new_dimensions


def remove_id_from_name(object_dict):
    name = object_dict["identity_data"]["primary_info"]["name"]
    name_clean = ":".join(name.split(":")[:-1])  # Remove ID
    object_dict["identity_data"]["primary_info"]["name"] = name_clean


def add_material_name(object_dict):
    if "Materials and Finishes" in object_dict["property_sets"] and "Structural Material" in object_dict["property_sets"]["Materials and Finishes"]:
        object_dict["material"]["name"] = object_dict["property_sets"]["Materials and Finishes"]["Structural Material"][
            "value"]
        del object_dict["property_sets"]["Materials and Finishes"]


def add_mock_manufacturing_data(object_dict):
    mock_manufacturer_data = [
        {
            "name": "ForgePoint Group",
            "address": "1450 Innovation Crescent, Hamilton 3204, New Zealand",
            "contact_email": "hello@forgepoint.nz",
            "link": "https://www.forgepoint.nz"
        },
        {
            "name": "Pacific Works Ltd",
            "address": "27 Enterprise Parade, Auckland 0626, New Zealand",
            "contact_email": "contact@pacificworks.co.nz",
            "link": "https://www.pacificworks.co.nz"
        },
        {
            "name": "Atlas Manufacturing Co.",
            "address": "9 Precision Way, Christchurch 8011, New Zealand",
            "contact_email": "info@atlasmfg.com",
            "link": "https://www.atlasmfg.com"
        },
        {
            "name": "Southern Cross Fabrication",
            "address": "201 Industry Loop, Dunedin 9016, New Zealand",
            "contact_email": "support@scfabrication.nz",
            "link": "https://www.scfabrication.nz"
        }
    ]
    object_dict["identity_data"]["manufacturer"] = random.choice(mock_manufacturer_data)


def asdict_enum(obj):
    """Does asdict on an dataclass, but converts Enums to their values."""
    if isinstance(obj, Enum):
        return obj.value
    elif is_dataclass(obj):
        return {k: asdict_enum(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, (list, tuple)):
        return type(obj)(asdict_enum(v) for v in obj)
    elif isinstance(obj, dict):
        return {asdict_enum(k): asdict_enum(v) for k, v in obj.items()}
    else:
        return obj


def add_mock_cost_data(object_dict):
    name = object_dict["identity_data"]["primary_info"]["name"].lower()

    name_filters = ['damper', 'purlin', 'custom']

    price = random.choice([1000, 1500, 3000])

    if any(filter in name for filter in name_filters):
        metric = CostMetric.COST_PER_UNIT
    elif 'timber' in name:
        metric = CostMetric.COST_PER_METER
    else:
        metric = CostMetric.COST_PER_TONNE

    cost = Cost(price=price, metric=metric, currency=Currency.NZD)

    object_dict["cost"] = asdict_enum(cost)


def clean_wsp_json(object_dict):
    """
    Clean the WSP JSON object by removing unnecessary attributes and renaming property sets.
    """
    remove_psets(object_dict)
    remove_pset_ids(object_dict)
    remove_pset_attributes(object_dict)
    rename_psets(object_dict)
    rename_dimensions(object_dict)
    add_dimensions(object_dict)
    remove_id_from_name(object_dict)
    add_material_name(object_dict)
    add_mock_property_sets(object_dict)
    add_mock_manufacturing_data(object_dict)
    add_mock_recycle_info(object_dict)
    add_mock_material_mechanical_properties(object_dict)
    add_mock_cost_data(object_dict)

    return object_dict


if __name__ == "__main__":
    ifc_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\ifc"
    json_dir = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\json"

    for file_name in os.listdir(ifc_dir):
        file_path = os.path.join(ifc_dir, file_name)

        file = ifcopenshell.open(file_path)

        obj, _ = LibraryObjectV2.from_ifc_file(file, object_types=["IfcBeam", "IfcColumn"])

        object_dict = obj.to_dict()

        # Clean and add mock data to the object
        clean_wsp_json(object_dict)

        file_path_json = os.path.join(json_dir, file_name.replace(".ifc", ".json"))
        with open(file_path_json, "w") as f:
            json.dump(object_dict, f, indent=4)

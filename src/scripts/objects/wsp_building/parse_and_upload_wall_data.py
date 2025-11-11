import numpy as np
import pandas as pd
import secrets, string
import json
import os
import hashlib
import base64
import re
from src.scripts.objects import fill_opensearch

# XLSX_PATH = r"C:\Users\hugop\Documents\Work\object-library\SmartObjectLibrary\data\wall-nse_top20_unique_all.xlsx"
XLSX_PATH = r"C:\Users\hugop\Documents\Work\object-library\SmartObjectLibrary\data\wall-nse-with-duration.xlsx"
OUTPUT_JSON_DIR = r"C:\Users\hugop\Documents\Work\object-library\SmartObjectLibrary\data\objects\wall_json"

PSB = "property_sets.wall_layer_basic"
PSM = "property_sets.wall_layer_material"
PSC = "property_sets.wall_layer_construction"

pset_mappings = {
    "Elem Level": PSB,
    "Structural Usage": PSB,
    "Family": PSB,
    "Type": PSB,
    "Material: Name": PSB,
    "Top20_Flag": PSB,
    "Material: Unit Rate (NZD)": PSM,
    "Material: Unit Description": PSM,
    "Material: Description": PSM,
    "Material: BRANZ Description": PSM,
    "Material: BRANZ classes": PSM,
    "Material: Keynote": PSM,
    "Material: Area": PSM,
    "Volume": PSM,
    "Material: Product code": PSM,
    "Material: Quantity basis": PSM,
    "Material: Embodied carbon (kg CO2/qty)": PSM,
    "Material: Comments": PSM,
    "Material: Cost": PSM,
    "cost per m3": PSM,
    "Max Prefab Rate": PSC,
    "std density(kg/m3)": PSC,
    "rate_site (m³/day)": PSC,
    "rate_prefab (m³/day)": PSC,
    "lead_time_prefab (days)": PSC,
    "transport_time (days)": PSC,
    "setup_time_site (days)": PSC,
    "setup_time_prefab (days)": PSC
}

attribute_mappings = {}

for attribute, pset in pset_mappings.items():
    attribute_mappings[attribute] = f"{pset}.{attribute}"


def create_wall_id(s) -> str:
    # generate an ID based on hash, deterministic so this script can be re-run with same json filenames
    h = hashlib.sha256(s.encode()).digest()
    b64 = base64.urlsafe_b64encode(h).decode()
    return re.sub(r'[^A-Za-z0-9]', '', b64)[:22]


def set_nested(d, key_path, value):
    keys = key_path.split('.')
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value


def wall_material_to_object_json(row):
    id = create_wall_id(row["Material: Name"] + row["Type"])

    branz_description = row["Material: BRANZ Description"]
    parsed_material_name = branz_description if isinstance(branz_description, str) else "Unknown Material"

    obj = {
        "object_id": id,
        "identity_data": {
            "primary_info": {
                "name": row["Material: Name"],
                "model": "NO_MODEL",
                "standard": "NO_STANDARD",
                "ifc_type": "NO-TYPE",
                "categories": ["wall-layer"]
            },
            "manufacturer": {
                "name": "Atlas Manufacturing Co.",
                "address": "9 Precision Way, Christchurch 8011, New Zealand",
                "contact_email": "info@atlasmfg.com",
                "link": "https://www.atlasmfg.com"
            },
            "recycle_info": {
                "is_recycled": False
            },
            "base_quantities": {
                "ifc_quantity_type": "Unknown",
                "properties": {}
            }
        },
        "supporting_documents": {},
        "property_sets": {
            "wall_layer_basic": {},
            "wall_layer_material": {},
            "wall_layer_construction": {},
            "Pset_EnvironmentalImpactIndicators": {
                "ClimateChangePerUnit": {
                    "value": row["Material: Embodied carbon (kg CO2/qty)"],
                    "unit": "MASSUNIT"
                }
            }
        },
        "cost": {
            "price": -1,
            "currency": "NZD",
            "metric": "COST_PER_M3"
        },
        "material": {
            "name": parsed_material_name,
            "ifc_material_type": "Unknown",
            "ifc_material_properties": {}
        }
    }

    for attribute, value in row.items():
        if pd.isna(value):
            continue
        mapped_attribute = attribute_mappings.get(attribute)

        if isinstance(value, np.float64):
            value = float(value)
        if isinstance(value, np.int64):
            value = int(value)

        if attribute == "Top20_Flag":
            value = value.split("; ")

        if attribute == "cost per m3":
            obj["cost"]["price"] = value

        value_obj = {
            "value": value,
            "unit": "NO-UNIT"
        }

        if mapped_attribute:
            set_nested(obj, mapped_attribute, value_obj)

    return obj


def get_entry_counts(wall_df):
    entry_counts = {}

    for i in range(len(wall_df)):
        row = wall_df.iloc[i]
        id = create_wall_id(row["Material: Name"] + row["Type"])
        entry_counts[id] = entry_counts.get(id, 0) + 1
    return entry_counts


def write_all_wall_materials_to_json(wall_df):
    seen_ids = set()
    for i in range(len(wall_df)):
        row = wall_df.iloc[i]
        obj_json = wall_material_to_object_json(row)

        id = obj_json["object_id"]

        if id in seen_ids:
            print(f"Duplicate ID found: {id}, skipping...")
            continue

        seen_ids.add(id)

        with open(os.path.join(OUTPUT_JSON_DIR, f"{id}.json"), "w") as f:
            json.dump(obj_json, f, indent=4)


if __name__ == "__main__":
    # wall_df = pd.read_excel(XLSX_PATH, sheet_name="Unique_Data")
    wall_df = pd.read_excel(XLSX_PATH)

    write_all_wall_materials_to_json(wall_df)

    # entry_dict = get_entry_counts(wall_df)
    #
    # with open("wall_entry_counts.json", "w") as f:
    #     json.dump(entry_dict, f, indent=4)

    fill_opensearch.upload_json_to_os("prod", json_dir=OUTPUT_JSON_DIR, sleep_interval=0.2)

import requests
import os
import pandas as pd
import urllib.parse
from pathlib import Path
import ifcopenshell
from src.core.LibraryObject import LibraryObject
import flatdict

steel_df = pd.read_csv(r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\st_data\steel-info.csv",
                       usecols=lambda x: x != "Component family")
ifc_path = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\st_data\ifc"

selected_attributes = {
    "Materials and Finishes": [
        ("Structural Material", None)
    ],
    "Structural Analysis": [
        ("Elastic Modulus strong axis", 'm3'),
        ("Elastic Modulus weak axis", 'm3'),
        ("Form Factor", None),
        ("Moment of Inertia strong axis", None),
        ("Moment of Inertia weak axis", None),
        ("Plastic Modulus strong axis", 'm3'),
        ("Plastic Modulus weak axis", 'm3'),
        ("Section Area", 'm2'),
        ("Shear Area strong axis", 'm2'),
        ("Shear Area weak axis", 'm2'),
        ("Tensile Strength", 'm3'),
    ]
}

multi_index_tuples = [("", "Type")]

for pset, value in selected_attributes.items():
    for attribute, unit in value:
        if unit:
            multi_index_tuples.append((pset, f'{attribute} ({unit})'))
        else:
            multi_index_tuples.append((pset, attribute))

file_names = set()

columns = pd.MultiIndex.from_tuples(multi_index_tuples)

parsed_steel_df = pd.DataFrame(columns=columns)

for row in steel_df.to_dict(orient="records"):
    link = row["IFC link"]

    if link in ["", "-", "na"] or pd.isna(link):
        continue

    link = urllib.parse.unquote(link)  # Decode URL-encoded characters

    file_name = link.split("/")[-1]

    if file_name not in file_names:
        target_dir = Path(ifc_path)
        target_dir.mkdir(parents=True, exist_ok=True)

        response = requests.get(link, stream=True)
        filepath = target_dir / file_name

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_names.add(file_name)

    id = row["IFC ID"]
    ifc_file = ifcopenshell.open(f"{ifc_path}/{file_name}")

    try:
        object = ifc_file.by_id(id)

        library_object = LibraryObject.from_ifc_object(ifc_file, object)
        library_object_dict = library_object.to_dict()

        new_dict = {
            "Type": row["Type"]
        }

        for pset, attributes in selected_attributes.items():

            for attribute, unit in attributes:
                try:
                    property_set = library_object_dict["property_sets"][pset]
                except KeyError:
                    print(f"Property set '{pset}' not found for object ID {id} in {file_name}, link: {link}")
                    continue

                if attribute not in property_set:
                    print(
                        f"Attribute '{attribute}' not found in property set '{pset}' for object ID {id} in {file_name}, link: {link}")
                    continue

                col_name = f'{pset}.{attribute}'
                if unit:
                    col_name += f' ({unit})'

                new_dict[col_name] = property_set[attribute]["value"]

        temp_df = pd.DataFrame([new_dict])
        temp_df.columns = pd.MultiIndex.from_tuples([
            tuple(col.split(".", maxsplit=1)) if "." in col else ("", col)
            for col in temp_df.columns
        ])

        parsed_steel_df = pd.concat([parsed_steel_df, temp_df], ignore_index=True)

    except RuntimeError as e:
        print(f"Object with ID {id} not found in {file_name}, link: {link}")
        continue

parsed_steel_df.to_csv("C:/Users/hugop/Documents/Work/SmartObjectLibrary/data/st_data/parsed_steel_info.csv",
                       index=False, float_format="%.3f")

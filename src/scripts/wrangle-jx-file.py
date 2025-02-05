import ifcopenshell
import re

ifc_file = ifcopenshell.open(r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\ifc\JX-B405-REVIT - Mar18_hphi344-structuralifc.ifc")

objects = ifc_file.by_type("IfcBeam")

unique_objects = {}

pattern = r"^Structural Columns [1-5]:Structural Columns [1-5]$"

for column in objects:

    name_lower = column.Name.lower()

    if "steel" in name_lower or "column" in name_lower:

        name_parsed = ":".join(column.Name.split(":")[:2])

        if re.match(pattern, name_parsed):
            continue

        if name_parsed not in unique_objects.keys():
            unique_objects[name_parsed] = column
            
            # print(name_parsed)

print(unique_objects)


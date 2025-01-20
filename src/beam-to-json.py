import ifcopenshell
import json

# Load the IFC file
ifc_file = ifcopenshell.open(r"C:\Users\Hugo\Documents\Work\SmartProductLibrary\data\Steel-UB Universal Beam-Steel & Tube-300.ifc")

beams = ifc_file.by_type("IfcBeam")

def save_beam(ifc_beam, i):
    # Prepare a dictionary to hold the beam data
    beam_data = {
        "id": ifc_beam.GlobalId,
        "name": ifc_beam.Name,
        "object_type": ifc_beam.ObjectType,
        "material": None,  # To store material data
        "object_placement": str(ifc_beam.ObjectPlacement),  # Example: Placement data
        "property_sets": []
    }

    # Retrieve material if available
    if ifc_beam.HasAssociations:
        for association in ifc_beam.HasAssociations:
            if association.is_a("IfcRelAssociatesMaterial"):
                material = association.RelatingMaterial
                if material:
                    beam_data["material"] = material.Name if hasattr(material, 'Name') else str(material)

    # Retrieve related property sets
    property_sets = ifc_file.get_inverse(ifc_beam, "IsDefinedBy")
    for rel in property_sets:
        if rel.is_a("IfcRelDefinesByProperties"):
            pset = rel.RelatingPropertyDefinition
            if pset.is_a("IfcPropertySet"):
                pset_data = {
                    "property_set_name": pset.Name,
                    "properties": []
                }
                for prop in pset.HasProperties:
                    pset_data["properties"].append({
                        "name": prop.Name,
                        "value": prop.NominalValue.wrappedValue if hasattr(prop.NominalValue, 'wrappedValue') else str(prop.NominalValue)
                    })
                beam_data["property_sets"].append(pset_data)

    # Optionally save to a file
    with open(f"./data/beams-json/beam_{i}", "w") as json_file:
        json.dump(beam_data, json_file, indent=4)

for i, beam in enumerate(beams):
    save_beam(beam, i)
import ifcopenshell
import json
import xmltodict

# Load the IFC file
ifc_file = ifcopenshell.open(r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\Steel-UB Universal Beam-Steel & Tube-300.ifc")

beams = ifc_file.by_type("IfcBeam")

def adjust_name(name):
    return "_".join(name.split(" "))

def save_beam(ifc_beam, i):
    # Prepare a dictionary to hold the beam data
    beam_data = {
        "id": ifc_beam.GlobalId,
        "name": ifc_beam.Name,
        "object_type": ifc_beam.ObjectType,
        "material": None,  # To store material data
        "object_placement": str(ifc_beam.ObjectPlacement),  # Example: Placement data
        "property_sets": {}
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
                pset_name_adj = adjust_name(pset.Name)
                beam_data["property_sets"][pset_name_adj] = {}

                for prop in pset.HasProperties:
                    name_adjusted = adjust_name(prop.Name)
                    beam_data["property_sets"][pset_name_adj][name_adjusted] = prop.NominalValue.wrappedValue if hasattr(prop.NominalValue, 'wrappedValue') else str(prop.NominalValue)

    # Optionally save to a file
    with open(rf"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\beams-json\beams_{i}.json", "w") as json_file:
        json.dump(beam_data, json_file, indent=4)
    #
    # beam_data_xml = beam_data.copy()
    # beam_data_xml["property_sets"] = {"property_set": beam_data_xml["property_sets"]}

    with open(rf"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\beams-xml\beams_{i}.xml", "w") as xml_file:
        xml_data = xmltodict.unparse({"root": beam_data}, pretty=True)
        xml_file.write(xml_data)

for i, beam in enumerate(beams):
    save_beam(beam, i)
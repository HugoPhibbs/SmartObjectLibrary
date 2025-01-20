import ifcopenshell as ifc

file = ifc.open(r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\Steel-UB Universal Beam-Steel & Tube-300.ifc")

entity = file.by_type("IfcBeam")[0]

print(entity)
new_ifc_file = ifc.file(schema='IFC2X3')  # Adjust schema if needed

new_ifc_file.add(entity)

# Extract and copy associated constraints (IfcRelConstraints)
for rel in entity.HasAssociations:
    if rel.is_a('IfcRelConstraints'):
        print(f"Adding Constraint: {rel}")
        new_ifc_file.add(rel)

# Extract and copy connections (e.g., connected elements like columns or walls)
for rel in entity.HasAssociations:
    if rel.is_a('IfcRelConnects'):
        print(f"Adding Connection: {rel}")
        new_ifc_file.add(rel)

# Extract and copy material associations (IfcRelAssociatesMaterial)
for rel in entity.HasAssociations:
    if rel.is_a('IfcRelAssociatesMaterial'):
        print(f"Adding Material Association: {rel}")
        new_ifc_file.add(rel)

# Extract and copy geometry representations if available
if entity.Representation:
    for rep in entity.Representation.Representations:
        print(f"Adding Geometry Representation: {rep}")
        new_ifc_file.add(rep)

# Extract and copy the Owner History if present
if entity.OwnerHistory:
    print(f"Adding Owner History: {entity.OwnerHistory}")
    new_ifc_file.add(entity.OwnerHistory)


# Save the new IFC file with just the extracted beams
new_ifc_file.write('extracted_beams.ifc')

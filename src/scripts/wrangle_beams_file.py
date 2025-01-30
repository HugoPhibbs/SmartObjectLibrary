import ifcopenshell.file

# Simple script to remove all beams from the Steel and Tube file and just keep the first one. For testing purposes.

ifc_file = ifcopenshell.open(r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\ifc\Steel-UB Universal Beam-Steel & Tube-300.ifc")

beams = ifc_file.by_type("IfcBeam")

for beam in beams[1:]:
    ifc_file.remove(beam)

ifc_file.write(r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\ifc\single-beam.ifc")
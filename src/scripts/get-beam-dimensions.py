import ifcopenshell

# Open IFC file
ifc_file = ifcopenshell.open(r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\ifc\1MqlONWM9DPguUA1H$xl0k.ifc")

# Get beam
beam = ifc_file.by_type("IfcBeam")[0]

# Access the beam's shape representation
for representation in beam.Representation.Representations:
    if representation.RepresentationType == "SweptSolid":
        swept_solid = representation.Items[0]

        # Get the profile definition
        profile = swept_solid.SweptArea
        print(profile)

        # Access profile properties (e.g., dimensions for IfcRectangleProfileDef)
        if profile.is_a("IfcRectangleProfileDef"):
            print("Width:", profile.XDim)
            print("Height:", profile.YDim)

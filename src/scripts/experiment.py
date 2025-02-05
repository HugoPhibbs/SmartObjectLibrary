import ifcopenshell

file = ifcopenshell.open(r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\ifc\JX-B405-REVIT - Mar18_hphi344-structuralifc.ifc")

element = file.by_type("IfcColumn")[0]


property_sets = file.get_inverse(element, True)
for rel in property_sets:
    if rel.is_a("IfcRelDefinesByProperties"):
        pset = rel.RelatingPropertyDefinition
        if pset.is_a("IfcPropertySet"):
            # if pset.Name not in object.property_sets:
            #     object.property_sets[pset.Name] = {}

            print(f"-- Property Set: {pset.Name}")

            for prop in pset.HasProperties:
                print(f"Property: {prop.Name}")
                print(f"Value: {prop.NominalValue.wrappedValue if hasattr(prop.NominalValue, 'wrappedValue') else str(prop.NominalValue)}")

                # object.property_sets[pset.Name][prop.Name] = {
                #     "value": prop.NominalValue.wrappedValue if hasattr(prop.NominalValue, 'wrappedValue') else str(
                #         prop.NominalValue),
                #     # "unit": LibraryObject.__unit_for_property(prop)
                # }


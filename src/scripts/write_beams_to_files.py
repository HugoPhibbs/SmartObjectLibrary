import json
import ifcopenshell.file

if __name__ == "__main__":

    ifc_file_path = r"../../data/ifc/Steel-UB Universal Beam-Steel & Tube-300.ifc"

    # Load the IFC file
    ifc_file = ifcopenshell.open(
        r"../../data/ifc/Steel-UB Universal Beam-Steel & Tube-300.ifc")

    beams = ifc_file.by_type("IfcBeam")

    # # Convert to JSON
    # ifc_json = ifcopenshell.file.to_json(ifc_file)
    #
    # # Save the JSON to a file
    # with open("output.json", "w") as json_file:
    #     json_file.write(ifc_json)

    for i, beam in enumerate(beams):
        object_dict = (ifc_file, beam, ifc_file_path, i)

        with open(rf"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\beams-json\beams_{i}.json", "w") as json_file:
            json.dump(object_dict, json_file, indent=4)


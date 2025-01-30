import json
from enum import Enum
from typing import List
import ifcopenshell.file


class IfcMeasureToUnit:

    def __init__(self, measures_list: List[str], unit):
        self.measures_list = measures_list
        self.unit = unit


class IfcMeasureToUnitEnum(Enum):
    LENGTH = IfcMeasureToUnit(["IfcPositiveLengthMeasure", "IfcLengthMeasure"], "LENGTHUNIT")
    AREA = IfcMeasureToUnit(["IfcAreaMeasure"], "AREAUNIT")
    ANGLE = IfcMeasureToUnit(["IfcPlaneAngleMeasure"], "PLANEANGLEUNIT")
    VOLUME = IfcMeasureToUnit(["IfcVolumeMeasure"], "VOLUMEUNIT")
    PRESSURE = IfcMeasureToUnit(["IfcPressureMeasure"], "PRESSUREUNIT")


def add_associations(ifc_object, object_data):
    if ifc_object.HasAssociations:
        for association in ifc_object.HasAssociations:
            if association.is_a("IfcRelAssociatesMaterial"):
                material = association.RelatingMaterial
                if material:
                    object_data["material"] = material.Name if hasattr(material, 'Name') else str(material)


def add_units(object_data, ifc_file):
    unit_assignments = ifc_file.by_type("IfcUnitAssignment")[0]

    for unit in unit_assignments.Units:
        unit_map = {}

        if unit.is_a("IfcSIUnit") or unit.is_a("IfcConversionBasedUnit"):
            unit_map["Name"] = unit.Name

        if unit.is_a("IfcSIUnit"):
            unit_map["Prefix"] = unit.Prefix if unit.Prefix is not None else "NO-PREFIX"

        object_data["units"][unit.UnitType] = (unit_map)


def unit_for_property(prop):
    if hasattr(prop, 'Unit') and prop.Unit is not None:
        return prop.Unit

    for unit_name in IfcMeasureToUnitEnum:
        for measure in unit_name.value.measures_list:
            if prop.NominalValue.is_a(measure):
                return unit_name.value.unit

    return "NO-UNIT"


def ifc_object_to_dict(ifc_file, ifc_object, ifc_file_path):
    # Prepare a dictionary to hold the beam data
    object_data = {
        "id": ifc_object.GlobalId,
        "name": ifc_object.Name,
        "object_type": ifc_object.ObjectType,
        "material": None,  # To store material data
        "object_placement": str(ifc_object.ObjectPlacement),  # Example: Placement data
        "ifc_type": "IfcBeam",
        "ifc_file_path": ifc_file_path,
        "units": {},
        "property_sets": {}
    }

    add_associations(ifc_object, object_data)

    add_units(object_data, ifc_file)

    # Retrieve related property sets
    property_sets = ifc_file.get_inverse(ifc_object, "IsDefinedBy")
    for rel in property_sets:
        if rel.is_a("IfcRelDefinesByProperties"):
            pset = rel.RelatingPropertyDefinition
            if pset.is_a("IfcPropertySet"):
                if pset.Name not in object_data["property_sets"]:
                    object_data["property_sets"][pset.Name] = {}

                for prop in pset.HasProperties:
                    object_data["property_sets"][pset.Name][prop.Name] = {
                        "value": prop.NominalValue.wrappedValue if hasattr(prop.NominalValue, 'wrappedValue') else str(
                            prop.NominalValue),
                        "unit": unit_for_property(prop)
                    }

    return object_data


def ifc_file_to_object_dict(ifc_file, ifc_file_name):
    """
    Extracts the object contained in an ifc file

    Assumes that there is just 1 object in the file

    :param ifc_file:
    :return:
    """

    project = ifc_file.by_type("IfcProject")[0]

    for site in project.IsDecomposedBy:
        for building in site.RelatedObjects:
            for storey in building.IsDecomposedBy:
                obj = storey.RelatedObjects[0]  # Take the first object we find
                return ifc_object_to_dict(ifc_file, obj, ifc_file_name)

    return None

if __name__ == "__main__":
    ifc_file = ifcopenshell.open(r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\ifc\single-beam.ifc")
    object_data = ifc_file_to_object_dict(ifc_file, "test.ifc")

    with open(r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\beams-json\test_single.json", "w") as json_file:
        json.dump(object_data, json_file, indent=4)

    print(object_data)
    print("Done")

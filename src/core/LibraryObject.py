from __future__ import annotations

from enum import Enum
from typing import List

import ifcopenshell

class IfcMeasureToUnit:
    """
    Object to map IFC measure types to unit types
    """

    def __init__(self, measures_list: List[str], unit):
        self.measures_list = measures_list
        self.unit = unit

class IfcMeasureToUnitEnum(Enum):
    """
    Enum to map units to ifc measure types, and hence ifc units
    """

    LENGTH = IfcMeasureToUnit(["IfcPositiveLengthMeasure", "IfcLengthMeasure"], "LENGTHUNIT")
    AREA = IfcMeasureToUnit(["IfcAreaMeasure"], "AREAUNIT")
    ANGLE = IfcMeasureToUnit(["IfcPlaneAngleMeasure"], "PLANEANGLEUNIT")
    VOLUME = IfcMeasureToUnit(["IfcVolumeMeasure"], "VOLUMEUNIT")
    PRESSURE = IfcMeasureToUnit(["IfcPressureMeasure"], "PRESSUREUNIT")


class LibraryObject:
    """
    Wrapper for a library object

    Represents what is stored in cloud storage
    """

    id: str
    name: str
    object_type: str
    material: str
    object_placement: str
    ifc_type: str
    ifc_file_path: str
    units: dict
    property_sets: dict
    manufacturer_link: str

    def __init__(self, name, object_type, material, object_placement, ifc_type, ifc_file_path, units, property_sets,
                 manufacturer_link=None,
                 id=None,
                 is_recycled=False):
        self.name = name
        self.object_type = object_type
        self.material = material
        self.object_placement = object_placement
        self.ifc_type = ifc_type
        self.ifc_file_path = ifc_file_path
        self.units = units
        self.property_sets = property_sets
        self.manufacturer_link = manufacturer_link
        self.id = id
        self.is_recycled = is_recycled

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "object_type": self.object_type,
            "material": self.material,
            "object_placement": self.object_placement,
            "ifc_type": self.ifc_type,
            "manufacturer_link": self.manufacturer_link,
            "ifc_file_path": self.ifc_file_path,
            "is_recycled": self.is_recycled,
            "units": self.units,
            "property_sets": self.property_sets
        }

    @staticmethod
    def __unit_for_property(prop):
        """Finds unit for an ifcopenshell property"""
        if hasattr(prop, 'Unit') and prop.Unit is not None:
            return prop.Unit

        for unit_name in IfcMeasureToUnitEnum:
            for measure in unit_name.value.measures_list:
                if prop.NominalValue.is_a(measure):
                    return unit_name.value.unit

        return "NO-UNIT"

    @staticmethod
    def from_ifc_file(ifc_file: ifcopenshell.file, object_type="IfcBeam", customID: str = None) \
            -> tuple[LibraryObject, str] | tuple[None, None]:
        ifc_object = ifc_file.by_type(object_type)[0]

        if customID:
            ifc_object.GlobalId = customID

        if ifc_object:
            file_name = f"{ifc_object.GlobalId}.ifc"
            return LibraryObject.__from_ifc_object(ifc_file, ifc_object, file_name), file_name

        return None, None

    @staticmethod
    def from_opensearch_hit(hit: dict) -> LibraryObject:
        return LibraryObject(
            name=hit["_source"]["name"],
            object_type=hit["_source"]["object_type"],
            material=hit["_source"]["material"],
            object_placement=hit["_source"]["object_placement"],
            ifc_type=hit["_source"]["ifc_type"],
            manufacturer_link=hit["_source"]["manufacturer_link"],
            ifc_file_path=hit["_source"]["ifc_file_path"],
            units=hit["_source"]["units"],
            property_sets=hit["_source"]["property_sets"],
            id=hit["_id"],
            is_recycled=hit["_source"]["is_recycled"]
        )

    @staticmethod
    def __from_ifc_object(ifc_file: ifcopenshell.file, ifc_object: ifcopenshell.entity_instance,
                          ifc_file_path: str) -> LibraryObject:
        # Prepare a dictionary to hold the object data
        object = LibraryObject(
            name=ifc_object.Name,
            object_type=ifc_object.ObjectType,
            material=None,  # To store material data
            object_placement=str(ifc_object.ObjectPlacement),  # Example: Placement data
            ifc_type="IfcBeam",
            ifc_file_path=ifc_file_path,
            units={},
            property_sets={},
            id=ifc_object.GlobalId
        )

        LibraryObject.__add_material(ifc_object, object)

        LibraryObject.__add_units(object, ifc_file)

        # Add property sets to object
        property_sets = ifc_file.get_inverse(ifc_object, True)
        for rel in property_sets:
            if rel.is_a("IfcRelDefinesByProperties"):
                pset = rel.RelatingPropertyDefinition
                if pset.is_a("IfcPropertySet"):
                    if pset.Name not in object.property_sets:
                        object.property_sets[pset.Name] = {}

                    for prop in pset.HasProperties:
                        object.property_sets[pset.Name][prop.Name] = {
                            "value": prop.NominalValue.wrappedValue if hasattr(prop.NominalValue,
                                                                               'wrappedValue') else str(
                                prop.NominalValue),
                            "unit": LibraryObject.__unit_for_property(prop)
                        }

        return object

    @staticmethod
    def __add_material(ifc_object: ifcopenshell.entity_instance, object: LibraryObject):
        if ifc_object.HasAssociations:
            for association in ifc_object.HasAssociations:
                if association.is_a("IfcRelAssociatesMaterial"):
                    material = association.RelatingMaterial
                    if material:
                        object.material = material.Name if hasattr(material, 'Name') else str(material)

    @staticmethod
    def __add_units(object: LibraryObject, ifc_file: ifcopenshell.file):
        unit_assignments = ifc_file.by_type("IfcUnitAssignment")[0]

        for unit in unit_assignments.Units:
            unit_map = {}

            if unit.is_a("IfcSIUnit") or unit.is_a("IfcConversionBasedUnit"):
                unit_map["Name"] = unit.Name

            if unit.is_a("IfcSIUnit"):
                unit_map["Prefix"] = unit.Prefix if unit.Prefix is not None else "NO-PREFIX"

            object.units[unit.UnitType] = (unit_map)

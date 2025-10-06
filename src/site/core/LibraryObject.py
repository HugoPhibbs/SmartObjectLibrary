from __future__ import annotations

from pprint import pprint
from dataclasses import dataclass, asdict
import ifcopenshell.util.element
from enum import Enum
from typing import List, Optional
import pydash as _
import random
import json

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


@dataclass
class PrimaryInfo:
    name: str
    model: str
    standard: str
    ifc_type: str
    categories: list[str]


class Currency(Enum):
    USD = "USD"
    EUR = "EUR"
    NZD = "NZD"


class CostMetric(Enum):
    COST_PER_UNIT = "COST_PER_UNIT"
    COST_PER_TONNE = "COST_PER_TONNE"
    COST_PER_METER = "COST_PER_METER"
    COST_PER_M3 = "COST_PER_M3"
    COST_PER_M2 = "COST_PER_M2"


@dataclass
class Cost:
    price: float
    currency: Currency
    metric: CostMetric

@dataclass
class Manufacturer:
    name: str
    link: str
    address: str
    contact_email: str


@dataclass
class RecycleInfo:
    salvage_method: Optional[str] = None
    previous_connection: Optional[str] = None
    is_recycled: bool = False


@dataclass
class BaseQuantities:
    ifc_quantity_type: str
    properties: dict


@dataclass
class IdentityData:
    primary_info: PrimaryInfo
    manufacturer: Manufacturer
    recycle_info: RecycleInfo
    base_quantities: BaseQuantities


@dataclass
class Profile:
    ifc_mechanics: dict
    ifc_profile_type: str
    ifc_profile_attributes: dict


@dataclass
class Material:
    name: str
    ifc_material_type: str
    ifc_material_properties: dict


@dataclass
class Unit:
    name: str
    prefix: str | None


@dataclass
class LibraryObject:
    """
    Wrapper for a library object

    Represents what is stored in cloud storage

    Stores data in a raw format, without any cleaning/adjustment of the data that it contains - this needs to be done
    on a case-by-case basis - depending on what input ifc data is used.
    """

    object_id: str
    identity_data: IdentityData
    supporting_documents: dict[str, str]
    property_sets: dict
    material: Material
    profile: Profile | None
    units: dict[str, Unit]
    cost: Cost | None = None

    def to_dict(self):
        return {
            "object_id": self.object_id,
            "identity_data": asdict(self.identity_data),
            "supporting_documents": self.supporting_documents,
            "property_sets": self.property_sets,
            "cost": asdict(self.cost) if self.cost else None,
            "material": asdict(self.material),
            "profile": asdict(self.profile) if self.profile else None,
            "units": {unit_type: asdict(unit) for unit_type, unit in self.units.items()}
        }

    @staticmethod
    def get_opensearch_schema():
        """
        Returns the OpenSearch schema for the LibraryObject

        Only does this for a subset of the object attributes, i.e. to set these as keywords, other the attribute types are to
        be inferred by OpenSearch.

        :return: dict
        """
        return {
            "object_id": {"type": "keyword"}
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
    def from_ifc_file(ifc_file: ifcopenshell.file, object_types=["IfcBeam"], customID: str = None) \
            -> tuple[LibraryObject, str] | tuple[None, None]:
        ifc_object = None
        for obj_type in object_types:
            try:
                ifc_object = ifc_file.by_type(obj_type)[0]
                break
            except IndexError:
                continue

        if not ifc_object:
            print(f"No object of types {object_types} found in the IFC file.")
            return None, None

        if customID:
            ifc_object.GlobalId = customID

        if ifc_object:
            file_name = f"{ifc_object.GlobalId}.ifc"
            return LibraryObject.from_ifc_object(ifc_file, ifc_object), file_name

        return None, None

    @staticmethod
    def from_ifc_object(ifc_file: ifcopenshell.file, ifc_object: ifcopenshell.entity_instance) -> LibraryObject:
        # Add property sets to object
        property_sets = ifc_file.get_inverse(ifc_object, True)

        property_set_dict = {}

        for rel in property_sets:
            if rel.is_a("IfcRelDefinesByProperties"):
                pset = rel.RelatingPropertyDefinition
                if pset.is_a("IfcPropertySet"):
                    if pset.Name not in property_set_dict:
                        property_set_dict[pset.Name] = {}

                    for prop in pset.HasProperties:
                        value = prop.NominalValue.wrappedValue if hasattr(prop.NominalValue,
                                                                          'wrappedValue') else str(prop.NominalValue)
                        value = LibraryObject.round_if_float(value)
                        property_set_dict[pset.Name][prop.Name] = {
                            "value": value,
                            "unit": LibraryObject.__unit_for_property(prop)
                        }

        # Getting primary info

        # Assume standard is found same place as S&T data
        primary_info = PrimaryInfo(
            name=ifc_object.Name,
            standard=_.get(property_set_dict, "Identity Data.Design Standard.value", "NO_STANDARD"),
            ifc_type=ifc_object.ObjectType,
            model=_.get(property_set_dict, "Identity Data.Model.value", "NO_MODEL")
        )

        # Manufacturer
        manufacturer = Manufacturer(
            name=_.get(property_set_dict, "Identity Data.Manufacturer.value", "NO_MANUFACTURER"),
            link=_.get(property_set_dict, "Identity Data.Manufacturer Link.value", "NO_LINK"),
            address=_.get(property_set_dict, "Identity Data.Manufacturer Address.value", "NO_ADDRESS"),
            contact_email=_.get(property_set_dict, "Identity Data.Manufacturer Contact Email.value", "NO_EMAIL")
        )

        recycle_info = RecycleInfo()

        base_quantities = LibraryObject.__extract_base_quantities(ifc_object)

        identity_data = IdentityData(
            primary_info=primary_info,
            manufacturer=manufacturer,
            recycle_info=recycle_info,
            base_quantities=base_quantities
        )

        profile = LibraryObject.__extract_profile(ifc_object)

        material = LibraryObject.__extract_material(ifc_object)

        units = LibraryObject.__extract_units(ifc_file)

        new_object = LibraryObject(
            object_id=ifc_object.GlobalId,
            identity_data=identity_data,
            supporting_documents={},
            property_sets=property_set_dict,
            units=units,
            material=material,
            profile=profile,
        )

        return new_object

    @staticmethod
    def __extract_material(ifc_object) -> Material:
        """
        Extracts:
        - name: the label of the material
        - ifc_material_type: the name of the material property set (if any)
        - ifc_material_properties: key-value pairs from that property set
        """
        material_name = "Unknown"
        material_pset_name = "Unknown"
        material_properties = {}
        material_entity = None

        for rel in getattr(ifc_object, "HasAssociations", []):
            if rel.is_a("IfcRelAssociatesMaterial"):
                mat = rel.RelatingMaterial

                if mat.is_a("IfcMaterial"):
                    material_entity = mat
                    material_name = mat.Name

                elif mat.is_a("IfcMaterialProfileSetUsage"):
                    profiles = mat.ForProfileSet.MaterialProfiles
                    if profiles:
                        profile_material = profiles[0].Material
                        if profile_material:
                            material_entity = profile_material
                            material_name = profile_material.Name

                break  # Assume only one material association is relevant

        if material_entity:
            for definition in getattr(material_entity, "HasProperties", []):
                if definition.is_a("IfcMaterialProperties") or definition.is_a("IfcGeneralMaterialProperties"):
                    material_pset_name = definition.Name or definition.is_a()
                    for prop in getattr(definition, "Properties", []):
                        val = getattr(prop.NominalValue, "wrappedValue", str(prop.NominalValue))
                        material_properties[prop.Name] = {
                            "value": LibraryObject.round_if_float(val),
                            "unit": None
                        }

        return Material(
            name=material_name,
            ifc_material_type=material_pset_name,
            ifc_material_properties=material_properties
        )

    @staticmethod
    def __extract_profile(ifc_object) -> Optional[Profile]:
        """
        Extracts the IfcProfileDef from a beam/column via material profile usage,
        and returns profile type, attributes, and Pset_ProfileMechanical.
        """
        profile_def = None

        for rel in getattr(ifc_object, "HasAssociations", []):
            if rel.is_a("IfcRelAssociatesMaterial"):
                usage = rel.RelatingMaterial
                if usage.is_a("IfcMaterialProfileSetUsage"):
                    mps = usage.ForProfileSet
                    if mps and mps.MaterialProfiles:
                        profile_def = mps.MaterialProfiles[0].Profile
                        break

        if not profile_def:
            return None

        # Extract attributes from IfcProfileDef
        profile_attrs = {
                            attr: getattr(profile_def, attr)
                            for attr in dir(profile_def)
                            if not attr.startswith("_") and not callable(getattr(profile_def, attr))
                        } or None

        # Extract Pset_ProfileMechanical
        pset_mechanical = {}
        for rel in getattr(ifc_object, "IsDefinedBy", []):
            if rel.is_a("IfcRelDefinesByProperties"):
                pset = rel.RelatingPropertyDefinition
                if pset.is_a("IfcPropertySet") and pset.Name == "Pset_ProfileMechanical":
                    for prop in pset.HasProperties:
                        val = getattr(prop.NominalValue, "wrappedValue", str(prop.NominalValue))
                        pset_mechanical[prop.Name] = {"value": LibraryObject.round_if_float(val), "unit": None}

        return Profile(
            ifc_mechanics=pset_mechanical,
            ifc_profile_type=profile_def.is_a(),
            ifc_profile_attributes=profile_attrs
        )

    @staticmethod
    def __extract_units(ifc_file: ifcopenshell.file):
        unit_assignments = ifc_file.by_type("IfcUnitAssignment")[0]

        unit_maps = {}

        for unit in unit_assignments.Units:
            this_unit = Unit("", None)

            if unit.is_a("IfcSIUnit") or unit.is_a("IfcConversionBasedUnit"):
                this_unit.name = unit.Name

            if unit.is_a("IfcSIUnit"):
                this_unit.prefix = unit.Prefix if unit.Prefix is not None else "NO-PREFIX"

            unit_maps[unit.UnitType] = this_unit

        return unit_maps

    @staticmethod
    def __extract_base_quantities(ifc_object: ifcopenshell.entity_instance) -> BaseQuantities:
        """
        Extracts Qto_*BaseQuantities from the IFC object.
        Assumes there's only one quantity set of interest.
        """

        quantities = ifcopenshell.util.element.get_quantities([ifc_object])
        base_qset_name = next(iter(quantities), None)

        if not base_qset_name:
            return BaseQuantities(ifc_quantity_type="Unknown", properties={})

        props = {}
        for name, value in quantities[base_qset_name].items():
            props[name] = {
                "value": LibraryObject.round_if_float(value),  # Already native Python type
                "unit": None  # IFC doesn't always associate units explicitly here
            }

        return BaseQuantities(
            ifc_quantity_type=base_qset_name,
            properties=props
        )

    @staticmethod
    def round_if_float(x, decimals=2):
        return round(x, decimals) if isinstance(x, float) else x


if __name__ == "__main__":
    pass

    # ifc_file_path = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\ifc\3SNP$Wt$z1zRVDzWDPAZ9I.ifc"
    #
    # ifc_file = ifcopenshell.open(ifc_file_path)
    #
    # object, file_name = LibraryObject.from_ifc_file(ifc_file)
    #
    # object_dict = object.to_dict()
    #
    # import json
    #
    # print(json.dumps(object_dict, indent=4))

import os
import re

from tqdm import trange

import ifcopenshell.api.spatial
import ifcopenshell.file
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import ifcopenshell.api.geometry
import ifcopenshell.api.spatial
import ifcopenshell.api.pset
import ifcopenshell.util.element
import ifcopenshell.api.project

# Script to extract objects from the S&T objects ifc file and write them to individual ifc files

__all__ = ["main"]


def get_family_and_type(ifc_object):
    for rel in ifc_object.IsDefinedBy:
        if not rel.is_a("IfcRelDefinesByProperties"):
            continue
        pset = rel.RelatingPropertyDefinition
        if not pset.is_a("IfcPropertySet") or pset.Name != "Other":
            continue
        for prop in pset.HasProperties:
            if prop.Name == "Family and Type" and hasattr(prop, "NominalValue"):
                val = prop.NominalValue
                return val.wrappedValue if hasattr(val, "wrappedValue") else str(val)
    return None


def should_add_object_wsp(object, unique_families_and_types: set[str]) -> bool:
    """
    Simple script to check if an object should be added from the ChCh WSP IFC file

    :param object: object to be checked
    :return: bool as to whether the object should be added
    """
    family_and_type = get_family_and_type(object)

    if family_and_type in unique_families_and_types:
        return False

    unique_families_and_types.add(family_and_type)
    return True


def copy_units(source_file, target_file, target_project):
    source_project = source_file.by_type("IfcProject")[0]
    if source_project and source_project.UnitsInContext:
        copied_units = ifcopenshell.util.element.copy_deep(
            target_file,
            source_project.UnitsInContext
        )
        target_project.UnitsInContext = copied_units


def get_quantities(obj):
    quantities = {}
    for rel in getattr(obj, "IsDefinedBy", []):
        if rel.is_a("IfcRelDefinesByProperties") and rel.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
            qset = rel.RelatingPropertyDefinition
            for q in qset.Quantities:
                val = getattr(q, "LengthValue", None) or getattr(q, "AreaValue", None) or getattr(q, "VolumeValue",
                                                                                                  None)
                if val is not None:
                    quantities.setdefault(qset.Name, {})[q.Name] = val
    return quantities


def copy_ifc_object(source_obj, ifc_file):
    # 1. Deep copy the object without placement
    obj_copy = ifcopenshell.util.element.copy_deep(
        ifc_file,
        element=source_obj,
        exclude_callback=lambda x: x.is_a("IfcObjectPlacement")
    )

    # 2. Copy property sets
    psets = ifcopenshell.util.element.get_psets(source_obj)
    for pset_name, props in psets.items():
        new_pset = ifcopenshell.api.pset.add_pset(ifc_file, product=obj_copy, name=pset_name)
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=new_pset,
                                        properties={k: v for k, v in props.items() if v is not None})

    # 3. Copy quantities manually
    qtos = get_quantities(source_obj)
    for qto_name, props in qtos.items():
        new_qto = ifcopenshell.api.pset.add_pset(ifc_file, product=obj_copy, name=qto_name)
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=new_qto,
                                        properties={k: v for k, v in props.items() if v is not None})

    # 4. Copy global ID
    obj_copy.GlobalId = source_obj.GlobalId

    return obj_copy


def write_object_to_single_ifc(ifc_file: ifcopenshell.file, object,
                               objects_dir=r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects"):
    ifc_file_copy = ifcopenshell.file(schema=ifc_file.schema)

    object_copy = copy_ifc_object(object, ifc_file_copy)

    site = ifcopenshell.api.root.create_entity(ifc_file_copy, "IfcSite")

    project = ifcopenshell.api.root.create_entity(ifc_file_copy, "IfcProject")
    copy_units(ifc_file, ifc_file_copy, project)
    ifcopenshell.api.aggregate.assign_object(ifc_file_copy, relating_object=project, products=[site])

    new_building = ifcopenshell.api.root.create_entity(ifc_file_copy, "IfcBuilding")
    ifcopenshell.api.aggregate.assign_object(ifc_file_copy, relating_object=site, products=[new_building])

    new_storey = ifcopenshell.api.root.create_entity(ifc_file_copy, "IfcBuildingStorey")
    ifcopenshell.api.aggregate.assign_object(ifc_file_copy, relating_object=new_building, products=[new_storey])

    # ifcopenshell.api.geometry.edit_object_placement(ifc_file_copy, object_copy)

    origin = ifc_file_copy.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
    placement3d = ifc_file_copy.create_entity("IfcAxis2Placement3D", Location=origin)
    local_placement = ifc_file_copy.create_entity("IfcLocalPlacement", RelativePlacement=placement3d)
    object_copy.ObjectPlacement = local_placement

    ifcopenshell.api.spatial.assign_container(ifc_file_copy, relating_structure=new_storey, products=[object_copy])

    object_dir = os.path.join(objects_dir, "ifc")

    os.makedirs(object_dir, exist_ok=True)

    curr_id = object_copy.GlobalId

    file_name = f"{curr_id}.ifc"

    ifc_file_copy.write(os.path.join(object_dir, file_name))

    return file_name


def write_objects_to_single_ifc(ifc_file_path, objects_dir, object_type="IfcBeam"):
    ifc_file = ifcopenshell.open(ifc_file_path)

    objects = ifc_file.by_type(object_type)

    num_objects = len(objects)

    unique_families_and_types = set()

    for i in trange(num_objects):

        if not should_add_object_wsp(objects[i], unique_families_and_types):
            continue

        write_object_to_single_ifc(ifc_file, objects[i], objects_dir)


def keep_ifc_column(ifc_column, unique_columns):
    pattern = r"^Structural Columns [1-5]:Structural Columns [1-5]$"

    if "steel" in ifc_column.Name.lower() or "column" in ifc_column.Name.lower():
        name_parsed = ":".join(ifc_column.Name.split(":")[:2])

        if re.match(pattern, name_parsed):
            return False

        if name_parsed not in unique_columns.keys():
            unique_columns[name_parsed] = ifc_column
            return True

    return False


def main():
    IFC_FILE_PATH = r"C:\Users\hugop\Downloads\ChCh_IFC\ChCh_IFC\CHCH-WSP-00-ALL-M3D-001_detached.ifc"
    OBJECTS_DIR = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects"

    write_objects_to_single_ifc(IFC_FILE_PATH, OBJECTS_DIR, object_type="IfcColumn")


if __name__ == "__main__":
    # For objects
    # IFC_FILE_PATH = r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\ifc\Steel-UB Universal Beam-Steel & Tube-300.ifc"
    # OBJECTS_DIR = r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\objects"

    main()

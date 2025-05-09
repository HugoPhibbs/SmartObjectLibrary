import re

__all__ = ["main"]


def correct_mass_per_metre(object_dict):
    # S&T has mass per metre in kg/ft, convert to kg/m
    value_ref = object_dict["property_sets"]["Structural"]["MassPerUnitLength_ANZRS"]  # A reference
    value_ref["value"] *= 3.28084
    value_ref["value"] = round(value_ref["value"], 1)


def remove_unused_property_sets(object_dict):
    del object_dict["property_sets"]["Constraints"]
    del object_dict["property_sets"]["Geometric Position"]
    del object_dict["property_sets"]["Phasing"]
    del object_dict["property_sets"]["Visibility"]
    del object_dict["property_sets"]["Other"]


def add_section_type(object_dict):
    model = object_dict["property_sets"]["Identity Data"]["Model"]["value"]
    pattern = r"(?P<section_type>\d{3,}[A-Z]{2})(?P<mass_per_length>\d+\.\d+)"
    match = re.match(pattern, model)
    if match:
        # TODO integrate this line of code into LibraryObject.from_ifc_file
        object_dict["property_sets"]["Identity Data"]["section_type"] = {"value": match.group("section_type"),
                                                                         "unit": "NO_UNIT"}
    else:
        raise Exception(f"Model: {model} does not match pattern")

def add_object_geometry(object_dict):
    dims = object_dict["property_sets"]["Dimensions"]

    # We simplify things and assume that the object is symmetric vertically
    # Modelled on https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAsymmetricIShapeProfileDef.htm
    I_beam_properties = {
        "Height": dims["Height"],
        "Width": dims["Width"],
        "Flange_Thickness": dims["Flange Thickness"],
        "Web_Thickness": dims["Web Thickness"],
        "Web_Fillet": dims["Web Fillet"],
        "Section_Type": object_dict["property_sets"]["Identity Data"]["section_type"],
        "Mass_Per_Length": object_dict["property_sets"]["Structural"]["MassPerUnitLength_ANZRS"],
    }

    object_dict["geometry"] = {
        "I_beam_profile": I_beam_properties,
    }

def reorganise_structural_information(object_dict):
    structural = object_dict["property_sets"]["Structural Analysis"]

    profile_mechanical = {
        "SectionArea": structural["Section Area"],
        "MomentOfInertiaZ": structural["Moment of Inertia strong axis"],
        "MomentOfInertiaY": structural["Moment of Inertia weak axis"],
        "MaximumSectionModulusZ": structural["Plastic Modulus strong axis"],
        "MaximumSectionModulusY": structural["Plastic Modulus weak axis"],
        "ShearAreaZ": structural["Shear Area strong axis"],
        "ShearAreaY": structural["Shear Area weak axis"],
        "TorsionalConstantX": structural["Torsional Modulus"],
        "WarpingConstant": structural["Warping Constant"],
        "ElasticSectionModulusZ": structural["X-Zex"],
        "ElasticSectionModulusY": structural["Y-Zey"],
    }

    structural_material_common = {
        "YieldStress": structural["Yield Stress Flange"],  # assuming same for web
        "UltimateStress": structural["Tensile Strength"],
        "ElasticModulus": structural["Elastic Modulus strong axis"],  # scalar simplification
    }

    object_dict["property_sets"]["Pset_ProfileMechanical"] = profile_mechanical
    object_dict["property_sets"]["Pset_StructuralMaterialCommon"] = structural_material_common


def main(object_dict):
    correct_mass_per_metre(object_dict)
    add_section_type(object_dict)
    remove_unused_property_sets(object_dict)

    return object_dict

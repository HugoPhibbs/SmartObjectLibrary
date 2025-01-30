# import ifcopenshell.api as ifc_api
import json
import ifcopenshell.api.project
import ifcopenshell.api.root as ifc_root
import ifcopenshell.api.unit as ifc_unit
import ifcopenshell.api.aggregate as ifc_aggregate
from ifcopenshell.api.pset.add_pset import add_pset
from ifcopenshell.api.pset.edit_pset import edit_pset
import ifcopenshell.api.geometry as ifc_geometry
import ifcopenshell.api.context
import ifcopenshell.api.spatial as ifc_spatial

# Load the JSON data
with open(r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\beams-json\beams_0.json", "r") as f:
    data = json.load(f)

model = ifcopenshell.api.project.create_file()
project = ifc_root.create_entity(model, ifc_class="IfcProject", name="MyProject")

ifc_unit.assign_unit(model)

context = ifcopenshell.api.context.add_context(model, context_type="Model")

body = ifcopenshell.api.context.add_context(model, context_type="Model",
                                            context_identifier="Body", target_view="MODEL_VIEW", parent=context)

site = ifc_root.create_entity(model, ifc_class="IfcSite", name="Site")
building = ifc_root.create_entity(model, ifc_class="IfcBuilding", name="Building")
storey = ifc_root.create_entity(model, ifc_class="IfcBuildingStorey", name="Ground Floor")

ifc_aggregate.assign_object(model, relating_object=project, products=[site])
ifc_aggregate.assign_object(model, relating_object=site, products=[building])
ifc_aggregate.assign_object(model, relating_object=building, products=[storey])

obj = ifc_root.create_entity(model, ifc_class=data["ifc_type"])

ifc_geometry.edit_object_placement(model, product=obj)

ifc_spatial.assign_container(model, relating_structure=storey, products=[obj])

for pset_name, properties in data["property_sets"].items():
    pset = add_pset(model, product=obj, name=pset_name)
    for key, value in properties.items():
        edit_pset(model, pset=pset, properties={key: value})

model.write("output.ifc")

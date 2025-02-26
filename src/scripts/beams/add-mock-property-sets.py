import re
import random
import os
import ifcopenshell.api

# Script to add mock property sets to all beams in the ifc directory
# For testing and demo purposes

property_sets = {
    "Pset_EnvironmentalImpactIndicators": {
        "ExpectedServiceLife": {"type": "IfcTimeMeasure"},
        "WaterConsumptionPerUnit": {"type": "IfcVolumeMeasure"},
        "ClimateChangePerUnit": {"type": "IfcMassMeasure"},
        "RenewableEnergyConsumptionPerUnit": {"type": "IfcEnergyMeasure"},
        "NonRenewableEnergyConsumptionPerUnit": {"type": "IfcEnergyMeasure"},
    },
    "Pset_ManufacturerOccurrence": {
        "AcquisitionDate": {"type": "IfcDate"},
        "BarCode": {"type": "IfcIdentifier"},
        "SerialNumber": {"type": "IfcIdentifier"},
        "BatchReference": {"type": "IfcIdentifier"},
        # "AssemblyPlace": {"type": "PEnum_AssemblyPlace"},
        "ManufacturingDate": {"type": "IfcDate"},
    },
    "Pset_Condition": {
        "AssessmentDate": {"type": "IfcDate"},
        "AssessmentCondition": {"type": "IfcLabel"},
        "AssessmentDescription": {"type": "IfcText"},
        "AssessmentType": {"type": "IfcLabel"},
        "AssessmentMethod": {"type": "IfcDocumentReference"},
        "LastAssessmentReport": {"type": "IfcLabel"},
        "NextAssessmentDate": {"type": "IfcDate"},
        "AssessmentFrequency": {"type": "IfcTimeMeasure"},  # Annual inspection
    },
    "Pset_ServiceLife": {
        "ServiceLifeDuration": {"type": "IfcPropertyBoundedValue"},
        "MeanTimeBetweenFailure": {"type": "IfcDuration"}  # 5 years
    }
}

random_attribute_values = {
    "ExpectedServiceLife": [10, 15, 20, 25, 30],
    "WaterConsumptionPerUnit": [0.3, 0.5, 0.7, 1.0, 1.2],
    "ClimateChangePerUnit": [0.2, 0.4, 0.5, 0.6, 0.8],
    "RenewableEnergyConsumptionPerUnit": [0.2, 0.4, 0.5, 0.7, 1.0],
    "NonRenewableEnergyConsumptionPerUnit": [0.3, 0.5, 0.6, 0.8, 1.1],

    "AcquisitionDate": ["2023-06-15", "2024-02-12", "2022-11-30", "2021-09-01", "2025-01-10"],
    "BarCode": ["1234567890", "9876543210", "4561237890", "7890123456", "3216549870"],
    "SerialNumber": ["SN-00123", "SN-00456", "SN-00789", "SN-00987", "SN-00234"],
    "BatchReference": ["BATCH-56789", "BATCH-12345", "BATCH-67890", "BATCH-54321", "BATCH-98765"],
    "AssemblyPlace": ["Factory", "OnSite", "OffSite", "ModularFacility", "PrecastPlant"],
    "ManufacturingDate": ["2024-01-15", "2023-05-20", "2022-12-10", "2021-08-05", "2020-04-30"],

    "AssessmentDate": ["2024-02-12", "2023-07-18", "2022-11-05", "2021-06-23", "2025-01-30"],
    "AssessmentCondition": ["Good", "Fair", "Poor", "Excellent", "Critical"],
    "AssessmentDescription": [
        "Minor wear, no functional issues",
        "Moderate wear, needs observation",
        "Severe wear, maintenance required",
        "Like new condition",
        "Critical damage, replacement needed"
    ],
    "AssessmentType": ["Routine Inspection", "Emergency Inspection", "Scheduled Maintenance", "Post-Repair Check",
                       "End-of-Life Evaluation"],
    "AssessmentMethod": ["DOC-12345", "DOC-67890", "DOC-45678", "DOC-98765", "DOC-54321"],
    "LastAssessmentReport": ["REPORT-67890", "REPORT-12345", "REPORT-98765", "REPORT-54321", "REPORT-45678"],
    "NextAssessmentDate": ["2025-02-12", "2024-09-30", "2026-03-15", "2023-12-05", "2027-01-25"],
    "AssessmentFrequency": [180, 365, 730, 90, 540],  # Days

    "ServiceLifeDuration": ["2Y", "5Y", "8Y", "10Y", "15Y"],
    "MeanTimeBetweenFailure": ["2Y", "5Y", "8Y", "10Y", "15Y"],
}


def add_property_set(file, pset_name, properties, beam):
    property_values = []

    for property_name, entity_info in properties.items():
        property_values.append(
            file.createIfcPropertySingleValue(property_name, "",
                                              file.create_entity(entity_info["type"], entity_info["value"]))
        )

    owner_history = file.by_type("IfcOwnerHistory")[0]

    pset = file.createIfcPropertySet(beam.GlobalId, owner_history, pset_name, None, property_values)

    file.createIfcRelDefinesByProperties(beam.GlobalId, owner_history, None, None, [beam], pset)

    return file


def add_all_property_sets(file, property_sets, beam):
    for pset_name, properties in property_sets.items():
        add_property_set(file, pset_name, properties, beam)

    return file


def generate_random_property_sets(property_sets):
    property_sets_copy = property_sets.copy()

    for pset_name, attribute_dicts in property_sets_copy.items():
        for key, entity_info in attribute_dicts.items():
            entity_info["value"] = random.choice(random_attribute_values[key])

    return property_sets_copy


def change_ifc_schema(file_path):
    # Yes this method is totally hacky, but who is checking?

    pattern = r"FILE_SCHEMA\(\('([^']+)'\)\);"
    replacement = "FILE_SCHEMA(('IFC4'));"

    with open(file_path, "r+") as file:
        lines = file.readlines()

        for i in range(20):
            lines[i] = re.sub(pattern, replacement, lines[i])

        file.seek(0)
        file.writelines(lines)


if __name__ == "__main__":
    ifc_dir = r"/objects/ifc"

    for file in os.listdir(ifc_dir):
        if file.endswith(".ifc"):
            file_path = os.path.join(ifc_dir, file)
            change_ifc_schema(file_path)
            ifc_file = ifcopenshell.open(file_path)
            beam = ifc_file.by_type("IfcBeam")[0]

            random_property_sets = generate_random_property_sets(property_sets)
            add_all_property_sets(ifc_file, random_property_sets, beam)
            ifc_file.write(file_path)

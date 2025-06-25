import random

units_map = {
    "ExpectedServiceLife": "TIMEUNIT",
    "WaterConsumptionPerUnit": "VOLUMEUNIT",
    "ClimateChangePerUnit": "MASSUNIT",
    "RenewableEnergyConsumptionPerUnit": "ENERGYUNIT",
    "NonRenewableEnergyConsumptionPerUnit": "ENERGYUNIT",

    "AcquisitionDate": "DATEUNIT",
    "BarCode": "IDENTIFIERUNIT",
    "SerialNumber": "IDENTIFIERUNIT",
    "BatchReference": "IDENTIFIERUNIT",
    "AssemblyPlace": "TEXTUNIT",
    "ManufacturingDate": "DATEUNIT",

    "AssessmentDate": "DATEUNIT",
    "AssessmentType": "TEXTUNIT",
    "AssessmentMethod": "DOCUMENTUNIT",
    "LastAssessmentReport": "TEXTUNIT",
    "NextAssessmentDate": "DATEUNIT",
    "AssessmentFrequency": "TIMEUNIT",

    "ServiceLifeDuration": "DURATIONUNIT",
    "MeanTimeBetweenFailure": "DURATIONUNIT",
}

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

condition_pairs = [
    ("Excellent", "Like new condition"),
    ("Good", "Minor wear, no functional issues"),
    ("Fair", "Moderate wear, needs observation"),
    ("Poor", "Severe wear, maintenance required"),
    ("Critical", "Critical damage, shouldn't be used"),
]

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
    "AssessmentType": ["Routine Inspection", "Emergency Inspection", "Scheduled Maintenance", "Post-Repair Check",
                       "End-of-Life Evaluation"],
    "AssessmentMethod": ["DOC-12345", "DOC-67890", "DOC-45678", "DOC-98765", "DOC-54321"],
    "LastAssessmentReport": ["REPORT-67890", "REPORT-12345", "REPORT-98765", "REPORT-54321", "REPORT-45678"],
    "NextAssessmentDate": ["2025-02-12", "2024-09-30", "2026-03-15", "2023-12-05", "2027-01-25"],
    "AssessmentFrequency": [180, 365, 730, 90, 540],  # Days

    "ServiceLifeDuration": ["2Y", "5Y", "8Y", "10Y", "15Y"],
    "MeanTimeBetweenFailure": ["2Y", "5Y", "8Y", "10Y", "15Y"],
}


def add_mock_property_sets(object_dict):
    """Attaches randomized mock property sets to an object_dict in-place, with 'value' and 'unit'."""
    object_dict.setdefault("property_sets", {})

    for pset_name, properties in property_sets.items():
        pset = {}
        for prop_name in properties:
            pset[prop_name] = {
                "value": random.choice(random_attribute_values[prop_name]),
                "unit": units_map.get(prop_name, "NO-UNIT")
            }

        if pset_name == "Pset_Condition":
            condition = random.choice(condition_pairs)
            pset["AssessmentCondition"] = {"value": condition[0], "unit": "TEXTUNIT"}
            pset["AssessmentDescription"] = {"value": condition[1], "unit": "TEXTUNIT"}

        object_dict["property_sets"][pset_name] = pset
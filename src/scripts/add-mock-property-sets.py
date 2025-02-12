import ifcopenshell
import ifcopenshell.api

file = ifcopenshell.open(
    r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\objects\ifc\1MqlONWM9DPguUA1H$xl0k.ifc")

# Get the first beam
beam = file.by_type("IfcBeam")[0]


def add_property_set(file, pset_name, properties):
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


def add_all_property_sets(file, property_sets):
    for pset_name, properties in property_sets.items():
        add_property_set(file, pset_name, properties)

    return file


property_sets = {
    "Pset_EnvironmentalImpactIndicators": {
        "ExpectedServiceLife": {"type": "IfcTimeMeasure", "value": 20},
        "WaterConsumptionPerUnit": {"type": "IfcVolumeMeasure", "value": 0.5},
        "ClimateChangePerUnit": {"type": "IfcMassMeasure", "value": 0.5},
        "RenewableEnergyConsumptionPerUnit": {"type": "IfcEnergyMeasure", "value": 0.5},
        "NonRenewableEnergyConsumptionPerUnit": {"type": "IfcEnergyMeasure", "value": 0.5},
    },
    "Pset_ManufacturerOccurrence": {
        "AcquisitionDate": {"type": "IfcDate", "value": "2024-02-12"},
        "BarCode": {"type": "IfcIdentifier", "value": "1234567890"},
        "SerialNumber": {"type": "IfcIdentifier", "value": "SN-00123"},
        "BatchReference": {"type": "IfcIdentifier", "value": "BATCH-56789"},
        # "AssemblyPlace": {"type": "PEnum_AssemblyPlace", "value": "Factory"},
        "ManufacturingDate": {"type": "IfcDate", "value": "2024-01-15"},
    },
    "Pset_Condition": {
        "AssessmentDate": {"type": "IfcDate", "value": "2024-02-12"},
        "AssessmentCondition": {"type": "IfcLabel", "value": "Good"},
        "AssessmentDescription": {"type": "IfcText", "value": "Minor wear, no functional issues"},
        "AssessmentType": {"type": "IfcLabel", "value": "Routine Inspection"},
        "AssessmentMethod": {"type": "IfcDocumentReference", "value": "DOC-12345"},
        "LastAssessmentReport": {"type": "IfcLabel", "value": "REPORT-67890"},
        "NextAssessmentDate": {"type": "IfcDate", "value": "2025-02-12"},
        "AssessmentFrequency": {"type": "IfcTimeMeasure", "value": 365},  # Annual inspection
    },
    "Pset_ServiceLife": {
        "ServiceLifeDuration": {"type": "IfcPropertyBoundedValue", "value": "20Y"}, # TODO, figure out how to use bounded value
        "MeanTimeBetweenFailure": {"type": "IfcDuration", "value": "5Y"}  # 5 years
    }
}

add_all_property_sets(file, property_sets)

file.write("output.ifc")

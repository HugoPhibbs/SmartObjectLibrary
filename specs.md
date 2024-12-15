# Product Library Specifications

* These are for the first level: material/components level only
* Objective: Provide essential data for individual materials/components like plates, bolts, welds, fire protection
  material, sound insulation material, etc.

[From Hafez] **Suggested objects to Include in the Product Library**:

* Product Identification:
    * Attributes: Unique Product ID, Name, Description, Category, Manufacturer Details.
    * Possible Psets:
        * [Pset_ManufacturerOccurrence](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Pset_ManufacturerOccurrence.htm)
        * [Pset_ManufacturerTypeInformation](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Pset_ManufacturerTypeInformation.htm)
* Physical Characteristics:
    * Attributes: Dimensions, Weight, Color, Material Composition, test certificates, inspection certificates etc
    * Descriptors are largely based on a per object basis, e.g. for a Beam, so not stored in Psets.
    * As for certificates, I don't think that there is anything
* Performance Specifications:
    * Attributes: Operational Parameters, Efficiency Ratings, Durability Metrics.
    * I think this information is largely based on a per-object basis. E.g. For HVAC products, these all have their own
      unique property sets to describe this information
* Lifecycle Information:
    * Attributes: Manufacturing Date, Warranty Period, Expected Lifespan, End-of-Life Disposal Guidelines.
    * Don't think there are any Psets on end of life information.
    * Don't think there is anything for seismic information either.
    * Possible Psets:
        * [Pset_Condition](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Pset_Condition.htm)
        * [Pset_ServiceLife](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Pset_ServiceLife.htm)
        * [Pset_Warranty](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Pset_Warranty.htm)
* Cost Data:
    * Attributes: Manufacturing Cost, Price, Cost of Ownership.
    * Likely needs a custom property set
* Sustainability Metrics:
    * Attributes: Carbon Footprint, Energy Consumption, Recyclability Index, Compliance with Environmental Standards.
    * Possible Psets:
        * [Pset_EnvironmentalEmissions](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Pset_EnvironmentalEmissions.htm)
        * [Pset_EnvironmentalImpactIndicators](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Pset_EnvironmentalImpactIndicators.htm)
        * [Pset_EnvironmentalImpactValues](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Pset_EnvironmentalImpactValues.htm)
* Te Ao Māori Considerations:
    * Attributes: Cultural Significance, Alignment with Māori Values (e.g., Kaitiakitanga - guardianship), Impact on
      Māori Communities.
    * Likely needs a custom property set
* Regulatory Compliance:
    * Attributes: Certifications, Building code compliance, Legal Restrictions.
* Supply Chain Information:
    * Attributes: Supplier Details, Geographic Origin, Supply Chain Transparency.
    * Likely needs a custom property set
    * This sounds like it could be enourmously complex by itself.
* User Feedback and Ratings:
    * Attributes: Customer Reviews, Satisfaction Scores, Reported Issues.
    * Probably involves a custom property set
    * I don't think there are marketplaces where people post reviews about these things, so not sure how this data could
      be integrated.

## SmartProduct

The main abstraction container of the above information.

Each of the above main points can be attached objects to a superclass called **SmartProduct**. Effectively this is a
wrapper around an IFC object. The idea being that the **SmartProduct** has it's underlying datastored in an IFC object.
These objects are linked to the underlying IFC object using *property sets* (whether custom or pre-existing).

The advantage of wrapping an IFC product is that it is an easy interface to other components of the app - providing
clean abstractions (e.g. for an API).

### Serialisation

SmartProduct should be stored as IFC objects. The idea being that if you can do this, then you can easily export and
import SmartProducts as needed.

Since SmartObjects can be serialised to IFC, then they can be easily stored online using object storage such as S3. If
they have a unique identifier, then they can easily be found via this way.

### Linking to external data

SmartProducts can link to external file data/links using *IfcDocumentReference* objects. This is usually a URL link to
an external file.

## Development and Technologies

The app will primarily be written in **Python**, using the following frameworks:

* IfcOpenShell for IFC object manipulation
* Flask for creating the interfacing API
* S3 for object storage, although at this stage we could just get way with storing IFC files locally using file
  directories.

## Data Sources

We don't (yet) have solid data sources for all of the above information. We can atleast start with readily available IFC
objects (i.e. from online), and then add attributes to this
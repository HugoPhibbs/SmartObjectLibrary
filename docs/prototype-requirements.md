# **Prototype Requirements**

* The prototype at this stage will be implemented as an API. This makes it easy to integrate with other apps such as websites or app plugins (e.g. for Revit, ArchiCAD, or ETABS)

## **Creating**

### Add a new beam (or beams) to product library.
* Take a request body that is an IFC file, and extract all beams and their property sets from this file. 
Then save the beams as JSON within object storage

## **Reading** 
* Fetching beams from the product library. Request body should precify whether this should be in IFC format or proprietary JSON
I think for prototype, I’m going to focus on returning prop JSON

### Select by ID#
* Return a beam with a given ID number

### Select with clear-cut filters
* Return all beams from product library that match the given filter pattern
* Query format is taken from OpenSearch standards. As an example, a query could look something like:
```json
{
  "query": {
    "bool": {
      "filter": [
        {
          "term": {
            "length": 10
          }
        }
      ]
    }
  }
}
```

### Select with natural language
* Return all beams matching an NLP query. E.g. “Return me all beams that align with Màtauranga Maori Values"
* Will use a LLM API in the backend (e.g. ChatGPT) to create OpenSearch filter patterns
* Intended to handle fuzzy boundaries when selecting objects. 
* Returned objects will be ranked by relavance where appropriate (OpenSearch handles relevance scoring of query to objects)

## **Updating**

### Update by ID#
* Take as a body either an IFC file or prop JSON, and rewrite the beam that is in storage beam given in the body. 
* Is a 're-write' and not an 'update'
* Otherwise self explanatory

## **Deleting**

### Delete by ID#
* Self-explanatory, delete the beam in product library with the given ID#

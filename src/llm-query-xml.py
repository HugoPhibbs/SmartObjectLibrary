from lxml import etree
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

openai_client = OpenAI()
openai_client.api_key = os.getenv("OPENAI_API_KEY")

with open(r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\beams_xml_schema.xsd", "r") as file:
    xml_schema = file.read()


def generate_xpath_filter(user_input):
    prompt = f"""You generate XPath filters for natural language queries.
    
                The general idea is that you are trying to search through a set of XML files representing objects to be used in construction projects. The created XML path filters
                are used to find matching objects based on the user's query.
                
                As of now, you can assume that the objects being searched over are steel beams, and the XML files contain information about these beams.
                
                The schema is as follows:
                
                {xml_schema}
                
                You will then respond to queries about the information contained in these XML files by generating an XPath filter that can be used to search for the relevant information.
                
                For example, given the query 'Find me a beam with an elastic modulus strong axis equal to 1.32e-05',
                the XPath filter should be (as a plain text string, ignore the single quotes):
                
                /root//Structural_Analysis[Elastic_Modulus_strong_axis=1.32e-05]
        
                You can also expect that that user may ask ranged queries, e.g. 'Find me a beam with a section area between 0.1 and 0.2', and you should generate the appropriate XPath filter.
                
                It is at your discretion to find the relevant path filter (i.e. map the user question into the relevant fields from the xml schema), if you are unable to find a match, you should respond with 'INVALID...', and briefly explain why.
                
                If you feel you need clarification on a question, start with 'MORE...'.
                
                Questions may not match completely with schema (e.g. different case etc). E.g. 'Find me a beam with an elastic modulus strong axis equal to 1.32e-05' should match with 'Elastic_Modulus_strong_axis', or "shear area strong axis" should match with 'Shear_Area_strong_axis'.
                
                Now, generate an XPath filter for the following queries"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "developer", "content": prompt},
            {"role": "user", "content": user_input}
        ],
        max_tokens=150,
        temperature=0.7
    )

    filter = response.choices[0].message.content

    if "INVALID" in filter or "MORE" in filter:
        return None

    return filter


def search_xml_files(xpath_filter):
    xml_folder_dir = r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\beams-xml"

    for xml_file in os.listdir(xml_folder_dir):
        file_path = os.path.join(xml_folder_dir, xml_file)
        if os.path.isfile(file_path) and xml_file.endswith(".xml"):
            with open(file_path, "rb") as file:
                xml_tree = etree.parse(file)
                matches = xml_tree.xpath(xpath_filter)
                if matches:
                    print(f"Match found in {xml_file}: {len(matches)} matches")
                else:
                    print(f"No match found in {xml_file}")


# Example of user query and filter
user_input = "Find me a beam with a elastic modulus weak axis equal to 0.000123 and width of 90"
xpath_filter = generate_xpath_filter(user_input)

# xpath_filter = "/root/property_sets/property_set[name='Structural Analysis' and properties/Elastic_Modulus_strong_axis='1.32e-05' and properties/Shear_Area_strong_axis=0.00178]"

print(xpath_filter)

search_xml_files(xpath_filter)

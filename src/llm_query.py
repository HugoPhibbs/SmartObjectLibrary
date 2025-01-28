import json
from openai import OpenAI
from dotenv import load_dotenv
import os
import jsonpath_ng.ext

load_dotenv()

openai_client = OpenAI()
openai_client.api_key = os.getenv("OPENAI_API_KEY")

def generate_json_filter(user_input):
    prompt = f"""You generate JSONPath filters for natural language queries. 
                    For example, given the query 'Find me a beam with an elastic modulus strong axis equal to 1.32e-05',
                    the JSONPATH filter should be (as a plain text string, ignore the single quotes):
                    '$.property_sets[?(@.property_set_name=="Structural Analysis")].properties[?(@.name=="Elastic Modulus strong axis" && @.value=="1.32e-05")]'
                    Now, generate a JSON filter for the following queries"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",  # or use gpt-3.5-turbo, depending on your need
        messages=[
            {"role": "developer", "content": prompt},
            {"role": "user", "content": user_input}
        ],
        max_tokens=150,
        temperature=0.7
    )

    return response.choices[0].message.content


def search_json_files(filter_pattern):
    json_folder_dir = r"C:\Users\hugop\Documents\Work\SteelProductLibrary\data\beams-json"

    # Compile the JSONPath filter
    jsonpath_expr = jsonpath_ng.ext.parse(filter_pattern)

    for json_file in os.listdir(json_folder_dir):
        with open(os.path.join(json_folder_dir, json_file), "r") as file:
            json_data = json.load(file)
            matches = jsonpath_expr.find(json_data)  # Use the find method for JSONPath
            if matches:
                print(f"Match found in {json_file}")
            else:
                print(f"No match found in {json_file}")


# Example of user query and filter
user_input = "Find me a beam with an elastic modulus strong axis equal to 1.32e-05"
# json_filter = generate_json_filter(user_input)

# Optionally, use a static filter for testing
json_filter = '$.property_sets[?(@.property_set_name=="Structural Analysis")].properties[?(@.name=="Elastic-Modulus-strong-axis" && @.value=="1.32e-05")]'

search_json_files(json_filter)

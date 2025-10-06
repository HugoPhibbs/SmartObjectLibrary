from src.site.core.opensearch_client import get_client
import os
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

api_key = os.getenv("OPENAPI_KEY")
ai_client = OpenAI(api_key=api_key)

os_client = get_client("prod")

base_dir = os.getenv("PROJECT_BASE_DIR", ".")


def get_objects(os_client):
    response = os_client.search(
        index="objects",
        body={
            "query": {"match_all": {}},
            "size": 1000
        }
    )

    objects = []

    for hit in response["hits"]["hits"]:
        source = hit["_source"]
        id = source["object_id"]
        name = source["identity_data"]["primary_info"]["name"]

        objects.append((id, name))

    objects.sort(key=lambda x: x[1])

    return objects


def generate_categories(object_name):
    category_choices = ["structural", "steel", "timber", "concrete", "column", "beam", "purlin", "miscellaneous",
                        "window", "glazing", "door", "furniture", "seating", "desk", "storage", "table", "angle",
                        "hollow-section", "universal-beam", "universal-column", "plate", "damper",
                        "pipe", "bracket", "roofing", "section", "PFC"]

    first_prompt = f"You are to be given a name of a construction object. Choose 1-3 categories (aim for atleast 2) from the list: {', '.join(category_choices)} that best fit the object. " \
                   f"Respond with only the categories, separated by commas, without any additional text. " \
                   f"An example: name: 'COL-WC:400WC303', categories = 'structural,column,steel'."

    prompt = f"{first_prompt}\n\nname: '{object_name}'"
    response = ai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=60,
        n=1,
        stop=None,
    )
    categories = response.choices[0].message.content.strip()

    category_list = [cat.strip() for cat in categories.split(",")]

    return category_list


def get_object_categories(objects, load_csv=True, csv_filename="object_categories.csv"):
    object_categories = []

    csv_file_path = os.path.join(base_dir, "data", csv_filename)

    if load_csv:
        df = pd.read_csv(csv_file_path)

    else:
        rows = []

        for object_id, name in objects:
            categories = generate_categories(name)
            categories = ";".join(categories)

            rows.append({"object_id": object_id, "name": name, "categories": categories})
            print(f"Processed {object_id}: {name} -> {categories}")

        df = pd.DataFrame(rows, columns=["object_id", "name", "categories"])
        df.to_csv(csv_file_path, index=False)

    for row in df.to_dict("records"):
        object_id = row["object_id"]
        categories = row["categories"].split(";")
        object_categories.append((object_id, categories))

    return object_categories


def upload_categories(object_categories, os_client):
    for object_id, categories in object_categories:
        response = os_client.update(
            index="objects",
            id=object_id,
            body={
                "doc": {
                    "identity_data" : {"primary_info": {"categories": categories}}  # directly overwrites or creates
                },
                "doc_as_upsert": True  # creates the field if missing
            }
        )
        print(f"Updated {object_id} with categories {categories}: {response['result']}")


if __name__ == "__main__":
    objects = get_objects(os_client)
    object_categories = get_object_categories(objects, load_csv=True)
    upload_categories(object_categories, os_client)
from src.site.core.opensearch_client import client

import pandas as pd
import genson

from src.scripts.utils import convert_schema

df = pd.read_csv(r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\connections\csv\all_connections.csv")

new_df = pd.DataFrame()

df_dict = df.to_dict(orient="records")

connections_list = []

for index, row in enumerate(df_dict):
    new_dict = {}
    new_dict["section_type"] = row["Member"]
    new_dict["mass_per_length"] = row["Mass"]
    new_dict["moment"] = row["Moment (%)"]
    new_dict["shear"] = row["Shear (%)"]

    new_dict["id"] = f"m{row['Moment (%)']}-s{row['Shear (%)']}-section{row['Member']}-mass{row['Mass']}"

    new_dict["connection"] = {}

    cleat = {"thickness": row["Thick."], "width": row["Width"], "length": row["Length"]}
    new_dict["connection"]["cleat"] = cleat

    bolts = {"total_top": row["Top"], "total_bottom": row["Bottom"], "diameter": row["Dia."]}
    new_dict["connection"]["bolts"] = bolts

    fillet_welds = {"flange": row["Flange"], "web": row["Web"]}
    new_dict["connection"]["fillet_welds"] = fillet_welds

    new_dict["design_capacity"] = {"moment_top": row["Moment"],
                                   "moment_bottom": row["Moment.1"],
                                   "shear_capacity": row["Shear"]}

    new_dict["connection_type"] = "MEP-8"

    connections_list.append(new_dict)

data_dict = connections_list[0]

builder = genson.SchemaBuilder()
builder.add_object(data_dict)
schema = builder.to_schema()

schema = convert_schema(schema)

# Adjust some fields to be keywords
schema["section_type"]["type"] = "keyword"
schema["id"]["type"] = "keyword"
schema["connection_type"]["type"] = "keyword"

if client.indices.exists(index="connections"):
    client.indices.delete(index="connections")

client.indices.create(index="connections", body={
    "mappings": {
        "properties": schema
    }
})

for index, connection in enumerate(connections_list):
    response = client.index(index="connections", body=connection, id=connection["id"])
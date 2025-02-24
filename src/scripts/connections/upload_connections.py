from core.opensearch_client import client

import pandas as pd
import genson

from scripts.utils import convert_schema

df = pd.read_csv(r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\connections\csv\all_connections.csv")

new_df = pd.DataFrame()

df_dict = df.to_dict(orient="records")

connections_list = []

for index, row in enumerate(df_dict):
    new_dict = {}
    new_dict["Member Section"] = row["Member Section"]
    new_dict["Mass"] = row["Mass (Kg/m)"]
    new_dict["Moment (%)"] = row["Moment"]
    new_dict["Shear (%)"] = row["Shear"]

    new_dict["Connection"] = {}

    cleat = {"Thickness": row["Thick. (mm)"], "Width": row["Width (mm)"], "Length": row["Length (mm)"]}
    new_dict["Connection"]["Cleat"] = cleat

    bolts = {"Total Bolts": row["Total Bolts"], "Diameter": row["Dia. (mm)"]}
    new_dict["Connection"]["Bolts"] = bolts

    fillet_welds = {"Flange": row["Flange Weld (mm)"], "Web": row["Web Weld (mm)"]}
    new_dict["Connection"]["Fillet Welds"] = fillet_welds

    new_dict["Design Capacity"] = {"Moment (Top)": row["Moment Capacity (Top) (KNm)"],
                                   "Moment (Bottom)": row["Moment Capacity (Bottom) (KNm)"],
                                   "Shear": row["Shear Capacity (KN)"]}

    connections_list.append(new_dict)

data_dict = connections_list[0]

builder = genson.SchemaBuilder()
builder.add_object(data_dict)
schema = builder.to_schema()

schema = convert_schema(schema)

if client.indices.exists(index="connections"):
    client.indices.delete(index="connections")

client.indices.create(index="connections", body={
    "mappings": {
        "properties": schema
    }
})

for index, connection in enumerate(connections_list):
    response = client.index(index="connections", body=connection, id=index)
import re
import os
import pandas as pd

# Script to combine all individual connection csv files into one complete csv file
# This is only for demo purposes - all the connection csvs are related to a MEP-8 connection

CONNECTIONS_CSV_DIR = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\connections\csv\individual"
complete_csv_path = r"C:\Users\hugop\Documents\Work\SmartObjectLibrary\data\connections\csv\all_connections.csv"

file_regex = r"m(\d+)-s(\d+)"

df = pd.DataFrame()

for csv_file in os.listdir(CONNECTIONS_CSV_DIR):
    if csv_file.endswith(".csv"):
        this_df = pd.read_csv(os.path.join(CONNECTIONS_CSV_DIR, csv_file))

        match = re.search(file_regex, csv_file)

        this_df["Moment (%)"] = int(match.group(1))
        this_df["Shear (%)"] = int(match.group(2))
        # this_df["Member Section"] = this_df['Member Section'].str.split().str[0]

        df = pd.concat([df, this_df], ignore_index=True)

df.drop(columns=["Unnamed: 13"], inplace=True)
df.to_csv(complete_csv_path, index=False)



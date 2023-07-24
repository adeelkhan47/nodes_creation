import json

import pandas as pd
import psycopg2
import requests

url = "https://inprove-sport.info/csv/getInproveDemo/hgnxjgTyrkCvdR"
# Get website data
response = requests.get(url)
data_raw = None
if response.status_code == 200:
    # Select json data
    data_raw = response.json()
else:
    print("Error loading the website")

data = pd.json_normalize(data_raw, record_path=['res'])
data['testID'] = data['testID'].astype(str)
table = data.pivot_table(index="athleteID", columns="testID",
                         values="testValue")
table["athID"] = table.index
athlethe_names = table['athID'].to_list()
# Create a connection
conn = psycopg2.connect(
    host="localhost",
    database="nodes_backend",
    user="postgres",
    password="postgres"
)

cur = conn.cursor()
cur.execute("""
    CREATE TABLE nodes (
        id SERIAL PRIMARY KEY,
        data JSONB
    )
""")

cur.execute("""
    CREATE TABLE edges (
        id SERIAL PRIMARY KEY,
        data JSONB
    )
""")

cur.execute("""
    CREATE TABLE threshold (
        id SERIAL PRIMARY KEY,
        data INTEGER 
    )
""")

cur.execute("""
    CREATE TABLE recommendations (
        id SERIAL PRIMARY KEY,
        data VARCHAR (1000),
        node_name VARCHAR (255)
    )
""")


cur.execute("""
    CREATE TABLE logs (
        id SERIAL PRIMARY KEY,
        data VARCHAR (255)
    )
""")


cur.execute("""
    CREATE TABLE url_data (
        id SERIAL PRIMARY KEY,
        data JSONB 
    )
""")

conn.commit()
# Website-url
url = "https://inprove-sport.info/csv/getInproveDemo/hgnxjgTyrkCvdR"
# Get website data
response = requests.get(url)
# Check if request is successful: status code 200
if response.status_code == 200:
    # Select json data
    data_raw = response.json()
    cur.execute("INSERT INTO url_data (data) VALUES (%s)", (json.dumps(data_raw),))

conn.commit()





#
cur.close()
conn.close()

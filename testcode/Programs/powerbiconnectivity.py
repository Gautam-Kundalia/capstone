import pymysql
import pandas as pd
import requests
import json

# MySQL Configuration
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DB = "accounts"
MYSQL_QUERY = "SELECT * FROM sales_pipeline_data"

# Power BI API Configuration
WORKSPACE_ID = "fc929ab3-ec9c-4de1-8117-52063a85b8a9"
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6ImltaTBZMnowZFlLeEJ0dEFxS19UdDVoWUJUayIsImtpZCI6ImltaTBZMnowZFlLeEJ0dEFxS19UdDVoWUJUayJ9.eyJhdWQiOiJodHRwczovL2FuYWx5c2lzLndpbmRvd3MubmV0L3Bvd2VyYmkvYXBpIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvZDFmMTQzNDgtZjFiNS00YTA5LWFjOTktN2ViZjIxM2NiYzgxLyIsImlhdCI6MTc0MDQxMjYxOSwibmJmIjoxNzQwNDEyNjE5LCJleHAiOjE3NDA0MTY1MTksImFpbyI6ImsyUmdZUGk1a3ExZTFXUEhFZTZtbjV1VVd6NHdBZ0E9IiwiYXBwaWQiOiIzMzJhZTI4MS02NTFlLTQ1MDItYmI1Ny1jZjI3YjYyMzI2NWMiLCJhcHBpZGFjciI6IjEiLCJpZHAiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9kMWYxNDM0OC1mMWI1LTRhMDktYWM5OS03ZWJmMjEzY2JjODEvIiwiaWR0eXAiOiJhcHAiLCJyaCI6IjEuQVQwQVNFUHgwYlh4Q1Vxc21YNl9JVHk4Z1FrQUFBQUFBQUFBd0FBQUFBQUFBQUE5QUFBOUFBLiIsInRpZCI6ImQxZjE0MzQ4LWYxYjUtNGEwOS1hYzk5LTdlYmYyMTNjYmM4MSIsInV0aSI6IlZTVW1pMUlnOFV5VE9KRlF5UE5JQUEiLCJ2ZXIiOiIxLjAiLCJ4bXNfaWRyZWwiOiIxMyAyIn0.JDanLa_t24tp0Lm_T_aQZNXrFUfEu7LgcZYy6_rXmHqtebIIL1uxWwiPKU9gMTAJNZAXjDhBO9WL12iH0rCcN2KsrLgR5hpGMNGUwJMOIAn4KWzhIFzHxr5BTXQaPDLPrfkE5GYmMOUTvSKQ1DVucP7pa4hVHFyXwV0tonlTjrHZqqYLm6EYm30MenMTY3qfer5IIRxDpgNgoy-zwC7-StkJ2zHBuN8VvugZlu4EkYwQDycAAdsrmSiNhsW9Cb463Nm87QYtuCU2VE53OjVqCvTcOnST9PsnXDVXW5Avo5wkiVvys2Ut9ioQsdCjouKmFDRp8A9ydsguNmei003oAQ"

# Dataset, Report, and Dashboard Names
DATASET_NAME = "Sales_Pipeline_Data"
REPORT_NAME = "Automated_Sales_Report"
DASHBOARD_NAME = "Automated_Sales_Dashboard"

# Step 1: Fetch Data from MySQL
def get_mysql_data():
    try:
        connection = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)
        df = pd.read_sql(MYSQL_QUERY, connection)
        connection.close()
        print("Data fetched from MySQL successfully.")
        return df
    except Exception as e:
        print(f"Error fetching data from MySQL: {e}")
        return None

# Step 2: Create a Power BI Dataset
import requests

def create_power_bi_dataset():
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/datasets"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    dataset_payload = {
        "name": DATASET_NAME,
        "defaultMode": "Push",
        "tables": [{
            "name": "SalesPipelineData",
            "columns": [
                {"name": "opportunity_id", "dataType": "String"},
                {"name": "sales_agent", "dataType": "String"},
                {"name": "product", "dataType": "String"},
                {"name": "account", "dataType": "String"},
                {"name": "deal_stage", "dataType": "String"},
                {"name": "engage_date", "dataType": "DateTime"},
                {"name": "close_date", "dataType": "DateTime"},
                {"name": "close_value", "dataType": "Double"}
            ]
        }]
    }
    
    response = requests.post(url, headers=headers, json=dataset_payload)
    
    if response.status_code == 201:
        print("Dataset created successfully!")
        return response.json().get("id")
    else:
        print(f"Error creating dataset: {response.text}")
        return None


# Step 3: Push Data to Power BI
def push_data_to_power_bi(df, dataset_id):
    url = f"https://api.powerbi.com/beta/{WORKSPACE_ID}/datasets/{dataset_id}/tables/SalesData/rows"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}
    data = {"rows": df.to_dict(orient="records")}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Data successfully pushed to Power BI!")
    else:
        print(f"Error pushing data: {response.text}")

# Step 4: Create Power BI Report
def create_power_bi_report(dataset_id):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {"name": REPORT_NAME, "datasetId": dataset_id}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print("Report created successfully!")
        return response.json().get("id")
    else:
        print(f"Error creating report: {response.text}")
        return None

# Step 5: Create Power BI Dashboard
def create_power_bi_dashboard():
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/dashboards"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {"name": DASHBOARD_NAME}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print("Dashboard created successfully!")
        return response.json().get("id")
    else:
        print(f"Error creating dashboard: {response.text}")
        return None

# Step 6: Add Visual to Power BI Dashboard
def add_tile_to_dashboard(dashboard_id, dataset_id):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/dashboards/{dashboard_id}/tiles"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {
        "datasetId": dataset_id,
        "visualizationType": "barChart",
        "title": "Revenue by Product",
        "dataMappings": {"X": "Product", "Y": "Revenue"}
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Tile added to dashboard successfully!")
    else:
        print(f"Error adding tile: {response.text}")

# Step 7: Trigger Dataset Refresh
def refresh_power_bi_dataset(dataset_id):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/datasets/{dataset_id}/refreshes"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.post(url, headers=headers)
    if response.status_code == 202:
        print("Power BI dataset refresh triggered successfully!")
    else:
        print(f"Error refreshing dataset: {response.text}")

# Run the Full Automation Process
if __name__ == "__main__":
    df = get_mysql_data()  # Step 1: Fetch Data

    if df is not None:
        dataset_id = create_power_bi_dataset()  # Step 2: Create Dataset
        if dataset_id:
            push_data_to_power_bi(df, dataset_id)  # Step 3: Push Data
            report_id = create_power_bi_report(dataset_id)  # Step 4: Create Report
            dashboard_id = create_power_bi_dashboard()  # Step 5: Create Dashboard

            if dashboard_id:
                add_tile_to_dashboard(dashboard_id, dataset_id)  # Step 6: Add Visual
                refresh_power_bi_dataset(dataset_id)  # Step 7: Refresh Dataset


import pymysql
import pandas as pd
import requests
import json

# MySQL Configuration
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DB = "accounts"
MYSQL_QUERY = "SELECT * FROM sales_pipeline_data"

# Power BI API Configuration
WORKSPACE_ID = "fc929ab3-ec9c-4de1-8117-52063a85b8a9"
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6ImltaTBZMnowZFlLeEJ0dEFxS19UdDVoWUJUayIsImtpZCI6ImltaTBZMnowZFlLeEJ0dEFxS19UdDVoWUJUayJ9.eyJhdWQiOiJodHRwczovL2FuYWx5c2lzLndpbmRvd3MubmV0L3Bvd2VyYmkvYXBpIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvZDFmMTQzNDgtZjFiNS00YTA5LWFjOTktN2ViZjIxM2NiYzgxLyIsImlhdCI6MTc0MDQxMjYxOSwibmJmIjoxNzQwNDEyNjE5LCJleHAiOjE3NDA0MTY1MTksImFpbyI6ImsyUmdZUGk1a3ExZTFXUEhFZTZtbjV1VVd6NHdBZ0E9IiwiYXBwaWQiOiIzMzJhZTI4MS02NTFlLTQ1MDItYmI1Ny1jZjI3YjYyMzI2NWMiLCJhcHBpZGFjciI6IjEiLCJpZHAiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9kMWYxNDM0OC1mMWI1LTRhMDktYWM5OS03ZWJmMjEzY2JjODEvIiwiaWR0eXAiOiJhcHAiLCJyaCI6IjEuQVQwQVNFUHgwYlh4Q1Vxc21YNl9JVHk4Z1FrQUFBQUFBQUFBd0FBQUFBQUFBQUE5QUFBOUFBLiIsInRpZCI6ImQxZjE0MzQ4LWYxYjUtNGEwOS1hYzk5LTdlYmYyMTNjYmM4MSIsInV0aSI6IlZTVW1pMUlnOFV5VE9KRlF5UE5JQUEiLCJ2ZXIiOiIxLjAiLCJ4bXNfaWRyZWwiOiIxMyAyIn0.JDanLa_t24tp0Lm_T_aQZNXrFUfEu7LgcZYy6_rXmHqtebIIL1uxWwiPKU9gMTAJNZAXjDhBO9WL12iH0rCcN2KsrLgR5hpGMNGUwJMOIAn4KWzhIFzHxr5BTXQaPDLPrfkE5GYmMOUTvSKQ1DVucP7pa4hVHFyXwV0tonlTjrHZqqYLm6EYm30MenMTY3qfer5IIRxDpgNgoy-zwC7-StkJ2zHBuN8VvugZlu4EkYwQDycAAdsrmSiNhsW9Cb463Nm87QYtuCU2VE53OjVqCvTcOnST9PsnXDVXW5Avo5wkiVvys2Ut9ioQsdCjouKmFDRp8A9ydsguNmei003oAQ"

# Dataset, Report, and Dashboard Names
DATASET_NAME = "Sales_Pipeline_Data"
REPORT_NAME = "Automated_Sales_Report"
DASHBOARD_NAME = "Automated_Sales_Dashboard"

# Step 1: Fetch Data from MySQL
def get_mysql_data():
    try:
        connection = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)
        df = pd.read_sql_query(MYSQL_QUERY, connection)
        connection.close()
        print("Data fetched from MySQL successfully.")
        return df
    except Exception as e:
        print(f"Error fetching data from MySQL: {e}")
        return None

# Step 2: Create a Power BI Dataset
def create_power_bi_dataset():
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/datasets"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    dataset_payload = {
        "name": DATASET_NAME,
        "defaultMode": "Push",
        "tables": [{
            "name": "SalesPipelineData",
            "columns": [
                {"name": "opportunity_id", "dataType": "String"},
                {"name": "sales_agent", "dataType": "String"},
                {"name": "product", "dataType": "String"},
                {"name": "account", "dataType": "String"},
                {"name": "deal_stage", "dataType": "String"},
                {"name": "engage_date", "dataType": "DateTime"},
                {"name": "close_date", "dataType": "DateTime"},
                {"name": "close_value", "dataType": "Double"}
            ]
        }]
    }
    
    response = requests.post(url, headers=headers, json=dataset_payload)
    
    if response.status_code == 201:
        print("Dataset created successfully!")
        return response.json().get("id")
    else:
        print(f"Error creating dataset: {response.text}")
        return None

# Step 3: Push Data to Power BI
def push_data_to_power_bi(df, dataset_id):
    url = f"https://api.powerbi.com/beta/{WORKSPACE_ID}/datasets/{dataset_id}/tables/SalesPipelineData/rows"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}
    data = {"rows": df.to_dict(orient="records")}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Data successfully pushed to Power BI.")
    else:
        print(f"Error pushing data: {response.text}")

# Step 4: Create Power BI Report
def create_power_bi_report(dataset_id):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {"name": REPORT_NAME, "datasetId": dataset_id}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print("Report created successfully.")
        return response.json().get("id")
    else:
        print(f"Error creating report: {response.text}")
        return None

# Step 5: Create Power BI Dashboard
def create_power_bi_dataset():
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/datasets"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    dataset_payload = {
        "name": DATASET_NAME,
        "defaultMode": "Push",
        "tables": [{
            "name": "SalesPipelineData",
            "columns": [
                {"name": "opportunity_id", "dataType": "String"},
                {"name": "sales_agent", "dataType": "String"},
                {"name": "product", "dataType": "String"},
                {"name": "account", "dataType": "String"},
                {"name": "deal_stage", "dataType": "String"},
                {"name": "engage_date", "dataType": "DateTime"},
                {"name": "close_date", "dataType": "DateTime"},
                {"name": "close_value", "dataType": "Double"}
            ]
        }]
    }
    
    response = requests.post(url, headers=headers, json=dataset_payload)
    
    if response.status_code == 201:
        print("Dataset created successfully!")
        return response.json().get("id")
    else:
        print(f"Error creating dataset: {response.status_code} - {response.text}")  # Print error details
        return None


# Step 6: Add Visual to Power BI Dashboard
def add_tile_to_dashboard(dashboard_id, dataset_id):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/dashboards/{dashboard_id}/tiles"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {
        "datasetId": dataset_id,
        "visualizationType": "barChart",
        "title": "Revenue by Product",
        "dataMappings": {"X": "product", "Y": "close_value"}
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Tile added to dashboard successfully.")
    else:
        print(f"Error adding tile: {response.text}")

# Step 7: Trigger Dataset Refresh
def refresh_power_bi_dataset(dataset_id):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/datasets/{dataset_id}/refreshes"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.post(url, headers=headers)
    if response.status_code == 202:
        print("Power BI dataset refresh triggered successfully.")
    else:
        print(f"Error refreshing dataset: {response.text}")

# Run the Full Automation Process
if __name__ == "__main__":
    df = get_mysql_data()  # Step 1: Fetch Data

    if df is not None:
        dataset_id = create_power_bi_dataset()  # Step 2: Create Dataset
        if dataset_id:
            push_data_to_power_bi(df, dataset_id)  # Step 3: Push Data
            report_id = create_power_bi_report(dataset_id)  # Step 4: Create Report
            dashboard_id = create_power_bi_dashboard()  # Step 5: Create Dashboard

            if dashboard_id:
                add_tile_to_dashboard(dashboard_id, dataset_id)  # Step 6: Add Visual
                refresh_power_bi_dataset(dataset_id)  # Step 7: Refresh Dataset

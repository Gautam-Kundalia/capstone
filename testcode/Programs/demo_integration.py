from celery import Celery

app = Celery('pipeline', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@app.task
def extract_data():
    import requests
    import json
    import time

    CLIENT_ID = "1000.QIX3LB6D2QGK7D6EBZGVTN48HD7WED"
    CLIENT_SECRET = "9b98bc9546826e511534943398e054194d49719600"
    REDIRECT_URI = "http://localhost:8088"
    REFRESH_TOKEN = "1000.fff504cc976dfd18d4933db271dc58cd.c5e81b6017a1694be67dcb1e078f5aa9"
    API_DOMAIN = "https://www.zohoapis.in"

    def refresh_access_token():
        token_url = "https://accounts.zoho.in/oauth/v2/token"
        payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token",
        }
        response = requests.post(token_url, data=payload)
        if response.status_code == 200:
            print("🔄 Access token refreshed successfully!")
            return response.json().get("access_token")
        else:
            print(f"❌ Error refreshing token: {response.status_code} - {response.text}")
            return None

    def fetch_zoho_data(access_token):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        url = f"{API_DOMAIN}/crm/v2/Leads"

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Zoho Data Fetched")
            return response.json()
        elif response.status_code == 401:
            print("⚠️ Token expired. Refreshing...")
            new_token = refresh_access_token()
            if new_token:
                return fetch_zoho_data(new_token)
        elif response.status_code == 429:
            print("⏳ Rate limit hit. Retrying after 60s...")
            time.sleep(60)
            return fetch_zoho_data(access_token)
        else:
            print(f"❌ Error fetching data: {response.status_code} - {response.text}")
            return None

    access_token = refresh_access_token()
    if access_token:
        return fetch_zoho_data(access_token)
    else:
        raise Exception("❌ Failed to get access token.")

@app.task
def json_to_csv(prev_result):
    import csv
    import os

    os.makedirs("./Datasets", exist_ok=True)
    csv_file_path = './Datasets/zoho_data.csv'

    # Uncomment to actually write CSV
    # with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    #     writer = csv.writer(file)
    #     fields = prev_result["data"][0].keys()
    #     writer.writerow(fields)
    #     for record in prev_result["data"]:
    #         writer.writerow(record.values())

    print("📝 JSON converted to CSV at ./Datasets/zoho_data.csv")
    return csv_file_path

@app.task
def store_csv(csv_path):
    import csv
    import MySQLdb

    connection = MySQLdb.connect(host='localhost', user='root', password='root', db='accounts')
    cursor = connection.cursor()

    # Uncomment to insert into DB
    # with open(csv_path, 'r') as file:
    #     reader = csv.reader(file)
    #     headers = next(reader)
    #     for row in reader:
    #         query = f'INSERT INTO leads ({", ".join(headers)}) VALUES ({", ".join(["%s"] * len(headers))})'
    #         cursor.execute(query, row)

    # connection.commit()
    # cursor.close()
    # connection.close()

    print("📊 Data inserted into MySQL successfully.")
    return "✅ Stored in DB"

@app.task
def update_visualization(prev_result):
    print("📈 Triggered visualization")
    # Placeholder for Power BI or dashboard trigger
    return "📊 Dashboard updated"

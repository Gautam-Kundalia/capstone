import requests
import json
import time

# Zoho CRM OAuth Credentials
CLIENT_ID = "1000.QIX3LB6D2QGK7D6EBZGVTN48HD7WED"
CLIENT_SECRET = "9b98bc9546826e511534943398e054194d49719600"
REDIRECT_URI = "http://localhost:8088"
REFRESH_TOKEN = "1000.fff504cc976dfd18d4933db271dc58cd.c5e81b6017a1694be67dcb1e078f5aa9"
API_DOMAIN = "https://www.zohoapis.in"

# Function to refresh access token
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
        new_access_token = response.json().get("access_token")
        print("Access token refreshed successfully!")
        return new_access_token
    else:
        print(f"Error refreshing access token: {response.status_code} - {response.text}")
        return None

# Function to fetch data from Zoho CRM
def fetch_zoho_data(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    url = f"{API_DOMAIN}/crm/v2/Leads"  # Change module if needed

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("Fetched Data:", json.dumps(data, indent=4))
        return data
    elif response.status_code == 401:
        print("Access token expired. Refreshing...")
        new_token = refresh_access_token()
        if new_token:
            return fetch_zoho_data(new_token)  # Retry with new token
    elif response.status_code == 429:
        print("Rate limit exceeded. Retrying in 60 seconds...")
        time.sleep(60)
        return fetch_zoho_data(access_token)
    else:
        print(f"Error fetching data: {response.status_code} - {response.text}")
        return None

# Main function to execute extraction
def main():
    access_token = refresh_access_token()
    if access_token:
        fetch_zoho_data(access_token)
    else:
        print("Failed to obtain access token. Exiting.")

if __name__ == "__main__":
    main()

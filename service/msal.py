import requests


def get_access_token(username, password):
    tenant_id = "b308f809-2724-407a-8152-5c50ccb03b1f"
    client_id = "3d5154df-e779-499f-bbb5-2143d9f5107a"
    client_secret = "D3A8Q~SCsngK~Vq3LBiX2Xaf-nH7rjlhHD-sZdhx"

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "username": username,
        "password": password,
        "grant_type": "password",
        "scope": "https://outlook.office365.com/.default",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=data, headers=headers)

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return access_token
    else:
        print(f"❌ Error obteniendo token: {response.status_code} - {response.text}")
        return None

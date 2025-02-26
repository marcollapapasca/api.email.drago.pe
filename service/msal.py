import requests
import msal

def get_access_token():
    TENANT_ID = "b308f809-2724-407a-8152-5c50ccb03b1f"
    CLIENT_ID = "3d5154df-e779-499f-bbb5-2143d9f5107a"
    CLIENT_SECRET = "s768Q~us6GVyqiA~MQGKZzg-tCPYh3GxSd2GuaFk"
    AUTHORITY_URL = f"https://login.microsoftonline.com/{TENANT_ID}"
    SCOPES = ["https://outlook.office365.com/.default"]

    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY_URL,
        client_credential=CLIENT_SECRET
    )


    result = None
    result = app.acquire_token_silent(SCOPES, account=None)

    if not result:
        print("No suitable token exists in cache. Let's get a new one from AAD.")
        result = app.acquire_token_for_client(SCOPES)

    if "access_token" in result:
        print("✅ Token obtenido correctamente:", result["access_token"][:20], "...")
        return result["access_token"]
    else:
        print("❌ Error al obtener el token:", result.get("error_description"))
        return None
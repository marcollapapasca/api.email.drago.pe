from msal import ConfidentialClientApplication
import requests
import json


class EmailServiceMsal:
    def __init__(self, tenant_id, client_id, client_secret, user_email):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_email = user_email
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.scopes = ["https://graph.microsoft.com/.default"]
        self.token = self.get_access_token()

    def get_access_token(self):
        """Obtiene un token de acceso usando MSAL."""

        app = ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
        token_response = app.acquire_token_for_client(scopes=self.scopes)

        if "access_token" in token_response:
            print(f"✅ Token exitoso {token_response}")
            return token_response["access_token"]
        else:
            raise Exception(f"Error obteniendo token: {token_response}")

    def get_accounts(self):
        headers = {"Authorization": f"Bearer {self.token}", "Content-type": "application/json"}
        response = requests.get(
            "https://graph.microsoft.com/v1.0/me", headers=headers
        )
        print(json.dumps(response.json(), indent=4))

    def get_inbox_messages(self):
        headers = {"Authorization": f"Bearer {self.token}", "ContentType": "application/json"}
        response = requests.get(
            f"https://graph.microsoft.com/v1.0/users/contacto@tumerka.pe/messages", headers=headers
        )
        print(json.dumps(response.json(), indent=4))
        return

        if response.status_code == 200:
            messages = response.json()["value"]
            for msg in messages:
                for msg in messages:
                    sender = (
                        msg.get("from", {})
                        .get("emailAddress", {})
                        .get("address", "Desconocido")
                    )
                    subject = msg.get("subject", "(Sin asunto)")
                    print(f"📩 De: {sender} | Asunto: {subject}")
        else:
            print(
                f"❌ Error obteniendo mensajes: {response.status_code} - {response.text}"
            )

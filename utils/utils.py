import os
import json

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def load_config(server_email, protocol, filename):
    config_path = os.path.join(base_path, "accounts", server_email, protocol, filename)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ La ruta de la cuenta no existe: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_html_template(template_path):
    config_path = os.path.join(base_path, "templates", template_path)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ La ruta de la plantilla no existe: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        return file.read()

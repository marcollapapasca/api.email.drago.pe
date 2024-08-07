 
from flask import Blueprint, request, jsonify, send_from_directory
from job_email.gmail import Gmail

main = Blueprint("main", __name__)

gmail = Gmail()

@main.route("/send_email", methods=["POST"])
def handle_send_email():
    data = request.json
    # config_path = 'config.json'
    config_path = data.get("config_smtp")
    config = gmail.load_config(config_path)
    to_address = data.get("to_address")
    print("to_address")
    print(to_address)

    event_type = data.get("event_type")
    if not to_address or not event_type:
        return jsonify({"error": "Error de validación"}), 400

    gmail.send_email(config, to_address, event_type, data)
    return jsonify({"message": "Email enviado satisfactoriamente"}), 200

@main.route("/")
def static_page_index():
    return 'Hola'
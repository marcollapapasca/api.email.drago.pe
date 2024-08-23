 
from flask import Blueprint, request, jsonify, send_from_directory
from job_email.gmail import Gmail

main = Blueprint("main", __name__)

gmail = Gmail()

@main.route("/send_email", methods=["POST"])
def handle_send_email():
    data = request.json
    # config_path = 'config.json'
    to_address = data.get("to_address")
    sku = data.get("sku")
    template_path = sku + ".html"
    config_smtp = sku.split('_')[0] +"_smtp.json"
    event_type = sku

    if not sku or not to_address:
        return jsonify({"error": "Error de validación"}), 400

    
    config = gmail.load_config(config_smtp)

    gmail.send_email(config, event_type, data, template_path)
    return jsonify({"message": "Email enviado satisfactoriamente"}), 200

@main.route("/")
def static_page_index():
    return 'Hola'
from flask import Blueprint, request, jsonify, send_from_directory 
from job_email.gmail import Gmail
from job_email.gmail_v2 import Gmail_v2
from flask import Flask, Response
import psycopg2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import json

main = Blueprint("main", __name__)

gmail = Gmail()
gmail_v2 = Gmail_v2()

@main.route("/send_email", methods=["POST"])
def handle_send_email():
    data = request.json
    print(data)
    # config_path = 'config.json'
    to_address = data.get("to_address")
    sku = data.get("sku")
    template_path = sku + ".html"
    config_smtp = sku.split('_')[0] + "_exchange_smtp.json"
    event_type = '_'.join(sku.split('_')[1:])
    print(event_type)

    if not sku or not to_address:
        return jsonify({"error": "Error de validación"}), 400

    
    config = gmail.load_config(config_smtp)

    gmail.send_email(config, event_type, data, template_path)
  
    return jsonify({"message": "Email enviado satisfactoriamente"}), 200


@main.route("/")
def static_page_index():
    return 'Holas'

# ===============================================
# Ruta de la API para enviar correos
@main.route("/send-email-stream", methods=["POST"])
def send_email():
    data = request.json
    config_smtp = data.get("smtp")
    try:
        config = gmail_v2.load_config(config_smtp)
        gmail_v2.send_email_massive_v1(config, data)
        
        return jsonify({"message": "Correo enviado y guardado correctamente"}), 200
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return jsonify({"error": "Error al enviar el correo"}), 500
 
# Detecta nuevos correos cada cierto tiempo y envía un mensaje SSE
def event_stream():
    last_checked_email_id = None

    while True:
        # Cargar la configuración para conectarse a Gmail
        config = gmail_v2.load_config("tumerka_exchange_smtp.json")  # Ruta al archivo de configuración SMTP
        
        # Leer los correos y obtener solo los no leídos
        new_emails = gmail_v2.read_emails(config)
        return 
        
        
        # Filtrar los correos no leídos y enviar notificación
        for email_data in new_emails:
            if not email_data.get("read_status", False):  # Solo correos no leídos
                email_info = {
                    "email_id": email_data["email_id"],
                    "subject": email_data["subject"],
                    "from": email_data["from"],
                    "received_at": email_data["received_at"]
                }
                yield f"data: {json.dumps(email_info)}\n\n"
                
        # Esperar unos segundos antes de la próxima verificación
        time.sleep(10)

@main.route('/stream')
def stream():
    return Response(event_stream(), mimetype="text/event-stream")


@main.route("/read-emails", methods=["POST"])
def read_emails():
    data = request.json
    config_path = data.get("smtp")  # Ruta al archivo de configuración
    try:
        config = gmail_v2.load_config(config_path)
        gmail_v2.read_emails(config)
        return jsonify({"message": "Correos leídos y guardados correctamente"}), 200
    except Exception as e:
        print(f"Error al leer correos: {e}")
        return jsonify({"error": "Error al leer correos"}), 500
    
@main.route("/get-emails", methods=["GET"])
def get_emails():
    sent_status = request.args.get("type", "sent")  # Por defecto es 'input'
    if sent_status not in ["sent", "received"]:
        return jsonify({"error": "Invalid email type. Must be 'sent' or 'received'."}), 400

    emails = gmail_v2.get_emails(sent_status)
    return jsonify(emails), 200

@main.route("/get-emails/<email_id>", methods=["GET"])
def get_email_by_id(email_id):
    emails = gmail_v2.get_email_by_id(email_id)
    if emails:
        return jsonify(emails), 200
    else:
        return jsonify({"error": "No emails found for the given id."}), 404
    
@main.route("/users", methods=["GET"])
def get_users():
    emails = gmail_v2.get_users()
    if emails:
        return jsonify(emails), 200
    else:
        return jsonify({"error": "No emails found for the given id."}), 404
    
@main.route("/groups", methods=["GET"])
def get_groups():
    groups = gmail_v2.get_groups()
    if groups:
        return jsonify(groups), 200
    else:
        return jsonify({"error": "No emails found for the given id."}), 404
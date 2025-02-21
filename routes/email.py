from flask import Blueprint, request, jsonify, Response
from utils.utils import load_config
from service.email import EmailService
from service.database.message import MessageService
import time
import json

email_router = Blueprint('email', __name__, url_prefix='/api')
email_service = EmailService()
message_service = MessageService()
# Ruta para enviar email mediante plantillas
@email_router.route("/send_email", methods=["POST"])
def send_email():
  data = request.json
  to_address = data.get("to_address")
  sku = data.get("sku")
  template_path = sku + ".html"
  config_smtp = sku.split('_')[0] + "_exchange_smtp.json"
  event_type = '_'.join(sku.split('_')[1:])
  print(event_type)

  if not sku or not to_address:
      return jsonify({"error": "Error de validación"}), 400

  
  config = load_config("outlook", "smtp", config_smtp)

  email_service.send_email(config, event_type, data, template_path)

  return jsonify({"message": "Email enviado satisfactoriamente"}), 200

# Ruta para enviar emails masivos
@email_router.route("/send-email-stream", methods=["POST"])
def send_email_stream():
  data = request.json
  config_smtp = data.get("smtp")
  try:
      config = load_config("outlook", "smtp", config_smtp)
      email_service.send_email_massive_v1(config, data)
      return jsonify({"message": "Correo enviado y guardado correctamente"}), 200
      
  except Exception as e:
      print(f"Error al enviar el correo: {e}")
      return jsonify({"error": "Error al enviar el correo"}), 500


def event_stream():
    while True:
        config = load_config("outlook", "smtp","drago_exchange_smtp.json")  # Ruta al archivo de configuración SMTP
        # Leer los correos y obtener solo los no leídos
        return
        new_emails = email_service.read_emails(config)
        
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
#ruta para el stream
@email_router.route('/stream')
def stream():
    return Response(event_stream(), mimetype="text/event-stream")

#ruta para leer emails
@email_router.route("/read-emails", methods=["POST"])
def read_emails():
  data = request.json
  config_path = data.get("smtp")  # Ruta al archivo de configuración
  try:
      config = load_config(config_path)
      email_service.read_emails(config)
      return jsonify({"message": "Correos leídos y guardados correctamente"}), 200
  except Exception as e:
      print(f"Error al leer correos: {e}")
      return jsonify({"error": "Error al leer correos"}), 500
    

#ruta para obtener emails
@email_router.route("/get-emails", methods=["GET"])
def emails():
  sent_status = request.args.get("type", "sent")  # Por defecto es 'input'
  if sent_status not in ["sent", "received"]:
      return jsonify({"error": "Invalid email type. Must be 'sent' or 'received'."}), 400

  emails = message_service.get_emails(sent_status)
  return jsonify(emails), 200

#ruta para obtener emails por id
@email_router.route("/get-emails/<email_id>", methods=["GET"])
def email_by_id(email_id):
  emails = message_service.get_email_by_id(email_id)
  if emails:
    return jsonify(emails), 200
  else:
    return jsonify({"error": "No emails found for the given id."}), 404

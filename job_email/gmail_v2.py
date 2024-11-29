import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
import base64
import os
import imaplib
import email
import time
from email.header import decode_header
from datetime import datetime


from database.save_email_v2 import EmailService 
class Gmail_v2:

    def __init__(self):
        self.email_service = EmailService()

    def load_config(self, config_path):
        with open(os.path.join(os.path.dirname(__file__),  config_path), "r") as file:
            return json.load(file)
        
    def send_email(self, config , data):

        # Configuración de credenciales de correo
        SMTP_SERVER = config["GMAIL_HOST"]
        SMTP_PORT = config["GMAIL_PORT"]
        SENDER_EMAIL = config["GMAIL_USER"]
        SENDER_PASSWORD = config["GMAIL_PASS"]
 
        to_email = data.get("to_address", [])
        subject = data.get("subject")
        body_html = data.get("body")
        body_text = None
        attachments = data.get("attachments", [])  # Lista de adjuntos como diccionarios

        if not to_email:
            return jsonify({"error": "No se especificaron destinatarios"}), 400
        # Guardar o actualizar el usuario del remitente
        # sender_email = SENDER_EMAIL  # Asumimos que el remitente es el mismo que se configura para SMTP
        sender_user_id = self.email_service.guardar_usuario(SENDER_EMAIL, "Remitente")
        
        # Crear y enviar el correo
        message = MIMEMultipart("alternative")
        message["From"] = config["FROM_ADDRESS"]
        message["To"] = ", ".join(to_email)
        #message["Bcc"] = config["BCC_ADDRESS"]

        # message["From"] = sender_email
        # message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body_html, "html"))

        for attachment in attachments:
            filename = attachment['filename']
            file_type = attachment['file_type']
            file_data = base64.b64decode(attachment['file_data'])
            
            # Añadir el archivo al correo
            part = MIMEText(file_data, 'base64')
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            message.attach(part)
        
        try:
            print(message)
            server = smtplib.SMTP(host=config["GMAIL_HOST"], port=config["GMAIL_PORT"], timeout=60)
            server.starttls()
            server.login(config["GMAIL_USER"], config["GMAIL_PASS"])
            server.send_message(message)
 
            # Guardar el correo en la base de datos
            sent_at = datetime.now()  # Fecha y hora actual al enviar el correo
            received_at= None
            email_id = self.email_service.guardar_correo(sender_user_id, subject, body_text, body_html, SENDER_EMAIL, False, "sent", "sent", received_at, sent_at)
            if email_id is None:
                return jsonify({"error": "No se pudo guardar el correo"}), 500
            
            # Guardar destinatarios
            destinatarios = [{"email": email, "type": "to"} for email in to_email]
            self.email_service.guardar_destinatarios(email_id, destinatarios)
            # self.email_service.guardar_destinatarios(email_id, [{"email": to_email, "type": "to"}])
            
            # Guardar adjuntos
            self.email_service.guardar_adjuntos(email_id, attachments)
            
            return jsonify({"message": "Correo enviado y guardado correctamente"}), 200
        except   smtplib.SMTPServerDisconnected as e:
            print(f"Error al enviar el correo: {e}")
            return jsonify({"error": "Error al enviar el correo"}), 500
        
    def send_email_massive(self, config , data):
        # Configuración de credenciales de correo
        SMTP_SERVER = config["GMAIL_HOST"]
        SMTP_PORT = config["GMAIL_PORT"]
        SENDER_EMAIL = config["GMAIL_USER"]
        SENDER_PASSWORD = config["GMAIL_PASS"]
 
        to_email = data.get("to_address", [])
        subject = data.get("subject")
        body_html = data.get("body")
        groups = data.get("groups", [])
        body_text = None
        attachments = data.get("attachments", [])  # Lista de adjuntos como diccionarios
        
        recipients_email = self.email_service.get_emails_by_groups(groups if groups else None)
        # si el destino dice que ers tú agradecido por haberte puesto en mi camino
        emails_users = [user['email'] for user in recipients_email]
        combined_emails = list(set(to_email + emails_users))
        print(combined_emails)

        if not combined_emails:
            return jsonify({"error": "No se especificaron destinatarios"}), 400
        # Guardar o actualizar el usuario del remitente
        # sender_email = SENDER_EMAIL  # Asumimos que el remitente es el mismo que se configura para SMTP
        # sender_user_id = self.email_service.guardar_usuario(SENDER_EMAIL, "Remitente")
 
        for email_user in combined_emails:
            sender_user_id = self.email_service.guardar_usuario(email_user, "")
            # Crear y enviar el correo
            message = MIMEMultipart("alternative")
            message["From"] = config["FROM_ADDRESS"]
            message["To"] = email_user
            # message["Bcc"] = config["BCC_ADDRESS"]
            # message["From"] = sender_email
            # message["To"] = to_email
            message["Subject"] = subject
            message.attach(MIMEText(body_html, "html"))

            for attachment in attachments:
                filename = attachment['filename']
                file_type = attachment['file_type']
                file_data = base64.b64decode(attachment['file_data'])
                
                # Añadir el archivo al correo
                part = MIMEText(file_data, 'base64')
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                message.attach(part)
            
            try:   
                server = smtplib.SMTP(host=config["GMAIL_HOST"], port=config["GMAIL_PORT"], timeout=60)
                server.starttls()
                server.login(config["GMAIL_USER"], config["GMAIL_PASS"])
                server.send_message(message)
                print("Correo enviado y guardado correctamente")
                # return jsonify({"message": "Correo enviado y guardado correctamente"}), 200
            except smtplib.SMTPServerDisconnected as e:
                print(f"Error al enviar el correo: {e}")
                #return jsonify({"error": "Error al enviar el correo"}), 500

            # Guardar el correo en la base de datos
            sent_at = datetime.now()  # Fecha y hora actual al enviar el correo
            received_at= None
            email_id = self.email_service.guardar_correo(sender_user_id, subject, body_text, body_html, SENDER_EMAIL, False, "sent", "sent", received_at, sent_at)
            
            if email_id is None:
                return jsonify({"error": "No se pudo guardar el correo"}), 500
            
            #actualizar el usuario
            self.email_service.update_send_status_user(sender_user_id)
            # Guardar destinatarios
            self.email_service.guardar_destinatarios(email_id, [{"email": email_user, "type": "to"}])
            
            # Guardar adjuntos
            self.email_service.guardar_adjuntos(email_id, attachments)

            time.sleep(3)

        print("Todos los correos fueron enviados")
        return jsonify({"message": "Correo enviado y guardado correctamente"}), 200
        

    # Método para leer correos no leídos de Gmail
    def read_emails(self, config):
            username = config["GMAIL_USER"]
            password = config["GMAIL_PASS"]

            # Conectar con el servidor de Gmail usando IMAP
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(username, password)

            # Seleccionar la bandeja de entrada
            mail.select("inbox")

            # Buscar correos no leídos
            status, messages = mail.search(None, 'UNSEEN')
            mail_ids = messages[0].split()

            new_emails = []

            # Procesar cada correo no leído
            for mail_id in mail_ids:
                status, msg_data = mail.fetch(mail_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        # Decodificar el mensaje
                        msg = email.message_from_bytes(response_part[1])

                        # Obtener el remitente y el asunto
                        from_email = email.utils.parseaddr(msg.get("From"))[1]
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else 'utf-8')

                        # Guardar el usuario en la base de datos
                        user_id = self.email_service.guardar_usuario(from_email, None)

                        # Procesar el cuerpo del mensaje y los adjuntos
                        body_text = None
                        body_html = None
                        attachments = []

                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))

                                # Si es el cuerpo del mensaje en texto plano
                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    body_text = part.get_payload(decode=True).decode()
                                # Si es el cuerpo del mensaje en HTML
                                elif content_type == "text/html" and "attachment" not in content_disposition:
                                    body_html = part.get_payload(decode=True).decode()
                                # Si es un adjunto
                                elif "attachment" in content_disposition:
                                    filename = part.get_filename()
                                    if filename:
                                        file_data = part.get_payload(decode=True)
                                        attachments.append({
                                            "filename": filename,
                                            "file_type": content_type,
                                            "file_data": base64.b64encode(file_data).decode("utf-8")
                                        })
                        else:
                            # Si el mensaje no es multipart, obtener el cuerpo en texto plano o HTML
                            if msg.get_content_type() == "text/plain":
                                body_text = msg.get_payload(decode=True).decode()
                            elif msg.get_content_type() == "text/html":
                                body_html = msg.get_payload(decode=True).decode()

                        # Guardar el correo y los detalles en la base de datos
                        received_at = datetime.now()  # Fecha y hora actual al recibir el correo
                        sent_at = None

                        email_id = self.email_service.guardar_correo(
                            user_id, subject, body_text, body_html, from_email, True, "unread", "received", received_at, sent_at
                        )
                        self.email_service.guardar_destinatarios(email_id, [{"email": from_email, "type": "from"}])
                        self.email_service.guardar_adjuntos(email_id, attachments)

                        # Añadir el correo a la lista de nuevos correos
                        new_emails.append({
                            "email_id": email_id,
                            "subject": subject,
                            "from": from_email,
                            "received_at": received_at.strftime('%Y-%m-%d %H:%M:%S')
                        })

            # Cerrar la conexión con el servidor de Gmail
            mail.logout()

            return new_emails
            

    def get_emails(self, sent_status):
        return self.email_service.get_emails(sent_status)
    
    def get_email_by_id(self, email_id):
        return self.email_service.get_email_by_id(email_id)
    
    def get_users(self):
        return self.email_service.get_users()
    
    def get_groups(self):
        return self.email_service.get_groups()
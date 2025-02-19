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
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests


from database.save_email_v2 import EmailService 
class Gmail_v2:

    def __init__(self):
        self.email_service = EmailService()

    def load_config(self, config_path):
        with open(os.path.join(os.path.dirname(__file__),  config_path), "r") as file:
            return json.load(file)
        
    def send_email(self, config , data):

        # Configuración de credenciales de correo
        SMTP_SERVER = config["OUTLOOK_HOST"]
        SMTP_PORT = config["OUTLOOK_PORT"]
        SENDER_EMAIL = config["OUTLOOK_USER"]
        SENDER_PASSWORD = config["OUTLOOK_PASS"]
 
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
        message.attach(MIMEText(body_html, "html", "utf-8"))

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
            server = smtplib.SMTP(host=config["OUTLOOK_HOST"], port=config["OUTLOOK_PORT"], timeout=60)
            server.starttls()
            server.login(config["OUTLOOK_USER"], config["OUTLOOK_PASS"])
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
        
    def send_email_massive_v1(self, config , data):
        # Configuración de credenciales de correo
        SMTP_SERVER = config["OUTLOOK_HOST"]
        SMTP_PORT = config["OUTLOOK_PORT"]
        SENDER_EMAIL = config["OUTLOOK_USER"]
        SENDER_PASSWORD = config["OUTLOOK_PASS"]
 
        to_email = data.get("to_address", [])
        subject = data.get("subject")
        body_html = data.get("body")
        groups = data.get("groups", [])
        body_text = None
        attachments = data.get("attachments", [])  # Lista de adjuntos como diccionarios
        
        recipients_email = self.email_service.get_emails_by_groups(groups if groups else None)
        emails_users = [user['email'] for user in recipients_email]
        combined_emails = list(set(to_email + emails_users))
        if not combined_emails:
            return jsonify({"error": "No se especificaron destinatarios"}), 400
        # Guardar o actualizar el usuario del remitente
        # sender_email = SENDER_EMAIL  # Asumimos que el remitente es el mismo que se configura para SMTP
        # sender_user_id = self.email_service.guardar_usuario(SENDER_EMAIL, "Remitente")
        body_html = body_html.replace("\n", "<br>")
        body_html += """
        <br> 
                <span>Nos puede contactar a</span>
<table>
  <tr>
    <td>1️⃣ Marco Llapapasca</td>
    <td><a style="text-decoration: none" href="https://wa.me/51923367852">📱(+51) 973 777 853</a></td>
  </tr>
  <tr>
    <td>2️⃣ Katherine Díaz</td>
    <td><a style="text-decoration: none" href="https://wa.me/51923367852" target="_blank">📱(+51) 923 367 852</a></td>
  </tr>
  <tr>
    <td>3️⃣ Denisse Ruíz</td>
    <td><a style="text-decoration: none" href="https://wa.me/51960370846" target="_blank">📱(+51) 960 370 846</a></td>
  </tr>
  <tr>
    <td>4️⃣ Omar Prado</td>
    <td><a style="text-decoration: none" href="https://wa.me/51948845033" target="_blank">📱(+51) 948 845 033</a></td>
  </tr>
</table>
<table
  style="font-family: Arial, sans-serif; font-size: 12px; color: #000; width: 100%; max-width: 500px; padding: 0; margin: 0">

  <tr>
    <td>
      <a href="https://drago.pe" style="text-decoration: none; color: black; font-size: 20px;">
        <strong>DRAGO</strong>
      </a>
    </td>
    <td style="padding-left: 10px;  border-left: 2px solid #008000;">
      <table>
        <tr>
          <td><strong>CORPORACIÓN GRUPO DRAGO S.A.C</strong></td>
        </tr>
        <tr>
          <td>RUC: 20608386387 </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
                """

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
            message.attach(MIMEText(body_html, "html", "utf-8"))

            for attachment in attachments:
                filename = attachment['filename']
                file_type = attachment['file_type']
                file_data = base64.b64decode(attachment['file_data'])
                
                # Añadir el archivo al correo
                part = MIMEText(file_data, 'base64')
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                message.attach(part)
            
            try:
                access_token = Gmail_v2.get_access_token()
                auth_string = f"user={config['OUTLOOK_USER']}\x01auth=Bearer {access_token}\x01\x01"
                auth_b64 = base64.b64encode(auth_string.encode()).decode()

                server = smtplib.SMTP(host="smtp-mail.outlook.com", port=587)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.docmd("AUTH", "XOAUTH2 " + auth_b64)
                time.sleep(2)
                server.send_message(message)
                print(f"✅ Correo enviado y guardado correctamente {email_user}")
                # return jsonify({"message": "Correo enviado y guardado correctamente"}), 200
            except smtplib.SMTPServerDisconnected as e:
                print(f"❌ Error al enviar el correo: {e}")
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

        print("🟩 Todos los correos fueron enviados") 
        return jsonify({"message": "Correo enviado y guardado correctamente"}), 200
        
    def send_email_massive(self, config, data):
        """Función principal para enviar correos masivos."""
        # Extraer datos de entrada
        to_email = data.get("to_address", [])
        subject = data.get("subject")
        body_html = data.get("body")
        groups = data.get("groups", [])
        attachments = data.get("attachments", [])

        # Obtener correos combinados
        recipients_email = self.email_service.get_emails_by_groups(groups if groups else None)
        emails_users = [user['email'] for user in recipients_email]
        combined_emails = list(set(to_email + emails_users))

        if not combined_emails:
            return {"error": "No se especificaron destinatarios"}

        print(f"Enviando correos a {len(combined_emails)} destinatarios...")

        # Función interna para enviar un correo individual
        def send_email(recipient):
            try:
                # Guardar usuario
                sender_user_id = self.email_service.guardar_usuario(recipient, "")

                # Crear el mensaje
                message = MIMEMultipart("alternative")
                message["From"] = config["FROM_ADDRESS"]
                message["To"] = recipient
                message["Subject"] = subject
                message.attach(MIMEText(body_html, "html", "utf-8"))

                # Adjuntar archivos
                for attachment in attachments:
                    filename = attachment['filename']
                    file_data = base64.b64decode(attachment['file_data'])
                    part = MIMEText(file_data, 'base64')
                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    message.attach(part)

                # Enviar el correo
                server = smtplib.SMTP(host=config["OUTLOOK_HOST"], port=config["OUTLOOK_PORT"], timeout=60)
                server.starttls()
                server.login(config["OUTLOOK_USER"], config["OUTLOOK_PASS"])
                server.send_message(message)
                server.quit()

                # Guardar correo
                email_id = self.email_service.guardar_correo(
                    sender_user_id, subject, None, body_html, config["FROM_ADDRESS"], False, "sent", "sent",
                    None, datetime.now()
                )

                # Actualizar estado del usuario
                self.email_service.update_send_status_user(sender_user_id)

                # Guardar destinatarios y adjuntos
                self.email_service.guardar_destinatarios(email_id, [{"email": recipient, "type": "to"}])
                self.email_service.guardar_adjuntos(email_id, attachments)

                print(f"Correo enviado correctamente a: {recipient}")
                return {"recipient": recipient, "status": "success"}
            except Exception as e:
                print(f"Error al enviar correo a {recipient}: {e}")
                return {"recipient": recipient, "status": "failed", "error": str(e)}

        # Enviar correos en paralelo
        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(send_email, email): email for email in combined_emails}
            for future in as_completed(futures):
                results.append(future.result())

        print("Todos los correos fueron procesados.")
        return results

    def get_access_token():
        tenant_id = "b308f809-2724-407a-8152-5c50ccb03b1f"
        client_id = "3d5154df-e779-499f-bbb5-2143d9f5107a"
        client_secret = "D3A8Q~SCsngK~Vq3LBiX2Xaf-nH7rjlhHD-sZdhx"

        url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "username": "contacto@drago.pe",
            "password": "Peru123...",
            "grant_type": "password",
            "scope": "https://outlook.office365.com/.default",
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post(url, data=data, headers=headers)

        if response.status_code == 200:
            access_token = response.json().get("access_token")
            return access_token
        else:
            print(
                f"❌ Error obteniendo token: {response.status_code} - {response.text}"
            )
            return None
        
    # Método para leer correos no leídos de Gmail
    def read_emails(self, config):
            # Gmail_v2.authorize_outlook()
            # return 
            access_token = Gmail_v2.get_access_token()
            

            # headers = {"Authorization": f"Bearer {access_token}"}
            # url = "https://graph.microsoft.com/v1.0/me/messages"

            # response = requests.get(url, headers=headers)
            # print(response.json())
            # return


            

            auth_string = f"user={config['OUTLOOK_USER']}\x01auth=Bearer {access_token}\x01\x01"
            auth_b64 = base64.b64encode(auth_string.encode()).decode()
            server = imaplib.IMAP4_SSL(host="outlook.office365.com")
            server.debug = 4
            response = server.authenticate("XOAUTH2", lambda x: auth_b64)
            print("Autenticación exitosa:", response)
            # status_code, response = server.ehlo()
            # print(f"[*] Echoing the server: {status_code} {response}")
            # status_code, response = server.starttls()
            # print(f"[*] Starting TLS the server: {status_code} {response}")
            # status_code, response = server.starttls()
            # print(f"[*] Echoing the server: {status_code} {response}")

            # print(auth_string)
            # Conectar con el servidor de Gmail usando IMAP
            # mail = imaplib.IMAP4_SSL(host=config["OUTLOOK_HOST"])
            # mail.authenticate("XOAUTH2", lambda x: auth_string)
            # mail = imaplib.IMAP4_SSL(config["OUTLOOK_HOST"])

            # status_code, response = mail.ehlo()
            # print(f"[*] Echoing the server: {status_code} {response}")

            # print(f"{mail}")
            # return
            # status_code, response = mail.starttls()
            # print(f"[*] Startin TLS the server: {status_code} {response}")

            # return
            # status_code, response = mail.ehlo()
            # print(f"[*] Echoing the server: {status_code} {response}")

            # Enviar la autenticación XOAUTH2 manualmente
            # result, _ = mail.authenticate("XOAUTH2", lambda x: auth_b64)

            # if result != "OK":
            #     print("Autenticación fallida")
            # else:
            #     print("✅ Autenticación exitosa con OAuth 2.0")

            # Seleccionar la bandeja de entrada
            server.select("inbox")
            # Aquí puedes continuar con la lógica para leer correos...

            # No olvides cerrar la conexión al final
            # status_code, response = mail.login(username, password)
            # print(f"[*] Login  the server: {status_code} {response}")
            # print("✅ Autenticación exitosa con OAuth 2.0")
             
            # mail.docmd("AUTH", "XOAUTH2 " + auth_string)

            # mail.login(username, password)

            # Seleccionar la bandeja de entrada
            server.select("inbox")

            # Buscar correos no leídos
            status, messages = server.search(None, 'UNSEEN')
            mail_ids = messages[0].split()

            new_emails = []

            # Procesar cada correo no leído
            for mail_id in mail_ids:
                status, msg_data = server.fetch(mail_id, '(RFC822)')
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
            server.logout()

            return new_emails
            

    def get_emails(self, sent_status):
        return self.email_service.get_emails(sent_status)
    
    def get_email_by_id(self, email_id):
        return self.email_service.get_email_by_id(email_id)
    
    def get_users(self):
        return self.email_service.get_users()
    
    def get_groups(self):
        return self.email_service.get_groups()
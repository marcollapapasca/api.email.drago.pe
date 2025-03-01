from service.database.message import MessageService
from service.database.user import UserService
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.header import decode_header
from flask import jsonify
from datetime import datetime
from utils.utils import load_html_template
from service.msal import get_access_token
from signature import signatureGlobal, signatureOther
import smtplib
import imaplib
import base64
import time
import email
import random


class EmailService:
    def __init__(self):
        self.message_service = MessageService()
        self.user_service = UserService()

    def send_email(self, config, event_type, data, template_path):
        msg = MIMEMultipart()
        msg["From"] = config["FROM_ADDRESS"]
        msg["To"] = data.get("to_address")
        to_email = data.get("to_address")
        SENDER_EMAIL = config["OUTLOOK_USER"]
        template_html = load_html_template(template_path)
        body_html = None
        body_text = None
        if event_type == "welcome_new_user":
            msg["Subject"] = "¡Bienvenido a tumerka.pe!"
            username = data.get("username", "Nuevo Usuario")
            body_html = template_html.replace("{{username}}", username)
            msg.attach(MIMEText(body_html, "html"))
        elif event_type == "welcome_new_member":
            msg["Subject"] = "¡Bienvenido al Marketplace tumerka.pe!"
            username = data.get("username", "Nuevo Usuario")
            body_html = template_html.replace("{{username}}", username)
            msg.attach(MIMEText(body_html, "html"))
        elif event_type == "welcome_new_seller":
            seller_name = data.get("seller_name", "Seller")

            msg["Subject"] = "Hemos recibido tu solicitud"

            service_type = data.get("service_type", "")

            body_html = template_html.replace("{{seller_name}}", seller_name)
            body_html = body_html.replace("{{service_type}}", service_type)

            msg.attach(MIMEText(body_html, "html"))
        elif event_type == "welcome_new_seller_approved":
            seller_name = data.get("seller_name", "Seller")

            msg["Subject"] = "Bienvenido a TuMerka, " + seller_name

            service_type = data.get("service_type", "")
            store_url = data.get("store_url", "")
            email = data.get("email", "")

            body_html = template_html.replace("{{seller_name}}", seller_name)
            body_html = body_html.replace("{{service_type}}", service_type)
            body_html = body_html.replace("{{store_url}}", store_url)
            body_html = body_html.replace("{{email}}", email)

            msg.attach(MIMEText(body_html, "html"))
        elif event_type == "welcome_new_subscription":
            msg["Subject"] = "¡Gracias por suscribirte!"
            body_html = template_html
            msg.attach(MIMEText(body_html, "html"))
        elif event_type == "new_invoice":
            msg["Subject"] = "Su comprobante está disponible"
            customer_name = data.get("customer_name", "Cliente")
            document_number = data.get("document_number", "Documento")
            amount = data.get("amount", "0.00")
            issue_date = data.get("issue_date", "Fecha")
            attachment_path = data.get("attachment_path", "adjunto.pdf")

            body_html = template_html.replace("{{customer_name}}", customer_name)
            body_html = body_html.replace("{{document_number}}", document_number)
            body_html = body_html.replace("{{amount}}", amount)
            body_html = body_html.replace("{{issue_date}}", issue_date)

            msg.attach(MIMEText(body_html, "html"))

            try:
                with open(attachment_path, "rb") as attachment_file:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment_file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {attachment_path.split('/')[-1]}",
                    )
                    msg.attach(part)
            except FileNotFoundError:
                print(f"Error: El archivo {attachment_path} no se encontró.")
                return {"error": "Attachment file not found"}, 400
        elif event_type == "new_order":
            msg["Subject"] = "Confirmación de tu pedido"

            customer_name = data.get("customer_name", "Cliente")
            order_number = data.get("order_number", "")
            document_type_name = data.get("document_type_name", "")
            document_number = data.get("document_number", "")
            delivery_address = data.get("delivery_address", "")

            order_items = data.get("order_items", [])

            shipping_cost = data.get("shipping_cost", "0.00")
            total_amount = data.get("total_amount", "0.00")

            order_items_html = ""
            for item in order_items:
                order_items_html += f"<tr><td>{item['sku']}</td><td>{item['product_name']}</td><td>{item['quantity']}</td><td>{item['price_unit']}</td><td>{item['price_total']}</td></tr>"

            body_html = template_html.replace("{{customer_name}}", customer_name)
            body_html = body_html.replace("{{document_type_name}}", document_type_name)
            body_html = body_html.replace("{{document_number}}", document_number)
            body_html = body_html.replace("{{delivery_address}}", delivery_address)

            body_html = body_html.replace("{{order_number}}", order_number)
            body_html = body_html.replace("{{order_items}}", order_items_html)
            body_html = body_html.replace("{{shipping_cost}}", shipping_cost)
            body_html = body_html.replace("{{total_amount}}", total_amount)

            msg.attach(MIMEText(body_html, "html"))
        elif event_type == "new_order_seller":
            msg["Subject"] = "Tienes un nuevo pedido"

            order_number = data.get("order_number", "-")
            seller_name = data.get("seller_name", "-")
            document_type_name = data.get("document_type_name", "")
            document_number = data.get("document_number", "")
            customer_name = data.get("customer_name", "")
            delivery_address = data.get("delivery_address", "")

            order_items = data.get("order_items", [])

            # total_amount = data.get("total_amount", "0.00")
            total_amount = 0.00
            # Construye la tabla HTML para order_items
            order_items_html = ""
            for item in order_items:
                order_items_html += f"<tr><td>{item['sku']}</td><td>{item['product_name']}</td><td>{item['quantity']}</td><td>{item['price_unit']}</td><td>{item['price_total']}</td></tr>"
                price_total_str = str(item["price_total"]).replace(",", ".")
                total_amount += float(price_total_str)

            body_html = template_html.replace("{{order_number}}", order_number)
            body_html = body_html.replace("{{seller_name}}", seller_name)
            body_html = body_html.replace("{{document_type_name}}", document_type_name)
            body_html = body_html.replace("{{document_number}}", document_number)
            body_html = body_html.replace("{{customer_name}}", customer_name)
            body_html = body_html.replace("{{delivery_address}}", delivery_address)
            body_html = body_html.replace("{{order_items}}", order_items_html)
            body_html = body_html.replace("{{total_amount}}", str(total_amount))
            msg.attach(MIMEText(body_html, "html"))
        elif event_type == "password_change":
            msg["Subject"] = "Solicitud de Cambio de Contraseña"

            customer_name = data.get("customer_name", "Cliente")
            reset_link = data.get(
                "reset_link", "https://tumerka.pe/auth/reset-password"
            )

            body_html = template_html.replace("{{username}}", customer_name)
            body_html = body_html.replace("{{reset_link}}", reset_link)
            msg.attach(MIMEText(body_html, "html"))
        elif event_type == "password_change_confirmation":
            msg["Subject"] = "Confirmación de Cambio de Contraseña"

            customer_name = data.get("customer_name", "Cliente")

            body_html = template_html.replace("{{username}}", customer_name)
            msg.attach(MIMEText(body_html, "html"))
        elif event_type == "publicidad_1":
            msg["Subject"] = "Publicidad 1"

            customer_name = data.get("", "")
            image_paths = data.get("image_paths", {})
            links = data.get("links", {})

            body_html = template_html.replace("{{username}}", customer_name)
            for key, value in links.items():
                body_html = body_html.replace(f"{{{{{key}}}}}", value)
            for key, value in image_paths.items():
                body_html = body_html.replace(f"{{{{{key}}}}}", value)

            msg.attach(MIMEText(body_html, "html"))
        elif event_type == "seller_accept_contract":
            seller_name = data.get("seller_name", "Seller")
            msg["Subject"] = "¡Contrato Aceptado!"

            body_html = template_html.replace("{{seller_name}}", seller_name)

            msg.attach(MIMEText(body_html, "html"))
        elif event_type == "welcome_user":
            msg["Subject"] = "¡Bienvenido a aula360!"
            username = data.get("username", "Usuario")
            body_html = template_html.replace("{{username}}", username)
            msg.attach(MIMEText(body_html, "html", "utf-8"))
        elif event_type == "recharge_balance":
            msg["Subject"] = (
                "📢 Pago confirmado: Verifica los detalles de tu transacción"
            )
            reference_id = data.get("id", "reference_id")
            amount = data.get("amount", "amount")
            date = data.get("date", "Fecha")
            body_html = template_html.replace("{{id}}", reference_id)
            body_html = body_html.replace("{{amount}}", f"{amount:.2f}")
            body_html = body_html.replace("{{date}}", date)
            msg.attach(MIMEText(body_html, "html", "utf-8"))
        else:
            print("Unknown event type")

        message_send = None
        try:
            access_token = get_access_token()
            if not access_token:
                return

            auth_string = (
                f"user={config['OUTLOOK_USER']}\x01auth=Bearer {access_token}\x01\x01"
            )
            auth_b64 = base64.b64encode(auth_string.encode()).decode()

            server = smtplib.SMTP(host="smtp-mail.outlook.com", port=587)
            status_code, response = server.ehlo()
            status_code, response = server.starttls()
            # status_code, response = server.ehlo()
            status_code, response = server.login(
                config["OUTLOOK_USER"], config["OUTLOOK_PASS"]
            )

            #     server = smtplib.SMTP(host=config["GMAIL_HOST"], port=config["GMAIL_PORT"])
            #     server.starttls()
            #     server.login(config ["GMAIL_USER"], config["GMAIL_PASS"])
            server.send_message(msg)
            sent_at = datetime.now()  # Fecha y hora actual al enviar el correo
            received_at = None
            subject = msg["Subject"]
            sender_user_id = self.user_service.guardar_usuario(
                SENDER_EMAIL, "Remitente"
            )
            email_id = self.message_service.guardar_correo(
                sender_user_id,
                subject,
                body_text,
                body_html,
                SENDER_EMAIL,
                False,
                "sent",
                "sent",
                received_at,
                sent_at,
            )
            self.user_service.guardar_destinatarios(
                email_id, [{"email": to_email, "type": "to"}]
            )

            message_send = "Correo enviado exitosamente"
            print(message_send)
        except Exception as e:
            message_send = "Error al enviar el correo: {e}"
            print(message_send)
        finally:
            server.quit()

    def send_email_massive_v1(self, config, data):
        MAX_CORREOS_POR_CONEXION = 29
        try:
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
            attachments = data.get(
                "attachments", []
            )  # Lista de adjuntos como diccionarios

            recipients_email = self.message_service.get_emails_by_groups(
                groups if groups else None
            )
            emails_users = [user["email"] for user in recipients_email]
            combined_emails = list(set(to_email + emails_users))
            if not combined_emails:
                return jsonify({"error": "No se especificaron destinatarios"}), 400
            print(combined_emails)
            
            if "</body>" in body_html:
                body_html = body_html.replace("</body>", f"{signatureOther}</body>")
            else:
                body_html = body_html.replace("\n", "<br>")
                body_html += signatureGlobal  # En caso de que no haya </body>, se agrega al final

            for i, email_user in enumerate(combined_emails, start=1):
                if i % MAX_CORREOS_POR_CONEXION == 1:
                    server = smtplib.SMTP(host="smtp-mail.outlook.com", port=587)
                    server.ehlo()
                    server.starttls()
                    data = server.login(SENDER_EMAIL, SENDER_PASSWORD)
                    print(data)
                    print("✅ Nueva conexión SMTP establecida.")
                try:
                    sender_user_id = self.user_service.guardar_usuario(email_user, "")
                    # Crear y enviar el correo
                    message = MIMEMultipart("alternative")
                    message["From"] = config["FROM_ADDRESS"]
                    message["To"] = email_user
                    message["Subject"] = subject
                    message.attach(MIMEText(body_html, "html", "utf-8"))

                    for attachment in attachments:
                        filename = attachment["filename"]
                        file_type = attachment["file_type"]
                        file_data = base64.b64decode(attachment["file_data"])

                        # Añadir el archivo al correo
                        part = MIMEText(file_data, "base64")
                        part.add_header(
                            "Content-Disposition", f'attachment; filename="{filename}"'
                        )
                        message.attach(part)

                    server.send_message(message)
                    print(f"📨 Enviado {i}/{len(combined_emails)} a {email_user}")
                except smtplib.SMTPResponseException as e:
                    error_code = e.smtp_code
                    error_message = (
                        e.smtp_error.decode()
                        if isinstance(e.smtp_error, bytes)
                        else str(e.smtp_error)
                    )
                    print(f"❌ Error en {email_user}: {error_code} - {error_message}")
                    # Detectar si el correo no existe
                    if error_code == 550 and "User unknown" in error_message:
                        print(
                            f"⚠️ El correo {email_user} no existe. Eliminándolo de la lista."
                        )

                    # Detectar si la cuenta ha sido bloqueada
                    elif error_code in [421, 550, 554]:
                        print("⚠️ Cuenta posiblemente bloqueada. Deteniendo el envío.")
                        time.sleep(300)  # Espera 5 minutos antes de continuar
                    # Detectar bloqueo de cuenta
                    elif error_code in [550, 554] and "policy" in error_message.lower():
                        print(
                            "🚨 Cuenta posiblemente bloqueada por políticas de spam. Deteniendo el envío."
                        )
                        break  # Detiene el envío masivo

                # Guardar el correo en la base de datos
                sent_at = datetime.now()  # Fecha y hora actual al enviar el correo
                received_at = None
                email_id = self.message_service.guardar_correo(
                    sender_user_id,
                    subject,
                    body_text,
                    body_html,
                    SENDER_EMAIL,
                    False,
                    "sent",
                    "sent",
                    received_at,
                    sent_at,
                )

                # if email_id is None:
                #     return jsonify({"error": "No se pudo guardar el correo"}), 500

                # actualizar el usuario
                self.user_service.update_send_status_user(sender_user_id)
                # Guardar destinatarios
                self.user_service.guardar_destinatarios(
                    email_id, [{"email": email_user, "type": "to"}]
                )

                # Guardar adjuntos
                self.message_service.guardar_adjuntos(email_id, attachments)

                # Control de tasa de envío para evitar bloqueos
                if i % 29 == 0:
                    print("⏳ Esperando 1 minuto para evitar bloqueo...")
                    time.sleep(60)  # Espera 10 minutos cada 800 correos
                else:
                    time.sleep(random.uniform(3, 6))  # Pausa de 2.7 segundos entre correos

                 # Cerrar y reabrir la conexión cada cierto número de correos
                if i % MAX_CORREOS_POR_CONEXION == 0 or i == len(combined_emails):
                    server.quit()
                    print("🔴 Conexión SMTP cerrada temporalmente para evitar bloqueos.")
                    time.sleep(10)  # Espera antes de abrir otra conexión
            print(
                "✅ Todos los correos fueron enviados, finalizado y conexión cerrada."
            )
        except smtplib.SMTPAuthenticationError as e:
            print("🚨 La cuenta está BLOQUEADA o la contraseña es incorrecta.")
        except Exception as e:
            print(f"⚠️ Error desconocido: {e}")
        # return jsonify({"message": "Correo enviado y guardado correctamente"}), 200

    # Método para leer correos no leídos de Gmail
    def read_emails(self, config):
        # access_token = get_access_token(config["OUTLOOK_USER"], config["OUTLOOK_PASS"])
        # auth_string = (
        #     f"user={config['OUTLOOK_USER']}\x01auth=Bearer {access_token}\x01\x01"
        # )
        # auth_b64 = base64.b64encode(auth_string.encode()).decode()
        server = imaplib.IMAP4_SSL(host="outlook.office365.com", timeout=60)
        server.debug = 4
        response = server.login(user="contacto@tumerka.pe", password="Peru123...")
        # status_code, response = server.docmd("AUTH", "XOAUTH2 " + auth_b64)
        # print(f"[*] Login the server: {status_code} {response}")
        # response = server.authenticate("XOAUTH2", lambda x: auth_b64)
        print("Autenticación exitosa:", response)
        server.select("inbox")
        status, messages = server.search(None, "UNSEEN")
        mail_ids = messages[0].split()

        new_emails = []

        # Procesar cada correo no leído
        for mail_id in mail_ids:
            status, msg_data = server.fetch(mail_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Decodificar el mensaje
                    msg = email.message_from_bytes(response_part[1])

                    # Obtener el remitente y el asunto
                    from_email = email.utils.parseaddr(msg.get("From"))[1]
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    # Guardar el usuario en la base de datos
                    user_id = self.user_service.guardar_usuario(from_email, None)

                    # Procesar el cuerpo del mensaje y los adjuntos
                    body_text = None
                    body_html = None
                    attachments = []

                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            # Si es el cuerpo del mensaje en texto plano
                            if (
                                content_type == "text/plain"
                                and "attachment" not in content_disposition
                            ):
                                body_text = part.get_payload(decode=True).decode()
                            # Si es el cuerpo del mensaje en HTML
                            elif (
                                content_type == "text/html"
                                and "attachment" not in content_disposition
                            ):
                                body_html = part.get_payload(decode=True).decode()
                            # Si es un adjunto
                            elif "attachment" in content_disposition:
                                filename = part.get_filename()
                                if filename:
                                    file_data = part.get_payload(decode=True)
                                    attachments.append(
                                        {
                                            "filename": filename,
                                            "file_type": content_type,
                                            "file_data": base64.b64encode(
                                                file_data
                                            ).decode("utf-8"),
                                        }
                                    )
                    else:
                        # Si el mensaje no es multipart, obtener el cuerpo en texto plano o HTML
                        if msg.get_content_type() == "text/plain":
                            body_text = msg.get_payload(decode=True).decode()
                        elif msg.get_content_type() == "text/html":
                            body_html = msg.get_payload(decode=True).decode()

                    # Guardar el correo y los detalles en la base de datos
                    received_at = (
                        datetime.now()
                    )  # Fecha y hora actual al recibir el correo
                    sent_at = None

                    email_id = self.message_service.guardar_correo(
                        user_id,
                        subject,
                        body_text,
                        body_html,
                        from_email,
                        True,
                        "unread",
                        "received",
                        received_at,
                        sent_at,
                    )
                    self.user_service.guardar_destinatarios(
                        email_id, [{"email": from_email, "type": "from"}]
                    )
                    self.message_service.guardar_adjuntos(email_id, attachments)

                    # Añadir el correo a la lista de nuevos correos
                    new_emails.append(
                        {
                            "email_id": email_id,
                            "subject": subject,
                            "from": from_email,
                            "received_at": received_at.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )

        # Cerrar la conexión con el servidor de Gmail
        server.logout()

        return new_emails

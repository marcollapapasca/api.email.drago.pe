import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

from database.save_email import EmailService
save_email = EmailService().save_email

class Gmail:

    def __init__(self):
        pass

    def load_config(self, config_path):
        with open(os.path.join(os.path.dirname(__file__), config_path), "r") as file:
            return json.load(file)

    def load_html_template(self, template_path):
        with open(os.path.join(os.path.dirname(__file__), template_path),"r",encoding="utf-8") as file:
            return file.read()
        

    def send_email(self, config, event_type, data, template_path):
               
        msg = MIMEMultipart()
        msg["From"] = config["FROM_ADDRESS"]
        msg["To"] = data.get("to_address")
        msg["Bcc"] = config["BCC_ADDRESS"]

        template_html = self.load_html_template(template_path)

        if event_type == "new_user":
                msg["Subject"] = "¡Bienvenido a tumerka.pe!"
                username = data.get("username", "Nuevo Usuario")
                body_html = template_html.replace("{{username}}", username)
                msg.attach(MIMEText(body_html, "html"))

                save_email(data, config, body_html)
        elif event_type == "new_member":
                msg["Subject"] = "¡Bienvenido al Marketplace tumerka.pe!"
                username = data.get("username", "Nuevo Usuario")
                body_html = template_html.replace("{{username}}", username)
                msg.attach(MIMEText(body_html, "html"))

                save_email(data, config, body_html)
        elif event_type =="subscription":
                msg["Subject"] = "¡Gracias por suscribirte!"
                body_html = template_html
                msg.attach(MIMEText(body_html, "html"))

                save_email(data, config, body_html)
        elif event_type =="invoice":
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

                save_email(data, config, body_html)

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
        elif event_type =="new_order":
                msg["Subject"] = "Confirmación de tu pedido"

                customer_name = data.get("customer_name", "Cliente")
                order_number = data.get("order_number", "Orden")

                order_items = data.get("order_items", [])
                
                shipping_cost = data.get("shipping_cost", "0.00")
                total_amount = data.get("total_amount", "0.00")

                order_items_html = ""
                for item in order_items:
                    order_items_html += f"<tr><td>{item['sku']}</td><td>{item['product_name']}</td><td>{item['quantity']}</td><td>{item['price_unit']}</td><td>{item['price_total']}</td></tr>"

                body_html = template_html.replace("{{customer_name}}", customer_name)
                body_html = body_html.replace("{{order_number}}", order_number)
                body_html = body_html.replace("{{order_items}}", order_items_html)
                body_html = body_html.replace("{{shipping_cost}}", shipping_cost)
                body_html = body_html.replace("{{total_amount}}", total_amount)
                msg.attach(MIMEText(body_html, "html"))

                save_email(data, config, body_html)
        elif event_type =="send_order_seller":
                msg["Subject"] = "Tienes un nuevo pedido"

                order_number = data.get("order_number", "Orden")
                seller_name = data.get("seller_name", "Seller")
                document_type_name = data.get("document_type_name", "")
                document_number = data.get("document_number", "")
                customer_name = data.get("customer_name", "")
                delivery_address = data.get("delivery_address", "")

                order_items = data.get("order_items", [])

                total_amount = data.get("total_amount", "0.00")
                # Construye la tabla HTML para order_items
                order_items_html = ""
                for item in order_items:
                    order_items_html += f"<tr><td>{item['sku']}</td><td>{item['product_name']}</td><td>{item['quantity']}</td><td>{item['price_unit']}</td><td>{item['price_total']}</td></tr>"

                body_html = template_html.replace("{{order_number}}", order_number)
                body_html = body_html.replace("{{seller_name}}", seller_name)
                body_html = body_html.replace("{{document_type_name}}", document_type_name)
                body_html = body_html.replace("{{document_number}}", document_number)
                body_html = body_html.replace("{{customer_name}}", customer_name)
                body_html = body_html.replace("{{delivery_address}}", delivery_address)
                body_html = body_html.replace("{{order_items}}", order_items_html )
                body_html = body_html.replace("{{total_amount}}", total_amount)
                msg.attach(MIMEText(body_html, "html"))

                save_email(data, config, body_html)
        elif event_type =="new_password":
                msg["Subject"] = "Solicitud de Cambio de Contraseña"

                customer_name = data.get("customer_name", "Cliente")
                reset_link = data.get("reset_link", "https://tumerka.pe/reset-password")

                body_html = template_html.replace("{{username}}", customer_name)
                body_html = body_html.replace("{{reset_link}}", reset_link)
                msg.attach(MIMEText(body_html, "html"))

                save_email(data, config, body_html)
        elif event_type =="new_password_confirmation":
                msg["Subject"] = "Confirmación de Cambio de Contraseña"

                customer_name = data.get("customer_name", "Cliente")

                body_html = template_html.replace("{{username}}", customer_name)
                msg.attach(MIMEText(body_html, "html"))

                save_email(data, config, body_html)
        elif event_type =="publicidad_1":
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

                save_email(data, config, body_html)
        elif event_type =="tumerka_welcome_new_seller":
                seller_name = data.get("seller_name", "Seller")

                msg["Subject"] = "Bienvenido a TuMerka, " + seller_name

                store_name = data.get("store_name", "")
                seller_email = data.get("seller_email", "")

                body_html = template_html.replace("{{seller_name}}", seller_name)
                body_html = body_html.replace("{{store_name}}", store_name)
                body_html = body_html.replace("{{seller_email}}", seller_email)
                
                msg.attach(MIMEText(body_html, "html"))

                save_email(data, config, body_html)
        elif event_type =="tumerka_seller_accept_contract":
                seller_name = data.get("seller_name", "Seller")
                msg["Subject"] = "¡Contrato Aceptado!"

                body_html = template_html.replace("{{seller_name}}", seller_name)
                  
                msg.attach(MIMEText(body_html, "html"))

                save_email(data, config, body_html)

        else:
                print("Unknown event type")

        try:
            # server = smtplib.SMTP(host=config["GMAIL_HOST"], port=config["GMAIL_PORT"])
            # server.starttls()
            # server.login(config["GMAIL_USER"], config["GMAIL_PASS"])
            # server.send_message(msg)
            print("Correo enviado exitosamente")
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
        # finally:
        #     server.quit()
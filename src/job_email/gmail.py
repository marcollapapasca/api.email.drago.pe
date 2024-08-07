import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


class Gmail:

    def __init__(self):
        pass

    def load_config(self, config_path):
        with open(os.path.join(os.path.dirname(__file__), config_path), "r") as file:
            return json.load(file)

    def load_html_template(self, template_path):
        with open(os.path.join(os.path.dirname(__file__), template_path),"r",encoding="utf-8") as file:
            return file.read()

    def send_email(self, config, to_address, event_type, data):
        msg = MIMEMultipart()
        msg["From"] = config["FROM_ADDRESS"]
        msg["To"] = to_address
        msg["Bcc"] = config["BCC_ADDRESS"]

        if event_type == "new_user":
                msg["Subject"] = "¡Bienvenido a tumerka.pe!"
                template_path = data.get("template_html")
                html_template = self.load_html_template(template_path)
                body_html = html_template.replace(
                    "{{username}}", data.get("username", "Nuevo Usuario")
                )
                msg.attach(MIMEText(body_html, "html"))
        elif event_type == "new_member":
                msg["Subject"] = "¡Bienvenido al Marketplace tumerka.pe!"
                template_path = data.get("template_html")
                html_template = self.load_html_template(template_path)
                body_html = html_template.replace(
                    "{{username}}", data.get("username", "Nuevo Usuario")
                )
                msg.attach(MIMEText(body_html, "html"))
        elif event_type =="subscription":
                msg["Subject"] = "¡Gracias por suscribirte!"
                template_path = data.get("template_html")
                html_template = self.load_html_template(template_path)
                body_html = html_template
                msg.attach(MIMEText(body_html, "html"))
        elif event_type =="invoice":
                msg["Subject"] = "Su comprobante está disponible"
                customer_name = data.get("customer_name", "Cliente")
                document_number = data.get("document_number", "Documento")
                amount = data.get("amount", "0.00")
                issue_date = data.get("issue_date", "Fecha")
                attachment_path = data.get("attachment_path", "adjunto.pdf")

                template_path = data.get("template_html")
                html_template = self.load_html_template(template_path)
                body_html = html_template.replace("{{customer_name}}", customer_name)
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
        elif event_type =="new_order":
                msg["Subject"] = "Confirmación de tu pedido"
                template_path = data.get("template_html")
                html_template = self.load_html_template(template_path)

                customer_name = data.get("customer_name", "Cliente")
                order_number = data.get("order_number", "Orden")

                order_items = data.get("order_items", [])
                
                shipping_cost = data.get("shipping_cost", "0.00")
                total_amount = data.get("total_amount", "0.00")

                order_items_html = ""
                for item in order_items:
                    order_items_html += f"<tr><td>{item['sku']}</td><td>{item['product_name']}</td><td>{item['quantity']}</td><td>{item['price_unit']}</td><td>{item['price_total']}</td></tr>"

                body_html = html_template.replace("{{customer_name}}", customer_name)
                body_html = body_html.replace("{{order_number}}", order_number)
                body_html = body_html.replace("{{order_items}}", order_items_html)
                body_html = body_html.replace("{{shipping_cost}}", shipping_cost)
                body_html = body_html.replace("{{total_amount}}", total_amount)
                msg.attach(MIMEText(body_html, "html"))
        elif event_type =="send_order_seller":
                msg["Subject"] = "Tiene un pedido"
                template_path = data.get("template_html")
                html_template = self.load_html_template(template_path)

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

                body_html = html_template.replace("{{order_number}}", order_number)
                body_html = body_html.replace("{{seller_name}}", seller_name)
                body_html = body_html.replace("{{document_type_name}}", document_type_name)
                body_html = body_html.replace("{{document_number}}", document_number)
                body_html = body_html.replace("{{customer_name}}", customer_name)
                body_html = body_html.replace("{{delivery_address}}", delivery_address)
                body_html = body_html.replace("{{order_items}}", order_items_html )
                body_html = body_html.replace("{{total_amount}}", total_amount)
                msg.attach(MIMEText(body_html, "html"))
        elif event_type =="new_password":
                msg["Subject"] = "Solicitud de Cambio de Contraseña"
                template_path = data.get("template_html")
                html_template = self.load_html_template(template_path)

                customer_name = data.get("customer_name", "Cliente")
                reset_link = data.get("reset_link", "https://tumerka.pe/reset-password")

                body_html = html_template.replace("{{username}}", customer_name)
                body_html = body_html.replace("{{reset_link}}", reset_link)
                msg.attach(MIMEText(body_html, "html"))
        elif event_type =="new_password_confirmation":
                msg["Subject"] = "Confirmación de Cambio de Contraseña"
                template_path = data.get("template_html")
                html_template = self.load_html_template(template_path)

                customer_name = data.get("customer_name", "Cliente")

                body_html = html_template.replace("{{username}}", customer_name)
                msg.attach(MIMEText(body_html, "html"))
        elif event_type =="publicidad_1":
                msg["Subject"] = "Publicidad 1"
                template_path = data.get("template_html")
                html_template = self.load_html_template(template_path)

                customer_name = data.get("", "")
                image_paths = data.get("image_paths", {})
                links = data.get("links", {})

                body_html = html_template.replace("{{username}}", customer_name)
                for key, value in links.items():
                    body_html = body_html.replace(f"{{{{{key}}}}}", value)
                for key, value in image_paths.items():
                    body_html = body_html.replace(f"{{{{{key}}}}}", value)

                msg.attach(MIMEText(body_html, "html"))

        else:
                print("Unknown event type")

        try:
            server = smtplib.SMTP(host=config["GMAIL_HOST"], port=config["GMAIL_PORT"])
            server.starttls()
            server.login(config["GMAIL_USER"], config["GMAIL_PASS"])
            server.send_message(msg)
            print("Correo enviado exitosamente")
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
        finally:
            server.quit()


# @app.route("/send_email", methods=["POST"])
# def handle_send_email():
#     data = request.json
#     # config_path = 'config.json'
#     config_path = data.get("config_smtp")
#     config = load_config(config_path)

#     to_address = data.get("to_address")
#     #subject = data.get("subject")
#     subject = ""
#     event_type = data.get("event_type")
#     if not to_address or not event_type:
#         return jsonify({"error": "Error de validación"}), 400

#     send_email(config, to_address, subject, event_type, data)
#     return jsonify({"message": "Email enviado satisfactoriamente"}), 200

# @app.route("/")
# def home():
#     return "Servidor de Tareas Programadas en Ejecución"

# if __name__ == "__main__":
#     print("Starting server...")
#     app.run(debug=True)

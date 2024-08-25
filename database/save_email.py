import json
from database.db_connect import Database

class EmailService:
    def __init__(self):
        self.database = Database()
        self.conn = self.database.get_connection()

    def save_email(self, data, config, body_html):
        try:
            sku = data.get("sku")
            to_address = data.get("to_address")
            gmail_user = config.get("GMAIL_USER")

            if not sku or not to_address or not gmail_user:
                raise ValueError("Faltan datos obligatorios en la entrada")

            # Convertir el HTML a formato JSON
            html_content = json.dumps({"html_content": body_html})

            # Preparar la consulta SQL
            sql = """
            INSERT INTO email.emails (sku, email_receiver, email_sender, html_submit) 
            VALUES (%s, %s, %s, %s)
            """
            values = (sku, to_address, gmail_user, html_content)

            # Ejecutar la consulta y confirmar la transacción
            with self.conn.cursor() as cursor:
                cursor.execute(sql, values)
                self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            raise

        finally:
            # Asegurarse de cerrar la conexión si no se va a usar más
            self.conn.close()

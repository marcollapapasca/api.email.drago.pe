import json
from database.db_connect import Database


class EmailService:
    def __init__(self):
        self.database = Database()

    def guardar_usuario(self, email, name):
        connection = None
        try:
            connection = self.database.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO gmail.users (email, name) VALUES (%s, %s)
                    ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
                    RETURNING user_id;
                """, (email, name))
                user_id = cursor.fetchone()[0]
                connection.commit()
                return user_id
        except Exception as e:
            print(f"Error al guardar usuario: {e}")
            connection.rollback()
            return None
    
    # Funciones para guardar en la base de datos (reutilizar funciones anteriores)
    def guardar_correo(self, user_id, subject, body_text, body_html, sender_email, is_incoming, status, sent_status, received_at=None, sent_at=None, read_status=False):
            connection = None
            try:
                connection = self.database.get_connection()
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO gmail.emails (user_id, subject, body_text, body_html, sender_email, is_incoming, status, sent_status, received_at, sent_at, read_status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING email_id;
                    """, (user_id, subject, body_text, body_html, sender_email, is_incoming, status, sent_status, received_at, sent_at, read_status))
                    email_id = cursor.fetchone()[0]
                    connection.commit()
                    return email_id
            except Exception as e:
                print(f"Error al guardar el correo: {e}")
                connection.rollback()
                return None


    def guardar_destinatarios(self, email_id, recipients):
        connection = None
        try:
            connection = self.database.get_connection()
            with connection.cursor() as cursor:
                for recipient in recipients:
                    cursor.execute("""
                        INSERT INTO gmail.email_recipients (email_id, recipient_email, recipient_type)
                        VALUES (%s, %s, %s);
                    """, (email_id, recipient['email'], recipient['type']))
                connection.commit()
        except Exception as e:
            print(f"Error al guardar destinatarios: {e}")
            connection.rollback()

    def guardar_adjuntos(self, email_id, attachments):
        connection = None
        try:
            connection = self.database.get_connection()
            with connection.cursor() as cursor:
                for attachment in attachments:
                
                    cursor.execute("""
                        INSERT INTO gmail.attachments (email_id, filename, file_type, file_data)
                        VALUES (%s, %s, %s, %s);
                    """, (email_id, attachment['filename'], attachment['file_type'], attachment['file_data']))
                connection.commit()
        except Exception as e:
            print(f"Error al guardar adjuntos: {e}")
            connection.rollback()
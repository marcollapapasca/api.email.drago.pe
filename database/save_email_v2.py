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

    def get_emails(self, sent_status):
        connection = None
        emails = []
        try:
            connection = self.database.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT email_id, subject, body_text, body_html, sender_email, received_at, sent_at, status, sent_status, read_status
                    FROM gmail.emails
                    WHERE sent_status = %s
                    ORDER BY received_at DESC, sent_at DESC;
                """, (sent_status,))
                rows = cursor.fetchall()

                for row in rows:
                    emails.append({
                        "email_id": row[0],
                        "subject": row[1],
                        "body_text": row[2],
                        "body_html": row[3],
                        "sender_email": row[4],
                        "received_at": row[5],
                        "sent_at": row[6],
                        "status": row[7],
                        "sent_status": row[8],
                        "read_status": row[9]
                    })
            return emails
        except Exception as e:
            print(f"Error al obtener correos: {e}")
            return []
        
    def get_email_by_id(self, email_id):
        connection = None
        try:
            connection = self.database.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT email_id,email, subject, sender_email, received_at, sent_at, sent_status, body_text, body_html
                    FROM gmail.emails E INNER JOIN gmail.users U ON E.user_id = U.user_id
                    where email_id = %s
                """, (email_id,))
                row = cursor.fetchone()

                if row:
                    return {
                        "email_id": row[0],
                        "email": row[1],
                        "subject": row[2],
                        "sender_email": row[3],
                        "received_at": row[4],
                        "sent_at": row[5],
                        "sent_status": row[6],
                        "body_text": row[7],
                        "body_html": row[8],
                    }
                else:
                    return None
        except Exception as e:
            print(f"Error al obtener correos: {e}")
            return None
        
    def get_users(self):
        connection = None
        users = []
        try:
            connection = self.database.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                     SELECT DISTINCT(email), user_id, name FROM gmail.users
                    ORDER BY user_id ASC 
                """)
                rows = cursor.fetchall()

                for row in rows:
                    users.append({
                        "email": row[0],
                        "user_id": row[1],
                        "name": row[2]
                    })
            return users
        except Exception as e:
            print(f"Error al obtener correos: {e}")
            return []
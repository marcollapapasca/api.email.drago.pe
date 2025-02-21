from database.connection import Database


class UserService:
    def __init__(self):
        self.connection = Database().connection

    def guardar_usuario(self, email, name):
        connection = None
        try:
            connection = self.connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO gmail.users (email, name) VALUES (%s, %s) ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name RETURNING user_id;
                """,
                    (email, name),
                )
                user_id = cursor.fetchone()[0]
                connection.commit()
                return user_id
        except Exception as e:
            connection.rollback()
            return None

    def guardar_destinatarios(self, email_id, recipients):
        connection = None
        try:
            connection = self.connection()
            with connection.cursor() as cursor:
                for recipient in recipients:
                    cursor.execute(
                        """
                        INSERT INTO gmail.email_recipients (email_id, recipient_email, recipient_type)
                        VALUES (%s, %s, %s);
                    """,
                        (email_id, recipient["email"], recipient["type"]),
                    )
                connection.commit()
        except Exception as e:
            print(f"Error al guardar destinatarios: {e}")
            connection.rollback()

    def update_send_status_user(self, user_id):
        connection = None
        try:
            connection = self.connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE gmail.users
                    SET send_status = true
                    WHERE user_id = %s
                """,
                    (user_id,),
                )
                connection.commit()
                return user_id
        except Exception as e:
            print(f"Error al actualizar el estado de envío del usuario: {e}")
            if connection:
                connection.rollback()
            return None

    def get_users(self):
        connection = None
        users = []
        try:
            connection = self.connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                     SELECT DISTINCT(email), user_id, name FROM gmail.users
                    WHERE send_status = false AND black_list = false
                    ORDER BY user_id ASC LIMIT 40 
                """
                )
                rows = cursor.fetchall()

                for row in rows:
                    users.append({"email": row[0], "user_id": row[1], "name": row[2]})
            return users
        except Exception as e:
            print(f"Error al obtener correos: {e}")
            return []

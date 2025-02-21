from database.connection import Database


class MessageService:
    def __init__(self):
        self.connection = Database().connection

    def guardar_correo(
        self,
        user_id,
        subject,
        body_text,
        body_html,
        sender_email,
        is_incoming,
        status,
        sent_status,
        received_at=None,
        sent_at=None,
        read_status=False,
    ):
        connection = None
        try:
            connection = self.connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO gmail.emails (user_id, subject, body_text, body_html, sender_email, is_incoming, status, sent_status, received_at, sent_at, read_status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING email_id;
                    """,
                    (
                        user_id,
                        subject,
                        body_text,
                        body_html,
                        sender_email,
                        is_incoming,
                        status,
                        sent_status,
                        received_at,
                        sent_at,
                        read_status,
                    ),
                )
                email_id = cursor.fetchone()[0]
                connection.commit()
                return email_id
        except Exception as e:
            print(f"Error al guardar el correo: {e}")
            connection.rollback()
            return None

    def guardar_adjuntos(self, email_id, attachments):
        connection = None
        try:
            connection = self.connection()
            with connection.cursor() as cursor:
                for attachment in attachments:

                    cursor.execute(
                        """
                        INSERT INTO gmail.attachments (email_id, filename, file_type, file_data)
                        VALUES (%s, %s, %s, %s);
                    """,
                        (
                            email_id,
                            attachment["filename"],
                            attachment["file_type"],
                            attachment["file_data"],
                        ),
                    )
                connection.commit()
        except Exception as e:
            print(f"Error al guardar adjuntos: {e}")
            connection.rollback()

    def get_emails(self, sent_status):
        connection = None
        emails = []
        try:
            connection = self.connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                  SELECT users.email as email_user, email_id, subject, body_text, body_html, sender_email, received_at, sent_at, status, sent_status, read_status FROM gmail.emails INNER JOIN gmail.users ON emails.user_id = users.user_id
                    WHERE sent_status = '"""
                    + sent_status
                    + """' and users.email NOT ILIKE 'postmaster@%' and users.email NOT ILIKE 'mailer-daemon@%' and users.email NOT ILIKE 'no-reply@%' and users.email NOT ILIKE 'sc-noreply@%'
                    ORDER BY received_at DESC, sent_at DESC
                    LIMIT 100;
                """
                )
                rows = cursor.fetchall()

                for row in rows:
                    emails.append(
                        {
                            "email_user": row[0],
                            "email_id": row[1],
                            "subject": row[2],
                            "body_text": row[3],
                            "body_html": row[4],
                            "sender_email": row[5],
                            "received_at": row[6],
                            "sent_at": row[7],
                            "status": row[8],
                            "sent_status": row[9],
                            "read_status": row[10],
                        }
                    )
            return emails
        except Exception as e:
            print(f"Error al obtener correos: {e}")
            return []

    def get_email_by_id(self, email_id):
        connection = None
        try:
            connection = self.connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT email_id,email, subject, sender_email, received_at, sent_at, sent_status, body_text, body_html
                    FROM gmail.emails E INNER JOIN gmail.users U ON E.user_id = U.user_id
                    where email_id = %s
                """,
                    (email_id,),
                )
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

    def get_groups(self):
        connection = None
        groups = []
        try:
            connection = self.connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT G.group_id, group_name, count(*), COUNT(CASE WHEN u.send_status = false THEN 1 END) AS false_send_status_count FROM gmail.groups G
                    INNER JOIN gmail.contact_group CG ON G.group_id = CG.group_id
                    INNER JOIN gmail.users u ON cg.user_id = u.user_id
                    GROUP BY G.group_id, group_name
                    HAVING COUNT(*) > 0
                    ORDER BY COUNT(*) desc
                """
                )
                rows = cursor.fetchall()

                for row in rows:
                    groups.append(
                        {
                            "group_id": row[0],
                            "group_name": row[1],
                            "count": row[2],
                            "false_send_status_count": row[3],
                        }
                    )
            return groups
        except Exception as e:
            print(f"Error al obtener correos: {e}")
            return []

    def get_emails_by_groups(self, groups):
        if not groups:
            print("Error: 'groups' está vacío o no definido.")
            return []

        connection = None
        emails = []
        try:
            connection = self.connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                SELECT DISTINCT c.email
                FROM gmail.groups G
                INNER JOIN gmail.contact_group cg ON g.group_id = cg.group_id
                INNER JOIN gmail.users c ON cg.user_id = c.user_id
                WHERE g.status = true AND cg.status AND g.group_id::TEXT = ANY(string_to_array(%s, ','))
                AND c.send_status = false LIMIT 1900
            """,
                    (",".join(str(group) for group in groups),),
                )
                rows = cursor.fetchall()

                for row in rows:
                    emails.append({"email": row[0]})
            return emails
        except Exception as e:
            print(f"Error al obtener correos: {e}")
            return []

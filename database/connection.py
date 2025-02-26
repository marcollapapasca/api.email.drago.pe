import psycopg2
import os

class Database:
    def __init__(self):
        self.conn = None

    def connection(self):
        self.conn = None
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("POSTGRESQL_HOST"),
                port=os.getenv("POSTGRESQL_PORT"),
                dbname=os.getenv("POSTGRESQL_DATABASE"),
                user=os.getenv("POSTGRESQL_USER"),
                password=os.getenv("POSTGRESQL_PASSWORD"),
            )
            self.conn.autocommit = True
        except Exception as e:
            print(f"❌ Error de conexión a la base de datos: {e}")
            self.conn = None
        return self.conn

import os
import psycopg2
from psycopg2 import OperationalError
from database.env_loader import load_environment

# Carga el archivo .env correcto basado en el entorno
env = os.getenv("FLASK_ENV", "development")
env_file = f".env.{env}"
load_environment(env_file)

# Obtén las variables de entorno
DB_HOST = os.getenv('POSTGRESQL_HOST')
DB_PORT = os.getenv('POSTGRESQL_PORT')
DB_NAME = os.getenv('POSTGRESQL_DATABASE')
DB_USER = os.getenv('POSTGRESQL_USER')
DB_PASSWORD = os.getenv('POSTGRESQL_PASSWORD')

class Database:
    def __init__(self):
        self.conn = None

    def get_connection(self):
        self.conn = None

        try:
            db_host = DB_HOST
            port = DB_PORT
            db_name = DB_NAME
            db_user = DB_USER
            db_password = DB_PASSWORD

            print("valores db")
            print(db_host, port, db_name, db_user, db_password)

            self.conn = psycopg2.connect(
                host=db_host,
                port=port,
                dbname=db_name,
                user=db_user,
                password=db_password,
            )
            self.conn.autocommit = True

        except OperationalError as e:
            print(f"Error de conexión: {e}")
        return self.conn

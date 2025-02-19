from flask import Flask
import os
from routes.main import main
import logging
from logging.handlers import RotatingFileHandler
from flask_cors import CORS
from dotenv import load_dotenv

# Determina qué archivo .env cargar basado en el entorno
env = os.getenv("FLASK_ENV", "development")
env_file = f".env.{env}"

# Carga las variables de entorno desde el archivo específico
load_dotenv(env_file)

app = Flask(__name__)
app.register_blueprint(main)

# Imprime el entorno seleccionado
print("FLASK_ENV SELECCIONADO")
print(env)

# Habilitar CORS para todas las rutas
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config["PORT"] = int(os.getenv("SERVICE_PORT", 3006))

# Configura la aplicación Flask según el entorno
if env == 'development':
    app.config['DEBUG'] = True
    app.config['ENV'] = 'development'
elif env == 'production':
    app.config['DEBUG'] = False
    app.config['ENV'] = 'production'
else:
    raise ValueError("No se ha establecido un entorno válido en la variable FLASK_ENV")

if __name__ == "__main__":
    # Configura el manejador de logging
    handler = RotatingFileHandler("error.log", maxBytes=10000, backupCount=1)
    handler.setLevel(logging.ERROR)
    app.logger.addHandler(handler)

    # Ejecuta la aplicación Flask en todas las interfaces de red (0.0.0.0)
    app.run(host="0.0.0.0", port=app.config['PORT'])

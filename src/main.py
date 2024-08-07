import os
from flask import Flask
from routes.main import main
import logging
from logging.handlers import RotatingFileHandler
from flask_cors import CORS
from env_loader import load_environment

from rich.console import Console
from rich.panel import Panel

# Determina qué archivo .env cargar basado en el entorno
env = os.getenv("FLASK_ENV", "development")
env_file = f".env.{env}"

# Carga las variables de entorno desde el archivo específico
load_environment(env_file)

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
    # Otras configuraciones específicas para desarrollo
elif env == 'production':
    app.config['DEBUG'] = False
    app.config['ENV'] = 'production'
    # Otras configuraciones específicas para producción
else:
    raise ValueError("No se ha establecido un entorno válido en la variable FLASK_ENV")


if __name__ == "__main__":
    # Configura el manejador de logging
    handler = RotatingFileHandler("error.log", maxBytes=10000, backupCount=1)
    handler.setLevel(logging.ERROR)
    app.logger.addHandler(handler)

    # Configura la consola de rich
    console = Console()

    port = app.config["PORT"]

    # Crea un panel con el mensaje de inicio
    print("\n")
    panel = Panel.fit(
        f"""[orange3]
 EMAIL
"""
        f"\n\n[green]Starting [underline]api.email.drago.oe[/underline]\n\n"
        f"Modo de ejecución: [green b]{env}[/green b]\n\n"
        f"* Running on [green b]http://127.0.0.1:{port}[/green b]",
        border_style="orange3",
        padding=(1, 2) 
    )

    # Imprime el panel en la consola
    console.print(panel)

    # Ejecuta la aplicación Flask en todas las interfaces de red (0.0.0.0)
    app.run(host="0.0.0.0", port=port)
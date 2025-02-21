from flask import Flask, jsonify
from routes.email import email_router
from routes.group import group_router
from routes.user import user_router
from dotenv import load_dotenv
from flask_cors import CORS

import os

app = Flask(__name__)
env = os.getenv("NODE_ENV", "development")

dotenv_path = f".env.{env}"
load_dotenv(dotenv_path)
CORS(app)

@app.route("/")
def homepage():
    return jsonify(message="Hello world!", env=os.getenv("NODE_ENV")), 200

app.register_blueprint(email_router)
app.register_blueprint(group_router)
app.register_blueprint(user_router)

if __name__ == "__main__":
    print(f"✅ Enviroment selected: {os.getenv('NODE_ENV')}")
    app.run(host="0.0.0.0", debug=(env == "development"), port=3006)

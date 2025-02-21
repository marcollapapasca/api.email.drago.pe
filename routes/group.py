from flask import Blueprint, jsonify
from service.database.message import MessageService

group_router = Blueprint("group", __name__, url_prefix="/api")
message_service = MessageService()

# ruta para obtener los grupos
@group_router.route("/groups", methods=["GET"])
def get_groups():
    groups = message_service.get_groups()
    if groups:
        return jsonify(groups), 200
    else:
        return jsonify({"error": "No emails found for the given id."}), 404

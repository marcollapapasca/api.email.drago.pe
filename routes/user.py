from flask import Blueprint, request, jsonify
from service.database.user import UserService

user_router = Blueprint('user', __name__, url_prefix='/api')
user_service = UserService()

@user_router.route("/users", methods=["GET"])
def get_users():
    emails = user_service.get_users()
    if emails:
        return jsonify(emails), 200
    else:
        return jsonify({"error": "No emails found for the given id."}), 404
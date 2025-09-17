from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user import Usuario
from app.extensions import db

auth_logando = Blueprint('logando', __name__)

@auth_logando.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"msg": "E-mail e senha obrigatórios"}), 400

    user = Usuario.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"msg": "E-mail ou senha inválidos"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify(access_token=token, user_id=str(user.id)), 200

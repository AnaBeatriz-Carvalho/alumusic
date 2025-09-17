from flask import Blueprint, request, jsonify
from app.models.user import Usuario
from app.extensions import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"msg": "E-mail e senha obrigatórios"}), 400

    if Usuario.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "E-mail já registrado"}), 400

    user = Usuario(email=data["email"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Usuário criado com sucesso", "user_id": str(user.id)}), 201

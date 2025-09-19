from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user import Usuario
from app.extensions import db

auth_bp = Blueprint("auth", __name__)

# Registro
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

    return jsonify({"msg": "Usuário criado com sucesso", "id": user.id}), 201

# Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"msg": "E-mail e senha obrigatórios"}), 400

    user = Usuario.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"msg": "E-mail ou senha inválidos"}), 401
    
    # Gerar o token JWT usando o ID do usuário como identidade
    token = create_access_token(identity=str(user.id))
    return jsonify(access_token=token, usuario_id=user.id), 200

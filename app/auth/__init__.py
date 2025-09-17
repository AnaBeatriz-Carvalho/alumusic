from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import Usuario
from app.extensions import db
from .auth import auth_bp

auth_bp = Blueprint('auth', __name__)



@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return {"error": "email e password são obrigatórios"}, 400

    if Usuario.query.filter_by(email=data["email"]).first():
        return {"error": "usuário já existe"}, 400

    user = Usuario(email=data["email"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return {"message": "usuário criado"}, 201



# Login → retorna JWT
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return {"error": "email e password são obrigatórios"}, 400

    user = Usuario.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return {"error": "usuário ou senha inválidos"}, 401

    token = create_access_token(identity=user.email)
    return {"access_token": token}, 200


# Exemplo de rota protegida
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    current_user = get_jwt_identity()
    return {"logged_in_as": current_user}, 200


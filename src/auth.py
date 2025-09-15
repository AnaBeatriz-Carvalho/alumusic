from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User

auth_bp = Blueprint("auth", __name__)

# Registrar usuário (só para teste inicial)
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data.get("username") or not data.get("password"):
        return {"error": "username e password são obrigatórios"}, 400

    if User.query.filter_by(username=data["username"]).first():
        return {"error": "usuário já existe"}, 400

    user = User(username=data["username"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return {"message": "usuário criado"}, 201


# Login → retorna JWT
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()

    if not user or not user.check_password(data["password"]):
        return {"error": "usuário ou senha inválidos"}, 401

    token = create_access_token(identity=user.username)
    return {"access_token": token}, 200


# Exemplo de rota protegida
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    current_user = get_jwt_identity()
    return {"logged_in_as": current_user}, 200

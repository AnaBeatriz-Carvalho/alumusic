from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import Usuario, db
import uuid

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if Usuario.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "E-mail já registrado"}), 400

    user = Usuario(
        id=str(uuid.uuid4()),
        email=data["email"],
        senha_hash=generate_password_hash(data["password"])
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Usuário criado com sucesso"}), 201

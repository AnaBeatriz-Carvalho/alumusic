from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from models import db, Comentario

bp = Blueprint("api", __name__)

@bp.route("/comentarios", methods=["POST"])
@jwt_required()
def add_comentario():
    data = request.get_json()
    comentario = Comentario(id=data["id"], texto=data["texto"])
    db.session.add(comentario)
    db.session.commit()
    return {"message": "Comentário salvo"}, 201
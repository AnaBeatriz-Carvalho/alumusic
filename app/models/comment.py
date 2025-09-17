
import uuid
from app.extensions import db

class Comentario(db.Model):
    __tablename__ = "comentarios"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    texto = db.Column(db.Text, nullable=False)
    data_recebimento = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    categoria = db.Column(db.String(50), nullable=True)
    confianca = db.Column(db.Float, nullable=True)

    usuario_id = db.Column(db.String, db.ForeignKey("usuarios.id"), nullable=False)

    tags = db.relationship(
        "TagFuncionalidade",
        backref="comentario",
        lazy=True,
        cascade="all, delete-orphan"
    )

class TagFuncionalidade(db.Model):
    __tablename__ = 'tags_funcionalidades'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.Integer, primary_key=True)
    comentario_id = db.Column(db.String(36), db.ForeignKey('comentarios.id'), nullable=False)
    codigo = db.Column(db.String(50), nullable=False)
    explicacao = db.Column(db.Text, nullable=False)


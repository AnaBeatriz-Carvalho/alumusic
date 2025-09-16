# app/models/comment.py
import uuid
from app.extensions import db

class Comentario(db.Model):
    __tablename__ = 'comentarios'
    __table_args__ = {'schema': 'public'}
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    texto = db.Column(db.Text, nullable=False)
    data_recebimento = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    classificacoes = db.relationship('Classificacao', backref='comentario', lazy=True, cascade="all, delete-orphan")

class Classificacao(db.Model):
    __tablename__ = 'classificacoes'
    __table_args__ = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    comentario_id = db.Column(db.String(36), db.ForeignKey('public.comentarios.id'), nullable=False)
    # A validação do ENUM é feita pelo banco de dados
    categoria = db.Column(db.String(50), nullable=False)
    confianca = db.Column(db.Float, nullable=False)
    data_classificacao = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    tags = db.relationship('TagFuncionalidade', backref='classificacao', lazy=True, cascade="all, delete-orphan")

class TagFuncionalidade(db.Model):
    __tablename__ = 'tags_funcionalidades'
    __table_args__ = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    classificacao_id = db.Column(db.Integer, db.ForeignKey('public.classificacoes.id'), nullable=False)
    codigo = db.Column(db.String(50), nullable=False)
    explicacao = db.Column(db.Text, nullable=False)
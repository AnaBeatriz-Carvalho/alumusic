import uuid
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID

class Comentario(db.Model):
    __tablename__ = 'comentarios'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    texto = db.Column(db.Text, nullable=False)
    data_recebimento = db.Column(db.DateTime, server_default=db.func.now())
    
    # Colunas para armazenar o resultado da classificação
    categoria = db.Column(db.String(50), nullable=True)
    confianca = db.Column(db.Float, nullable=True)
    
    # Coluna CRÍTICA para o fluxo assíncrono
    status = db.Column(db.String(20), nullable=False, default='PENDENTE') # FLUXO: PENDENTE -> PROCESSANDO -> CONCLUIDO -> FALHOU
    
    # Chave estrangeira e relacionamento
    usuario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('usuarios.id'), nullable=False)
    usuario = db.relationship('Usuario', backref='comentarios')
    tags = db.relationship('TagFuncionalidade', backref='comentario', lazy=True, cascade="all, delete-orphan")

class TagFuncionalidade(db.Model):
    __tablename__ = 'tags_funcionalidades'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(100), nullable=False)
    explicacao = db.Column(db.Text, nullable=False)
    comentario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('comentarios.id'), nullable=False)
# app/models/comment.py

import uuid
import logging
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timedelta
semana_atras = datetime.now() - timedelta(days=7)

class Comentario(db.Model):
    __tablename__ = 'comentarios'
    # __table_args__ = {'schema': 'public'} # Descomente se precisar
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    texto = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(50))
    confianca = db.Column(db.Float)
    data_recebimento = db.Column(db.DateTime, server_default=db.func.now())
    status = db.Column(db.String(20), nullable=False, default='PENDENTE')
    usuario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relacionamentos (Estes estão corretos)
    usuario = db.relationship('Usuario', back_populates='comentarios')
    tags = db.relationship('TagFuncionalidade', back_populates='comentario', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Comentario {self.id}>'
    
class TagFuncionalidade(db.Model):
    __tablename__ = 'tags_funcionalidades'
    # __table_args__ = {'schema': 'public'} # Descomente se precisar

    id = db.Column(db.Integer, primary_key=True)
    comentario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('comentarios.id'), nullable=False)
    codigo = db.Column(db.String(50), nullable=False)
    explicacao = db.Column(db.Text, nullable=False)

 
    comentario = db.relationship('Comentario', back_populates='tags')

    def __repr__(self):
        return f'<TagFuncionalidade {self.codigo}>'

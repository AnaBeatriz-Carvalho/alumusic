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

    # FK para música (opcional)
    musica_id = db.Column(UUID(as_uuid=True), db.ForeignKey('musicas.id'), nullable=True)

    # FK para artista (opcional)
    artista_id = db.Column(UUID(as_uuid=True), db.ForeignKey('artistas.id'), nullable=True)

    # Relacionamentos
    usuario = db.relationship('Usuario', back_populates='comentarios')
    musica = db.relationship('Musica', back_populates='comentarios')
    artista = db.relationship('Artista')  # Relacionamento direto com o artista
    tags = db.relationship('TagFuncionalidade', back_populates='comentario', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Comentario {self.id}>'
    
class TagFuncionalidade(db.Model):
    __tablename__ = 'tag_funcionalidade'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = db.Column(db.String, nullable=False)
    codigo = db.Column(db.String, nullable=True) 
    explicacao = db.Column(db.Text, nullable=True)  # Adiciona o campo explicacao
    comentario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('comentarios.id'), nullable=False)
    tag_catalogo_id = db.Column(db.Integer, db.ForeignKey('tag_catalogo.id'), nullable=False)

    comentario = db.relationship('Comentario', back_populates='tags')
    tag = db.relationship('TagCatalogo')  # link para o catálogo

    def __repr__(self):
        return f'<TagFuncionalidade {self.nome}>'

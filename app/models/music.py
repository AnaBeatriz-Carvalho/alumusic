from app.extensions import db
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import time, datetime

class Musica(db.Model):
    __tablename__ = 'musicas'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo = db.Column(db.String(300), nullable=False)
    duracao_segundos = db.Column(db.Integer, nullable=True)  # opcional
    lancamento = db.Column(db.Date, nullable=True)

    artista_id = db.Column(UUID(as_uuid=True), db.ForeignKey('artistas.id'), nullable=False)
    artista = db.relationship('Artista', back_populates='musicas')

    comentarios = db.relationship('Comentario', back_populates='musica', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Musica {self.titulo} - {self.artista_id}>'
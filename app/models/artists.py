from app.extensions import db
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Artista(db.Model):
    __tablename__ = 'artistas'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = db.Column(db.String(200), nullable=False, unique=False)
    slug = db.Column(db.String(200), nullable=True, unique=True)
    bio = db.Column(db.Text, nullable=True)

    musicas = db.relationship('Musica', back_populates='artista', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Artista {self.nome}>'
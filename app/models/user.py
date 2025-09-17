from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class Usuario(db.Model):
    __tablename__ = "usuarios"
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String, unique=True, nullable=False)
    senha_hash = db.Column(db.String, nullable=False)
    criado_em = db.Column(db.DateTime, server_default=db.func.now())

    # Métodos de senha
    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)

# app/models/user.py

import uuid
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
# 👇 Importe as funções de hash de senha
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Relacionamento com comentários
    comentarios = db.relationship('Comentario', back_populates='usuario', lazy=True)
    
    # =================== MÉTODOS ADICIONAIS ===================

    def set_password(self, password):
        """Cria um hash da senha e o armazena no campo password_hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        return check_password_hash(self.password_hash, password)

    # ==========================================================

    def __repr__(self):
        return f'<Usuario {self.email}>'
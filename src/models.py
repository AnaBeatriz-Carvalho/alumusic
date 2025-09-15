from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Comentario(db.Model):
    __tablename__ = "comentarios"

    id = db.Column(db.String, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String, nullable=True)
    confianca = db.Column(db.Float, nullable=True)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

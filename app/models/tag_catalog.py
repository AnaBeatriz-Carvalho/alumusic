from app.extensions import db

class TagCatalogo(db.Model):
    __tablename__ = 'tag_catalogo'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(120), unique=True, nullable=False)
    explicacao = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<TagCatalogo {self.codigo}>'
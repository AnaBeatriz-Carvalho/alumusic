# app/models/summary.py

from app.extensions import db

class ResumoSemanal(db.Model):
    __tablename__ = 'public.resumos_semanais'

    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, nullable=False)
    semana = db.Column(db.Integer, nullable=False)
    texto_resumo = db.Column(db.Text, nullable=False)
    data_geracao = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    # Garante que não haverá mais de um resumo para a mesma semana/ano
    __table_args__ = (db.UniqueConstraint('ano', 'semana', name='_ano_semana_uc'),)

    def __repr__(self):
        return f'<Resumo Semanal {self.ano}-W{self.semana}>'
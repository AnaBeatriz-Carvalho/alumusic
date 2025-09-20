import sys
import os
import uuid
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# --- Ajusta o path para achar o pacote 'app' mesmo estando na raiz ---
sys.path.append(os.path.abspath("app"))

# Agora dá para importar normalmente
from app.extensions import db
from app.models.summary import WeeklySummary

# --- Carrega variáveis de ambiente ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
if not DATABASE_URI:
    raise RuntimeError("❌ Variável SQLALCHEMY_DATABASE_URI não encontrada no .env")

print(f"🔗 Conectando no banco: {DATABASE_URI}")

# --- Testa conexão manual ---
try:
    engine = create_engine(DATABASE_URI)
    with engine.connect() as conn:
        print("✅ Conexão bem-sucedida com o banco!")
except Exception as e:
    print("❌ Erro ao conectar no banco:", e)
    exit(1)

# --- Cria sessão para inserir registros ---
Session = sessionmaker(bind=engine)
session = Session()

# --- Gera resumos fake das últimas 3 semanas ---
hoje = date.today()
for i in range(3):
    start = hoje - timedelta(days=(i + 1) * 7)
    end = start + timedelta(days=6)
    resumo = WeeklySummary(
        id=uuid.uuid4(),
        period_start=start,
        period_end=end,
        subject=f"Resumo da semana {i+1}",
        body=f"Resumo gerado automaticamente para testes — semana {i+1}.",
        charts_json={"grafico": f"semana_{i+1}"}
    )
    session.add(resumo)

# --- Commit no banco ---
try:
    session.commit()
    print("✅ Resumos semanais inseridos com sucesso!")
except Exception as e:
    session.rollback()
    print("❌ Erro ao inserir resumos:", e)
finally:
    session.close()

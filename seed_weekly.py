import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Text, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Definição dos Modelos (alinhado com a sua base de dados) ---
Base = declarative_base()

class WeeklySummary(Base):
    __tablename__ = 'weekly_summaries'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    # 👇 CORREÇÃO: Adicionada a coluna 'subject' que faltava
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# --- Conexão e Lógica do Script ---

# Ajuste para conectar via localhost, como o script é executado
DATABASE_URL = os.getenv('DATABASE_URL', '').replace('@alumusic:', '@localhost:')
print(f"🔗 Conectando no banco: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.execute(text("SELECT 1"))
    print("✅ Conexão bem-sucedida com o banco!")
except Exception as e:
    print(f"❌ Falha na conexão com o banco: {e}")
    exit()

# --- Dados de Exemplo ---
for i in range(3):
    end_date = datetime.utcnow().date() - timedelta(weeks=i)
    start_date = end_date - timedelta(days=6)
    
    summary_text_exemplo = f"""
    **Principais Elogios da Semana {i+1}:**
    - A qualidade de produção do novo single foi amplamente elogiada.
    - As performances ao vivo continuam a receber feedback extremamente positivo.

    **Principais Críticas da Semana {i+1}:**
    - Houve reclamações sobre a instabilidade da aplicação em dispositivos Android.
    - O preço dos bilhetes para o próximo festival foi um ponto de crítica recorrente.

    **Sugestões Acionáveis da Semana {i+1}:**
    - Utilizadores sugeriram a criação de playlists colaborativas.
    """

    print(f"\nGerando resumo para a semana de {start_date.strftime('%d/%m')} a {end_date.strftime('%d/%m')}...")
    
    # 👇 CORREÇÃO: Adicionado o valor para o campo 'subject'
    resumo = WeeklySummary(
        period_start=start_date,
        period_end=end_date,
        subject=f"Resumo Semanal: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
        body=summary_text_exemplo.strip()
    )
    
    session.add(resumo)

# Salva todas as mudanças na base de dados
session.commit()
print("\n🎉 3 resumos semanais de teste foram criados com sucesso na base de dados!")

session.close()


import click
from datetime import datetime, timedelta
import random
from app.extensions import db
from app.models.user import Usuario
from app.models.comment import Comentario
from app.models.summary import WeeklySummary
from app.core.llm_service import generate_weekly_summary

SAMPLE_COMMENTS = [
    "A nova música é incrível, a produção está impecável!",
    "O clipe da banda é uma obra de arte, adorei a narrativa.",
    "A letra desta faixa é um pouco fraca, esperava mais.",
    "O show foi sensacional! Que energia contagiante ao vivo.",
    "Porque é que a plataforma não tem um modo offline para playlists?",
    "Sugestão: uma integração com as letras das músicas seria perfeita.",
    "O som do álbum está muito comprimido, a mixagem podia ser melhor.",
    "A batida viciante desta música é perfeita para treinar.",
    "O preço do bilhete para o festival está muito caro este ano.",
    "Quando será o lançamento do próximo álbum?",
    "A qualidade do som no concerto de ontem estava péssima.",
    "A voz deste cantor é simplesmente espetacular.",
    "A fila para entrar no espetáculo estava desorganizada e demorou horas.",
    "A capa do álbum é linda, combina perfeitamente com o som.",
    "O solo de guitarra nesta faixa é de outro mundo!"
]

def register_commands(app):
    @app.cli.command("seed-historical-data")
    @click.option('--weeks', default=4, help='Número de semanas de dados históricos a serem gerados.')
    def seed_command(weeks):
        """
        Cria um utilizador de teste (se não existir) e popula a base de dados com
        comentários e resumos semanais para N semanas passadas.
        """
        print(f">>> A iniciar o processo de seeding para {weeks} semanas...")
        
        # 1. Cria um utilizador de teste se não existir
        usuario = db.session.scalar(db.select(Usuario).filter_by(email="curador@alumusic.com"))
        if not usuario:
            print(">>> Utilizador de teste 'curador@alumusic.com' não encontrado. A criar...")
            usuario = Usuario(email="curador@alumusic.com")
            usuario.set_password("senha123")
            db.session.add(usuario)
            # 👇 CORREÇÃO: Salva o novo utilizador imediatamente para gerar o seu ID
            db.session.commit()
            print(">>> Utilizador de teste criado com sucesso.")
        
        # 2. Gera dados históricos
        for i in range(weeks):
            end_date = datetime.utcnow().date() - timedelta(weeks=i)
            start_date = end_date - timedelta(days=6)
            print(f"--- A processar semana de {start_date.strftime('%d/%m')} a {end_date.strftime('%d/%m')} ---")

            comentarios_semana = []
            comment_texts = []
            for j in range(random.randint(15, 30)):
                data_comentario = start_date + timedelta(days=random.randint(0, 6), hours=random.randint(0, 23))
                texto = random.choice(SAMPLE_COMMENTS)
                comment_texts.append(texto)
                comentarios_semana.append(Comentario(
                    texto=texto,
                    usuario_id=usuario.id, # Agora usuario.id terá um valor
                    status='CONCLUIDO',
                    categoria=random.choice(["ELOGIO", "CRÍTICA", "SUGESTÃO", "DÚVIDA"]),
                    confianca=random.uniform(0.8, 0.99),
                    data_recebimento=data_comentario
                ))
            
            db.session.add_all(comentarios_semana)
            
            summary_text = generate_weekly_summary(comment_texts)
            novo_resumo = WeeklySummary(
                start_date=start_date,
                end_date=end_date,
                summary_text=summary_text
            )
            db.session.add(novo_resumo)
            print(f"✅ {len(comentarios_semana)} comentários e 1 resumo gerados para a semana.")

        db.session.commit()
        print(f"\n🎉 Seeding de dados históricos para {weeks} semanas concluído com sucesso!")

    @app.cli.command("generate-summary")
    def generate_summary_command():
        """
        Aciona a tarefa de resumo semanal manualmente para fins de teste.
        """
        from tasks.weekly_summary import generate_weekly_summary_task
        print(">>> A enfileirar a tarefa de resumo semanal...")
        generate_weekly_summary_task.delay()
        print(">>> Tarefa enfileirada com sucesso! Verifique os logs do worker e o MailHog.")
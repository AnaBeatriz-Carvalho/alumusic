import click
from datetime import datetime, timedelta
from app.extensions import db
from app.models.user import Usuario
from app.models.comment import Comentario
from app.models.summary import WeeklySummary


def register_commands(app):
    @app.cli.command("seed-db")
    @click.argument("count", type=int)
    def seed_db(count):
        # Comando CLI para popular o banco de dados com comentários de teste
        user = db.session.scalar(db.select(Usuario).limit(1))
        if not user:
            print("ERRO: Nenhum usuário encontrado. Por favor, registre um usuário primeiro.")
            return

        print(f"Gerando {count} comentários para o usuário {user.email}...")
        comments = []
        for i in range(count):
            comments.append(Comentario(
                texto=f"Este é um comentário de teste gerado via CLI número {i+1}.",
                usuario_id=user.id,
                status='PENDENTE'
            ))
        
        db.session.add_all(comments)
        db.session.commit()
        print(f"{count} comentários inseridos com sucesso (com status PENDENTE).")

    @app.cli.command("trigger-summary")
    def trigger_summary_task_command():
        """
        Aciona a tarefa de geração de resumo semanal manualmente para fins de teste.
        """
        # 👇 A importação é feita AQUI, dentro da função, quebrando o ciclo.
        from tasks.weekly_summary import generate_weekly_summary_task
        
        print(">>> Enfileirando a tarefa de resumo semanal...")
        generate_weekly_summary_task.delay()
        print(">>> Tarefa enfileirada com sucesso! Verifique os logs do worker e o MailHog.")
    
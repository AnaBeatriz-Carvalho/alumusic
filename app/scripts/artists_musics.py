from app import create_app
from app.extensions import db
from app.models.artists import Artista
from app.models.music import Musica
import logging

logger = logging.getLogger(__name__)

def init_database():
    """Inicializa o banco de dados com dados básicos"""
    app = create_app()
    with app.app_context():
        try:
            # Verificar se já existem artistas
            if Artista.query.count() > 0:
                logger.info("Banco já possui artistas. Pulando inicialização.")
                return

            logger.info("Inicializando banco de dados com dados básicos...")
            
            artistas = [
                ("Ana Silva", "ana-silva"),
                ("Banda Exemplo", "banda-exemplo"),
                ("DJ Teste", "dj-teste"),
                ("Rock Nacional", "rock-nacional"),
                ("MPB Clássica", "mpb-classica"),
                ("Eletrônica BR", "eletronica-br"),
            ]
            
            created = {}
            for nome, slug in artistas:
                a = Artista.query.filter_by(nome=nome).first()
                if not a:
                    a = Artista(nome=nome, slug=slug)
                    db.session.add(a)
                    db.session.flush()
                    logger.info(f"Artista criado: {nome}")
                created[nome] = a

            # Músicas vinculadas
            musicas = [
                ("Canção da Ana", created["Ana Silva"].id),
                ("Balada Romântica", created["Ana Silva"].id),
                ("Hit da Banda", created["Banda Exemplo"].id),
                ("Rock Brasileiro", created["Banda Exemplo"].id),
                ("Mix Teste", created["DJ Teste"].id),
                ("Beat Eletrônico", created["DJ Teste"].id),
                ("Clássico Nacional", created["Rock Nacional"].id),
                ("Guitarra Brasileira", created["Rock Nacional"].id),
                ("MPB Tradicional", created["MPB Clássica"].id),
                ("Samba Moderno", created["MPB Clássica"].id),
                ("House Music", created["Eletrônica BR"].id),
                ("Techno Brasil", created["Eletrônica BR"].id),
            ]
            
            for titulo, artista_id in musicas:
                if not Musica.query.filter_by(titulo=titulo, artista_id=artista_id).first():
                    db.session.add(Musica(titulo=titulo, artista_id=artista_id))
                    logger.info(f"Música criada: {titulo}")

            db.session.commit()
            logger.info("Inicialização do banco de dados concluída com sucesso!")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise

if __name__ == "__main__":
    init_database()
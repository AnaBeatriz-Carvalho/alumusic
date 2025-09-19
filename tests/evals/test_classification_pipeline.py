import pytest
import time
import json
from pathlib import Path
import sys
import uuid 

# Adiciona o diretório raiz para permitir importações da aplicação
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

# Importa os helpers e os modelos do app
from tests.helpers import get_auth_token, generate_test_comments, run_bulk_load
from app.extensions import db
from app.models.comment import Comentario, TagFuncionalidade

from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd

# Carrega o gabarito uma vez
EVAL_DATASET_PATH = ROOT_DIR / "tests" / "evals" / "dataset.json"
with open(EVAL_DATASET_PATH, 'r', encoding='utf-8') as f:
    GABARITO = json.load(f)

# Define o usuário de teste
TEST_USER_EMAIL = "email@teste.com"
TEST_USER_PASSWORD = "teste123"

@pytest.mark.e2e
def test_classification_pipeline(app):
    """
    Teste de ponta a ponta que agora executa dentro do contexto da aplicação.
    """
    # Abre um contexto para a Fase 1
    with app.app_context():
        # --- FASE 1: SETUP E CARGA DE DADOS ---
        token = get_auth_token(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        comments_to_load = generate_test_comments(GABARITO)
        comment_ids_map = {item["texto"]: item["id"] for item in comments_to_load}
        run_bulk_load(token, comments_to_load)

    # --- FASE 2: AGUARDAR PROCESSAMENTO ---
    # Tempo de espera para que os workers processem os 100+ comentários.
    # Este valor pode precisar de ajuste dependendo da velocidade da API da LLM.
    processing_time_seconds = 300 
    print(f"\nCarga enviada. Aguardando {processing_time_seconds} segundos para o processamento...")
    time.sleep(processing_time_seconds)

    # --- FASE 3: COLETA E AVALIAÇÃO DOS RESULTADOS ---
    print("Iniciando a coleta de resultados do banco de dados...")
    
    # Abre um NOVO contexto para a Fase 3, garantindo uma sessão de DB válida.
    with app.app_context():
        y_true_cat = []  # Lista para as categorias REAIS (gabarito)
        y_pred_cat = []  # Lista para as categorias PREVISTAS (IA)
        tag_matches = 0

        for item_gabarito in GABARITO:
            texto_original = item_gabarito["texto"]
            comment_id_str = comment_ids_map[texto_original]
            comment_id = uuid.UUID(comment_id_str)
            
            # Busca o resultado do processamento no banco de dados
            comentario_processado = db.session.get(Comentario, comment_id)

            # Verificações importantes
            assert comentario_processado is not None, f"Comentário '{texto_original}' não foi encontrado no DB."
            # Assert aprimorado para dar mais detalhes em caso de falha
            assert comentario_processado.status == "CONCLUIDO", f"Comentário '{texto_original}' não foi processado a tempo (status atual: {comentario_processado.status})."

            # Prepara os dados para comparação
            categoria_esperada = item_gabarito["categoria_esperada"]
            tags_esperadas = sorted(item_gabarito["tags_esperadas"])
            
            categoria_prevista = comentario_processado.categoria
            tags_previstas = sorted([tag.codigo for tag in comentario_processado.tags])

            # Adiciona os resultados nas listas na ordem correta
            y_true_cat.append(categoria_esperada) 
            y_pred_cat.append(categoria_prevista) 

            if tags_previstas == tags_esperadas:
                tag_matches += 1

        # --- FASE 4: GERAÇÃO DO RELATÓRIO ---
        print_report(y_true_cat, y_pred_cat, tag_matches, len(GABARITO))

def print_report(y_true_cat, y_pred_cat, tag_matches, total_items):
    """Imprime o relatório final de métricas no console."""
    print("\n" + "="*60)
    print(" Relatório Final de Avaliação da Pipeline de Classificação ".center(60, "="))
    print("="*60 + "\n")

    # Garante que todas as categorias do gabarito apareçam no relatório
    labels = sorted(list(set(y_true_cat)))
    
    print(">>> Métricas de Classificação de Categoria:")
    # 'zero_division=0' evita avisos caso uma categoria nunca tenha sido prevista
    print(classification_report(y_true_cat, y_pred_cat, labels=labels, zero_division=0))

    print(">>> Matriz de Confusão (Real vs. Previsto):")
    conf_matrix = confusion_matrix(y_true_cat, y_pred_cat, labels=labels)
    conf_matrix_df = pd.DataFrame(conf_matrix, index=[f"Real: {l}" for l in labels], columns=[f"Prev: {l}" for l in labels])
    print(conf_matrix_df)
    print("\n")
    
    tag_accuracy = (tag_matches / total_items)
    print(">>> Métricas de Extração de Tags:")
    print(f"Acurácia de Tags (correspondência exata): {tag_accuracy:.2%}")
    print("\n" + "="*60)


import requests
import json
import uuid

API_URL = "http://api:5000" 

def get_auth_token(email, password):
    # Realiza login e retorna o token JWT
    print(f"Autenticando com o usuário {email}...")
    try:
        resp = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
        resp.raise_for_status()
        print("Autenticação bem-sucedida!")
        return resp.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"Erro ao autenticar: {e}")
       
        raise

def generate_test_comments(dataset):
    # Gera uma lista de comentários com UUIDs para a carga de teste.
    comments_to_load = []
    for item in dataset:
        comments_to_load.append({
            "id": str(uuid.uuid4()),
            "texto": item["texto"]
        })
    return comments_to_load

def run_bulk_load(token, comments):
    # Envia uma lista de comentários para a API em uma única requisição.
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Enviando {len(comments)} comentários em lote para a API...")
    try:
        resp = requests.post(f"{API_URL}/api/comentarios", json=comments, headers=headers)
        resp.raise_for_status()
        print("Carga de dados enviada com sucesso!")
        return resp.json().get("ids_enfileirados", [])
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar carga de dados: {e}")
        raise
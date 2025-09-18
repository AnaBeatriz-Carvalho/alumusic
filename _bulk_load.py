# bulk_load.py
import requests
import json
import time

# --- CONFIGURAÇÕES ---
# IMPORTANTE: Use o URL do seu host local, não o nome do serviço Docker.
# O script roda na sua máquina, não dentro da rede Docker.
API_URL = "http://localhost:5001" 
# Crie este usuário na sua aplicação ou use um que já exista
USER_EMAIL = "ana@teste.com"
USER_PASSWORD = "senha123"
JSON_FILE_PATH = "comentarios_carga.json"
BATCH_SIZE = 50  # Enviar em lotes de 50 para não sobrecarregar uma única requisição

def get_auth_token():
    """Faz login na API e retorna o token de acesso."""
    print("Autenticando para obter o token...")
    try:
        resp = requests.post(f"{API_URL}/auth/login", json={"email": USER_EMAIL, "password": USER_PASSWORD})
        resp.raise_for_status()  # Lança um erro se a requisição falhar (status 4xx ou 5xx)
        token = resp.json()["access_token"]
        print("Autenticação bem-sucedida!")
        return token
    except requests.exceptions.RequestException as e:
        print(f"Erro ao autenticar: {e}")
        return None

def send_comments_in_batches(token, comments):
    """Envia a lista de comentários em lotes."""
    headers = {"Authorization": f"Bearer {token}"}
    total_comments = len(comments)
    
    for i in range(0, total_comments, BATCH_SIZE):
        batch = comments[i:i + BATCH_SIZE]
        print(f"Enviando lote {i//BATCH_SIZE + 1}/{(total_comments + BATCH_SIZE - 1)//BATCH_SIZE} (comentários {i+1} a {i+len(batch)})...")
        
        try:
            resp = requests.post(f"{API_URL}/api/comentarios", json=batch, headers=headers)
            
            if resp.status_code == 202:
                print(f"  -> Lote enviado com sucesso! Status: {resp.status_code}")
                # print(f"  -> Resposta: {resp.json()}")
            else:
                print(f"  -> Erro ao enviar lote. Status: {resp.status_code}, Resposta: {resp.text}")
            
            time.sleep(1) # Pequena pausa para não sobrecarregar o servidor
        
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão ao enviar lote: {e}")

if __name__ == "__main__":
    token = get_auth_token()
    
    if token:
        try:
            with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
                all_comments = json.load(f)
            
            send_comments_in_batches(token, all_comments)
            print("\nCarga massiva concluída!")
        except FileNotFoundError:
            print(f"Erro: Arquivo '{JSON_FILE_PATH}' não encontrado. Execute o script 'generate_data.py' primeiro.")
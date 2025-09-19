import io
import json
import pytest


def test_llm_upload_requires_auth(app):
    """Verifica que o endpoint exige autenticação (401/403) quando chamado sem token."""
    client = app.test_client()
    csv_content = "texto\nEste é um elogio\nIsto é uma crítica"
    data = {
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'comentarios.csv')
    }

    resp = client.post('/api/llm/analyze', data=data, content_type='multipart/form-data')
    assert resp.status_code in (401, 403)


def test_llm_upload_with_token_can_enqueue(app):
    """Se existir suporte a autenticação em testes, este teste tentará usar um token de teste.
    Caso o projeto tenha fixtures para criar usuários e tokens, substitua este teste por uma versão
    que obtenha token via endpoint /auth/register + /auth/login.
    """
    # Tentamos buscar um token na configuração de teste se fornecido
    test_token = app.config.get('TEST_AUTH_TOKEN')
    if not test_token:
        # Não há token configurado no ambiente de teste; pule o teste
        pytest.skip('Nenhum TEST_AUTH_TOKEN configurado para testes integrados de API')

    client = app.test_client()
    csv_content = "texto\nTeste de análise pelo LLM"
    data = {
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'comentarios.csv')
    }
    headers = {'Authorization': f'Bearer {test_token}'}
    resp = client.post('/api/llm/analyze', data=data, content_type='multipart/form-data', headers=headers)
    assert resp.status_code == 202
    body = resp.get_json()
    assert 'task_id' in body

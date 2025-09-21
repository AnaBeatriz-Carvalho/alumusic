import io
import json
import pytest


def test_llm_upload_requires_auth(app):
    
    client = app.test_client()
    csv_content = "texto\nEste é um elogio\nIsto é uma crítica"
    data = {
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'comentarios.csv')
    }

    resp = client.post('/api/llm/analyze', data=data, content_type='multipart/form-data')
    assert resp.status_code in (401, 403)


def test_llm_upload_with_token_can_enqueue(app):
        # Usa um token de autenticação pré-configurado para testes
    test_token = app.config.get('TEST_AUTH_TOKEN')
    if not test_token:
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

# streamlit_app.py

import streamlit as st
import requests
import base64
from streamlit_autorefresh import st_autorefresh 
import pandas as pd

API_URL = "http://api:5000"

st.set_page_config(page_title="Alumusic", layout="wide")
st.title("Alumusic")

# Sessão para armazenar token e email
if "token" not in st.session_state:
    st.session_state.token = None
if "email" not in st.session_state:
    st.session_state.email = None

def show_login():
    st.header("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")
        if submit:
            resp = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
            if resp.status_code == 200:
                st.session_state.token = resp.json()["access_token"]
                st.session_state.email = email
                st.success("Login realizado!")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

def show_register():
    st.header("Registrar")
    with st.form("register_form"):
        email = st.text_input("Email (registro)")
        password = st.text_input("Senha (registro)", type="password")
        submit = st.form_submit_button("Registrar")
        if submit:
            resp = requests.post(f"{API_URL}/auth/register", json={"email": email, "password": password})
            if resp.status_code == 201:
                st.success("Usuário registrado! Faça login.")
            else:
                st.error(f"Erro ao registrar: {resp.text}")

def show_dashboard():
    st.header("Dashboard Privado")
    
    # Botão de logout
    if st.button("Logout"):
        st.session_state.token = None
        st.session_state.email = None
        st.rerun()

    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    # 1. Buscar comentários
    st.subheader("Meus Comentários")
    resp = requests.get(f"{API_URL}/api/comentarios", headers=headers)
    if resp.status_code == 200:
        comentarios = resp.json().get("comentarios", [])
        if comentarios:
            comentarios_display = []
            for comentario in comentarios:
                comentarios_display.append({
                    "Data": comentario.get("data_recebimento", "").split("T")[0] if comentario.get("data_recebimento") else "",
                    "Texto": comentario.get("texto", ""),
                    "Associado a": comentario.get("associado_a", "Não especificado")
                })
            df = pd.DataFrame(comentarios_display)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nenhum comentário encontrado.")
    else:
        st.error("Erro ao buscar comentários.")

    # 2. Buscar artistas e músicas
    st.subheader("Enviar Novo Comentário")
    artistas_resp = requests.get(f"{API_URL}/api/artistas")
    musicas_resp = requests.get(f"{API_URL}/api/musicas")

    if artistas_resp.status_code == 200 and musicas_resp.status_code == 200:
        artistas = artistas_resp.json()
        musicas = musicas_resp.json()

        artistas_opcoes = {artista["nome"]: artista["id"] for artista in artistas}
        musicas_opcoes = {musica["titulo"]: musica["id"] for musica in musicas}

        # Rádio fora do form → atualiza automaticamente
        tipo_selecionado = st.radio(
            "Associar comentário a:",
            ["Artista", "Música"],
            key="tipo_associacao"
        )

        with st.form("comment_form"):
            comentario = st.text_area("Comentário")

            if tipo_selecionado == "Artista":
                artista_selecionado = st.selectbox(
                    "Selecione o Artista",
                    options=["Selecione um artista"] + list(artistas_opcoes.keys()),
                    key="artista_select"
                )
                musica_selecionada = None
            else:
                musica_selecionada = st.selectbox(
                    "Selecione a Música",
                    options=["Selecione uma música"] + list(musicas_opcoes.keys()),
                    key="musica_select"
                )
                artista_selecionado = None

            enviar = st.form_submit_button("Enviar Comentário")

            if enviar:
                if not comentario:
                    st.error("O texto do comentário é obrigatório.")
                elif tipo_selecionado == "Artista" and artista_selecionado == "Selecione um artista":
                    st.error("Por favor, selecione um artista válido.")
                elif tipo_selecionado == "Música" and musica_selecionada == "Selecione uma música":
                    st.error("Por favor, selecione uma música válida.")
                else:
                    artista_id = artistas_opcoes.get(artista_selecionado)
                    musica_id = musicas_opcoes.get(musica_selecionada)

                    payload = {"texto": comentario}
                    if artista_id:
                        payload["artista_id"] = artista_id
                    if musica_id:
                        payload["musica_id"] = musica_id

                    resp = requests.post(f"{API_URL}/api/comentarios", json=payload, headers=headers)
                    if resp.status_code == 201:
                        st.success("Comentário enviado com sucesso!")
                        st.rerun()
                    else:
                        st.error(f"Erro ao enviar comentário: {resp.text}")
    else:
        st.error("Erro ao carregar artistas ou músicas.")


    # 2. Ver histórico de classificações
    st.subheader("Histórico de Classificações")
    resp = requests.get(f"{API_URL}/api/classificacoes", headers=headers)
    if resp.status_code == 200:
        historico = resp.json().get("classificacoes", [])
        if historico:
            # Preparar dados para exibição
            classificacoes_display = []
            for item in historico:
                classificacoes_display.append({
                    "Data": item.get("data_processamento", "").split("T")[0] if item.get("data_processamento") else "",
                    "Texto": item.get("texto", "")[:50] + "..." if len(item.get("texto", "")) > 50 else item.get("texto", ""),
                    "Categoria": item.get("categoria", "Não classificado"),
                    "Confiança": f"{item.get('confianca', 0):.2f}" if item.get('confianca') else "N/A",
                    "Tag": item.get("tag_nome", ""),
                    "Associado a": item.get("associado_a", "Não especificado")
                })
            
            df_hist = pd.DataFrame(classificacoes_display)
            st.dataframe(df_hist, use_container_width=True)
        else:
            st.info("Nenhuma classificação encontrada.")
    else:
        st.error("Erro ao buscar histórico de classificações.")

    # 3. Exportar dados
    st.subheader("Exportar Dados")
    if st.button("Exportar Comentários CSV"):
        if comentarios:
            df = pd.DataFrame(comentarios)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Baixar CSV de Comentários",
                data=csv,
                file_name='comentarios.csv',
                mime='text/csv'
            )
        else:
            st.info("Nenhum comentário para exportar.")

    if st.button("Exportar Classificações CSV"):
        if historico:
            df_hist = pd.DataFrame(historico)
            csv = df_hist.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Baixar CSV de Classificações",
                data=csv,
                file_name='classificacoes.csv',
                mime='text/csv'
            )
        else:
            st.info("Nenhuma classificação para exportar.")

def show_relatorio():
    st_autorefresh(interval=60000, key="relatorio_refresh")
    st.header("Relatório em tempo real (última semana)")
    
    try:
        resp = requests.get(f"{API_URL}/api/relatorio/semana", timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            graficos = data.get("graficos", [])
            mensagem = data.get("mensagem", "")
            
            if mensagem:
                st.info(mensagem)
            
            st.write(f"Número de gráficos retornados: {len(graficos)}")
            
            for graf in graficos:
                st.subheader(graf["titulo"])
                try:
                    st.image(base64.b64decode(graf["imagem_base64"]), use_column_width=True)
                except Exception as e:
                    st.error(f"Erro ao exibir gráfico: {e}")
        else:
            st.error(f"Erro ao carregar relatório: {resp.status_code}")
    except requests.exceptions.Timeout:
        st.error("Timeout ao carregar relatório. Tente novamente.")
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {e}")

# --- Interface principal ---
if st.session_state.token:
    menu = st.sidebar.radio("Menu", ["Dashboard", "Relatório em tempo real"])
    if menu == "Dashboard":
        show_dashboard()
    else:
        show_relatorio()
else:
    aba = st.radio("Escolha uma opção:", ["Login", "Registrar", "Relatório em tempo real"])
    if aba == "Login":
        show_login()
    elif aba == "Registrar":
        show_register()
    else:
        show_relatorio()
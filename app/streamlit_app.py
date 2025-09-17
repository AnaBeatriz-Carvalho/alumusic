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
    st.subheader("Buscar Comentários")
    resp = requests.get(f"{API_URL}/api/comentarios", headers=headers)
    if resp.status_code == 200:
        comentarios = resp.json().get("comentarios", [])
        if comentarios:
            df = pd.DataFrame(comentarios)
            st.dataframe(df)
        else:
            st.info("Nenhum comentário encontrado.")
    else:
        st.error("Erro ao buscar comentários.")

    # 2. Ver histórico de classificações
    st.subheader("Histórico de Classificações")
    resp = requests.get(f"{API_URL}/api/classificacoes", headers=headers)
    if resp.status_code == 200:
        historico = resp.json().get("classificacoes", [])
        if historico:
            df_hist = pd.DataFrame(historico)
            st.dataframe(df_hist)
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

    # Enviar novo comentário
    st.subheader("Enviar Comentário")
    with st.form("comment_form"):
        comentario = st.text_area("Comentário")
        enviar = st.form_submit_button("Enviar")
        if enviar:
            resp = requests.post(
                f"{API_URL}/api/comentarios",
                json={"texto": comentario},
                headers=headers
            )
            if resp.status_code == 202:
                st.success("Comentário enviado!")
            else:
                st.error(f"Erro ao enviar: {resp.text}")

def show_relatorio():
    st_autorefresh(interval=60000, key="relatorio_refresh")
    st.header("Relatório em tempo real (última semana)")
    try:
        resp = requests.get(f"{API_URL}/api/relatorio/semana")
        if resp.status_code == 200:
            graficos = resp.json().get("graficos", [])
            for graf in graficos:
                st.subheader(graf["titulo"])
                st.image(base64.b64decode(graf["imagem_base64"]), use_column_width=True)
        else:
            st.error("Erro ao carregar relatório.")
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
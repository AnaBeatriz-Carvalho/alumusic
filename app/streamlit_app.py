# streamlit_app.py

import streamlit as st
import requests

API_URL = "http://api:5000" # ajuste se necessário

st.title("Alumusic - Demo Frontend")

# Sessão para armazenar token
if "token" not in st.session_state:
    st.session_state.token = None

# Registro
st.header("Registrar")
with st.form("register_form"):
    reg_email = st.text_input("Email (registro)")
    reg_password = st.text_input("Senha (registro)", type="password")
    reg_submit = st.form_submit_button("Registrar")
    if reg_submit:
        resp = requests.post(f"{API_URL}/auth/register", json={"email": reg_email, "password": reg_password})
        if resp.status_code == 201:
            st.success("Usuário registrado com sucesso!")
        else:
            st.error(f"Erro ao registrar: {resp.text}")

# Login
st.header("Login")
with st.form("login_form"):
    login_email = st.text_input("Email (login)")
    login_password = st.text_input("Senha (login)", type="password")
    login_submit = st.form_submit_button("Entrar")
    if login_submit:
        resp = requests.post(f"{API_URL}/auth/login", json={"email": login_email, "password": login_password})
        if resp.status_code == 200:
            st.session_state.token = resp.json()["access_token"]
            st.success("Login realizado!")
        else:
            st.error("Usuário ou senha inválidos.")

# Enviar comentário
if st.session_state.token:
    st.header("Enviar Comentário")
    with st.form("comment_form"):
        comentario = st.text_area("Comentário")
        enviar = st.form_submit_button("Enviar")
        if enviar:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            resp = requests.post(f"{API_URL}/api/comentarios", json={"texto": comentario}, headers=headers)
            if resp.status_code == 202:
                st.success("Comentário enviado!")
            else:
                st.error(f"Erro ao enviar: {resp.text}")
else:
    st.info("Faça login para enviar comentários.")
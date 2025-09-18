# streamlit_app.py

import streamlit as st
import requests
import pandas as pd
import json
from streamlit_autorefresh import st_autorefresh

# O URL da sua API rodando no Docker
API_URL = "http://api:5000"

st.set_page_config(page_title="AluMusic Insights", layout="wide")
st.title("🔎 AluMusic Insights")

# --- GERENCIAMENTO DE SESSÃO E AUTENTICAÇÃO (Sem alterações) ---
if "token" not in st.session_state:
    st.session_state.token = None
if "email" not in st.session_state:
    st.session_state.email = None

def show_login():
    st.header("Login da Equipe de Curadoria")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")
        if submit:
            resp = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
            if resp.status_code == 200:
                st.session_state.token = resp.json()["access_token"]
                st.session_state.email = email
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

def show_register():
    st.header("Registrar Novo Membro da Equipe")
    with st.form("register_form"):
        email = st.text_input("Email (registro)")
        password = st.text_input("Senha (registro)", type="password")
        submit = st.form_submit_button("Registrar")
        if submit:
            resp = requests.post(f"{API_URL}/auth/register", json={"email": email, "password": password})
            if resp.status_code == 201:
                st.success("Usuário registrado! Agora você pode fazer login.")
            else:
                st.error(f"Erro ao registrar: {resp.text}")

# --- DASHBOARD REATORADO ---
def show_dashboard():
    # 👇 COLOQUE ESTA LINHA AQUI 👇
    st_autorefresh(interval=15000, key="data_refresh")  # Atualiza a cada 15 segundos

    st.header(f"Dashboard de Análise - Bem-vindo(a), {st.session_state.email}")
    
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.email = None
        st.rerun()

    st.subheader("Ferramentas de Análise de Comentários")

    # --- 1. FERRAMENTAS DE FILTRO E BUSCA ---
    col1, col2, col3 = st.columns(3)
    with col1:
        search_query = st.text_input("Buscar por texto no comentário:")
    with col2:
        status_filter = st.multiselect(
            "Filtrar por Status:",
            options=["PENDENTE", "PROCESSANDO", "CONCLUIDO", "FALHOU"],
            
        )
    with col3:
        category_filter = st.multiselect(
            "Filtrar por Categoria:",
            options=["ELOGIO", "CRÍTICA", "SUGESTÃO", "DÚVIDA", "SPAM"]
        )
    
    # --- 2. CHAMADA À API COM OS FILTROS ---
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    params = {
        "search": search_query,
        "status": status_filter,
        "category": category_filter
    }
    
    try:
        resp = requests.get(f"{API_URL}/api/comentarios", headers=headers, params=params)
        
        if resp.status_code == 200:
            comentarios = resp.json().get("comentarios", [])
            
            if comentarios:
                # --- 3. EXIBIÇÃO DOS DADOS EM UMA TABELA ÚNICA E COMPLETA ---
                st.write(f"**Exibindo {len(comentarios)} comentários:**")
                
                # Prepara os dados para um DataFrame do Pandas
                data_for_df = []
                for c in comentarios:
                    tags_formatadas = ", ".join([tag['codigo'] for tag in c.get('tags', [])])
                    data_for_df.append({
                        # Adicionamos o ID aqui
                        "ID": str(c.get("id")), 
                        "Status": c.get("status"),
                        "Categoria": c.get("categoria"),
                        "Confiança": f"{c.get('confianca'):.2f}" if c.get('confianca') is not None else "N/A",
                        "Texto": c.get("texto"),
                        "Tags": tags_formatadas,
                        "Data": pd.to_datetime(c.get("data_recebimento")).strftime('%Y-%m-%d %H:%M') if c.get("data_recebimento") else "N/A"
                    })

                # Criamos o DataFrame e DEFINIMOS A ORDEM DAS COLUNAS
                df = pd.DataFrame(data_for_df)
                st.dataframe(df, 
                    column_order=("ID", "Status", "Categoria", "Confiança", "Texto", "Tags", "Data"),
                    use_container_width=True
                )

                # --- 4. FUNCIONALIDADE DE EXPORTAÇÃO ---
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Exportar Resultados para CSV",
                    data=csv,
                    file_name=f"relatorio_comentarios_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                    mime='text/csv',
                )
            else:
                st.info("Nenhum comentário encontrado com os filtros selecionados.")
        else:
            st.error(f"Erro ao buscar comentários: {resp.status_code} - {resp.text}")

    except requests.exceptions.RequestException as e:
        st.error(f"Não foi possível conectar à API. Verifique se o serviço está no ar. Erro: {e}")

# --- RELATÓRIO PÚBLICO (Sem grandes alterações) ---
def show_relatorio():
    # ... seu código para o relatório público pode continuar o mesmo ...
    # Lembre-se que ele não precisa de token.
    st.header("Relatório Público em Tempo Real")
    # ... o resto do código ...

# --- LÓGICA PRINCIPAL DE NAVEGAÇÃO ---
if st.session_state.token:
    show_dashboard()
else:
    aba = st.sidebar.radio("Navegação", ["Login", "Registrar", "Relatório Público"])
    if aba == "Login":
        show_login()
    elif aba == "Registrar":
        show_register()
    else:
        show_relatorio()
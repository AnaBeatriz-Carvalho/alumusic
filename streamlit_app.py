# streamlit_app.py

import streamlit as st
import requests
import pandas as pd
import json
import base64
from streamlit_autorefresh import st_autorefresh

# O URL da sua API rodando no Docker
API_URL = "http://api:5000"

st.set_page_config(page_title="AluMusic Insights", layout="wide")
st.title("🔎 AluMusic Insights")

# --- GERENCIAMENTO DE SESSÃO E AUTENTICAÇÃO ---
if "token" not in st.session_state:
    st.session_state.token = None
if "email" not in st.session_state:
    st.session_state.email = None

def show_login():
    # ... (seu código de login, sem alterações)
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
    # ... (seu código de registro, sem alterações)
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

# --- DASHBOARD ATUALIZADO ---
def show_dashboard():
    st_autorefresh(interval=15000, key="data_refresh")
    st.header(f"Dashboard de Análise - Bem-vindo(a), {st.session_state.email}")
    
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.email = None
        st.rerun()

    st.subheader("Ferramentas de Análise de Comentários")

    # --- Filtros (sem alterações) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        search_query = st.text_input("Buscar por texto no comentário:")
    with col2:
        status_filter = st.multiselect("Filtrar por Status:", options=["PENDENTE", "PROCESSANDO", "CONCLUIDO", "FALHOU"])
    with col3:
        category_filter = st.multiselect("Filtrar por Categoria:", options=["ELOGIO", "CRÍTICA", "SUGESTÃO", "DÚVIDA", "SPAM"])
    
    # --- Chamada à API (sem alterações) ---
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    params = {"search": search_query, "status": status_filter, "category": category_filter}
    
    try:
        resp = requests.get(f"{API_URL}/api/comentarios", headers=headers, params=params)
        
        if resp.status_code == 200:
            comentarios = resp.json().get("comentarios", [])
            
            if comentarios:
                st.write(f"**Exibindo {len(comentarios)} comentários:**")
                
                # --- Preparação e exibição do DataFrame (sem alterações) ---
                data_for_df = []
                for c in comentarios:
                    tags_formatadas = ", ".join([tag['codigo'] for tag in c.get('tags', [])])
                    data_for_df.append({
                        "ID": str(c.get("id")), "Status": c.get("status"), "Categoria": c.get("categoria"),
                        "Confiança": f"{c.get('confianca'):.2f}" if c.get('confianca') is not None else "N/A",
                        "Texto": c.get("texto"), "Tags": tags_formatadas,
                        "Data": pd.to_datetime(c.get("data_recebimento")).strftime('%Y-%m-%d %H:%M') if c.get("data_recebimento") else "N/A"
                    })
                df = pd.DataFrame(data_for_df)
                st.dataframe(df, column_order=("ID", "Status", "Categoria", "Confiança", "Texto", "Tags", "Data"), use_container_width=True)

                # --- Funcionalidade de exportação (sem alterações) ---
                col1_exp, col2_exp = st.columns(2)
                with col1_exp:
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Exportar para CSV", data=csv, file_name=f"comentarios_{pd.Timestamp.now().strftime('%Y%m%d')}.csv", mime='text/csv', key='csv_download')
                with col2_exp:
                    json_data = json.dumps(comentarios, indent=2, ensure_ascii=False).encode('utf-8')
                    st.download_button(label="📥 Exportar para JSON", data=json_data, file_name=f"comentarios_{pd.Timestamp.now().strftime('%Y%m%d')}.json", mime='application/json', key='json_download')

                # =================================================================
                # 👇 ADIÇÃO DA SEÇÃO DE DETALHES DO HISTÓRICO AQUI 👇
                # =================================================================
                st.markdown("---")
                with st.expander("🔍 Ver Detalhes de um Comentário Específico (Histórico)"):
                    id_para_buscar = st.text_input("Cole o ID do comentário da tabela acima aqui:")
                    
                    if st.button("Buscar Detalhes por ID"):
                        if id_para_buscar:
                            try:
                                resp_detalhes = requests.get(f"{API_URL}/api/comentarios/{id_para_buscar}", headers=headers)
                                if resp_detalhes.status_code == 200:
                                    detalhes = resp_detalhes.json()
                                    st.write(f"**Texto:** {detalhes['texto']}")
                                    col_d1, col_d2, col_d3 = st.columns(3)
                                    col_d1.metric("Categoria", detalhes.get('categoria', 'N/A'))
                                    col_d2.metric("Status", detalhes.get('status', 'N/A'))
                                    col_d3.metric("Confiança da IA", f"{detalhes.get('confianca', 0):.1%}" if detalhes.get('confianca') else "N/A")
                                    st.write("**Tags de Funcionalidades Identificadas:**")
                                    if detalhes.get('tags'):
                                        for tag in detalhes['tags']:
                                            st.markdown(f"- **{tag['codigo']}:** *{tag['explicacao']}*")
                                    else:
                                        st.info("Nenhuma tag foi identificada para este comentário.")
                                else:
                                    st.error(f"Erro ao buscar detalhes: {resp_detalhes.json().get('erro', 'ID não encontrado')}")
                            except Exception as e:
                                st.error(f"Ocorreu um erro na requisição: {e}")
                        else:
                            st.warning("Por favor, insira um ID para buscar.")

            else:
                st.info("Nenhum comentário encontrado com os filtros selecionados.")
        else:
            st.error(f"Erro ao buscar comentários: {resp.status_code} - {resp.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Não foi possível conectar à API. Verifique se o serviço está no ar. Erro: {e}")

# --- RELATÓRIO PÚBLICO ---
def show_relatorio():
    # ... (seu código do relatório, sem alterações) ...
    st_autorefresh(interval=60000, key="relatorio_refresh")
    st.header("Relatório Público em Tempo Real")
    try:
        resp = requests.get(f"{API_URL}/api/relatorio/semana", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            graficos = data.get("graficos", [])
            if not graficos:
                st.info("Os dados para o relatório ainda estão sendo gerados. Por favor, aguarde e a página será atualizada em breve.")
            for graf in graficos:
                st.subheader(graf["titulo"])
                st.image(base64.b64decode(graf["imagem_base64"]), use_column_width=True)
        elif resp.status_code == 202:
            st.info(resp.json().get("mensagem"))
        else:
            st.error(f"Erro ao carregar relatório: {resp.status_code} - {resp.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com a API do relatório: {e}")

# --- LÓGICA PRINCIPAL DE NAVEGAÇÃO ---
if st.session_state.token:
    # ... (sua navegação para usuário logado, sem alterações) ...
    st.sidebar.title("Menu")
    pagina_selecionada = st.sidebar.radio("Navegue por", ["Dashboard de Análise", "Relatório Público"])
    if pagina_selecionada == "Dashboard de Análise":
        show_dashboard()
    else:
        show_relatorio()
else:
    # ... (sua navegação para visitante, sem alterações) ...
    st.sidebar.title("Bem-vindo(a)!")
    pagina_selecionada = st.sidebar.radio("Navegue por", ["Login", "Registrar", "Relatório Público"])
    if pagina_selecionada == "Login":
        show_login()
    elif pagina_selecionada == "Registrar":
        show_register()
    else:
        show_relatorio()
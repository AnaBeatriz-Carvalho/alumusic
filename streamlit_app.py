import streamlit as st
import requests
import pandas as pd
import json
import base64
from streamlit_autorefresh import st_autorefresh

# Configuração inicial da página
st.set_page_config(
    page_title="AluMusic Insights",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css(file_path):
    """Lê um arquivo CSS e o injeta na aplicação."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Arquivo CSS não encontrado: {file_path}")

load_css("assets/style.css")

# Variável global para a URL da API
API_URL = "http://api:5000"

# Gerenciamento de estado da sessão
if "token" not in st.session_state: st.session_state.token = None
if "email" not in st.session_state: st.session_state.email = None
if 'uploader_key' not in st.session_state: st.session_state.uploader_key = 0

# Funções para cada seção da aplicação

def show_login_register():
    """Exibe os formulários de login e registro em abas."""
    st.markdown("### 🔑 Acesso da Equipe de Curadoria")
    login_tab, register_tab = st.tabs(["Entrar", "Registrar"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="voce@alumusic.com")
            password = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                try:
                    resp = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
                    if resp.status_code == 200:
                        st.session_state.token = resp.json()["access_token"]
                        st.session_state.email = email
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha inválidos.")
                except requests.exceptions.ConnectionError:
                    st.error("Não foi possível conectar à API.")

    with register_tab:
        with st.form("register_form"):
            email = st.text_input("Email para registro", placeholder="novo.membro@alumusic.com")
            password = st.text_input("Crie uma senha", type="password")
            if st.form_submit_button("Registrar"):
                try:
                    resp = requests.post(f"{API_URL}/auth/register", json={"email": email, "password": password})
                    if resp.status_code == 201:
                        st.success("Usuário registrado! Agora pode fazer login.")
                    else:
                        st.error(f"Erro ao registrar: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Não foi possível conectar à API.")

def show_history_analysis(headers):
    # Exibe a aba de Histórico e Análise
    st_autorefresh(interval=30000, key="data_refresh")
    with st.container():
        st.subheader("⚙️ Ferramentas de Análise de Histórico")
        col1, col2, col3 = st.columns(3)
        with col1:
            search_query = st.text_input("Buscar por texto no comentário:")
        with col2:
            status_filter = st.multiselect("Filtrar por Status:", options=["PENDENTE", "PROCESSANDO", "CONCLUIDO", "FALHOU"])
        with col3:
            category_filter = st.multiselect("Filtrar por Categoria:", options=["ELOGIO", "CRÍTICA", "SUGESTÃO", "DÚVIDA", "SPAM"])
    
    params = {"search": search_query, "status": status_filter, "category": category_filter}
    try:
        resp = requests.get(f"{API_URL}/api/comentarios", headers=headers, params=params)
        if resp.status_code == 200:
            comentarios = resp.json().get("comentarios", [])
            st.markdown("---")
            if comentarios:
                st.write(f"**Exibindo {len(comentarios)} comentários:**")
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
                
                # Funcionalidade de Exportação
                st.markdown("---")
                st.subheader("📥 Exportar Dados da Tabela")
                col1_exp, col2_exp, _ = st.columns([1,1,3])
                with col1_exp:
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(label="Exportar para CSV", data=csv, file_name="comentarios.csv", mime='text/csv', key='csv_download')
                with col2_exp:
                    json_data = json.dumps(comentarios, indent=2, ensure_ascii=False).encode('utf-8')
                    st.download_button(label="Exportar para JSON", data=json_data, file_name="comentarios.json", mime='application/json', key='json_download')
            else:
                st.info("Nenhum comentário encontrado com os filtros selecionados.")
    except requests.exceptions.RequestException as e:
        st.error(f"Não foi possível conectar à API. Erro: {e}")

def show_new_analysis(headers):
    """Exibe a aba para Análise de Novos Comentários."""
    st.subheader("🔍 Enviar Comentários para Análise da IA")
    st.caption("Envie um texto bruto ou um ficheiro (.csv ou .json) para ser processado e adicionado ao histórico.")

    text_upload_tab, file_upload_tab = st.tabs(["Enviar Texto Único", "Enviar Arquivo em Lote"])

    with text_upload_tab:
        with st.form("text_upload_form"):
            text_to_analyze = st.text_area("Cole o comentário aqui:", height=150)
            if st.form_submit_button("Analisar Texto"):
                if text_to_analyze and text_to_analyze.strip():
                    with st.spinner("Enviando texto para a fila de análise..."):
                        try:
                            resp = requests.post(f"{API_URL}/api/llm/analyze", headers=headers, data={'text': text_to_analyze})
                            if resp.status_code == 202:
                                st.success(f"Texto enviado! {resp.json().get('mensagem')}")
                                st.info("O resultado aparecerá na aba 'Histórico e Análise' em breve.")
                            else:
                                st.error(f"Erro: {resp.status_code} - {resp.text}")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Erro de conexão: {e}")
                else:
                    st.warning("Por favor, insira um texto para analisar.")

    with file_upload_tab:
        uploaded_file = st.file_uploader(
            "Escolha um arquivo .csv ou .json", 
            type=['csv', 'json'], 
            key=f"file_uploader_{st.session_state.uploader_key}"
        )
        if uploaded_file is not None:
            if st.button("Analisar Arquivo"):
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                with st.spinner("Enviando arquivo para a fila de análise..."):
                    try:
                        resp = requests.post(f"{API_URL}/api/llm/analyze", headers=headers, files=files)
                        if resp.status_code == 202:
                            st.success(f"Arquivo enviado! {resp.json().get('mensagem')}")
                            st.info("Os resultados aparecerão na aba 'Histórico e Análise' em breve.")
                            st.session_state.uploader_key += 1
                            st.rerun()
                        else:
                            st.error(f"Erro ao enviar arquivo: {resp.status_code} - {resp.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Erro de conexão: {e}")

def show_qa_insights(headers):
    """Exibe a aba de Insights Q&A."""
    st.subheader("🤖 Pergunte à IA sobre as Tendências Recentes")
    st.caption("Faça uma pergunta em linguagem natural com base nos resumos das últimas semanas.")
    question = st.text_area("Sua pergunta:", placeholder="Quais foram as principais críticas sobre os shows nas últimas semanas?", height=100, key="qa_question")
    
    if st.button("Enviar Pergunta", key="ask_button"):
        if question and question.strip():
            payload = {"pergunta": question}
            with st.spinner("Analisando resumos e gerando resposta..."):
                try:
                    resp = requests.post(f"{API_URL}/api/insights/perguntar", json=payload, headers=headers, timeout=30)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.info("**Resposta da IA:**")
                        st.markdown(data.get("texto_gerado"))
                        st.caption(f"Fontes consultadas: Resumos das semanas {', '.join(data.get('semanas_citadas', []))}")
                    else:
                        st.error(f"Erro ao processar a pergunta: {resp.json().get('erro', resp.text)}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Não foi possível conectar à API de insights. Erro: {e}")
        else:
            st.warning("Escreva uma pergunta antes de enviar.")

def show_stakeholder_management(headers):
    """Exibe a aba para Gerenciar Stakeholders."""
    st.subheader("📬 Gerir Stakeholders do Relatório Semanal")
    st.caption("Adicione ou remova os e-mails que receberão o resumo por e-mail.")

    try:
        resp = requests.get(f"{API_URL}/api/stakeholders", headers=headers)
        if resp.status_code == 200:
            stakeholders = resp.json()
            if stakeholders:
                for s in stakeholders:
                    col1, col2 = st.columns([4, 1])
                    col1.write(s['email'])
                    if col2.button("Remover", key=f"del_{s['id']}"):
                        requests.delete(f"{API_URL}/api/stakeholders/{s['id']}", headers=headers)
                        st.success(f"E-mail {s['email']} removido.")
                        st.rerun()
            else:
                st.info("Nenhum stakeholder cadastrado.")
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar stakeholders: {e}")

    st.markdown("---")
    with st.form("add_stakeholder_form"):
        new_email = st.text_input("Adicionar novo e-mail:")
        if st.form_submit_button("Adicionar Stakeholder"):
            if new_email:
                try:
                    resp = requests.post(f"{API_URL}/api/stakeholders", headers=headers, json={"email": new_email})
                    if resp.status_code == 201:
                        st.success("Stakeholder adicionado com sucesso!")
                        st.rerun()
                    else:
                        st.error(f"Erro ao adicionar: {resp.json().get('erro', resp.text)}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Erro de conexão: {e}")
            else:
                st.warning("Por favor, insira um e-mail.")

def show_relatorio():
    """Exibe a página do Relatório Público."""
    st_autorefresh(interval=60000, key="relatorio_refresh")
    st.markdown("### 📈 Relatório Público em Tempo Real")
    st.caption("Estes dados são atualizados a cada 60 segundos.")
    try:
        resp = requests.get(f"{API_URL}/api/relatorio/semana", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            graficos = data.get("graficos", [])
            if not graficos:
                st.info("Os dados para o relatório ainda estão sendo gerados...")
            cols = st.columns(2)
            for i, graf in enumerate(graficos):
                with cols[i % 2]:
                    with st.container():
                        st.subheader(graf["titulo"])
                        st.image(base64.b64decode(graf["imagem_base64"]), use_column_width=True)
        else:
            st.error(f"Erro ao carregar relatório: {resp.status_code} - {resp.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com a API do relatório: {e}")

# Roteamento principal da aplicação
st.sidebar.markdown("<h2 class='sidebar-title'>🎵 AluMusic Insights</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

if st.session_state.token:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    st.sidebar.markdown(f"👤 Logado como: **{st.session_state.email}**")
    pagina_selecionada = st.sidebar.radio("📌 Navegação", ["Dashboard de Análise", "Relatório Público"], key="nav_logado")
    
    if st.sidebar.button("🚪 Logout", key="logout_button"):
        st.session_state.token = None
        st.session_state.email = None
        st.rerun()
    
    if pagina_selecionada == "Dashboard de Análise":
        st.markdown(f"## 📊 Dashboard de Análise")
        
        history_tab, new_analysis_tab, qa_tab, stakeholder_tab = st.tabs([
            "📖 Histórico e Análise", 
            "📤 Análise de Novos Comentários", 
            "🤖 Insights Q&A",
            "👥 Stakeholders" 
        ])
        
        with history_tab:
            show_history_analysis(headers)
        with new_analysis_tab:
            show_new_analysis(headers)
        with qa_tab:
            show_qa_insights(headers)
        with stakeholder_tab:
            show_stakeholder_management(headers)

    else:
        show_relatorio()
else:
    st.sidebar.markdown("👋 Bem-vindo(a)! ")
    pagina_selecionada = st.sidebar.radio("📌 Navegação", ["Acesso da Equipe", "Relatório Público"], key="nav_visitante")
    
    if pagina_selecionada == "Acesso da Equipe":
        show_login_register()
    else:
        show_relatorio()


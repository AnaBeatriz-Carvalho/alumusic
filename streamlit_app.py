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
    # Função para carregar um arquivo CSS e aplicá-lo ao Streamlit
    try:
        with open(file_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Arquivo de estilo não encontrado em: {file_path}")

# Carregando o CSS
load_css("assets/style.css")

API_URL = "http://api:5000"

# Gerenciamento de estado da sessão
if "token" not in st.session_state:
    st.session_state.token = None
if "email" not in st.session_state:
    st.session_state.email = None

# Funções para cada página
def show_login_register():
    # Card principal
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)

    # título dentro do card
    st.markdown("## 🔑 Acesso da Equipe de Curadoria")

    # abas de login/registro
    login_tab, register_tab = st.tabs(["Entrar", "Registrar"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="voce@alumusic.com")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar")
            if submit:
                try:
                    resp = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
                    if resp.status_code == 200:
                        st.session_state.token = resp.json()["access_token"]
                        st.session_state.email = email
                        st.success("✅ Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha inválidos.")
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ Não foi possível conectar à API.")

    with register_tab:
        with st.form("register_form"):
            email = st.text_input("Email para registro", placeholder="novo.membro@alumusic.com")
            password = st.text_input("Crie uma senha", type="password")
            submit = st.form_submit_button("Registrar")
            if submit:
                try:
                    resp = requests.post(f"{API_URL}/auth/register", json={"email": email, "password": password})
                    if resp.status_code == 201:
                        st.success("🎉 Usuário registrado! Agora você pode fazer login.")
                    else:
                        st.error(f"Erro ao registrar: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ Não foi possível conectar à API.")

    
    st.markdown('</div>', unsafe_allow_html=True)

def show_dashboard():
    st_autorefresh(interval=30000, key="data_refresh")
    st.markdown("## 📊 Dashboard de Análise")
    st.caption(f"Bem-vindo(a), {st.session_state.email}")

    with st.container():
        st.subheader("⚙️ Ferramentas de Análise")
        col1, col2, col3 = st.columns(3)
        with col1:
            search_query = st.text_input("Buscar por texto no comentário:", key="search_dash")
        with col2:
            status_filter = st.multiselect(
                "Filtrar por Status:",
                options=["PENDENTE", "PROCESSANDO", "CONCLUIDO", "FALHOU"]
            )
        with col3:
            category_filter = st.multiselect(
                "Filtrar por Categoria:",
                options=["ELOGIO", "CRÍTICA", "SUGESTÃO", "DÚVIDA", "SPAM"]
            )

    # --- Upload para análise por LLM ---
    st.markdown("---")
    st.subheader("🧠 Analisar com LLM (CSV/JSON ou texto)")
    upload_col1, upload_col2 = st.columns([2,1])
    uploaded_file = upload_col1.file_uploader("Envie um arquivo .csv ou .json (coluna 'texto' ou array de objetos)", type=['csv','json'])
    raw_text = upload_col2.text_area("Ou cole um texto para analisar (campo 'text')", height=150)
    if upload_col2.button("Enviar para LLM", key='send_llm'):
        headers_llm = {"Authorization": f"Bearer {st.session_state.token}"}
        try:
            if uploaded_file is not None:
                files = {'file': (uploaded_file.name, uploaded_file.getvalue())}
                resp_llm = requests.post(f"{API_URL}/api/llm/analyze", headers=headers_llm, files=files, timeout=60)
            elif raw_text:
                data = {'text': raw_text}
                resp_llm = requests.post(f"{API_URL}/api/llm/analyze", headers=headers_llm, data=data, timeout=60)
            else:
                st.warning("Envie um arquivo ou cole um texto antes de enviar.")
                resp_llm = None

            if resp_llm is not None:
                if resp_llm.status_code == 200:
                    resultados = resp_llm.json().get('resultados', [])
                    for r in resultados:
                        with st.expander(r.get('texto')[:120] + ('...' if len(r.get('texto'))>120 else '')):
                            st.json(r.get('analise'))
                elif resp_llm.status_code == 202:
                    body = resp_llm.json()
                    # Se o servidor retornou ids_enfileirados, atualize o histórico local
                    ids = body.get('ids_enfileirados') or body.get('ids_enfileirados', [])
                    if ids:
                        st.success(f"{len(ids)} comentários enviados e enfileirados. Atualizando histórico...")
                        # Força refresh do dashboard para puxar os comentários recém-criados
                        st.experimental_rerun()
                    else:
                        # fallback para task_id-based flow
                        task_id = body.get('task_id')
                        st.info(f"Análise enfileirada (task_id: {task_id}). Você pode checar o resultado:")
                        if st.button("Verificar resultado agora", key=f"check_{task_id}"):
                            try:
                                resp_status = requests.get(f"{API_URL}/api/tasks/{task_id}", headers=headers_llm, timeout=10)
                                if resp_status.status_code == 200:
                                    data = resp_status.json()
                                    status = data.get('status')
                                    result = data.get('result')
                                    st.write(f"Status: {status}")
                                    if result:
                                        for r in result:
                                            with st.expander(r.get('texto')[:120] + ('...' if len(r.get('texto'))>120 else '')):
                                                st.json(r.get('analise'))
                                    else:
                                        st.info("Resultado ainda não disponível. Tente novamente em alguns segundos.")
                                else:
                                    st.error(f"Erro ao consultar status: {resp_status.status_code} - {resp_status.text}")
                            except requests.exceptions.RequestException as e:
                                st.error(f"Falha ao consultar status da task: {e}")
                else:
                    st.error(f"Erro na análise: {resp_llm.status_code} - {resp_llm.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Falha ao conectar com API LLM: {e}")

    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    params = {"search": search_query, "status": status_filter, "category": category_filter}

    try:
        resp = requests.get(f"{API_URL}/api/comentarios", headers=headers, params=params)
        if resp.status_code == 200:
            comentarios = resp.json().get("comentarios", [])
            with st.container():
                if comentarios:
                    st.write(f"**Exibindo {len(comentarios)} comentários:**")
                    data_for_df = []
                    for c in comentarios:
                        # Display tag explanation when available, fall back to code
                        tags_formatadas = ", ".join([tag['codigo'] for tag in c.get('tags', [])])
                        data_for_df.append({
                            "ID": str(c.get("id")),
                            "Status": c.get("status"),
                            "Categoria": c.get("categoria"),
                            "Confiança": f"{c.get('confianca'):.2f}" if c.get('confianca') is not None else "N/A",
                            "Texto": c.get("texto"),
                            "Tags": tags_formatadas,
                            "Data": pd.to_datetime(c.get("data_recebimento")).strftime('%Y-%m-%d %H:%M')
                                    if c.get("data_recebimento") else "N/A"
                        })
                    df = pd.DataFrame(data_for_df)
                    st.dataframe(
                        df,
                        column_order=("ID", "Status", "Categoria", "Confiança", "Texto", "Tags", "Data"),
                        use_container_width=True
                    )
                    st.markdown("---")
                    st.subheader("📥 Exportar Dados")
                    col1_exp, col2_exp, _ = st.columns([1,1,3])
                    with col1_exp:
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="⬇️ Exportar para CSV",
                            data=csv,
                            file_name="comentarios.csv",
                            mime='text/csv',
                            key='csv_download'
                        )
                    with col2_exp:
                        json_data = json.dumps(comentarios, indent=2, ensure_ascii=False).encode('utf-8')
                        st.download_button(
                            label="⬇️ Exportar para JSON",
                            data=json_data,
                            file_name="comentarios.json",
                            mime='application/json',
                            key='json_download'
                        )
                else:
                    st.info("Nenhum comentário encontrado com os filtros selecionados.")
    except requests.exceptions.RequestException as e:
        st.error(f"Não foi possível conectar à API. Erro: {e}")

def show_relatorio():
    st_autorefresh(interval=60000, key="relatorio_refresh")
    st.markdown("## 📈 Relatório Público em Tempo Real")
    st.caption("Estes dados são atualizados a cada 60 segundos.")

    try:
        # public blueprint is registered under /public in the Flask app
        resp = requests.get(f"{API_URL}/public/relatorio/semana", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            graficos = data.get("graficos", [])
            if not graficos:
                st.info("⏳ Os dados para o relatório ainda estão sendo gerados...")
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

#Navegação principal
st.sidebar.markdown("<h2 class='sidebar-title'>🎵 AluMusic Insights</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

if st.session_state.token:
    st.sidebar.markdown(f"👤 Logado como: **{st.session_state.email}**")
    pagina_selecionada = st.sidebar.radio("📌 Navegação", ["Dashboard de Análise", "Relatório Público"], key="nav_logado")
    if st.sidebar.button("🚪 Logout", key="logout_button"):
        st.session_state.token = None
        st.session_state.email = None
        st.rerun()
    if pagina_selecionada == "Dashboard de Análise":
        show_dashboard()
    else:
        show_relatorio()
else:
    st.sidebar.markdown("👋 Bem-vindo(a)! Acesse o dashboard ou veja o relatório público.")
    pagina_selecionada = st.sidebar.radio("📌 Navegação", ["Acesso da Equipe", "Relatório Público"], key="nav_visitante")
    if pagina_selecionada == "Acesso da Equipe":
        show_login_register()
    else:
        show_relatorio()

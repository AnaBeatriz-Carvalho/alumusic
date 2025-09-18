def show_relatorio():
    try:
        resp = requests.get(f"{API_URL}/api/relatorio/semana", timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            graficos = data.get("graficos", [])
            mensagem = data.get("mensagem", "")
            
            if mensagem:
                st.info(mensagem)
            
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
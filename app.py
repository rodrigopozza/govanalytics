import os
import streamlit as st

st.set_page_config(
    page_title="Dashboard de Governo",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Caminho apontando corretamente para a pasta pages
logo_path = os.path.join(os.path.dirname(__file__), "pages", "logo.png")

# ==========================================
# CONFIGURAÇÃO DA BARRA LATERAL (TOPO)
# ==========================================
with st.sidebar:
    # Exibe a logo apenas uma vez (com fallback para a URL do GitHub se necessário)
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.image(
            "https://raw.githubusercontent.com/rodrigopozza/govanalytics/main/pages/logo.png",
            use_container_width=True,
        )

    st.markdown("---")

# Definindo as páginas
pg_acoes = st.Page("pages/acoes.py", title="Programas e Ações")
pg_divida = st.Page("pages/divida.py", title="Dívida")
pg_saude = st.Page("pages/saude.py", title="Saúde")
pg_educacao = st.Page("pages/educacao.py", title="Educação")

# Criando a navegação com seções
pg = st.navigation({"Indicadores": [pg_acoes, pg_divida, pg_saude, pg_educacao]})

# Executa a navegação
pg.run()
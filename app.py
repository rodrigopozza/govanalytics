import os
import streamlit as st

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Gov Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ESTILIZAÇÃO CSS GLOBAL - DESIGN SYSTEM GOV.BR
# ==========================================
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rawline:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"], [class*="st-"] {
            font-family: 'Rawline', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            color: #141414;
        }

        h1, h2, h3, .stMarkdown p {
            text-align: left;
        }

        h1 {
            font-weight: 10000 !important;
            color: #0c326f !important;
            font-size: 5rem !important;
            border-bottom: 2px solid #004587;
            padding-bottom: 8px;
        }

        h2 {
            font-weight: 600 !important;
            color: #1351b4 !important;
            margin-top: 1.5rem !important;
        }

        h3 {
            font-weight: 600 !important;
            color: #2670e8 !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# DEFINIÇÃO E EXECUÇÃO DA NAVEGAÇÃO
# ==========================================
pg_acoes = st.Page("pages/acoes.py", title="Programas e Ações")
pg_divida = st.Page("pages/divida.py", title="Dívida")
pg_saude = st.Page("pages/saude.py", title="Saúde")
pg_educacao = st.Page("pages/educacao.py", title="Educação")

# Criando a navegação com seções estilizadas
pg = st.navigation(
    {"Indicadores": [pg_acoes, pg_divida, pg_saude, pg_educacao]}
)

# Executa a navegação mantendo o padrão visual
pg.run()
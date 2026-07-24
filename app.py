import streamlit as st

# Definindo as páginas
pg_acoes = st.Page("pages/acoes.py", title="Programas e Ações")
pg_divida = st.Page("pages/divida.py", title="Dívida")
pg_saude = st.Page("pages/saude.py", title="Saúde")
pg_educacao = st.Page("pages/educacao.py", title="Educação")

# Criando a navegação com seções (opcional)
pg = st.navigation({
    "Indicarores": [pg_acoes, pg_divida, pg_saude, pg_educacao]
})

pg.run()


# ==========================================
# CONFIGURAÇÃO DA BARRA LATERAL (TOPO)
# ==========================================
with st.sidebar:
    # 1. Logo no topo da barra lateral
    st.image("logo.png", use_container_width=True)
    
    # 2. Título opcional abaixo da logo (sem nenhum texto de ícone quebrado)
    st.markdown("### GovAnalytics")
    st.markdown("---")
    
    # Seus outros elementos da barra lateral continuam aqui...

# ==========================================
# RODAPÉ DA PÁGINA PRINCIPAL (FINAL DO SCRIPT)
# ==========================================
st.markdown("---")
col_esq, col_centro, col_dir = st.columns([2, 1, 2])
with col_centro:
    st.image("logo.png", use_container_width=True)
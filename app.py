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
# RODAPÉ DA PÁGINA PRINCIPAL (FINAL DO SCRIPT)
# ==========================================
st.markdown("---")
col_esq, col_centro, col_dir = st.columns([2, 1, 2])
with col_centro:
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.image("logo.png", use_container_width=True)
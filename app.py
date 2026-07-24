import streamlit as st

# Definindo as páginas
pg_acoes = st.Page("pages/acoes.py", title="Ações")
pg_divida = st.Page("pages/divida.py", title="Dívida")
pg_saude = st.Page("pages/saude.py", title="Saúde")
pg_educacao = st.Page("pages/educacao.py", title="Educação")

# Criando a navegação com seções (opcional)
pg = st.navigation({
    "Indicarores": [pg_acoes, pg_divida, pg_saude, pg_educacao]
})

pg.run()
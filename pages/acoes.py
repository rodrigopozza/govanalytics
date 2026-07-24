import streamlit as st
import pandas as pd
import plotly.express as pdx
import numpy as np

st.set_page_config(
    page_title="Dashboard de Metas - Programas e Ações",
    page_icon="🇧🇷",
    layout="wide"
)

# Estilização inspirada no Design System do GOV.BR
st.markdown("""
    <style>
        .stApp {
            background-color: #F8F9FA;
        }
        h1 {
            color: #0C326F !important;
            font-family: 'Rawline', sans-serif, Arial;
            border-left: 6px solid #1351B4;
            padding-left: 12px;
            font-weight: 700;
        }
        h2, h3 {
            color: #1351B4 !important;
            font-family: 'Rawline', sans-serif, Arial;
        }
        [data-testid="stVerticalBlock"] div[data-testid="stContainer"] {
            background-color: #FFFFFF !important;
            border: 1px solid #D7D7D7 !important;
            border-top: 4px solid #1351B4 !important;
            padding: 12px 16px !important;
            border-radius: 4px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        [data-testid="metric-container"] {
            background-color: transparent !important;
            padding: 2px 0px !important;
        }
        div.stMarkdown h4 {
            color: #0C326F !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            margin-bottom: 6px !important;
        }
        .stRadio > div {
            background-color: #FFFFFF;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #D7D7D7;
        }
        .stButton button {
            background-color: #1351B4 !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            border-radius: 4px !important;
            border: none !important;
        }
        .stButton button:hover {
            background-color: #0C326F !important;
        }
    </style>
""", unsafe_allow_html=True)

# Mapeamento oficial de Nomes e Ícones por Código de Programa
PROGRAMAS_INFO = {
    "0000": {"nome": "ENCARGOS ESPECIAIS", "icone": "⚖️"},
    "0001": {"nome": "PROCESSO LEGISLATIVO", "icone": "🏛️"},
    "0002": {"nome": "APOIO ADMINISTRATIVO", "icone": "🏢"},
    "0003": {"nome": "PREVIDÊNCIA SOCIAL", "icone": "🛡️"},
    "0005": {"nome": "EDUCAÇÃO", "icone": "📚"},
    "0006": {"nome": "SAÚDE", "icone": "🏥"},
    "0007": {"nome": "DESENVOLVIMENTO SOCIAL E CIDADANIA", "icone": "🤝"},
    "0008": {"nome": "EMPREENDEDORISMO E TRABALHO", "icone": "💼"},
    "0009": {"nome": "CULTURA", "icone": "🎭"},
    "0010": {"nome": "ESPORTE, JUVENTUDE E LAZER", "icone": "⚽"},
    "0011": {"nome": "DESENVOLVIMENTO URBANO", "icone": "🏙️"},
    "0012": {"nome": "MEIO AMBIENTE, PAISAGISMO E BEM-ESTAR ANIMAL", "icone": "🌿"},
    "0013": {"nome": "FOMENTO AGROPECUÁRIO E ABASTECIMENTO", "icone": "🌾"},
    "0014": {"nome": "OBRAS E SERVIÇOS URBANOS", "icone": "🏗️"},
    "0015": {"nome": "SEGURANÇA PÚBLICA E TRÂNSITO", "icone": "🚨"},
    "0016": {"nome": "DESENVOLVIMENTO TURÍSTICO", "icone": "✈️"},
    "0017": {"nome": "+ LEITE DAS CRIANÇAS", "icone": "🥛"},
    "0018": {"nome": "ÁGUA SOLIDÁRIA", "icone": "💧"},
    "0019": {"nome": "PARANAVAÍ MAIS HABITAÇÃO", "icone": "🏠"},
    "0020": {"nome": "CONSTRUSOCIAL", "icone": "🧱"},
    "0021": {"nome": "PROGRAMA DE INCENTIVO AO ESPORTE AMADOR DE PARANAVAÍ", "icone": "🏅"},
    "0022": {"nome": "PROGRAMA FUNDO ROTATIVO", "icone": "🔄"},
    "0023": {"nome": "PROGRAMA DE PACIFICAÇÃO RESTAURATIVA DE PARANAVAÍ", "icone": "🕊️"},
    "9999": {"nome": "RESERVA DE CONTINGÊNCIA", "icone": "🔒"}
}

@st.cache_data
def load_data():
    filepath = 'IEGM - Acoes e Metas Programas e Indicadores (2).csv'
    df = pd.read_csv(filepath, encoding='latin1', sep=',', header=5)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = df.columns.str.replace('"', '').str.strip()
    return df

df = load_data()

st.title("Programas e Ações de Governo")
st.markdown("Monitoramento Estratégico de Metas Físicas e Financeiras")

st.markdown("---")

st.markdown("### 🎛️ Filtros de Navegação")
tab_choice = st.radio(
    "Selecione a Visão:", 
    ["Visão Geral", "Análise por Programas", "Análise por Ações"],
    horizontal=True
)

st.markdown("---")

# Validação defensiva
if 'Código Programa' not in df.columns:
    st.error(f"Erro crítico: A coluna 'Código Programa' não foi encontrada nas colunas disponíveis: {list(df.columns)}")
    st.stop()

# Limpeza e filtragem da base de dados
base_df = df.dropna(subset=['Código Programa']).copy()
base_df = base_df[~base_df['Código Programa'].astype(str).str.replace('"', '').str.strip().isin(['Código Programa', 'Programas e indicadores'])]

if 'Código da Ação' in base_df.columns:
    base_df['Código da Ação Limpo'] = base_df['Código da Ação'].astype(str).str.replace('"', '').str.strip()
    actions_df = base_df[base_df['Código da Ação Limpo'].str.isnumeric()].copy()
else:
    actions_df = base_df.copy()

for col in ['Meta Física Estimada', 'Meta Física Alcançada', 'Dotação Final', 'Valor Liquidado']:
    if col in actions_df.columns:
        actions_df[col] = actions_df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        actions_df[col] = pd.to_numeric(actions_df[col], errors='coerce').fillna(0.0)

# Cálculos de Percentual de Execução por Ação
if 'Dotação Final' in actions_df.columns and 'Valor Liquidado' in actions_df.columns:
    actions_df['% Exec. Financeira'] = np.where(
        actions_df['Dotação Final'] > 0, 
        (actions_df['Valor Liquidado'] / actions_df['Dotação Final']) * 100, 
        0.0
    )
if 'Meta Física Estimada' in actions_df.columns and 'Meta Física Alcançada' in actions_df.columns:
    actions_df['% Exec. Física'] = np.where(
        actions_df['Meta Física Estimada'] > 0, 
        (actions_df['Meta Física Alcançada'] / actions_df['Meta Física Estimada']) * 100, 
        0.0
    )

# Função auxiliar para formatar o nome do programa com o código e ícone
def formatar_programa(codigo):
    c_str = str(codigo).replace('"', '').strip().zfill(4)
    info = PROGRAMAS_INFO.get(c_str, {"nome": "OUTROS PROGRAMAS", "icone": "📁"})
    return f"{info['icone']} {c_str} - {info['nome']}"

actions_df['Programa Formatado'] = actions_df['Código Programa'].apply(formatar_programa)

if tab_choice == "Visão Geral":
    st.subheader("Visão Geral Executiva — Programas")
    st.markdown("Acompanhamento consolidado por programa de governo.")
    
    prog_summary = actions_df.groupby(['Código Programa', 'Programa Formatado']).agg({
        'Dotação Final': 'sum',
        'Valor Liquidado': 'sum',
        'Meta Física Estimada': 'sum',
        'Meta Física Alcançada': 'sum',
        'Código da Ação': 'count'
    }).reset_index()

    prog_summary['% Financeira'] = np.where(
        prog_summary['Dotação Final'] > 0, 
        (prog_summary['Valor Liquidado'] / prog_summary['Dotação Final']) * 100, 
        0.0
    )
    prog_summary['% Física'] = np.where(
        prog_summary['Meta Física Estimada'] > 0, 
        (prog_summary['Meta Física Alcançada'] / prog_summary['Meta Física Estimada']) * 100, 
        0.0
    )

    total_dotacao = actions_df['Dotação Final'].sum()
    total_liquidado = actions_df['Valor Liquidado'].sum()
    execucao_financeira = (total_liquidado / total_dotacao * 100) if total_dotacao > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Dotação Final Total", f"R$ {total_dotacao:,.2f}")
    col2.metric("Valor Liquidado Total", f"R$ {total_liquidado:,.2f}")
    col3.metric("Taxa Média de Execução", f"{execucao_financeira:.2f}%")
    col4.metric("Total de Ações Numéricas", f"{len(actions_df)}")
    
    st.markdown("---")

    programas_lista = prog_summary.to_dict('records')
    for i in range(0, len(programas_lista), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(programas_lista):
                p_item = programas_lista[i + j]
                p_label = p_item['Programa Formatado']
                
                with cols[j]:
                    with st.container(border=True):
                        st.markdown(f"#### {p_label}")
                        st.metric("Exec. Financeira", f"{p_item['% Financeira']:.2f}%")
                        st.metric("Exec. Física", f"{p_item['% Física']:.2f}%")
                        st.metric("Nº de Ações", int(p_item['Código da Ação']))

    st.markdown("---")

    fig = pdx.bar(prog_summary, x='Programa Formatado', y=['Dotação Final', 'Valor Liquidado'], 
                   barmode='group', title="Dotação vs. Valor Liquidado por Programa",
                   labels={'value': 'Valor (R$)', 'Programa Formatado': 'Programa', 'variable': 'Métrica'},
                   color_discrete_sequence=['#1351B4', '#168821'])
    fig.update_layout(xaxis_tickangle=-45, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

elif tab_choice == "Análise por Programas":
    st.subheader("Desempenho por Programas (Metas Físicas e Financeiras)")
    
    valid_programas = sorted(actions_df['Código Programa'].dropna().unique())
    prog_options = {p: formatar_programa(p) for p in valid_programas}
    
    prog_selected_key = st.selectbox("Selecione o Programa:", options=list(prog_options.keys()), format_func=lambda x: prog_options[x])
    sub_df = actions_df[actions_df['Código Programa'] == prog_selected_key]
    
    p_dotacao = sub_df['Dotação Final'].sum()
    p_liquidado = sub_df['Valor Liquidado'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Dotação do Programa", f"R$ {p_dotacao:,.2f}")
    c2.metric("Liquidado do Programa", f"R$ {p_liquidado:,.2f}")
    c3.metric("Ações Vinculadas", len(sub_df))
    
    st.dataframe(sub_df[['Código da Ação', 'Descrição', 'Descrição da Meta', 'Unidade Medida', 'Meta Física Estimada', 'Meta Física Alcançada', '% Exec. Física', 'Dotação Final', 'Valor Liquidado', '% Exec. Financeira']], use_container_width=True)
    
    fig_prog = pdx.bar(sub_df, x='Código da Ação', y=['Meta Física Estimada', 'Meta Física Alcançada'],
                        barmode='group', title=f"Metas Físicas (Estimada vs Alcançada) - {prog_options[prog_selected_key]}",
                        color_discrete_sequence=['#1351B4', '#FFCD07'])
    fig_prog.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_prog, use_container_width=True)

elif tab_choice == "Análise por Ações":
    st.subheader("Análise Detalhada de Ações")
    
    search_term = st.text_input("Buscar Ação por Código da Ação:")
    filtered_actions = actions_df[actions_df['Código da Ação Limpo'].str.contains(search_term, case=False, na=False)] if search_term else actions_df
    
    st.dataframe(filtered_actions[['Programa Formatado', 'Código da Ação', 'Descrição', 'Dotação Final', 'Valor Liquidado', '% Exec. Financeira', 'Meta Física Estimada', 'Meta Física Alcançada', '% Exec. Física']], use_container_width=True)
    
    if not filtered_actions.empty:
        # Cria uma lista formatada para o selectbox exibir o código junto com a descrição
        filtered_actions['Opcao_Select'] = filtered_actions['Código da Ação Limpo'] + " - " + filtered_actions['Descrição']
        selected_option = st.selectbox("Selecione uma ação para detalhar:", filtered_actions['Opcao_Select'].unique())
        
        act_row = filtered_actions[filtered_actions['Opcao_Select'] == selected_option].iloc[0]
        
        st.info(f"**Ação:** {act_row['Código da Ação Limpo']} - {act_row['Descrição']} | **Programa:** {act_row['Programa Formatado']}")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Meta Física Estimada", f"{act_row['Meta Física Estimada']} {act_row['Unidade Medida']}")
            st.metric("Meta Física Alcançada", f"{act_row['Meta Física Alcançada']} {act_row['Unidade Medida']}")
            st.metric("Execução Física (%)", f"{act_row['% Exec. Física']:.2f}%")
        with col_b:
            st.metric("Dotação Final", f"R$ {act_row['Dotação Final']:,.2f}")
            st.metric("Valor Liquidado", f"R$ {act_row['Valor Liquidado']:,.2f}")
            st.metric("Execução Financeira (%)", f"{act_row['% Exec. Financeira']:.2f}%")
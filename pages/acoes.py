import os
import streamlit as st
import pandas as pd
import plotly.express as pdx
import numpy as np

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Dashboard de Metas - Programas e Ações",
    page_icon="🇧🇷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# ESTILIZAÇÃO CSS GLOBAL - DESIGN SYSTEM GOV.BR
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rawline:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"], [class*="st-"] {
            font-family: 'Rawline', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            color: #141414;
        }

        /* Barra superior institucional simulando a barra do Governo */
        header::before {
            content: "GovAnalytics — Monitoramento de Metas";
            display: block;
            background-color: #004587;
            color: #ffffff;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 4px 16px;
            letter-spacing: 0.05em;
        }

        /* Alinhamento à esquerda padrão do GOV.BR */
        h1, h2, h3, .stMarkdown p {
            text-align: left;
        }

        h1 {
            font-weight: 700 !important;
            color: #0c326f !important;
            font-size: 2rem !important;
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

        /* CARDS NO ESTILO GOV.BR (Borda lateral azul institucional) */
        .unified-card {
            background-color: #ffffff;
            border: 1px solid #d7d7d7;
            border-left: 4px solid #1351b4;
            border-radius: 4px;
            padding: 20px 16px;
            text-align: left;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            transition: all 0.2s ease-in-out;
        }
        
        .unified-card:hover {
            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.1);
            border-color: #1351b4;
        }
        
        .card-icon-wrapper {
            width: 36px;
            height: 36px;
            border-radius: 4px;
            background-color: #e5f1f8;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 12px;
        }
        
        .card-kpi-title {
            color: #454545;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }
        
        .card-kpi-value {
            color: #0c326f;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 4px;
        }
        
        .card-kpi-delta {
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 12px;
        }
        
        .card-divider {
            width: 100%;
            height: 1px;
            background-color: #d7d7d7;
            margin-bottom: 12px;
        }

        .card-explanation {
            color: #333333;
            font-size: 0.82rem;
            line-height: 1.4;
            font-weight: 400;
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

# ==========================================
# MAPEAMENTO DE PROGRAMAS
# ==========================================
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

# ==========================================
# CARREGAMENTO DE DADOS ROBUSTO
# ==========================================
@st.cache_data
def load_data():
    possible_paths = [
        'IEGM - Acoes e Metas Programas e Indicadores (2).csv',
        os.path.join(os.path.dirname(__file__), 'IEGM - Acoes e Metas Programas e Indicadores (2).csv'),
        os.path.join(os.path.dirname(__file__), '..', 'IEGM - Acoes e Metas Programas e Indicadores (2).csv'),
        './IEGM - Acoes e Metas Programas e Indicadores (2).csv'
    ]
    
    filepath = None
    for path in possible_paths:
        if os.path.exists(path):
            filepath = path
            break
            
    if not filepath:
        st.error("❌ Arquivo CSV não encontrado. Verifique se 'IEGM - Acoes e Metas Programas e Indicadores (2).csv' está presente no repositório.")
        st.stop()
        
    df_loaded = pd.read_csv(filepath, encoding='latin1', sep=',', header=5)
    df_loaded = df_loaded.loc[:, ~df_loaded.columns.str.contains('^Unnamed')]
    df_loaded.columns = df_loaded.columns.str.replace('"', '').str.strip()
    return df_loaded

df = load_data()

# ==========================================
# CABEÇALHO DO PAINEL
# ==========================================
st.title("Monitoramento Estratégico de Metas Físicas e Financeiras")
st.caption("Hierarquia: Programas >> Ações. Acompanhamento de execução orçamentária e metas governamentais.")

st.markdown("""
    <div style="background-color: #f8f9fa; border: 1px solid #d7d7d7; border-top: 4px solid #004587; border-radius: 4px; padding: 16px; margin-bottom: 20px;">
        <div style="font-weight: 700; color: #0c326f; font-size: 1rem; margin-bottom: 4px; display: flex; align-items: center; gap: 8px;">
            <span>🎛️</span> Painel de Navegação por Visão Estratégica
        </div>
    </div>
""", unsafe_allow_html=True)

tab_choice = st.radio(
    "Selecione a Visão:", 
    ["Visão Geral", "Análise por Programas", "Análise por Ações"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")

# ==========================================
# VALIDAÇÃO E TRATAMENTO DOS DADOS
# ==========================================
if 'Código Programa' not in df.columns:
    st.error(f"Erro crítico: A coluna 'Código Programa' não foi encontrada nas colunas disponíveis: {list(df.columns)}")
    st.stop()

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

def formatar_programa(codigo):
    c_str = str(codigo).replace('"', '').strip().zfill(4)
    info = PROGRAMAS_INFO.get(c_str, {"nome": "OUTROS PROGRAMAS", "icone": "📁"})
    return f"{info['icone']} {c_str} - {info['nome']}"

actions_df['Programa Formatado'] = actions_df['Código Programa'].apply(formatar_programa)

# ==========================================
# ABA 1: VISÃO GERAL
# ==========================================
if tab_choice == "Visão Geral":
    st.subheader("Visão Geral Executiva — Programas")
    st.markdown("Acompanhamento consolidado e comparativo por programa de governo.")
    
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
    
    # Cards de KPI com o Design System exato
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="unified-card">
                <div class="card-kpi-title">Dotação Final Total</div>
                <div class="card-kpi-value">R$ {total_dotacao:,.2f}</div>
                <div class="card-divider"></div>
                <div class="card-explanation">Montante global autorizado para o exercício.</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class="unified-card">
                <div class="card-kpi-title">Valor Liquidado Total</div>
                <div class="card-kpi-value">R$ {total_liquidado:,.2f}</div>
                <div class="card-divider"></div>
                <div class="card-explanation">Total de despesas efetivamente liquidadas.</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class="unified-card">
                <div class="card-kpi-title">Taxa Média Execução</div>
                <div class="card-kpi-value">{execucao_financeira:.2f}%</div>
                <div class="card-divider"></div>
                <div class="card-explanation">Percentual geral executado sobre a dotação.</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
            <div class="unified-card">
                <div class="card-kpi-title">Total de Ações</div>
                <div class="card-kpi-value">{len(actions_df)}</div>
                <div class="card-divider"></div>
                <div class="card-explanation">Número de ações numéricas ativadas.</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Detalhamento por Programa")

    programas_lista = prog_summary.to_dict('records')
    for i in range(0, len(programas_lista), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(programas_lista):
                p_item = programas_lista[i + j]
                p_label = p_item['Programa Formatado']
                
                with cols[j]:
                    st.markdown(f"""
                        <div class="unified-card">
                            <div class="card-kpi-title" style="font-size:0.7rem;">{p_label}</div>
                            <div class="card-kpi-value" style="font-size:1.1rem;">Exec. Fin: {p_item['% Financeira']:.1f}%</div>
                            <div class="card-kpi-delta">Ações Vinculadas: {int(p_item['Código da Ação'])}</div>
                            <div class="card-divider"></div>
                            <div class="card-explanation">Exec. Física: <b>{p_item['% Física']:.1f}%</b></div>
                        </div>
                    """, unsafe_allow_html=True)

    st.markdown("---")

    fig = pdx.bar(prog_summary, x='Programa Formatado', y=['Dotação Final', 'Valor Liquidado'], 
                   barmode='group', title="Dotação vs. Valor Liquidado por Programa",
                   labels={'value': 'Valor (R$)', 'Programa Formatado': 'Programa', 'variable': 'Métrica'},
                   color_discrete_sequence=['#1351B4', '#168821'])
    fig.update_layout(xaxis_tickangle=-45, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_family="Rawline, Inter")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# ABA 2: ANÁLISE POR PROGRAMAS
# ==========================================
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
    fig_prog.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_family="Rawline, Inter",
        bargap=0.9, bargroupgap=0.10)
    st.plotly_chart(fig_prog, use_container_width=True)

# ==========================================
# ABA 3: ANÁLISE POR AÇÕES
# ==========================================
elif tab_choice == "Análise por Ações":
    st.subheader("Análise Detalhada de Ações")
    
    search_term = st.text_input("Buscar Ação por Código da Ação:")
    filtered_actions = actions_df[actions_df['Código da Ação Limpo'].str.contains(search_term, case=False, na=False)] if search_term else actions_df
    
    st.dataframe(filtered_actions[['Programa Formatado', 'Código da Ação', 'Descrição', 'Dotação Final', 'Valor Liquidado', '% Exec. Financeira', 'Meta Física Estimada', 'Meta Física Alcançada', '% Exec. Física']], use_container_width=True)
    
    if not filtered_actions.empty:
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
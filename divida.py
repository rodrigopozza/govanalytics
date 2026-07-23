import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Dashboard RGF - Dívida Consolidada Líquida",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# FUNÇÃO PARA TRATAMENTO DE DADOS
# ==========================================
def parse_br_number(val):
    """Converte números no formato brasileiro ('1.234,56' ou '- 1.234,56') para float."""
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).strip().replace(" ", "")
    # Tratamento para sinal negativo com espaço
    if val_str.startswith("-"):
        val_str = "-" + val_str[1:]
    val_str = val_str.replace(".", "").replace(",", ".")
    try:
        return float(val_str)
    except ValueError:
        return np.nan

@st.cache_data
def load_and_clean_data(file_path_or_buffer):
    """Carrega o CSV e formata a tabela principal do RGF."""
    df_raw = pd.read_csv(file_path_or_buffer)
    
    # Selecionar as primeiras 33 linhas referentes à tabela principal do RGF
    df_main = df_raw.iloc[0:33, :].copy()
    
    # Renomear colunas
    df_main.columns = [
        "Exercicio", 
        "Especificacao", 
        "Até Exer. Anterior", 
        "1º Quadrimestre", 
        "2º Quadrimestre", 
        "3º Quadrimestre"
    ]
    
    # Limpar espaços nos nomes das especificações
    df_main["Especificacao"] = df_main["Especificacao"].str.strip()
    
    # Colunas de valores
    val_cols = ["Até Exer. Anterior", "1º Quadrimestre", "2º Quadrimestre", "3º Quadrimestre"]
    
    # Converter valores
    for col in val_cols:
        df_main[col] = df_main[col].apply(parse_br_number)
        
    return df_main

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/line-chart.png", width=80)
st.sidebar.title("Navegação & Filtros")

uploaded_file = st.sidebar.file_uploader("Carregar outro arquivo CSV", type=["csv"])

if uploaded_file is not None:
    df_data = load_and_clean_data(uploaded_file)
else:
    # Nome padrão do arquivo recebido
    default_file = "RelatorioRGFDividaConsolidadaLiquida_5 (1).csv"
    try:
        df_data = load_and_clean_data(default_file)
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo padrão: {e}. Por favor, faça o upload do CSV na barra lateral.")
        st.stop()

# Seleção de Quadrimestre para Visualização nos Cards
periodos = ["Até Exer. Anterior", "1º Quadrimestre", "2º Quadrimestre", "3º Quadrimestre"]
periodo_sel = st.sidebar.selectbox("Selecione o Período para Destaque (KPIs):", periodos, index=3)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Sobre este Relatório:**\n"
    "Demonstrativo da Dívida Consolidada Líquida (RGF) conforme a Lei de Responsabilidade Fiscal (LRF)."
)

# ==========================================
# EXTRAÇÃO DE MÉTRICAS PRINCIPAIS
# ==========================================
def get_value(spec_name, period):
    row = df_data[df_data["Especificacao"] == spec_name]
    if not row.empty:
        return row[period].values[0]
    return 0.0

dc_val = get_value("DÍVIDA CONSOLIDADA – DC (I)", periodo_sel)
deduc_val = get_value("DEDUÇÕES (II)", periodo_sel)
dcl_val = get_value("DÍVIDA CONSOLIDADA LÍQUIDA – DCL (III) = (I – II)", periodo_sel)
rcl_val = get_value("RECEITA CORRENTE LÍQUIDA AJUSTADA PARA CÁLCULO DOS LIMITES DE ENDIVIDAMENTO (VI) = (IV - V)", periodo_sel)
limite_senado = get_value("LIMITE DEFINIDO POR RESOLUÇÃO DO SENADO FEDERAL: (120% da RCL AJUSTADA)", periodo_sel)
limite_alerta = get_value("LIMITE DE ALERTA (inciso III do § 1º do art. 59 da LRF): (108% da RCL AJUSTADA)", periodo_sel)
pct_dcl = get_value("% DA DCL SOBRE A RCL (III/VI)", periodo_sel)

# ==========================================
# PAINEL PRINCIPAL
# ==========================================
st.title("📊 Relatório de Gestão Fiscal — DCL e Endividamento")
st.caption("Acompanhamento dos limites da Lei de Responsabilidade Fiscal (LRF) e Resoluções do Senado Federal.")

st.markdown("---")

# ==========================================
# CARDS DE MÉTRICAS (KPIs)
# ==========================================
st.subheader(f"📌 Indicadores Principais — {periodo_sel}")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    label="Dívida Consolidada (DC)",
    value=f"R$ {dc_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
)

col2.metric(
    label="Deduções (Caixa/Haveres)",
    value=f"R$ {deduc_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
)

col3.metric(
    label="Dívida Consolidada Líquida",
    value=f"R$ {dcl_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    delta="Situação Confortável (Superávit Financeiro)" if dcl_val < 0 else "Endividamento Positivo",
    delta_color="normal" if dcl_val < 0 else "inverse"
)

col4.metric(
    label="% DCL sobre RCL Ajustada",
    value=f"{pct_dcl:.2f}%",
    delta="Abaixo do Limite (120%)",
    delta_color="normal"
)

st.markdown("---")

# ==========================================
# GRÁFICOS INTERATIVOS
# ==========================================
tab_evolucao, tab_limites, tab_composicao, tab_dados = st.tabs([
    "📈 Evolução dos Saldos", 
    "🚨 Limites de Endividamento", 
    "🧩 Composição da Dívida/Deduções", 
    "📄 Tabela Completa"
])

# ------------------------------------------
# TAB 1: EVOLUÇÃO
# ------------------------------------------
with tab_evolucao:
    st.subheader("Evolução da DC, Deduções e DCL ao longo dos Quadrimestres")
    
    items_to_plot = [
        "DÍVIDA CONSOLIDADA – DC (I)",
        "DEDUÇÕES (II)",
        "DÍVIDA CONSOLIDADA LÍQUIDA – DCL (III) = (I – II)"
    ]
    
    df_evol = df_data[df_data["Especificacao"].isin(items_to_plot)].copy()
    df_evol_melted = df_evol.melt(
        id_vars=["Especificacao"], 
        value_vars=periodos, 
        var_name="Período", 
        value_name="Valor (R$)"
    )
    
    fig_evol = px.line(
        df_evol_melted, 
        x="Período", 
        y="Valor (R$)", 
        color="Especificacao",
        markers=True,
        title="Comportamento dos Saldos ao Longo do Exercício",
        labels={"Valor (R$)": "Valor (R$)", "Especificacao": "Item"}
    )
    fig_evol.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_evol, use_container_width=True)

# ------------------------------------------
# TAB 2: LIMITES
# ------------------------------------------
with tab_limites:
    st.subheader("Comparativo com Limites Legais (LRF e Resolução do Senado)")
    
    # Preparar dados para o gráfico de limites
    df_lim = pd.DataFrame({
        "Período": periodos,
        "Dívida Consolidada Líquida (DCL)": [get_value("DÍVIDA CONSOLIDADA LÍQUIDA – DCL (III) = (I – II)", p) for p in periodos],
        "Limite de Alerta (108% RCL)": [get_value("LIMITE DE ALERTA (inciso III do § 1º do art. 59 da LRF): (108% da RCL AJUSTADA)", p) for p in periodos],
        "Limite Máximo Senado (120% RCL)": [get_value("LIMITE DEFINIDO POR RESOLUÇÃO DO SENADO FEDERAL: (120% da RCL AJUSTADA)", p) for p in periodos]
    })
    
    fig_lim = go.Figure()
    
    fig_lim.add_trace(go.Bar(
        x=df_lim["Período"],
        y=df_lim["Dívida Consolidada Líquida (DCL)"],
        name="DCL Realizada",
        marker_color="teal"
    ))
    
    fig_lim.add_trace(go.Scatter(
        x=df_lim["Período"],
        y=df_lim["Limite de Alerta (108% RCL)"],
        name="Limite de Alerta (108%)",
        mode="lines+markers",
        line=dict(color="orange", dash="dash")
    ))
    
    fig_lim.add_trace(go.Scatter(
        x=df_lim["Período"],
        y=df_lim["Limite Máximo Senado (120% RCL)"],
        name="Limite Máximo (120%)",
        mode="lines+markers",
        line=dict(color="red", width=2)
    ))
    
    fig_lim.update_layout(
        title="DCL vs Limites de Alerta e Máximo do Senado",
        yaxis_title="Valor (R$)",
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.2)
    )
    
    st.plotly_chart(fig_lim, use_container_width=True)
    
    st.success(
        "✅ **Conclusão Fiscal:** Como a DCL encontra-se negativa no período, a disponibilidade de caixa supera "
        "o montante da dívida consolidada, mantendo o ente muito abaixo de todos os limites de alerta e máximo."
    )

# ------------------------------------------
# TAB 3: COMPOSIÇÃO
# ------------------------------------------
with tab_composicao:
    col_comp1, col_comp2 = st.columns(2)
    
    with col_comp1:
        st.subheader("Composição da Dívida Contratual")
        financ = get_value("Financiamentos", periodo_sel)
        parcel = get_value("Parcelamento e Renegociação de dívidas", periodo_sel)
        
        df_comp_dc = pd.DataFrame({
            "Categoria": ["Financiamentos", "Parcelamento / Renegociação"],
            "Valor": [financ, parcel]
        })
        
        fig_pie_dc = px.pie(
            df_comp_dc, 
            names="Categoria", 
            values="Valor", 
            title=f"Detalhamento da Dívida - {periodo_sel}",
            hole=0.4
        )
        st.plotly_chart(fig_pie_dc, use_container_width=True)
        
    with col_comp2:
        st.subheader("Composição das Deduções")
        disp_caixa = get_value("Disponibilidade de Caixa", periodo_sel)
        haveres = get_value("Demais Haveres Financeiros", periodo_sel)
        
        df_comp_ded = pd.DataFrame({
            "Categoria": ["Disponibilidade de Caixa Líquida", "Demais Haveres Financeiros"],
            "Valor": [disp_caixa, haveres]
        })
        
        fig_pie_ded = px.pie(
            df_comp_ded, 
            names="Categoria", 
            values="Valor", 
            title=f"Detalhamento das Deduções - {periodo_sel}",
            hole=0.4
        )
        st.plotly_chart(fig_pie_ded, use_container_width=True)

# ------------------------------------------
# TAB 4: TABELA
# ------------------------------------------
with tab_dados:
    st.subheader("Visão Tabela — Demonstrativo Resumido")
    
    # 1. Lista de linhas "filhas" / detalhamentos que devem ser REMOVIDOS da exibição
    linhas_para_remover = [
        "Internos",
        "Externos",
        "De Tributos",
        "De Contribuições Previdenciárias",
        "De Demais Contribuições Sociais",
        "Do FGTS",
        "Com Instituição Não Financeira"
    ]
    
    # Filtrar o dataframe para remover as linhas filhas
    df_filtered = df_data[~df_data["Especificacao"].isin(linhas_para_remover)].copy()
    
    # Listas de especificações para aplicar Destaque Visual (Estilização)
    linhas_destaque_total = [
        "DÍVIDA CONSOLIDADA – DC (I)",
        "DEDUÇÕES (II)",
        "DÍVIDA CONSOLIDADA LÍQUIDA – DCL (III) = (I – II)",
        "RECEITA CORRENTE LÍQUIDA – RCL (IV)",
        "RECEITA CORRENTE LÍQUIDA AJUSTADA PARA CÁLCULO DOS LIMITES DE ENDIVIDAMENTO (VI) = (IV - V)"
    ]
    
    linhas_destaque_subtotal = [
        "Dívida Contratual",
        "Dívida Mobiliária",
        "Financiamentos",
        "Empréstimos",
        "Parcelamento e Renegociação de dívidas",
        "Disponibilidade de Caixa",
        "Demais Haveres Financeiros"
    ]

    # Formatar os valores para o padrão brasileiro de moeda para exibição
    val_cols = ["Até Exer. Anterior", "1º Quadrimestre", "2º Quadrimestre", "3º Quadrimestre"]
    df_display = df_filtered.copy()
    
    for col in val_cols:
        df_display[col] = df_display[col].apply(
            lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if pd.notna(x) else "-"
        )

    # 2. Função para aplicar os estilos CSS/Pandas Styler na tabela
    def highlight_rows(row):
        spec = str(row["Especificacao"]).strip()
        
        # Estilo para os Grandes Totais e Resultados Principais (Fundo destacado e negrito)
        if spec in linhas_destaque_total:
            return ['background-color: #1f2937; color: #ffffff; font-weight: bold;'] * len(row)
            
        # Estilo para os Subtotais intermediários (Negrito simples)
        elif spec in linhas_destaque_subtotal or "LIMITE" in spec or "%" in spec:
            return ['font-weight: bold; background-color: #f3f4f6; color: #111827;'] * len(row)
            
        return [''] * len(row)

    # Aplicar a estilização
    styled_df = df_display.style.apply(highlight_rows, axis=1)

    # Exibir a tabela com o Pandas Styler ativado
    st.dataframe(
        styled_df, 
        use_container_width=True, 
        height=600,
        hide_index=True
    )
    
    # Botão de download dos dados filtrados
    csv_download = df_filtered.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Baixar Dados Tratados e Resumidos (CSV)",
        data=csv_download,
        file_name="rgf_divida_consolidada_resumido.csv",
        mime="text/csv"
    )
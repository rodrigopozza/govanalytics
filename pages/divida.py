import os
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
    initial_sidebar_state="collapsed"
)

# ==========================================
# CONFIGURAÇÃO DA BARRA LATERAL (TOPO)
# ==========================================
with st.sidebar:
    # Logo no topo à esquerda (Via GitHub)
    st.image("https://raw.githubusercontent.com/rodrigopozza/govanalytics/main/pages/logo.png", use_container_width=True)
    st.markdown("---")
    
    # Exemplo de conteúdo do menu
    st.markdown("### Navegação")

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
        
        .card-icon-wrapper svg {
            width: 18px;
            height: 18px;
            stroke: #1351b4;
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
    </style>
""", unsafe_allow_html=True)

# ==========================================
# FUNÇÃO PARA TRATAMENTO DE DADOS
# ==========================================
def parse_br_number(val):
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).strip().replace(" ", "")
    if val_str.startswith("-"):
        val_str = "-" + val_str[1:]
    val_str = val_str.replace(".", "").replace(",", ".")
    try:
        return float(val_str)
    except ValueError:
        return np.nan

@st.cache_data
def load_and_clean_data(file_path_or_buffer):
    df_raw = pd.read_csv(file_path_or_buffer)
    df_main = df_raw.iloc[0:33, :].copy()
    df_main.columns = [
        "Exercicio", 
        "Especificacao", 
        "Até Exer. Anterior", 
        "1º Quadrimestre", 
        "2º Quadrimestre", 
        "3º Quadrimestre"
    ]
    df_main["Especificacao"] = df_main["Especificacao"].str.strip()
    val_cols = ["Até Exer. Anterior", "1º Quadrimestre", "2º Quadrimestre", "3º Quadrimestre"]
    for col in val_cols:
        df_main[col] = df_main[col].apply(parse_br_number)
    return df_main

# ==========================================
# CARREGAMENTO INTERNO DOS DADOS
# ==========================================
diretorio_atual = os.path.dirname(__file__)
default_file = os.path.join(diretorio_atual, "RelatorioRGFDividaConsolidadaLiquida_5.csv")

try:
    df_raw_data = load_and_clean_data(default_file)
except Exception as e:
    st.error(f"Erro ao carregar o arquivo padrão: {e}. Verifique se o arquivo CSV está na pasta correta.")
    st.stop()

# ==========================================
# PAINEL PRINCIPAL & FILTROS NO TOPO
# ==========================================
st.title("Relatório de Gestão Fiscal — DCL e Endividamento")
st.caption("Acompanhamento dos limites da Lei de Responsabilidade Fiscal (LRF) e Resoluções do Senado Federal.")

st.markdown("""
    <div style="background-color: #f8f9fa; border: 1px solid #d7d7d7; border-top: 4px solid #004587; border-radius: 4px; padding: 16px; margin-bottom: 20px;">
        <div style="font-weight: 700; color: #0c326f; font-size: 1rem; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>🔍</span> Filtros e Seleção de Período / Exercício
        </div>
    </div>
""", unsafe_allow_html=True)

with st.container():
    col_ex, col_sel = st.columns([2, 2])
    with col_ex:
        if "Exercicio" in df_raw_data.columns:
            exercicios_disponiveis = sorted(df_raw_data["Exercicio"].dropna().unique().tolist())
            if not exercicios_disponiveis:
                exercicios_disponiveis = ["Geral"]
            exercicio_sel = st.selectbox("Selecione o Exercício (Ano):", exercicios_disponiveis)
        else:
            exercicio_sel = None
    with col_sel:
        periodos = ["Até Exer. Anterior", "1º Quadrimestre", "2º Quadrimestre", "3º Quadrimestre"]
        periodo_sel = st.selectbox("Selecione o Período para Destaque (KPIs):", periodos, index=1)

if exercicio_sel and "Exercicio" in df_raw_data.columns:
    df_data = df_raw_data[df_raw_data["Exercicio"] == exercicio_sel].copy()
    if df_data.empty:
        df_data = df_raw_data.copy()
else:
    df_data = df_raw_data.copy()

st.markdown("---")

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
pct_dcl = get_value("% DA DCL SOBRE A RCL (III/VI)", periodo_sel)

# ==========================================
# CARDS DE MÉTRICAS (KPIs)
# ==========================================
st.subheader(f"Indicadores Principais — {periodo_sel}")

icon_dc = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-6h6m6 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'
icon_ded = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 14.25l6-6m4.5-3.493V21.75l-3.75-1.5-3.75 1.5-3.75-1.5-3.75 1.5V4.757c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0c1.1.128 1.907 1.077 1.907 2.185z" /></svg>'
icon_dcl = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" /></svg>'
icon_pct = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6a7.5 7.5 0 107.5 7.5h-7.5V6z" /><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 10.5H21A7.5 7.5 0 0013.5 3v7.5z" /></svg>'

col1, col2, col3, col4 = st.columns(4)

with col1:
    v_str = f"R$ {dc_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.markdown(f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_dc}</div>
            <div class="card-kpi-title">Dívida Consolidada (DC)</div>
            <div class="card-kpi-value">{v_str}</div>
            <div class="card-divider"></div>
            <div class="card-explanation">Montante total das obrigações financeiras do ente.</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    v_str = f"R$ {deduc_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.markdown(f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_ded}</div>
            <div class="card-kpi-title">Deduções (Caixa/Haveres)</div>
            <div class="card-kpi-value">{v_str}</div>
            <div class="card-divider"></div>
            <div class="card-explanation">Disponibilidades de caixa e demais haveres financeiros dedutíveis.</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    v_str = f"R$ {dcl_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    delta_texto = "Situação Confortável (Superávit)" if dcl_val < 0 else "Endividamento Positivo"
    cor_delta = "#059669" if dcl_val < 0 else "#dc2626"
    st.markdown(f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_dcl}</div>
            <div class="card-kpi-title">Dívida Consolidada Líquida</div>
            <div class="card-kpi-value">{v_str}</div>
            <div class="card-kpi-delta" style="color: {cor_delta};">{delta_texto}</div>
            <div class="card-divider"></div>
            <div class="card-explanation">Resultado líquido entre a Dívida Consolidada e as Deduções.</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    v_str = f"{pct_dcl:.2f}%"
    st.markdown(f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_pct}</div>
            <div class="card-kpi-title">% DCL sobre RCL Ajustada</div>
            <div class="card-kpi-value">{v_str}</div>
            <div class="card-kpi-delta" style="color: #059669;">Abaixo do Limite (120%)</div>
            <div class="card-divider"></div>
            <div class="card-explanation">Percentual de comprometimento da Receita Corrente Líquida Ajustada.</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# GRÁFICOS INTERATIVOS E TABELAS
# ==========================================
tab_evolucao, tab_limites, tab_composicao, tab_dados = st.tabs([
    "📈 Evolução dos Saldos", 
    "🚨 Limites de Endividamento", 
    "🧩 Composição da Dívida/Deduções", 
    "📄 Tabela Completa"
])

with tab_evolucao:
    st.subheader("Evolução da DC, Deduções e DCL ao longo dos Quadrimestres")
    items_to_plot = [
        "DÍVIDA CONSOLIDADA – DC (I)",
        "DEDUÇÕES (II)",
        "DÍVIDA CONSOLIDADA LÍQUIDA – DCL (III) = (I – II)"
    ]
    df_evol = df_data[df_data["Especificacao"].isin(items_to_plot)].copy()
    df_evol_melted = df_evol.melt(id_vars=["Especificacao"], value_vars=periodos, var_name="Período", value_name="Valor (R$)")
    
    fig_evol = px.line(df_evol_melted, x="Período", y="Valor (R$)", color="Especificacao", markers=True, title="Comportamento dos Saldos ao Longo do Exercício")
    fig_evol.update_layout(font_family="Rawline, Inter", title_x=0.5, hovermode="x unified", legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_evol, use_container_width=True)

with tab_limites:
    st.subheader("Comparativo com Limites Legais (LRF e Resolução do Senado)")
    df_lim = pd.DataFrame({
        "Período": periodos,
        "Dívida Consolidada Líquida (DCL)": [get_value("DÍVIDA CONSOLIDADA LÍQUIDA – DCL (III) = (I – II)", p) for p in periodos],
        "Limite de Alerta (108% RCL)": [get_value("LIMITE DE ALERTA (inciso III do § 1º do art. 59 da LRF): (108% da RCL AJUSTADA)", p) for p in periodos],
        "Limite Máximo Senado (120% RCL)": [get_value("LIMITE DEFINIDO POR RESOLUÇÃO DO SENADO FEDERAL: (120% da RCL AJUSTADA)", p) for p in periodos]
    })
    
    fig_lim = go.Figure()
    fig_lim.add_trace(go.Bar(x=df_lim["Período"], y=df_lim["Dívida Consolidada Líquida (DCL)"], name="DCL Realizada", marker_color="#1351b4"))
    fig_lim.add_trace(go.Scatter(x=df_lim["Período"], y=df_lim["Limite de Alerta (108% RCL)"], name="Limite de Alerta (108%)", mode="lines+markers", line=dict(color="orange", dash="dash")))
    fig_lim.add_trace(go.Scatter(x=df_lim["Período"], y=df_lim["Limite Máximo Senado (120% RCL)"], name="Limite Máximo (120%)", mode="lines+markers", line=dict(color="red", width=2)))
    fig_lim.update_layout(font_family="Rawline, Inter", title_x=0.5, title="DCL vs Limites de Alerta e Máximo do Senado", yaxis_title="Valor (R$)", hovermode="x unified", legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_lim, use_container_width=True)

with tab_composicao:
    col_comp1, col_comp2 = st.columns(2)
    with col_comp1:
        st.subheader("Composição da Dívida Contratual")
        financ = get_value("Financiamentos", periodo_sel)
        parcel = get_value("Parcelamento e Renegociação de dívidas", periodo_sel)
        df_comp_dc = pd.DataFrame({"Categoria": ["Financiamentos", "Parcelamento / Renegociação"], "Valor": [max(0, financ), max(0, parcel)]})
        if df_comp_dc["Valor"].sum() > 0:
            fig_pie_dc = px.pie(df_comp_dc, names="Categoria", values="Valor", title=f"Detalhamento da Dívida - {periodo_sel}", hole=0.4, color_discrete_sequence=['#1351b4', '#2670e8'])
            fig_pie_dc.update_layout(font_family="Rawline, Inter", title_x=0.5)
            st.plotly_chart(fig_pie_dc, use_container_width=True)
        else:
            st.info("ℹ️ Não há valores positivos para exibir na composição da dívida neste período.")
            
    with col_comp2:
        st.subheader("Deduções")
        disp_caixa = get_value("Disponibilidade de Caixa", periodo_sel)
        haveres = get_value("Demais Haveres Financeiros", periodo_sel)
        df_comp_ded = pd.DataFrame({"Categoria": ["Disponibilidade de Caixa", "Demais Haveres Financeiros"], "Valor": [max(0, disp_caixa), max(0, haveres)]})
        if df_comp_ded["Valor"].sum() > 0:
            fig_pie_ded = px.pie(df_comp_ded, names="Categoria", values="Valor", title=f"Detalhamento das Deduções - {periodo_sel}", hole=0.4, color_discrete_sequence=['#1351b4', '#5391ff'])
            fig_pie_ded.update_layout(font_family="Rawline, Inter", title_x=0.5)
            st.plotly_chart(fig_pie_ded, use_container_width=True)
        else:
            st.info("ℹ️ Não há valores positivos para exibir na composição das deduções neste período.")

with tab_dados:
    st.subheader("Visão Tabela — Demonstrativo Resumido")
    linhas_para_remover = ["Internos", "Externos", "De Tributos", "De Contribuições Previdenciárias", "De Demais Contribuições Sociais", "Do FGTS", "Com Instituição Não Financeira"]
    df_filtered = df_data[~df_data["Especificacao"].isin(linhas_para_remover)].copy()
    
    val_cols = ["Até Exer. Anterior", "1º Quadrimestre", "2º Quadrimestre", "3º Quadrimestre"]
    df_display = df_filtered.copy()
    for col in val_cols:
        df_display[col] = df_display[col].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if pd.notna(x) else "-")

    st.dataframe(df_display, use_container_width=True, height=600, hide_index=True)

# ==========================================
# RODAPÉ DA PÁGINA PRINCIPAL
# ==========================================
st.markdown("---")
col_esq, col_centro, col_dir = st.columns([2, 1, 2])
with col_centro:
    st.image("https://raw.githubusercontent.com/rodrigopozza/govanalytics/main/pages/logo.png", use_container_width=True)
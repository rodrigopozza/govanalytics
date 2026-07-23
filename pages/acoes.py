import streamlit as st
import pandas as pd
import plotly.express as px
import csv

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    layout="wide", 
    page_title="Análise Orçamentária - Programas e Ações",
    page_icon="📊"
)

# -----------------------------------------------------------------------------
# INJEÇÃO DO DESIGN SYSTEM (CSS & HTML)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [data-testid="stAppViewContainer"], [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            background-color: #f8fafc !important; 
            color: #1e293b !important;
        }

        [data-testid="stHeader"] {
            background-color: rgba(248, 250, 252, 0.8) !important;
            backdrop-filter: blur(8px);
        }

        h1 {
            font-weight: 700 !important;
            color: #0f172a !important;
            letter-spacing: -0.02em !important;
            margin-bottom: 8px !important;
        }
        h2 {
            font-weight: 600 !important;
            color: #1e3a8a !important; 
            letter-spacing: -0.01em !important;
            margin-top: 30px !important;
            margin-bottom: 20px !important;
        }
        
        hr {
            margin: 40px 0 !important;
            border-bottom: 1px solid #e2e8f0 !important;
        }

        .custom-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 30px 24px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            min-height: 320px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
        }
        .custom-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
            border-color: #cbd5e1;
        }
        .card-icon-container {
            background-color: #eff6ff;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 18px;
        }
        .card-icon {
            font-size: 28px;
        }
        .card-value {
            font-size: 26px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }
        .card-title {
            font-size: 15px;
            font-weight: 600;
            color: #2563eb; 
            margin-bottom: 10px;
        }
        .card-description {
            font-size: 13.5px;
            color: #64748b;
            line-height: 1.6;
        }

        .stDataFrame, data-testid="stTable" {
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid #e2e8f0 !important;
        }
        
        .card-delta-positivo {
            font-size: 13px;
            font-weight: 600;
            color: #10b981; 
            background-color: #ecfdf5;
            padding: 4px 10px;
            border-radius: 20px;
            margin-top: 5px;
            display: inline-block;
        }
        .icon-verde { background-color: #e6f4ea !important; }
        .icon-azul { background-color: #eff6ff !important; }
    </style>
""", unsafe_allow_html=True)

PALETA_PROGRAMAS = ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#cbd5e1']

# -----------------------------------------------------------------------------
# 2. FUNÇÃO PARA TRATAMENTO DOS DADOS DO CSV DE AÇÕES
# -----------------------------------------------------------------------------
@st.cache_data
def carregar_e_tratar_dados(file_path):
    # Altere o separador se o seu arquivo utilizar vírgula ou tabulação
    df = pd.read_csv(file_path, sep=';', encoding='utf-8')
    
    # Padronização de colunas para evitar problemas de maiúsculas/minúsculas
    df.columns = [c.strip() for c in df.columns]
    
    # Função helper para limpar valores monetários
    def limpar_valor(val):
        if pd.isna(val) or val == "" or val == "-" or str(val).isspace():
            return 0.0
        # Remove pontos de milhar e troca a vírgula decimal por ponto
        return float(str(val).replace('.', '').replace(',', '.').strip())
    
    # Identificar colunas financeiras (meta financeira, valor liquidado, etc.)
    # Ajuste os nomes abaixo conforme as colunas exatas do seu arquivo CSV
    colunas_financeiras = [c for c in df.columns if 'financeira' in c.lower() or 'valor' in c.lower() or 'pago' in c.lower() or 'executado' in c.lower()]
    
    for col in colunas_financeiras:
        df[col] = df[col].apply(limpar_valor)
        
    return df

# Caminho para o seu novo arquivo CSV
csv_path = r"C:\Users\rodrigop\Python\GOV-ANALYTICS\GOV-ANALYTICS\DADOS_TCE_PR\Acoes por Programa.csv"

try:
    df_acoes = carregar_e_tratar_dados(csv_path)
except Exception as e:
    st.error(f"Erro ao processar o arquivo CSV: {e}")
    st.stop()

def formatar_moeda_ptbr(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Mapeamento dinâmico de colunas do seu novo CSV (Ajuste os nomes baseados nas colunas reais)
col_programa = [c for c in df_acoes.columns if 'programa' in c.lower()][0]
col_acao = [c for c in df_acoes.columns if 'acao' in c.lower() or 'ação' in c.lower()][0]
col_meta_fin = [c for c in df_acoes.columns if 'financeira' in c.lower() or 'valor' in c.lower()][0]
col_meta_fis = [c for c in df_acoes.columns if 'fisica' in c.lower() or 'física' in c.lower() or 'meta' in c.lower()][0]

# -----------------------------------------------------------------------------
# 3. CÁLCULOS E KPI PRINCIPAIS
# -----------------------------------------------------------------------------
total_orcamento_acoes = df_acoes[col_meta_fin].sum()
total_programas = df_acoes[col_programa].nunique()
total_acoes = df_acoes[col_acao].nunique()

# -----------------------------------------------------------------------------
# INTERFACE DO DASHBOARD
# -----------------------------------------------------------------------------
st.title("Raio-X de Programas, Ações e Metas")

st.markdown(f"""
    <div style="margin-top: 15px; margin-bottom: 30px;">
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px; flex-wrap: wrap;">
            <h2 style="color: #2563eb !important; font-size: 26px; font-weight: 700; margin: 0; border: none; padding: 0;">
                O que é o Relatório de Ações?
            </h2>
            <span style="background-color: #f1f5f9; color: #475569; font-size: 13px; font-weight: 600; padding: 6px 14px; border-radius: 30px; border: 1px solid #e2e8f0;">
                ⏱️ Planejado vs. Executado
            </span>
        </div>
        <p style="font-size: 16px; color: #334155; line-height: 1.6; margin-bottom: 15px;">
            Este painel detalha as metas físicas (entregas qualitativas/quantitativas) e financeiras (recursos alocados) divididas por 
            cada iniciativa governamental do município.
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- BLOCO 1: KPIs Principais ---
st.header("Indicadores Gerais do Planejamento")

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.markdown(f"""
        <div class="custom-card">
            <div class="card-icon-container icon-azul"><span class="card-icon">💵</span></div>
            <div class="card-value">{formatar_moeda_ptbr(total_orcamento_acoes)}</div>
            <div class="card-title">Orçamento Total Alocado</div>
            <div class="card-description" style="margin-top: 15px;">
                Somatório de todos os recursos planejados e distribuídos nas ações listadas.
            </div>
        </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
        <div class="custom-card">
            <div class="card-icon-container icon-verde"><span class="card-icon">📁</span></div>
            <div class="card-value">{total_programas}</div>
            <div class="card-title">Programas Governamentais</div>
            <div class="card-description" style="margin-top: 15px;">
                Quantidade de macroprogramas/diretrizes estratégicas mapeadas no município.
            </div>
        </div>
    """, unsafe_with_html=True)

with kpi3:
    st.markdown(f"""
        <div class="custom-card">
            <div class="card-icon-container icon-azul"><span class="card-icon">⚡</span></div>
            <div class="card-value">{total_acoes}</div>
            <div class="card-title">Ações em Execução</div>
            <div class="card-description" style="margin-top: 15px;">
                Total de projetos, atividades e operações mapeadas vinculadas aos programas.
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- BLOCO 2: Visão de Orçamento por Programa (Gráfico de Barras) ---
st.header("1. Alocação de Recursos por Programa")

# Agrupa o orçamento por Programa
df_resumo_prog = df_acoes.groupby(col_programa)[col_meta_fin].sum().reset_index()

fig_prog = px.bar(
    df_resumo_prog, x=col_meta_fin, y=col_programa, 
    title="Orçamento Planejado por Programa Governamental",
    labels={col_meta_fin: 'Meta Financeira (R$)', col_programa: 'Programa'},
    orientation='h', color_discrete_sequence=PALETA_PROGRAMAS
)
fig_prog.update_layout(
    yaxis={'categoryorder':'total ascending'}, 
    margin=dict(l=50, r=20, t=40, b=20),
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_prog, use_container_width=True)

# --- BLOCO 3: Tabela Geral ---
st.markdown("**Tabela Detalhada de Metas:**")

df_tab_formatada = df_acoes[[col_programa, col_acao, col_meta_fis, col_meta_fin]].copy()
df_tab_formatada[col_meta_fin] = df_tab_formatada[col_meta_fin].apply(formatar_moeda_ptbr)

st.dataframe(df_tab_formatada, hide_index=True, use_container_width=True)

st.markdown("---")

# --- BLOCO 4: Cards Detalhados dos 3 Maiores Programas ---
st.header("Destaques: Programas com Maior Investimento")

# Captura os 3 maiores programas por orçamento
top_3_programas = df_resumo_prog.nlargest(3, col_meta_fin)

card_cols = st.columns(3)

for i, row in enumerate(top_3_programas.itertuples()):
    nome_prog = getattr(row, col_programa)
    valor_prog = getattr(row, col_meta_fin)
    
    # Formatação simplificada (Milhões ou Mil)
    if valor_prog >= 1_000_000:
        valor_card = f"R$ {valor_prog / 1_000_000:.1f} Milhões"
    else:
        valor_card = f"R$ {valor_prog / 1_000:.1f} Mil"
        
    # Conta quantas ações existem dentro desse programa específico
    qtd_acoes_prog = df_acoes[df_acoes[col_programa] == nome_prog][col_acao].nunique()
    
    with card_cols[i]:
        st.markdown(f"""
            <div class="custom-card">
                <div class="card-icon-container"><span class="card-icon">⭐</span></div>
                <div class="card-value">{valor_card}</div>
                <div class="card-title">{nome_prog}</div>
                <div class="card-description" style="margin-top: 15px;">
                    Este programa concentra uma parcela estratégica do orçamento e engloba <b>{qtd_acoes_prog} ações</b> focadas no cumprimento das metas físicas planejadas.
                </div>
            </div>
        """, unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import plotly.express as px
import csv
import os
import re

# Configuração Inicial da Página
st.set_page_config(layout="wide", page_title="Análise RREO - Anexo 8 (Educação - MDE e FUNDEB)")

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS GLOBAL - DESIGN SYSTEM GOV.BR
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rawline:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"], [class*="st-"] {
            font-family: 'Rawline', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            color: #141414;
        }

        /* Barra superior institucional simulando a barra do Governo */
        header::before {
            content: "GovAnalytics";
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
            color: #0c326f !important; /* Azul Oficial GOV.BR */
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
            border-left: 4px solid #1351b4; /* Destaque padrão Gov.BR */
            border-radius: 4px; /* Bordas menos arredondadas, estilo gov */
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
        
        .card-bold {
            font-weight: 700;
            color: #141414;
        }
    </style>
""", unsafe_allow_html=True)

# Formatadores
def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_milhoes(valor):
    if valor >= 1_000_000:
        return f"R$ {valor / 1_000_000:,.1f} Milhões".replace(".", ",")
    return formatar_brl(valor)

# -----------------------------------------------------------------------------
# 1. LEITURA E TRATAMENTO DOS DADOS
# -----------------------------------------------------------------------------
@st.cache_data
def carregar_e_tratar_dados_educacao(file):
    if isinstance(file, str):
        with open(file, 'r', encoding='utf-8-sig') as f:
            linhas = f.readlines()
    else:
        linhas = [line.decode('utf-8-sig') for line in file.readlines()]

    def limpar_valor(val):
        if pd.isna(val) or val == "" or val == "-" or str(val).isspace():
            return 0.0
        val_str = str(val).replace('.', '').replace(',', '.').strip()
        try:
            return float(val_str)
        except ValueError:
            return 0.0

    # 1.1 Receitas de Impostos
    data_rec_imp = []
    for l in linhas[1:17]:
        if l.strip():
            row = list(csv.reader([l.strip()]))[0]
            if len(row) >= 3:
                item = row[0].strip()
                prev = limpar_valor(row[1])
                real = limpar_valor(row[2])
                data_rec_imp.append({
                    'Item de Receita': item, 
                    'Previsão Atualizada': prev, 
                    'Realizado até o Bimestre': real
                })
    df_rec_imp = pd.DataFrame(data_rec_imp)

    # 1.2 Receitas do FUNDEB
    data_rec_fundeb = []
    for l in linhas[21:38]:
        if l.strip():
            row = list(csv.reader([l.strip()]))[0]
            if len(row) >= 3:
                item = row[0].strip()
                prev = limpar_valor(row[1])
                real = limpar_valor(row[2])
                data_rec_fundeb.append({
                    'Fonte FUNDEB': item, 
                    'Previsão Atualizada': prev, 
                    'Realizado até o Bimestre': real
                })
    df_rec_fundeb = pd.DataFrame(data_rec_fundeb)

    # 1.3 Despesas por Etapa de Ensino
    data_desp_etapas = []
    for l in linhas[100:105]:
        if l.strip():
            row = list(csv.reader([l.strip()]))[0]
            if len(row) >= 3:
                etapa = row[0].strip()
                dot = limpar_valor(row[1])
                emp = limpar_valor(row[2])
                liq = limpar_valor(row[3]) if len(row) > 3 else emp
                pag = limpar_valor(row[4]) if len(row) > 4 else liq
                data_desp_etapas.append({
                    'Etapa / Modalidade': etapa,
                    'Dotação Atualizada': dot,
                    'Despesas Empenhadas': emp,
                    'Despesas Liquidadas': liq,
                    'Despesas Pagas': pag
                })
    df_desp_etapas = pd.DataFrame(data_desp_etapas)

    # Indicadores Oficiais
    pct_mde_oficial = 0.0
    pct_profissionais_fundeb = 0.0
    pct_superavit_fundeb = 0.0
    receita_base_impostos = 0.0
    receita_fundeb_total = 0.0

    # Busca MDE Oficial (Linha 29)
    for l in linhas:
        if "29 - APLICAÇÃO EM MDE" in l.upper():
            row = list(csv.reader([l.strip()]))[0]
            for col in reversed(row):
                val = limpar_valor(col)
                if val > 0:
                    pct_mde_oficial = val
                    break

    # Busca Profissionais FUNDEB (Linha 15)
    for l in linhas:
        if "15 - " in l and "PROFISSIONAIS" in l.upper():
            row = list(csv.reader([l.strip()]))[0]
            for col in reversed(row):
                val = limpar_valor(col)
                if val > 0:
                    pct_profissionais_fundeb = val
                    break

    # Busca Superávit FUNDEB
    for l in linhas:
        if "18" in l and ("RECEITA RECEBIDA E NÃO APLICADA" in l.upper() or "TOTAL DA RECEITA" in l.upper()):
            numeros = re.findall(r'[\d\.]+\,\d+|[\d\.]+', l)
            if numeros:
                pct_superavit_fundeb = limpar_valor(numeros[-1])
            break

    row_rec3 = df_rec_imp[df_rec_imp['Item de Receita'].str.contains("3 - TOTAL DA RECEITA RESULTANTE DE IMPOSTOS", case=False, na=False)]
    if len(row_rec3) > 0:
        receita_base_impostos = row_rec3['Realizado até o Bimestre'].values[0]

    row_fundeb6 = df_rec_fundeb[df_rec_fundeb['Fonte FUNDEB'].str.contains("6 - RECEITAS RECEBIDAS DO FUNDEB", case=False, na=False)]
    if len(row_fundeb6) > 0:
        receita_fundeb_total = row_fundeb6['Realizado até o Bimestre'].values[0]

    return df_rec_imp, df_rec_fundeb, df_desp_etapas, pct_mde_oficial, pct_profissionais_fundeb, pct_superavit_fundeb, receita_base_impostos, receita_fundeb_total

# -----------------------------------------------------------------------------
# 2. CARREGAMENTO DO ARQUIVO
# -----------------------------------------------------------------------------
diretorio_atual = os.path.dirname(__file__)
csv_path = os.path.join(diretorio_atual, "RelatorioRREORecDespMDE_6.csv")

source = None
if os.path.exists(csv_path):
    source = csv_path
else:
    uploaded_file = st.file_uploader("Selecione o arquivo CSV RREO Anexo 8", type=["csv"])
    if uploaded_file is not None:
        source = uploaded_file

if source is None:
    st.warning("Aguardando carregamento do arquivo CSV da Educação.")
    st.stop()

try:
    df_rec_imp, df_rec_fundeb, df_desp_etapas, pct_mde_oficial, pct_profissionais_fundeb, pct_superavit_fundeb, receita_base_impostos, receita_fundeb_total = carregar_e_tratar_dados_educacao(source)
except Exception as e:
    st.error(f"Erro ao processar o arquivo CSV da Educação: {e}")
    st.stop()

def buscar_desp_etapa(nome):
    row = df_desp_etapas[df_desp_etapas['Etapa / Modalidade'].str.contains(nome, case=False, na=False)]
    return row['Despesas Empenhadas'].values[0] if len(row) > 0 else 0.0

v_infantil = buscar_desp_etapa("INFANTIL")
v_fundamental = buscar_desp_etapa("FUNDAMENTAL")

# -----------------------------------------------------------------------------
# 3. INTERFACE DO DASHBOARD
# -----------------------------------------------------------------------------
st.title("RREO Anexo 8 (Financiamento da Educação)")
st.markdown("Este painel demonstra o cumprimento da aplicação constitucional em **Manutenção e Desenvolvimento do Ensino (Art. 212 CF)** e a aplicação dos recursos do **FUNDEB (Lei 14.113/2020)**.")

# --- BLOCO 1: CARDS UNIFICADOS ---
st.header("Indicadores de Cumprimento Constitucional e Legal")

icon_mde = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 14l9-5-9-5-9 5 9 5z" /><path stroke-linecap="round" stroke-linejoin="round" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0112 20.055a11.952 11.952 0 01-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" /></svg>'
icon_teacher = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" /></svg>'
icon_coin = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-6h6m6 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'
icon_alert = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>'

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

delta_mde = pct_mde_oficial - 25.0
delta_prof = pct_profissionais_fundeb - 70.0
delta_superavit = 10.0 - pct_superavit_fundeb

with kpi1:
    st.markdown(f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_mde}</div>
            <div class="card-kpi-title">% Aplicado em MDE</div>
            <div class="card-kpi-value">{pct_mde_oficial:.2f}%</div>
            <div class="card-kpi-delta" style="color: #059669;">+{delta_mde:.2f}% acima do mín. (25%)</div>
            <div class="card-divider"></div>
            <div class="card-explanation">
                <span class="card-bold">Mínimo Constitucional (25%):</span><br>
                O Art. 212 da CF exige a aplicação de no mínimo 25% das receitas de impostos na MDE.
            </div>
        </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_teacher}</div>
            <div class="card-kpi-title">% Profissionais FUNDEB</div>
            <div class="card-kpi-value">{pct_profissionais_fundeb:.2f}%</div>
            <div class="card-kpi-delta" style="color: #059669;">+{delta_prof:.2f}% acima do mín. (70%)</div>
            <div class="card-divider"></div>
            <div class="card-explanation">
                <span class="card-bold">Regra dos Profissionais (70%):</span><br>
                A Lei do FUNDEB (Lei 14.113/20) exige no mínimo 70% dos recursos no pagamento dos profissionais.
            </div>
        </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_coin}</div>
            <div class="card-kpi-title">Receita Impostos Base</div>
            <div class="card-kpi-value">{formatar_milhoes(receita_base_impostos)}</div>
            <div class="card-kpi-delta" style="color: #64748b;">Base MDE (Art. 212)</div>
            <div class="card-divider"></div>
            <div class="card-explanation">
                <span class="card-bold">Base de Arrecadação:</span><br>
                Soma dos impostos próprios (IPTU, ISS, ITBI, IRRF) com repasses (FPM, ICMS, IPVA).
            </div>
        </div>
    """, unsafe_allow_html=True)

with kpi4:
    cor_delta_superavit = "#059669" if pct_superavit_fundeb <= 10.0 else "#dc2626"
    texto_delta_superavit = f"{delta_superavit:.2f}% margem até o limite" if pct_superavit_fundeb <= 10.0 else f"+{abs(delta_superavit):.2f}% acima do limite!"

    st.markdown(f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_alert}</div>
            <div class="card-kpi-title">Superávit FUNDEB</div>
            <div class="card-kpi-value">{pct_superavit_fundeb:.2f}%</div>
            <div class="card-kpi-delta" style="color: {cor_delta_superavit};">{texto_delta_superavit}</div>
            <div class="card-divider"></div>
            <div class="card-explanation">
                <span class="card-bold">Limite de Superávit (10%):</span><br>
                O Art. 25, § 3º da Lei 14.113/20 permite acumular no máximo 10% de saldo para o 1º quadrimestre seguinte.
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- BLOCO 2: VISÃO DE RECEITAS DA EDUCAÇÃO ---
st.header("Origem das Receitas da Educação")

df_rec_grafico = df_rec_imp[
    ~df_rec_imp['Item de Receita'].str.contains(r"TOTAL|1 - RECEITA DE IMPOSTOS|2 - RECEITA DE TRANSFERÊNCIAS|2\.1\.1|2\.1\.2", case=False, na=False)
].copy()

fig_rec = px.bar(
    df_rec_grafico, 
    x='Realizado até o Bimestre', 
    y='Item de Receita', 
    title="Arrecadação Efetiva por Fonte de Receita de Impostos (Base MDE)",
    labels={'Realizado até o Bimestre': 'Valor Realizado (R$)', 'Item de Receita': 'Origem da Receita'},
    orientation='h', 
    color_discrete_sequence=['#1351b4'],
    text_auto='.2s'
)
fig_rec.update_layout(
    font_family="Rawline, Inter",
    title_x=0.5,
    yaxis={'categoryorder': 'total ascending'}, 
    margin=dict(l=50, r=20, t=40, b=20), 
    height=450
)
st.plotly_chart(fig_rec, use_container_width=True)

# Tabela Completa de Receitas
st.subheader("Tabela de Arrecadação de Impostos e Transferências")

itens_destaque = [
    "1 - RECEITA DE IMPOSTOS",
    "2 - RECEITA DE TRANSFERÊNCIAS CONSTITUCIONAIS E LEGAIS",
    "3 - TOTAL DA RECEITA RESULTANTE DE IMPOSTOS (1 + 2)",
    "2.1 - Cota-Parte FPM"
]

def destacar_linhas_imp(row):
    for item in itens_destaque:
        if item in row['Item de Receita']:
            return ['font-weight: 600; background-color: #f8fafc;'] * len(row)
    if "2.1.1" in row['Item de Receita'] or "2.1.2" in row['Item de Receita']:
        return ['color: #475569; font-size: 0.88rem;'] * len(row)
    return [''] * len(row)

df_rec_styled = (
    df_rec_imp.style
    .apply(destacar_linhas_imp, axis=1)
    .format({
        'Previsão Atualizada': lambda x: formatar_brl(x),
        'Realizado até o Bimestre': lambda x: formatar_brl(x)
    })
)

st.dataframe(df_rec_styled, use_container_width=True, hide_index=True)

st.markdown("---")

# --- BLOCO 3: EXECUÇÃO ORÇAMENTÁRIA POR ETAPA ---
st.header("Destinação dos Recursos por Etapa de Ensino")

df_etapas_itens = df_desp_etapas[~df_desp_etapas['Etapa / Modalidade'].str.contains("21 - TOTAL", case=False, na=False)].copy()

fig_desp = px.pie(
    df_etapas_itens, 
    values='Despesas Empenhadas', 
    names='Etapa / Modalidade', 
    title='Distribuição da Despesa por Etapa de Ensino (MDE + FUNDEB)',
    hole=0.45, 
    color_discrete_sequence=['#1351b4', '#2670e8', '#5391ff', '#85b5ff']
)
fig_desp.update_layout(
    font_family="Rawline, Inter",
    title_x=0.5,
    margin=dict(l=20, r=20, t=40, b=20), 
    height=450
)
st.plotly_chart(fig_desp, use_container_width=True)

st.subheader("Execução Orçamentária por Etapa de Ensino")
st.dataframe(
    df_desp_etapas.style.format({
        'Dotação Atualizada': lambda x: formatar_brl(x),
        'Despesas Empenhadas': lambda x: formatar_brl(x),
        'Despesas Liquidadas': lambda x: formatar_brl(x),
        'Despesas Pagas': lambda x: formatar_brl(x)
    }), 
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# --- BLOCO 4: DETALHANDO OS INVESTIMENTOS NA EDUCAÇÃO ---
st.header("Detalhando os Investimentos")

card_col1, card_col2, card_col3 = st.columns(3)

icon_child = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.182 15.182a4.5 4.5 0 01-6.364 0M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'
icon_school = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147L12 14.6l7.74-4.453a1.125 1.125 0 000-1.954L12 3.74 4.26 8.193a1.125 1.125 0 000 1.954z" /><path stroke-linecap="round" stroke-linejoin="round" d="M6 12v5.25A2.25 2.25 0 008.25 19.5h7.5A2.25 2.25 0 0018 17.25V12" /></svg>'
icon_fundeb_prof = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" /></svg>'

with card_col1:
    st.markdown(f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_child}</div>
            <div class="card-kpi-title">Educação Infantil</div>
            <div class="card-kpi-value">{formatar_milhoes(v_infantil)}</div>
            <div class="card-divider"></div>
            <div class="card-explanation">
                Investimentos dedicados à manutenção, custeio e desenvolvimento de creches e pré-escolas na rede municipal.
            </div>
        </div>
    """, unsafe_allow_html=True)

with card_col2:
    st.markdown(f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_school}</div>
            <div class="card-kpi-title">Ensino Fundamental</div>
            <div class="card-kpi-value">{formatar_milhoes(v_fundamental)}</div>
            <div class="card-divider"></div>
            <div class="card-explanation">
                Recursos direcionados ao custeio do Ensino Fundamental (1º ao 9º ano), transporte escolar e material didático.
            </div>
        </div>
    """, unsafe_allow_html=True)

with card_col3:
    st.markdown(f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_fundeb_prof}</div>
            <div class="card-kpi-title">Recursos do FUNDEB</div>
            <div class="card-kpi-value">{formatar_milhoes(receita_fundeb_total)}</div>
            <div class="card-divider"></div>
            <div class="card-explanation">
                Recursos repassados pelo fundo e destinados prioritariamente à valorização e remuneração dos profissionais da educação básica.
            </div>
        </div>
    """, unsafe_allow_html=True)
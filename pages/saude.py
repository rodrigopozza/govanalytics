import csv
import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    layout="wide", page_title="Análise RREO - Anexo 12 (Saúde)", page_icon="📊"
)
# ==========================================
# CONFIGURAÇÃO DA BARRA LATERAL (TOPO)
# ==========================================
with st.sidebar:
    # Logo no topo à esquerda
    st.image("logo.png", use_container_width=True)
    st.markdown("---")
    
    # Exemplo de conteúdo do menu que você já tem ou vai usar:
    st.markdown("### Navegação")
    # (Seus filtros ou links da barra lateral entram aqui)
# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS GLOBAL (Padrão GOV.BR & Design System Institucional)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Importação das Fontes Rawline e Inter do Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Rawline:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

        /* Aplicação global da tipografia padrão Gov.br */
        html, body, [class*="css"], [class*="st-"] {
            font-family: 'Rawline', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            color: #141414;
        }

        /* Barra superior institucional simulando a barra do Governo Federal/Estadual */
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

        /* Alinhamento e Cores de Títulos no Padrão Gov.br */
        h1, h2, h3, .stMarkdown p {
            text-align: left;
        }

        h1 {
            font-weight: 700 !important;
            color: #0c326f !important;
            font-size: 2rem !important;
            border-bottom: 2px solid #004587;
            padding-bottom: 8px;
            letter-spacing: -0.025em;
        }

        h2 {
            font-weight: 600 !important;
            color: #1351b4 !important;
            letter-spacing: -0.02em;
            margin-top: 1.5rem !important;
        }

        h3 {
            font-weight: 600 !important;
            color: #2670e8 !important;
        }

        /* ----------------------------------------------------------------- */
        /* CARDS UNIFICADOS NO ESTILO GOV.BR (Borda lateral azul institucional) */
        /* ----------------------------------------------------------------- */
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
            letter-spacing: -0.02em;
            margin-bottom: 4px;
        }
        
        .card-kpi-delta {
            color: #059669;
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
            color: #0c326f;
        }
    </style>
""",
    unsafe_allow_html=True,
)


# Helper para formatação de moeda em padrão BRL
def formatar_brl(valor):
  return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# Helper para formatação amigável em Milhões
def formatar_milhoes(valor):
  if valor >= 1_000_000:
    return (
        f"R$ {valor / 1_000_000:,.1f} Milhões".replace(".", ",")
        .replace("Milhões", "milhões")
    )
  return formatar_brl(valor)


# -----------------------------------------------------------------------------
# 1. TRATAMENTO DOS DADOS DO CSV MISTO
# -----------------------------------------------------------------------------
@st.cache_data
def carregar_e_tratar_dados(file):
  if isinstance(file, str):
    with open(file, "r", encoding="utf-8-sig") as f:
      linhas = f.readlines()
  else:
    linhas = [line.decode("utf-8-sig") for line in file.readlines()]

  def limpar_valor(val):
    if pd.isna(val) or val == "" or val == "-" or str(val).isspace():
      return 0.0
    val_str = str(val).replace(".", "").replace(",", ".").strip()
    try:
      return float(val_str)
    except ValueError:
      return 0.0

  # 1.1 Receitas
  linhas_receitas = [l.strip() for l in linhas[0:14] if l.strip()]
  data_rec = [list(csv.reader([l]))[0] for l in linhas_receitas[1:]]
  df_rec = pd.DataFrame(
      data_rec,
      columns=[
          "Item de Receita",
          "Previsão Inicial",
          "Previsão Atualizada",
          "Realizado até o Bimestre",
          "% Realizado",
      ],
  )

  for col in [
      "Previsão Inicial",
      "Previsão Atualizada",
      "Realizado até o Bimestre",
  ]:
    df_rec[col] = df_rec[col].apply(limpar_valor)
  df_rec["% Realizado"] = df_rec["% Realizado"].str.replace(",", ".").astype(float)

  # 1.2 Despesas Próprias da Saúde
  linhas_desp = [l.strip() for l in linhas[15:38] if l.strip()]
  data_desp = [list(csv.reader([l]))[0] for l in linhas_desp[1:]]
  cols_desp = [
      "Subfunção",
      "Dotação Inicial",
      "Dotação Atualizada",
      "Despesas Empenhadas",
      "% Emp",
      "Despesas Liquidadas",
      "% Liq",
      "Despesas Pagas",
      "% Pag",
  ]
  df_desp = pd.DataFrame(data_desp, columns=cols_desp)

  for col in [
      "Dotação Inicial",
      "Dotação Atualizada",
      "Despesas Empenhadas",
      "Despesas Liquidadas",
      "Despesas Pagas",
  ]:
    df_desp[col] = df_desp[col].apply(limpar_valor)
  for col in ["% Emp", "% Liq", "% Pag"]:
    df_desp[col] = df_desp[col].str.replace(",", ".").astype(float)

  # 1.3 Percentuais Oficiais
  pct_empenhado_oficial = 0.0
  pct_liquidado_oficial = 0.0

  for l in linhas:
    if "PERCENTUAL DA RECEITA DE IMPOSTOS E TRANSFERÊNCIAS CONSTITUCIONAIS" in l:
      row = list(csv.reader([l.strip()]))[0]
      nums = []
      for col in row:
        if col.strip() and not col.strip().startswith("PERCENTUAL"):
          val = limpar_valor(col)
          if val > 0:
            nums.append(val)

      if len(nums) >= 2:
        pct_empenhado_oficial = nums[0]
        pct_liquidado_oficial = nums[1]
      elif len(nums) == 1:
        pct_empenhado_oficial = nums[0]
      break

  return df_rec, df_desp, pct_empenhado_oficial, pct_liquidado_oficial


# -----------------------------------------------------------------------------
# 2. CARREGAMENTO DO ARQUIVO LOCAL OU VIA UPLOAD
# -----------------------------------------------------------------------------
diretorio_atual = os.path.dirname(__file__)
csv_path = os.path.join(
    diretorio_atual, "RelatorioRREORecDespAcoesServPublicoSaude_3.csv"
)

source = None
if os.path.exists(csv_path):
  source = csv_path
else:
  uploaded_file = st.file_uploader("Selecione o arquivo RREO Anexo 12", type=["csv"])
  if uploaded_file is not None:
    source = uploaded_file

if source is None:
  st.warning("Aguardando carregamento do arquivo CSV.")
  st.stop()

try:
  df_rec, df_desp, pct_empenhado_oficial, pct_liquidado_oficial = (
      carregar_e_tratar_dados(source)
  )
except Exception as e:
  st.error(f"Erro ao processar o arquivo CSV: {e}")
  st.stop()

# -----------------------------------------------------------------------------
# 3. VALORES PARA OS KPIS PRINCIPAIS
# -----------------------------------------------------------------------------
row_rec_total = df_rec[
    df_rec["Item de Receita"].str.contains(
        "TOTAL DAS RECEITAS", case=False, na=False
    )
]
receita_base = (
    row_rec_total["Realizado até o Bimestre"].values[0]
    if len(row_rec_total) > 0
    else 0.0
)

row_desp_total = df_desp[
    df_desp["Subfunção"].str.contains("TOTAL", case=False, na=False)
]
despesa_empenhada_saude = (
    row_desp_total["Despesas Empenhadas"].values[0]
    if len(row_desp_total) > 0
    else 0.0
)

minimo_constitucional = 15.0


def buscar_valor_subfuncao(nome):
  row = df_desp[df_desp["Subfunção"].str.contains(nome, case=False, na=False)]
  return row["Despesas Empenhadas"].values[0] if len(row) > 0 else 0.0


v_atencao_basica = buscar_valor_subfuncao("Atenção Básica")
v_hospitalar = buscar_valor_subfuncao("Assistência Hospitalar")
v_vigilancia = (
    buscar_valor_subfuncao("Vigilância em Saúde")
    + buscar_valor_subfuncao("Vigilância Epidemiológica")
    + buscar_valor_subfuncao("Vigilância Sanitária")
)

# -----------------------------------------------------------------------------
# 4. INTERFACE DO DASHBOARD
# -----------------------------------------------------------------------------
st.title("RREO Anexo 12 — Financiamento da Saúde")
st.markdown(
    "Demonstrativo das receitas de impostos e das despesas próprias com ações e"
    " serviços públicos de saúde, em conformidade com a **LC nº 141/2012**."
)

# --- BLOCO 1: CARDS UNIFICADOS DE INDICADORES CONSTITUCIONAIS ---
st.header("Indicadores de Cumprimento Constitucional")

# Ícones SVG institucionais
icon_chart = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg>'
icon_check = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'
icon_coin = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-6h6m6 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'
icon_box = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" /></svg>'

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

delta_val = pct_empenhado_oficial - minimo_constitucional

with kpi1:
  st.markdown(
      f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_chart}</div>
            <div class="card-kpi-title">% Aplicado (Empenhado)</div>
            <div class="card-kpi-value">{pct_empenhado_oficial:.2f}%</div>
            <div class="card-kpi-delta">+{delta_val:.2f}% acima do mínimo (15%)</div>
            <div class="card-divider"></div>
            <div class="card-explanation">
                <span class="card-bold">Mínimo Legal (15%):</span><br>
                A LC nº 141/2012 exige a aplicação mínima de 15% das receitas de impostos em saúde. O índice empenhado atesta o cumprimento da regra.
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

with kpi2:
  st.markdown(
      f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_check}</div>
            <div class="card-kpi-title">% Liquidado em Saúde</div>
            <div class="card-kpi-value">{pct_liquidado_oficial:.2f}%</div>
            <div class="card-kpi-delta" style="color: #1351b4;">Execução Comprovada</div>
            <div class="card-divider"></div>
            <div class="card-explanation">
                <span class="card-bold">Execução Efetiva:</span><br>
                Representa os recursos cujos serviços ou suprimentos médicos foram efetivamente prestados e validados pelo município.
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

with kpi3:
  st.markdown(
      f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_coin}</div>
            <div class="card-kpi-title">Receitas de Impostos Base</div>
            <div class="card-kpi-value">{formatar_milhoes(receita_base)}</div>
            <div class="card-kpi-delta" style="color: #1351b4;">Base LC 141/2012</div>
            <div class="card-divider"></div>
            <div class="card-explanation">
                <span class="card-bold">Base de Cálculo:</span><br>
                Soma dos impostos próprios (IPTU, ISS, ITBI) com repasses constitucionais obrigatórios da União e Estado (ICMS, IPVA, FPM).
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

with kpi4:
  st.markdown(
      f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_box}</div>
            <div class="card-kpi-title">Total Empenhado em Saúde</div>
            <div class="card-kpi-value">{formatar_milhoes(despesa_empenhada_saude)}</div>
            <div class="card-kpi-delta" style="color: #1351b4;">Orçamento Reservado</div>
            <div class="card-divider"></div>
            <div class="card-explanation">
                <span class="card-bold">Montante Alocado:</span><br>
                Valor total reservado para o pagamento de equipes de saúde, insumos, medicamentos e contratos de serviços hospitalares.
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

st.markdown("---")

# --- BLOCO 2: VISÃO DE RECEITAS GOVERNAMENTAIS ---
st.header("Origem das Receitas Governamentais")

df_rec_itens = df_rec[
    ~df_rec["Item de Receita"].str.contains(
        r"TOTAL|RECEITA DE IMPOSTOS \(I\)|RECEITA DE TRANSFERÊNCIAS",
        case=False,
        na=False,
    )
].copy()

# 2.1 Gráfico de Receitas com paleta institucional Gov.br
fig_rec = px.bar(
    df_rec_itens,
    x="Realizado até o Bimestre",
    y="Item de Receita",
    title="Arrecadação Efetiva por Tipo de Imposto e Transferência Legal",
    labels={
        "Realizado até o Bimestre": "Valor Realizado (R$)",
        "Item de Receita": "Origem da Receita",
    },
    orientation="h",
    color_discrete_sequence=["#1351b4"],
    text_auto=".2s",
)
fig_rec.update_layout(
    font_family="Rawline, Inter",
    title_x=0.5,
    yaxis={"categoryorder": "total ascending"},
    margin=dict(l=50, r=20, t=40, b=20),
    height=450,
)
st.plotly_chart(fig_rec, use_container_width=True)

# 2.2 Tabela de Receitas
st.subheader("Tabela de Arrecadação de Receitas")

itens_negrito = [
    "RECEITA DE IMPOSTOS (I)",
    "RECEITA DE TRANSFERÊNCIAS CONSTITUCIONAIS E LEGAIS (II)",
    (
        "TOTAL DAS RECEITAS RESULTANTES DE IMPOSTOS E TRANSFERÊNCIAS"
        " CONSTITUCIONAIS E LEGAIS (III) = (I + II)"
    ),
]


def destacar_totais(row):
  if row["Item de Receita"] in itens_negrito:
    return ["font-weight: 700; background-color: #f3f4f6; color: #0c326f;"] * len(
        row
    )
  return [""] * len(row)


df_rec_styled = df_rec.style.apply(destacar_totais, axis=1).format({
    "Previsão Inicial": lambda x: formatar_brl(x),
    "Previsão Atualizada": lambda x: formatar_brl(x),
    "Realizado até o Bimestre": lambda x: formatar_brl(x),
    "% Realizado": "{:.2f}%",
})

st.dataframe(df_rec_styled, use_container_width=True, hide_index=True)

st.markdown("---")

# --- BLOCO 3: DESTINAÇÃO DAS DESPESAS ---
st.header("Destinação dos Recursos")

df_desp_itens = df_desp[
    ~df_desp["Subfunção"].str.contains(
        "TOTAL|Despesas Correntes|Despesas de Capital", case=False, na=False
    )
].copy()

# 3.1 Gráfico de Despesas com cores institucionais
fig_desp = px.pie(
    df_desp_itens,
    values="Despesas Empenhadas",
    names="Subfunção",
    title="Distribuição da Despesa",
    hole=0.45,
    color_discrete_sequence=[
        "#1351b4",
        "#2670e8",
        "#5391ff",
        "#0c326f",
        "#8bc34a",
    ],
)
fig_desp.update_layout(
    font_family="Rawline, Inter",
    title_x=0.5,
    margin=dict(l=20, r=20, t=40, b=20),
    height=450,
)
st.plotly_chart(fig_desp, use_container_width=True)

# 3.2 Tabela de Despesas
st.subheader("Execução Orçamentária por Subfunção")
st.dataframe(
    df_desp_itens[[
        "Subfunção",
        "Dotação Atualizada",
        "Despesas Empenhadas",
        "% Emp",
        "Despesas Liquidadas",
        "% Liq",
        "Despesas Pagas",
        "% Pag",
    ]].style.format({
        "Dotação Atualizada": lambda x: formatar_brl(x),
        "Despesas Empenhadas": lambda x: formatar_brl(x),
        "% Emp": "{:.2f}%",
        "Despesas Liquidadas": lambda x: formatar_brl(x),
        "% Liq": "{:.2f}%",
        "Despesas Pagas": lambda x: formatar_brl(x),
        "% Pag": "{:.2f}%",
    }),
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")

# --- BLOCO 4: DETALHANDO OS INVESTIMENTOS ---
st.header("Detalhando os Investimentos")

card_col1, card_col2, card_col3 = st.columns(3)

# SVG Icons para Investimentos
icon_steth = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9 9 0 009-9H3a9 9 0 009 9zM12 3v9" /></svg>'
icon_hospital = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5m0 0v-4a1 1 0 011-1h2a1 1 0 011 1v4m-4 0h4m-2-12v3m-1.5-1.5h3" /></svg>'
icon_shield = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751A11.959 11.959 0 0112 2.714z" /></svg>'

with card_col1:
  st.markdown(
      f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_steth}</div>
            <div class="card-kpi-title">Atenção Básica</div>
            <div class="card-kpi-value">{formatar_milhoes(v_atencao_basica)}</div>
            <div class="card-divider"></div>
            <div class="card-explanation">
                Investimentos em Unidades Básicas de Saúde (UBSs), consultas de rotina, vacinação e programas de saúde da família nos bairros.
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

with card_col2:
  st.markdown(
      f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_hospital}</div>
            <div class="card-kpi-title">Assistência Hospitalar</div>
            <div class="card-kpi-value">{formatar_milhoes(v_hospitalar)}</div>
            <div class="card-divider"></div>
            <div class="card-explanation">
                Custeio de UPAs 24h, repasses hospitalares locais, cirurgias, exames de alta complexidade e atendimento de urgência.
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

with card_col3:
  st.markdown(
      f"""
        <div class="unified-card">
            <div class="card-icon-wrapper">{icon_shield}</div>
            <div class="card-kpi-title">Vigilância em Saúde</div>
            <div class="card-kpi-value">{formatar_milhoes(v_vigilancia)}</div>
            <div class="card-divider"></div>
            <div class="card-explanation">
                Ações integradas de Vigilância Sanitária e Epidemiológica para prevenção e controle de doenças no município.
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )
# RODAPÉ DA PÁGINA PRINCIPAL (FINAL DO SCRIPT)
# ==========================================
st.markdown("---")
col_esq, col_centro, col_dir = st.columns([2, 1, 2])
with col_centro:
    st.image("logo.png", use_container_width=True)
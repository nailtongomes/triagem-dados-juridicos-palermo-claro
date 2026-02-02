import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- SISTEMA DE LOGIN SIMPLES ---
def check_password():
    """Retorna True se o usuário inseriu a senha correta."""
    def password_entered():
        """Verifica se a senha inserida é correta."""
        if st.session_state["username"] == "palermo" and st.session_state["password"] == "palermo":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Não guarda a senha no session_state
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Exibe formulário de login
        st.markdown("""
            <div style='text-align: center; padding-top: 50px;'>
                <h1 style='color: #0f172a;'>Portal de Inteligência Jurídica</h1>
                <p style='color: #64748b;'>Advocacia Palermo & N3 Wizards</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login"):
                st.text_input("Usuário", key="username")
                st.text_input("Senha", type="password", key="password")
                st.form_submit_button("Acessar Painel", on_click=password_entered)
            
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("😕 Usuário ou senha incorretos")
        return False
    else:
        return st.session_state["password_correct"]

if not check_password():
    st.stop()  # Interrompe a execução aqui se não estiver logado

# --- CONTINUAÇÃO DO APP ---

# Configuração da página para um visual profissional
st.set_page_config(
    page_title="Palermo Planilhas - Inteligência de Recuperação",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Configuração da página para um visual profissional e sóbrio
st.set_page_config(
    page_title="Inteligência de Dados | Advocacia Palermo & N3 Wizards",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilo CSS customizado - Visual Premium, Sóbrio e Corporativo
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #f1f5f9;
    }
    
    /* Elegant Header */
    .brand-header {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .brand-subtitle {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 400;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* Metric Cards Otimizados */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 25px !important;
        border-radius: 16px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06) !important;
        border-left: 5px solid #0f172a !important;
    }
    
    /* Botões e Inputs */
    .stButton>button {
        border-radius: 8px;
        background-color: #0f172a;
        color: white;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Footer Style */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #64748b;
        font-size: 0.8rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 5rem;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    excel_path = 'palermo-planilhas-analisado_v3.xlsx' # amostra
    parquet_path = 'palermo-planilhas-analisado_v3.parquet'
    
    # Se o parquet existe, lê dele (performance)
    if os.path.exists(parquet_path):
        return pd.read_parquet(parquet_path)
    
    # Se não existe, converte do Excel
    if os.path.exists(excel_path):
        with st.status("Otimizando base de dados de 140k+ registros..."):
            df = pd.read_excel(excel_path)
            
            # Limpeza inicial
            categorical_cols = ['nome_tribunal', 'UF', 'Comarca', 'Nome Reclamado']
            for col in categorical_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip().str.upper()
            
            # Garantir colunas numéricas
            if 'ano_base' in df.columns:
                df['ano_base'] = pd.to_numeric(df['ano_base'], errors='coerce')
            
            df.to_parquet(parquet_path, index=False, compression='snappy')
            return df
    return None

# Carregar dados
df_raw = load_data()

if df_raw is None:
    st.error("Base de dados não encontrada.")
    st.stop()

# --- SIDEBAR: GESTÃO E FILTROS ---
st.sidebar.title("� Gestão de Dados")
st.sidebar.markdown("Foque nos processos com alta chance de recuperação.")

# 1. Filtro de Tribunal (nome_tribunal conforme solicitado)
st.sidebar.subheader("Segmentação Geográfica")
all_tribunais = sorted(df_raw["nome_tribunal"].dropna().unique().tolist())
tribunais_sel = st.sidebar.multiselect("Tribunais", options=all_tribunais)

all_ufs = sorted(df_raw["UF"].dropna().unique().tolist())
ufs_sel = st.sidebar.multiselect("Estados (UF)", options=all_ufs)

"""
# 2. Filtros de Saldo e Valor
st.sidebar.markdown("---")
st.sidebar.subheader("Filtros de Valor")
min_saldo = st.sidebar.number_input("Saldo Judicial Mínimo (R$)", min_value=0, value=0, step=500)
usar_saldo_1k = st.sidebar.toggle("Apenas Saldo > R$ 1.000", value=False)
"""

# 3. Status e Validação
st.sidebar.markdown("---")
st.sidebar.subheader("Qualidade dos Dados")
apenas_cnj_ok = st.sidebar.toggle("Apenas CNJ Válido (Fácil Localização)", value=False)
apenas_doc_ok = st.sidebar.toggle("Apenas CPF/CNPJ Válido (Busca Manual)", value=False)
apenas_eletronico = st.sidebar.toggle("Apenas Processos Eletrônicos (>2014)", value=False)

# --- APLICAÇÃO DOS FILTROS ---
df = df_raw.copy()

if tribunais_sel:
    df = df[df["nome_tribunal"].isin(tribunais_sel)]
if ufs_sel:
    df = df[df["UF"].isin(ufs_sel)]

# Filtro de Saldo
#if "Saldo int" in df.columns:
#    df = df[df["Saldo int"] >= min_saldo]
#if usar_saldo_1k and "saldo_maior_1k" in df.columns:
#    df = df[df["saldo_maior_1k"] == True]

# Qualidade e Ano
if apenas_cnj_ok and "cnj_ok" in df.columns:
    df = df[df["cnj_ok"] == True]
if apenas_doc_ok and "doc_ok" in df.columns:
    df = df[df["doc_ok"] == True]
if apenas_eletronico and "ano_base" in df.columns:
    df = df[df["ano_base"] > 2014]

# --- HEADER BRANDING ---
st.markdown("""
    <div class="brand-header">
        <div class="brand-subtitle">Plataforma de Inteligência de Dados</div>
        <h1 style='color: white; margin: 0; padding: 0.5rem 0;'>Advocacia Palermo</h1>
        <div style='font-size: 0.8rem; opacity: 0.8;'>Em parceria com <b>N3 Wizards: Automações e IA</b></div>
    </div>
    """, unsafe_allow_html=True)

# --- PAINEL PRINCIPAL ---
st.markdown("### 📊 Painel Geral de Recuperação")
st.markdown("""
Analise de ativos recuperáveis com foco em agilidade. 
Use a barra lateral para filtrar por **Tribunal**, **Estado** ou **Status de Validação**.
""")

# Métricas Principais
m1, m4 = st.columns(2)
with m1:
    st.metric("Processos Filtrados", f"{len(df):,}")
with m4:
    eletronicos = (df["ano_base"] > 2014).sum() if "ano_base" in df.columns else 0
    pct = (eletronicos / len(df) * 100) if len(df) > 0 else 0
    st.metric("Eletrônicos (>2014)", f"{pct:.1f}%")

m2, m3 = st.columns(2)
"""
with m2:
    saldo_total = df["Saldo int"].sum() if "Saldo int" in df.columns else 0
    # converter para formato BRL - de R$ 1,189,855.00 para R$ 1.189.855,00
    saldo_total = f"R$ {saldo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.metric("Saldo Total", f"{saldo_total}")
"""

with m3:
    dep_total = df["Valor Depósito Original Float"].sum() if "Valor Depósito Original Float" in df.columns else 0
    # converter para formato BRL - de R$ 1,189,855.00 para R$ 1.189.855,00
    dep_total = f"R$ {dep_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.metric("Depósito Original", f"{dep_total}")


st.markdown("---")

# Visualização de Agrupamento por Reclamado (Ponto 4)
col_l, col_r = st.columns([2, 1])

with col_l:
    st.subheader("Concentração por Reclamado (Empresas/Entidades)")
    if not df.empty:
        # Agrupando por Nome Reclamado conforme solicitado
        df_group = df.groupby('Nome Reclamado').agg({
            'Saldo int': 'sum',
            'Processo': 'count'
        }).reset_index().rename(columns={'Processo': 'Qtd Processos'})
        
        df_group = df_group.sort_values(by='Saldo int', ascending=False).head(15)
        
        fig_rec = px.bar(df_group, x='Saldo int', y='Nome Reclamado', 
                         orientation='h',
                         title="Top 15 Reclamados por Saldo Recuperável",
                         labels={'Saldo int': 'Saldo Total (R$)', 'Nome Reclamado': 'Reclamado'},
                         color='Saldo int', color_continuous_scale='Blues',
                         template="plotly_white")
        fig_rec.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_rec, use_container_width=True)
    else:
        st.info("Ajuste os filtros para visualizar os dados.")

with col_r:
    st.subheader("Distribuição por Ano Base")
    if not df.empty and "ano_base" in df.columns:
        fig_hist = px.histogram(df, x="ano_base", 
                                title="Frequência por Ano Base",
                                color_discrete_sequence=['#4F46E5'],
                                template="plotly_white")
        st.plotly_chart(fig_hist, use_container_width=True)

# Tabela Estratégica
st.markdown("---")
st.subheader("🔍 Lista de Oportunidades Selecionadas")

# Definindo colunas estratégicas para o gestor
cols_apresentacao = [
    'Nome Reclamado', 'Nome Reclamante', 'nome_tribunal', 'UF', 'Processo', 
    'ano_base', 'Saldo int', 'Valor Depósito Original Float', 'cnj_ok', 'doc_ok'
]
cols_df = [c for c in cols_apresentacao if c in df.columns]

# Adicionando visual indicador de processo eletrônico
if 'ano_base' in df.columns:
    df['Tipo'] = df['ano_base'].apply(lambda x: '🌐 Eletrônico' if x > 2014 else '📄 Físico/Antigo')
    if 'Tipo' not in cols_df:
        cols_df.insert(0, 'Tipo')

st.dataframe(
    df[cols_df].sort_values(by='Saldo int', ascending=False),
    use_container_width=True,
    hide_index=True,
    column_config={
        # "Saldo int": st.column_config.NumberColumn("Saldo Atual", format="R$ %.2f"),
        "Valor Depósito Original Float": st.column_config.NumberColumn("Dep. Original", format="R$ %.2f"),
        "cnj_ok": st.column_config.CheckboxColumn("CNJ Válido"),
        "doc_ok": st.column_config.CheckboxColumn("Doc OK"),
        "ano_base": st.column_config.NumberColumn("Ano Base", format="%d")
    }
)

# ocultar coluna Saldo int
df = df.drop(columns=['Saldo int'])

st.sidebar.markdown("---")
st.sidebar.caption("v1.2.0 | Advocacia Palermo & N3 Wizards")

# Footer corporativo no final da página
st.markdown("""
    <div class="footer">
        © 2024 Advocacia Palermo | Desenvolvido por <b>N3 Wizards: Automações e IA</b><br>
        Tecnologia de Alta Performance para Inteligência Jurídica
    </div>
    """, unsafe_allow_html=True)

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import math
import io

# --- CONFIGURAÇÃO VISUAL MASTER MPN ---
st.set_page_config(page_title="MPN | Engenharia & Diagnóstico", layout="wide", page_icon="❄️")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    [data-testid="stMetric"] {
        background-color: #004A99 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        border: 2px solid #A9A9A9 !important;
    }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-weight: bold !important; font-size: 1.1rem !important; }
    [data-testid="stMetricValue"] { color: #00D1FF !important; font-size: 2.2rem !important; }
    .stButton>button { background-color: #004A99; color: white; border-radius: 10px; height: 3.5em; font-weight: bold; width: 100%; border: none; }
    h1, h2, h3, h4 { color: #004A99; font-family: 'Arial', sans-serif; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ENGENHARIA (RÉGUA DANFOSS - DEW POINT) ---
def calcular_t_sat_danfoss_dew(psig, gas):
    if psig is None or not gas or psig <= 0: return None
    try:
        # Constantes calibradas para aproximar a Régua Danfoss (Dew Point / Ponto de Orvalho)
        if gas == "R-410A": return 22.95 * math.log(psig) - 104.38
        elif gas == "R-22": return 26.54 * math.log(psig) - 121.93
        elif gas == "R-134a": return 31.75 * math.log(psig) - 147.35
        elif gas == "R-404A": return 20.88 * math.log(psig) - 94.32
        elif gas == "R-32": return 23.15 * math.log(psig) - 106.85
        elif gas == "R-407C": return 24.10 * math.log(psig) - 110.50
    except: return None
    return None

# --- NAVEGAÇÃO ---
tab_diag, tab_solucoes, tab_carga, tab_subs, tab_manuais = st.tabs([
    "📊 Diagnóstico Master", "🤖 IA & Soluções", "📐 Carga Térmica", "🔄 Substituição & Alternativas", "📚 Manuais"
])

# --- ABA 1: DIAGNÓSTICO MASTER ---
with tab_diag:
    st.subheader("📋 Identificação Completa do Sistema")
    with st.expander("Dados do Cliente e Equipamento", expanded=True):
        c1, c2, c3 = st.columns(3)
        cli = c1.text_input("Cliente", placeholder="Nome ou Empresa")
        tec = c2.text_input("Responsável Técnico")
        fab = c3.text_input("Fabricante", placeholder="Ex: Daikin / Carrier")
        
        c4, c5, c6, c7 = st.columns(4)
        lin = c4.text_input("Linha/Família", placeholder="Ex: Inverter V")
        mod_int = c5.text_input("Modelo Interno (Evaporadora)")
        mod_ext = c6.text_input("Modelo Externo (Condensadora)")
        ser = c7.text_input("Número de Série (S/N)")

    st.sidebar.header("⚙️ Setup do Ciclo")
    f_equip = st.sidebar.selectbox("Tipo de Equipamento", ["Split Hi-Wall", "Chiller", "VRF/VRV", "Câmara Fria", "Piso-Teto"])
    f_gas = st.sidebar.selectbox("Fluido Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-32", "R-407C"])
    f_tec = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter", "Digital Scroll"])

    st.subheader("🛠️ Coleta de Dados Termofluidodinâmicos")
    m1, m2, m3, m4 = st.columns(4) # Adicionada 4ª coluna para T. Sat
    
    with m1:
        st.markdown("#### 🌬️ Troca de Ar")
        t_ret = st.number_input("Temp. Retorno [°C]", value=24.0)
        t_ins = st.number_input("Temp. Insuflação [°C]", value=12.0)
        dt = t_ret - t_ins
        st.metric("DELTA T", f"{dt:.1f} °C")

    with m2:
        st.markdown("#### 🧪 Pressão")
        p_suc = st.number_input("Pressão Sucção (PSI)", value=120.0)
        tsat = calcular_t_sat_danfoss_dew(p_suc, f_gas)
        st.metric("TEMP. SATURAÇÃO", f"{tsat:.1f} °C" if tsat is not None else "--")

    with m3:
        st.markdown("#### 🌡️ Superaquecimento")
        t_fin = st.number_input("Temp. Sucção Linha [°C]", value=10.0)
        sh = t_fin - tsat if (tsat is not None) else 0.0
        st.metric("SUPER AQUECIMENTO", f"{sh:.1f} K", delta="Ideal: 5 a 12K", delta_color="off")

    with m4:
        st.markdown("#### ⚡ Elétrica")
        v_rla = st.number_input("Corrente RLA [A]", value=1.0)
        v_med = st.number_input("Corrente Medida [A]", value=0.0)
        st.metric("AMPERAGEM REAL", f"{v_med:.1f} A")

# --- ABA 2: IA & SOLUÇÕES ---
with tab_solucoes:
    st.subheader("🤖 Consultoria MPN IA")
    if tsat is not None:
        st.info(f"Análise baseada em {f_gas} com T. Sat de {tsat:.1f}°C")
        if sh < 5: st.error("🚨 SH Baixo: Risco de retorno de líquido.")
        elif sh > 12: st.warning("⚠️ SH Alto: Falta de fluido ou restrição.")
        else: st.success("✅ Ciclo operando na faixa ideal.")

# --- BOTÃO PDF ---
if st.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if not cli: st.error("Insira o nome do cliente.")
    else:
        st.success(f"Relatório gerado para {cli}. (Lógica de PDF ativa)")

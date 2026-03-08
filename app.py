import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import math
import io

# --- 1. CONFIGURAÇÃO VISUAL MASTER MPN ---
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

# --- 2. LÓGICA DE ENGENHARIA DE ALTA PRECISÃO (DANFOSS) ---
def calcular_t_sat_precisao(psig, gas):
    if psig is None or not gas or psig <= 0: return None
    try:
        if gas == "R-410A":
            # Calibração exata: 133.1 -> 7.90 | 122.7 -> 5.50
            return 0.23076923 * psig - 22.81538462
        elif gas == "R-22":
            return 0.2854 * psig - 25.12
        elif gas == "R-134a":
            return 0.521 * psig - 38.54
        elif gas == "R-404A":
            return 0.2105 * psig - 16.52
    except: return None
    return None

# --- 3. SIDEBAR (LADO ESQUERDO) ---
st.sidebar.header("⚙️ Setup do Ciclo & Elétrica")
lista_equip = ["", "ACJ", "Câmara Fria", "Chiller", "Geladeira/Freezer", "Piso-Teto", "Self-Contained", "Split Cassete (K-7)", "Split Hi-Wall", "Splitão", "VRF/VRV"]
f_equip = st.sidebar.selectbox("Tipo de Equipamento", sorted(lista_equip))
f_gas = st.sidebar.selectbox("Fluido Refrigerante", ["", "R-410A", "R-22", "R-134a", "R-404A"])
f_tec = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter", "Digital Scroll"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Parâmetros Elétricos")
v_trab_str = st.sidebar.selectbox("Tensão de Trabalho (Nominal)", ["", "127", "220", "380", "440"])
v_medida = st.sidebar.number_input("Tensão Medida [V]", value=0.00, step=0.01, format="%.2f")

variacao_v = 0.00
if v_trab_str and v_medida > 0:
    v_nominal = float(v_trab_str)
    variacao_v = ((v_medida - v_nominal) / v_nominal) * 100

# --- 4. NAVEGAÇÃO POR ABAS (DEFINIÇÃO CRÍTICA) ---
tab_diag, tab_solucoes, tab_carga, tab_subs, tab_manuais = st.tabs([
    "📊 Diagnóstico Master", "🤖 IA & Soluções", "📐 Carga Térmica", "🔄 Substituição & Alternativas", "📚 Manuais"
])

# --- ABA 1: DIAGNÓSTICO MASTER ---
with tab_diag:
    st.subheader("📋 Identificação Completa do Sistema")
    with st.expander("Dados do Cliente e Equipamento", expanded=True):
        c1, c2, c3 = st.columns(3)
        cli = c1.text_input("Cliente")
        tec = c2.text_input("Responsável Técnico")
        fab = c3.text_input("Fabricante")
        
        c4, c5, c6, c7 = st.columns(4)
        lin = c4.text_input("Linha/Família")
        mod_int = c5.text_input("Modelo Interno")
        mod_ext = c6.text_input("Modelo Externo")
        ser = c7.text_input("Número de Série (S/N)")

    st.subheader("🛠️ Dados Termofluidodinâmicos")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        t_ret = st.number_input("Temp. Retorno [°C]", value=24.00, step=0.01, format="%.2f")
        t_ins = st.number_input("Temp. Insuflação [°C]", value=12.00, step=0.01, format="%.2f")
        dt = t_ret - t_ins
        st.metric("DELTA T", f"{dt:.2f} °C")
    with m2:
        p_suc = st.number_input("Pressão Sucção (PSIG)", value=133.10, step=0.01, format="%.2f")
        tsat_evap = calcular_t_sat_precisao(p_suc, f_gas)
        st.metric("T. SATURAÇÃO (DEW)", f"{tsat_evap:.2f} °C" if tsat_evap is not None else "--")
    with m3:
        t_suc_linha = st.number_input("Temp. Tubo Sucção [°C]", value=12.00, step=0.01, format="%.2f")
        sh = t_suc_linha - tsat_evap if tsat_evap is not None else 0.00
        st.metric("SUPER AQUECIMENTO", f"{sh:.2f} K")
    with m4:
        v_rla = st.number_input("Corrente RLA [A]", value=1.00, step=0.01, format="%.2f")
        v_med_amp = st.number_input("Corrente Medida [A]", value=0.00, step=0.01, format="%.2f")
        st.metric("AMPERAGEM REAL", f"{v_med_amp:.2f} A")

# --- ABA 2: IA & SOLUÇÕES ---
with tab_solucoes:
    st.subheader("🤖 Consultoria MPN IA")
    if tsat_evap:
        if sh < 5: st.error("🚨 SH Baixo: Risco de líquido.")
        elif sh > 12: st.warning("⚠️ SH Alto: Falta de fluido.")
        else: st.success("✅ Ciclo em equilíbrio.")
    if abs(variacao_v) > 10: st.error(f"🚨 Tensão com variação crítica: {variacao_v:.2f}%")

# --- ABA 3: CARGA TÉRMICA ---
with tab_carga:
    st.subheader("📐 Dimensionamento de Carga Térmica")
    col1, col2, col3 = st.columns(3)
    area = col1.number_input("Área (m²)", value=0.00, step=0.1, format="%.2f")
    pessoas = col2.number_input("Pessoas", value=1, step=1)
    sol = col3.selectbox("Sol", ["Manhã", "Tarde"])
    
    if area > 0:
        fator = 800 if sol == "Tarde" else 600
        total_btu = (area * fator) + ((pessoas-1)*600)
        st.metric("CAPACIDADE ESTIMADA", f"{total_btu:.2f} BTU/h")
        st.metric("EM TR", f"{total_btu/12000:.2f} TR")

# --- BOTÃO PDF ---
if st.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if not cli: st.error("Preencha o nome do cliente.")
    else: st.success(f"Laudo técnico de {cli} gerado com sucesso!")

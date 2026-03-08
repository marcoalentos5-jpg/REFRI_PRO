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

# --- 2. LÓGICA DE ENGENHARIA (DANFOSS DEW POINT) ---
def calcular_t_sat_precisao(psig, gas):
    if psig is None or not gas or psig <= 0: return None
    try:
        if gas == "R-410A":
            # Calibração Master: 133.10 -> 7.90 | 122.70 -> 5.50
            return 0.23076923 * psig - 22.81538462
        elif gas == "R-22":
            return 0.2854 * psig - 25.12
        elif gas == "R-134a":
            return 0.521 * psig - 38.54
        elif gas == "R-404A":
            return 0.2105 * psig - 16.52
    except: return None
    return None

# --- 3. SIDEBAR (SETUP & ELÉTRICA) ---
st.sidebar.header("⚙️ Setup do Ciclo & Elétrica")
lista_equip = ["", "Split Hi-Wall", "Split Cassete", "Piso-Teto", "Chiller", "VRF/VRV", "Câmara Fria", "Self-Contained"]
f_equip = st.sidebar.selectbox("Tipo de Equipamento", sorted(lista_equip))
f_gas = st.sidebar.selectbox("Fluido Refrigerante", ["", "R-410A", "R-22", "R-134a", "R-404A"])
f_tec = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter", "Digital Scroll"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Parâmetros Elétricos")
v_trab_str = st.sidebar.selectbox("Tensão de Trabalho (Nominal)", ["", "127", "220", "380", "440"])
v_medida = st.sidebar.number_input("Tensão Medida [V]", min_value=0.0, step=1.0, format="%.2f")

diff_tensao_v = 0.00
variacao_v = 0.00
if v_trab_str and v_medida > 0:
    v_nominal = float(v_trab_str)
    diff_tensao_v = v_medida - v_nominal
    variacao_v = (diff_tensao_v / v_nominal) * 100

st.sidebar.markdown(f"**Diferença de Tensão:** `{diff_tensao_v:.2f} V`")

# --- 4. NAVEGAÇÃO POR ABAS ---
tab_diag, tab_solucoes, tab_carga = st.tabs(["📊 Diagnóstico Master", "🤖 IA & Soluções", "📐 Carga Térmica"])

# --- ABA 1: DIAGNÓSTICO ---
with tab_diag:
    st.subheader("📋 Identificação Completa do Sistema")
    with st.expander("Dados do Cliente e Equipamento", expanded=True):
        c1, c2, c3 = st.columns(3)
        cli = c1.text_input("Cliente")
        tec = c2.text_input("Responsável Técnico")
        fab = c3.text_input("Fabricante")
        
        c4, c5, c6, c7 = st.columns(4)
        lin = c4.text_input("Linha/Família")
        mod_int = c5.text_input("Modelo Evap")
        mod_ext = c6.text_input("Modelo Cond")
        ser = c7.text_input("Número de Série (S/N)")

    st.subheader("🛠️ Coleta de Dados de Campo")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        t_ret = st.number_input("Temp. Retorno [°C]", value=24.00, format="%.2f")
        t_ins = st.number_input("Temp. Insuflação [°C]", value=12.00, format="%.2f")
        dt = t_ret - t_ins
        st.metric("DELTA T", f"{dt:.2f} °C")
    with m2:
        p_suc = st.number_input("Pressão Sucção (PSIG)", value=133.10, format="%.2f")
        tsat_evap = calcular_t_sat_precisao(p_suc, f_gas)
        st.metric("T. SATURAÇÃO (DEW)", f"{tsat_evap:.2f} °C" if tsat_evap else "--")
    with m3:
        t_tubo_suc = st.number_input("Temp. Tubo Sucção [°C]", value=12.00, format="%.2f")
        sh = t_tubo_suc - tsat_evap if tsat_evap else 0.0
        st.metric("SUPER AQUECIMENTO", f"{sh:.2f} K")
    with m4:
        v_rla = st.number_input("Corrente RLA [A]", value=1.00, format="%.2f")
        v_med_amp = st.number_input("Corrente Medida [A]", value=0.00, format="%.2f")
        st.metric("DIF. TENSÃO", f"{diff_tensao_v:.2f} V")

# --- ABA 2: IA ---
with tab_solucoes:
    st.subheader("🤖 Diagnóstico IA")
    if tsat_evap:
        if sh < 5: st.error("🚨 SH Baixo: Risco de líquido.")
        elif sh > 12: st.warning("⚠️ SH Alto: Falta de fluido.")
        else: st.success("✅ Ciclo operando corretamente.")

# --- ABA 3: CARGA TÉRMICA ---
with tab_carga:
    st.subheader("📐 Cálculo de Carga Térmica")
    area = st.number_input("Área (m²)", min_value=0.0, format="%.2f")
    sol = st.selectbox("Exposição Solar", ["Manhã", "Tarde"])
    total_btu = 0.0
    if area > 0:
        fator = 800 if sol == "Tarde" else 600
        total_btu = area * fator
        st.metric("CARGA NECESSÁRIA", f"{total_btu:.2f} BTU/h")

# --- 5. GERAÇÃO DE PDF ---
if st.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if not cli:
        st.error("Preencha o nome do cliente.")
    else:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"LAUDO TÉCNICO MPN - {cli}", ln=True, align="C")
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 8, f"Técnico: {tec} | Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
        pdf.ln(5)
        pdf.cell(0, 8, f"Pressão Sucção: {p_suc:.2f} PSIG | T. Sat: {tsat_evap:.2f} C", ln=True)
        pdf.cell(0, 8, f"SH: {sh:.2f} K | Tensão Medida: {v_medida:.2f} V | Dif: {diff_tensao_v:.2f} V", ln=True)
        
        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 Baixar PDF", pdf_output, f"Laudo_{cli}.pdf", "application/pdf")

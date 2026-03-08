import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import math
import io
import urllib.parse

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

# --- 2. LÓGICA DE ENGENHARIA DE PRECISÃO (DANFOSS) ---
def calcular_t_sat_precisao(psig, gas):
    if psig is None or not gas or psig <= 0: return None
    try:
        if gas == "R-410A":
            # Calibração Master: 133.10 -> 7.90 | 122.70 -> 5.50
            return 0.23076923 * psig - 22.81538462
        elif gas == "R-22": return 0.2854 * psig - 25.12
        elif gas == "R-134a": return 0.521 * psig - 38.54
        elif gas == "R-404A": return 0.2105 * psig - 16.52
    except: return None
    return None

# --- 3. SIDEBAR (SETUP ÚNICO) ---
st.sidebar.header("⚙️ Setup do Ciclo & Elétrica")
f_equip = st.sidebar.selectbox("Equipamento", ["", "Split Hi-Wall", "Split Cassete", "Piso-Teto", "Chiller", "VRF/VRV", "Câmara Fria"])
f_gas = st.sidebar.selectbox("Fluido Refrigerante", ["", "R-410A", "R-22", "R-134a", "R-404A"])
f_tec = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter", "Digital Scroll"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Parâmetros Elétricos")
v_trab_str = st.sidebar.selectbox("Tensão de Trabalho (Nominal) [V]", ["", "127", "220", "380", "440"])
v_medida = st.sidebar.number_input("Tensão Medida [V]", min_value=0, step=1, format="%d")

diff_tensao_v = 0
variacao_v = 0.0
if v_trab_str and v_medida > 0:
    v_nominal = int(v_trab_str)
    diff_tensao_v = v_medida - v_nominal
    variacao_v = (diff_tensao_v / v_nominal) * 100
st.sidebar.markdown(f"**Diferença:** `{diff_tensao_v} V` ({variacao_v:.1f}%)")

# --- 4. NAVEGAÇÃO POR ABAS (DEFINIÇÃO DAS ABAS) ---
tab_diag, tab_solucoes, tab_carga, tab_fotos = st.tabs(["📊 Diagnóstico Master", "🤖 IA & Soluções", "📐 Carga Térmica VRF", "📸 Fotos"])

with tab_diag:
    st.subheader("📋 Identificação do Sistema")
    with st.expander("Dados Cadastrais", expanded=True):
        c1, c2, c3 = st.columns(3)
        cli = c1.text_input("Cliente")
        tec = c2.text_input("Técnico")
        fab = c3.text_input("Fabricante")
        
        c4, c5, c6 = st.columns(3)
        mod_int = c4.text_input("Modelo Evap")
        mod_ext = c5.text_input("Modelo Cond")
        ser = c6.text_input("S/N")

    st.subheader("🛠️ Coleta de Dados Termofluidodinâmicos")
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
        p_desc = st.number_input("Pressão Descarga (PSIG)", value=380.00, format="%.2f")
        tsat_cond = calcular_t_sat_precisao(p_desc, f_gas)
        t_tubo_liq = st.number_input("Temp. Linha Líquido [°C]", value=30.00, format="%.2f")
        sr = tsat_cond - t_tubo_liq if tsat_cond else 0.0
        st.metric("SUB-RESFRIAMENTO", f"{sr:.2f} K")

with tab_carga:
    st.subheader("📐 Dimensionamento VRF / Engenharia")
    col_v1, col_v2 = st.columns(2)
    area_vrf = col_v1.number_input("Área Útil (m²)", min_value=0.00, format="%.2f")
    n_pessoas = col_v2.number_input("Pessoas", min_value=1, step=1)
    f_simult = st.slider("Fator de Simultaneidade VRF (%)", 50, 130, 100)
    
    total_btu = (area_vrf * 800 + n_pessoas * 450) * (f_simult / 100) if area_vrf > 0 else 0
    st.metric("CARGA TOTAL (VRF)", f"{total_btu:,.2f} BTU/h")

# --- 5. EXPORTAÇÃO E WHATSAPP ---
st.markdown("---")
if st.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if not cli: st.error("Informe o cliente.")
    else:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 74, 153)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 15, 'LAUDO TÉCNICO - MPN REFRIGERAÇÃO', 0, 1, 'C')
        pdf.ln(25)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 10, f"Cliente: {cli} | Tensão: {v_medida}V | SH: {sh:.2f}K | SR: {sr:.2f}K", ln=True)
        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 Baixar PDF", pdf_output, f"Laudo_{cli}.pdf", "application/pdf")

texto_wa = f"*MPN REFRIGERAÇÃO*\n👤 *Cliente:* {cli}\n🌡️ *SH:* {sh:.2f}K | *SR:* {sr:.2f}K\n⚡ *Tensão:* {v_medida}V"
st.link_button("📲 ENVIAR VIA WHATSAPP", f"https://wa.me{urllib.parse.quote(texto_wa)}")

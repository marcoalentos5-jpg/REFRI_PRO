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
            return 0.23076923 * psig - 22.81538462
        elif gas == "R-22": return 0.2854 * psig - 25.12
        elif gas == "R-134a": return 0.521 * psig - 38.54
        elif gas == "R-404A": return 0.2105 * psig - 16.52
    except: return None
    return None

# --- 3. SIDEBAR (SETUP & ELÉTRICA EM INTEIROS) ---
st.sidebar.header("⚙️ Setup do Ciclo & Elétrica")
f_equip = st.sidebar.selectbox("Equipamento", ["", "Split Hi-Wall", "Split Cassete", "Piso-Teto", "Chiller", "VRF/VRV", "Câmara Fria"])
f_gas = st.sidebar.selectbox("Fluido Refrigerante", ["", "R-410A", "R-22", "R-134a", "R-404A"])
f_tec = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter", "Digital Scroll"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Parâmetros Elétricos")
v_trab_str = st.sidebar.selectbox("Tensão de Trabalho (Nominal) [V]", ["", "127", "220", "380", "440"])
v_medida = st.sidebar.number_input("Tensão Medida [V]", min_value=0, step=1, format="%d")

diff_tensao_v = 0
if v_trab_str and v_medida > 0:
    diff_tensao_v = v_medida - int(v_trab_str)
st.sidebar.markdown(f"**Diferença de Tensão:** `{diff_tensao_v} V`")

# --- 4. NAVEGAÇÃO POR ABAS REORGANIZADAS ---
tab_iden, tab_termo, tab_solucoes, tab_carga, tab_fotos = st.tabs([
    "📋 Identificação & Elétrica", "🌡️ Termodinâmica", "🤖 IA & Soluções", "📐 Carga Térmica VRF", "📸 Fotos"
])

# --- ABA 1: IDENTIFICAÇÃO & ELÉTRICA ---
with tab_iden:
    st.subheader("📋 Dados Cadastrais e Corrente")
    with st.expander("Dados do Cliente e Equipamento", expanded=True):
        c1, c2, c3 = st.columns(3)
        cli = c1.text_input("Cliente", placeholder="Nome/Empresa")
        tec = c2.text_input("Responsável Técnico")
        ser = c3.text_input("Número de Série (S/N)")

    st.subheader("⚡ Análise de Amperagem (RLA/LRA)")
    e1, e2, e3, e4 = st.columns(4)
    v_rla = e1.number_input("Corrente RLA [A]", value=0.00, step=0.01, format="%.2f")
    v_lra = e2.number_input("Corrente LRA [A]", value=0.00, step=0.01, format="%.2f")
    v_med_amp = e3.number_input("Corrente Medida [A]", value=0.00, step=0.01, format="%.2f")
    diff_amp = v_med_amp - v_rla if v_rla > 0 else 0.00
    e4.metric("DIF. CORRENTE", f"{diff_amp:.2f} A", delta=f"{diff_amp:.2f} vs RLA")

# --- ABA 2: TERMODINÂMICA (SUCÇÃO & DESCARGA) ---
with tab_termo:
    st.subheader("🛠️ Diagnóstico Termofluidodinâmico Completo")
    
    # Bloco Evaporadora (Baixa)
    st.markdown("### 🌬️ Lado de Baixa (Evaporação / Sucção)")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        t_ret = st.number_input("Temp. Ar Retorno [°C]", value=24.00, format="%.2f")
        t_ins = st.number_input("Temp. Ar Insuflação [°C]", value=12.00, format="%.2f")
        dt = t_ret - t_ins
        st.metric("DELTA T (Ar)", f"{dt:.2f} °C")
    with m2:
        p_suc = st.number_input("Pressão Sucção (PSIG)", value=133.10, format="%.2f")
        tsat_evap = calcular_t_sat_precisao(p_suc, f_gas)
        st.metric("T. SATURAÇÃO (DEW)", f"{tsat_evap:.2f} °C" if tsat_evap else "--")
    with m3:
        t_tubo_suc = st.number_input("Temp. Tubo Sucção [°C]", value=12.00, format="%.2f")
        sh = t_tubo_suc - tsat_evap if tsat_evap else 0.00
        st.metric("SUPER AQUECIMENTO", f"{sh:.2f} K")
    with m4:
        st.metric("FLUIDO SELECIONADO", f"{f_gas}")

    st.markdown("---")
    
    # Bloco Condensadora (Alta)
    st.markdown("### ⚙️ Lado de Alta (Condensação / Descarga)")
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        t_amb = st.number_input("Temp. Ambiente Externo [°C]", value=35.00, format="%.2f")
        st.metric("DIF. TENSÃO (SIDEBAR)", f"{diff_tensao_v} V")
    with d2:
        p_desc = st.number_input("Pressão Descarga (PSIG)", value=380.00, format="%.2f")
        tsat_cond = calcular_t_sat_precisao(p_desc, f_gas)
        st.metric("T. SAT (BUBBLE)", f"{tsat_cond:.2f} °C" if tsat_cond else "--")
    with d3:
        t_tubo_liq = st.number_input("Temp. Linha Líquido [°C]", value=30.00, format="%.2f")
        sr = tsat_cond - t_tubo_liq if tsat_cond else 0.00
        st.metric("SUB-RESFRIAMENTO", f"{sr:.2f} K")
    with d4:
        st.metric("TECNOLOGIA", f"{f_tec}")

# --- ABA 3: IA & SOLUÇÕES ---
with tab_solucoes:
    st.subheader("🤖 Consultoria MPN IA")
    if tsat_evap:
        if sh < 5: st.error("🚨 SH Baixo: Risco de líquido no compressor.")
        elif sh > 12: st.warning("⚠️ SH Alto: Falta de fluido ou restrição.")
        else: st.success("✅ Ciclo de Baixa em equilíbrio.")
    if tsat_cond:
        if sr < 3: st.warning("⚠️ SR Baixo: Verifique carga de fluido.")
        elif sr > 10: st.error("🚨 SR Alto: Excesso de fluido ou obstrução.")

# --- ABA 4: CARGA TÉRMICA VRF ---
with tab_carga:
    st.subheader("📐 Carga Térmica VRF")
    area_vrf = st.number_input("Área Útil (m²)", min_value=0.00, format="%.2f")
    f_simult = st.slider("Fator de Simultaneidade (%)", 50, 130, 100)
    total_btu = (area_vrf * 800) * (f_simult / 100) if area_vrf > 0 else 0
    st.metric("TOTAL ESTIMADO", f"{total_btu:,.2f} BTU/h")

# --- 5. EXPORTAÇÃO ---
st.markdown("---")
col_p, col_w = st.columns(2)
if col_p.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if not cli: st.error("Informe o cliente.")
    else:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 74, 153); pdf.rect(0, 0, 210, 35, 'F')
        pdf.set_font('Arial', 'B', 14); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 15, 'LAUDO TÉCNICO MPN REFRIGERAÇÃO', 0, 1, 'C')
        pdf.ln(10); pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, f"CLIENTE: {cli} | TÉCNICO: {tec}", ln=True)
        pdf.cell(0, 8, f"SH: {sh:.2f}K | SR: {sr:.2f}K | Delta T: {dt:.2f}C", ln=True)
        st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), f"Laudo_{cli}.pdf")

texto_wa = f"*MPN REFRIGERAÇÃO*\n👤 *Cliente:* {cli}\n🌡️ *SH:* {sh:.2f}K | *SR:* {sr:.2f}K\n⚡ *Tensão:* {v_medida}V"
col_w.link_button("📲 ENVIAR WHATSAPP", f"https://wa.me{urllib.parse.quote(texto_wa)}")

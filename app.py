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

# --- 2. LÓGICA DE ENGENHARIA DE PRECISÃO (DANFOSS DEW POINT) ---
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

# --- 3. SIDEBAR (SETUP & ELÉTRICA EM INTEIROS) ---
st.sidebar.header("⚙️ Setup do Ciclo & Elétrica")
f_equip = st.sidebar.selectbox("Equipamento", ["", "Split Hi-Wall", "Split Cassete", "Piso-Teto", "Chiller", "VRF/VRV", "Câmara Fria"])
f_gas = st.sidebar.selectbox("Fluido Refrigerante", ["", "R-410A", "R-22", "R-134a", "R-404A"])
f_tec = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter", "Digital Scroll"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Parâmetros Elétricos")
v_trab_str = st.sidebar.selectbox("Tensão de Trabalho (Nominal) [V]", ["", "127", "220", "380", "440"])
# Tensão medida como inteiro (sem zeros à esquerda e sem decimais)
v_medida = st.sidebar.number_input("Tensão Medida [V]", min_value=0, step=1, format="%d")

diff_tensao_v = 0
variacao_v = 0.0
if v_trab_str and v_medida > 0:
    v_nominal = int(v_trab_str)
    diff_tensao_v = v_medida - v_nominal
    variacao_v = (diff_tensao_v / v_nominal) * 100
st.sidebar.markdown(f"**Diferença de Tensão:** `{diff_tensao_v} V`")

# --- 4. NAVEGAÇÃO POR ABAS ---
tab_diag, tab_solucoes, tab_carga = st.tabs(["📊 Diagnóstico Master", "🤖 IA & Soluções", "📐 Carga Térmica VRF"])

# --- ABA 1: DIAGNÓSTICO MASTER ---
with tab_diag:
    st.subheader("📋 Identificação Completa do Sistema")
    with st.expander("Dados Cadastrais", expanded=True):
        c1, c2, c3 = st.columns(3)
        cli = c1.text_input("Cliente", placeholder="Nome/Empresa")
        tec = c2.text_input("Responsável Técnico")
        fab = c3.text_input("Fabricante")
        
        c4, c5, c6 = st.columns(3)
        mod_int = c4.text_input("Modelo Evap")
        mod_ext = c5.text_input("Modelo Cond")
        ser = c6.text_input("S/N (Série)")

    st.subheader("⚡ Análise de Corrente (RLA/LRA)")
    e1, e2, e3, e4 = st.columns(4)
    v_rla = e1.number_input("Corrente RLA [A]", value=0.00, step=0.01, format="%.2f")
    v_lra = e2.number_input("Corrente LRA [A]", value=0.00, step=0.01, format="%.2f")
    v_med_amp = e3.number_input("Corrente Medida [A]", value=0.00, step=0.01, format="%.2f")
    diff_amp = v_med_amp - v_rla if v_rla > 0 else 0.00
    e4.metric("DIF. CORRENTE", f"{diff_amp:.2f} A", delta=f"{diff_amp:.2f} vs RLA", delta_color="inverse" if diff_amp > (v_rla*0.1) else "normal")

    st.subheader("🛠️ Termodinâmica (Sucção & Descarga)")
    m1, m2, m3, m4 = st.columns(4)
    p_suc = m1.number_input("Pressão Sucção (PSIG)", value=133.10, format="%.2f")
    tsat_evap = calcular_t_sat_precisao(p_suc, f_gas)
    m2.metric("T. SATURAÇÃO (DEW)", f"{tsat_evap:.2f} °C" if tsat_evap else "--")
    t_tubo_suc = m3.number_input("Temp. Tubo Sucção [°C]", value=12.00, format="%.2f")
    sh = t_tubo_suc - tsat_evap if tsat_evap else 0.00
    m4.metric("SUPER AQUECIMENTO", f"{sh:.2f} K")

    d1, d2, d3, d4 = st.columns(4)
    p_desc = d1.number_input("Pressão Descarga (PSIG)", value=380.00, format="%.2f")
    tsat_cond = calcular_t_sat_precisao(p_desc, f_gas)
    d2.metric("T. SAT (BUBBLE)", f"{tsat_cond:.2f} °C" if tsat_cond else "--")
    t_tubo_liq = d3.number_input("Temp. Linha Líquido [°C]", value=30.00, format="%.2f")
    sr = tsat_cond - t_tubo_liq if tsat_cond else 0.00
    d4.metric("SUB-RESFRIAMENTO", f"{sr:.2f} K")

# --- ABA 2: IA & SOLUÇÕES ---
with tab_solucoes:
    st.subheader("🤖 Consultoria MPN IA - Diagnóstico")
    if v_med_amp == 0 or p_suc == 0:
        st.warning("⚠️ Aguardando medições na Aba 1...")
    else:
        c_ia1, c_ia2 = st.columns(2)
        with c_ia1:
            st.markdown("### ⚡ Elétrica")
            if v_med_amp > v_rla: st.error(f"🚨 SOBRECARGA: Corrente {((v_med_amp-v_rla)/v_rla)*100:.1f}% acima do RLA.")
            if v_lra > 0 and v_med_amp > (v_lra * 0.9): st.error("🚨 ROTOR BLOQUEADO: Corrente próxima ao LRA.")
        with c_ia2:
            st.markdown("### 🌡️ Ciclo")
            if sh < 5: st.error("❌ SH BAIXO: Risco de golpe de líquido.")
            if sh > 12: st.warning("❌ SH ALTO: Falta de fluido ou restrição.")
            if sr > 10: st.error("❌ SR ALTO: Excesso de fluido refrigerante.")

# --- ABA 3: CARGA TÉRMICA VRF ---
with tab_carga:
    st.subheader("📐 Dimensionamento VRF / Engenharia")
    col_v1, col_v2 = st.columns(2)
    area_vrf = col_v1.number_input("Área Útil (m²)", min_value=0.00, format="%.2f")
    f_simult = col_v2.slider("Fator de Simultaneidade VRF (%)", 50, 130, 100)
    total_btu = (area_vrf * 800) * (f_simult / 100) if area_vrf > 0 else 0
    st.metric("TOTAL ESTIMADO (BTU/h)", f"{total_btu:,.2f}")

# --- 5. EXPORTAÇÃO (PDF & WHATSAPP) ---
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
        pdf.cell(0, 8, f"ELÉTRICA: Tensão Medida {v_medida}V | Diferença {diff_tensao_v}V | Corrente {v_med_amp}A", ln=True)
        pdf.cell(0, 8, f"TÉRMICA: SH {sh:.2f}K | SR {sr:.2f}K | P.Suc {p_suc} PSIG", ln=True)
        st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), f"Laudo_{cli}.pdf", "application/pdf")

texto_wa = f"*MPN REFRIGERAÇÃO - LAUDO*\n👤 *Cliente:* {cli}\n⚡ *Tensão:* {v_medida}V (Dif: {diff_tensao_v}V)\n🌡️ *SH:* {sh:.2f}K | *SR:* {sr:.2f}K\n✅ *Status:* Analisado por {tec}"
col_w.link_button("📲 ENVIAR WHATSAPP", f"https://wa.me{urllib.parse.quote(texto_wa)}")

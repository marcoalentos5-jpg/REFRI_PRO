import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import math
import io
import urllib.parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- 1. CONFIGURAÇÃO VISUAL MASTER MPN ---
st.set_page_config(page_title="MPN | Engenharia & Diagnóstico", layout="wide", page_icon="❄️")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    [data-testid="stMetric"] {
        background-color: #004A99 !important; border-radius: 15px !important;
        padding: 20px !important; border: 2px solid #A9A9A9 !important;
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
            # Calibração Master: 133.10 psig -> 7.90 °C | 122.70 psig -> 5.50 °C
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
variacao_v = 0.0
if v_trab_str and v_medida > 0:
    v_nominal = int(v_trab_str)
    diff_tensao_v = v_medida - v_nominal
    variacao_v = (diff_tensao_v / v_nominal) * 100
st.sidebar.markdown(f"**Diferença:** `{diff_tensao_v} V` ({variacao_v:.1f}%)")

# --- 4. NAVEGAÇÃO POR ABAS ---
tab_iden, tab_termo, tab_solucoes, tab_carga, tab_subs = st.tabs([
    "📋 Identificação & Elétrica", "🌡️ Termodinâmica", "🤖 IA & Diagnóstico", "📐 Carga Térmica VRF", "🔄 Peças Alternativas"
])

# ABA 1: IDENTIFICAÇÃO
with tab_iden:
    st.subheader("📋 Dados do Cliente e Amperagem")
    c1, c2, c3 = st.columns(3)
    cli = c1.text_input("Cliente")
    tec = c2.text_input("Técnico")
    ser = c3.text_input("S/N (Série)")
    v_rla = st.number_input("Corrente RLA [A]", value=0.00, step=0.01, format="%.2f")
    v_med_amp = st.number_input("Corrente Medida [A]", value=0.00, step=0.01, format="%.2f")

# ABA 2: TERMODINÂMICA
with tab_termo:
    st.subheader("🛠️ Diagnóstico de Pressões e Troca")
    m1, m2, m3 = st.columns(3)
    t_ret = m1.number_input("Temp. Ar Retorno [°C]", value=24.00, format="%.2f")
    t_ins = m1.number_input("Temp. Ar Insuflação [°C]", value=12.00, format="%.2f")
    dt = t_ret - t_ins
    
    p_suc = m2.number_input("Pressão Sucção (PSIG)", value=133.10, format="%.2f")
    tsat_evap = calcular_t_sat_precisao(p_suc, f_gas)
    m2.metric("T. SATURAÇÃO (DEW)", f"{tsat_evap:.2f} °C" if tsat_evap else "--")
    
    t_tubo_suc = m3.number_input("Temp. Tubo Sucção [°C]", value=12.00, format="%.2f")
    sh = t_tubo_suc - tsat_evap if tsat_evap else 0.00
    m3.metric("SUPER AQUECIMENTO", f"{sh:.2f} K")

    p_desc = st.number_input("Pressão Descarga (PSIG)", value=380.00, format="%.2f")
    tsat_cond = calcular_t_sat_precisao(p_desc, f_gas)
    t_tubo_liq = st.number_input("Temp. Tubo Líquido [°C]", value=30.00, format="%.2f")
    sr = tsat_cond - t_tubo_liq if tsat_cond else 0.00

# ABA 5: PEÇAS ALTERNATIVAS
with tab_subs:
    st.subheader("🔄 Referência Cruzada de Compressores")
    dados_comp = {
        "Capacidade": ["9k BTU", "12k BTU", "18k BTU", "24k BTU"],
        "Embraco": ["FFU 80HAX", "FFU 130HAX", "FFU 160HAX", "VNEK 213U"],
        "Tecumseh": ["THB1380YS", "AE4440YS", "AK4476YS", "AWS4524ZXG"],
        "Danfoss": ["TLS5FT", "SC12G", "SC18G", "GS26CLX"]
    }
    df_comp = pd.DataFrame(dados_comp)
    st.table(df_comp)

# --- 5. EXPORTAÇÃO MASTER (PDF & WHATSAPP) ---
st.markdown("---")
col_p, col_w = st.columns(2)

if col_p.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if not cli: st.error("Informe o cliente.")
    else:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 74, 153); pdf.rect(0, 0, 210, 35, 'F')
        pdf.set_font('Arial', 'B', 15); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 15, 'LAUDO TÉCNICO MPN REFRIGERAÇÃO', 0, 1, 'C')
        pdf.ln(10); pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, f"Cliente: {cli} | Tensão Medida: {v_medida}V | SH: {sh:.2f}K | SR: {sr:.2f}K", ln=True)
        # Tabela de Peças no PDF
        pdf.ln(5); pdf.set_font('Arial', 'B', 10); pdf.cell(0, 8, "REFERÊNCIA DE PEÇAS SUGERIDAS", ln=True)
        pdf.set_font('Arial', '', 8)
        for i in range(len(df_comp)):
            pdf.cell(40, 7, df_comp['Capacidade'][i], 1)
            pdf.cell(50, 7, df_comp['Embraco'][i], 1)
            pdf.cell(50, 7, df_comp['Tecumseh'][i], 1); pdf.ln()
            
        st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), f"Laudo_{cli}.pdf", "application/pdf")

texto_wa = f"*MPN REFRIGERAÇÃO*\n👤 *Cliente:* {cli}\n🌡️ *SH:* {sh:.2f}K | *SR:* {sr:.2f}K\n⚡ *Tensão:* {v_medida}V"
col_w.link_button("📲 ENVIAR WHATSAPP", f"https://wa.me{urllib.parse.quote(texto_wa)}")

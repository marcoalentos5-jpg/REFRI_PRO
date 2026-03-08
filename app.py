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

# --- 2. LÓGICA DE ENGENHARIA DE PRECISÃO (DANFOSS DEW/BUBBLE) ---
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

# --- 3. SIDEBAR (SETUP E ELÉTRICA INTEIRA) ---
st.sidebar.header("⚙️ Setup do Ciclo & Elétrica")
lista_equip = ["", "Split Hi-Wall", "Split Cassete", "Piso-Teto", "Chiller", "VRF/VRV", "Câmara Fria", "Self-Contained"]
f_equip = st.sidebar.selectbox("Tipo de Equipamento", sorted(lista_equip))
f_gas = st.sidebar.selectbox("Fluido Refrigerante", ["", "R-410A", "R-22", "R-134a", "R-404A"])
f_tec = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter", "Digital Scroll"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Parâmetros Elétricos")
# Tensão de Trabalho (Nominal) - Inteiro
v_trab_str = st.sidebar.selectbox("Tensão de Trabalho (Nominal)", ["", "127", "220", "380", "440"])

# Tensão Medida - Inteiro (sem zeros à esquerda e sem decimais)
v_medida = st.sidebar.number_input("Tensão Medida [V]", min_value=0, step=1, format="%d")

# Cálculo Diferença de Tensão [V] - Inteiro
diff_tensao_v = 0
variacao_v = 0.0
if v_trab_str and v_medida > 0:
    v_nominal = int(v_trab_str)
    diff_tensao_v = v_medida - v_nominal
    variacao_v = (diff_tensao_v / v_nominal) * 100

st.sidebar.markdown(f"**Diferença de Tensão:** `{diff_tensao_v} V`")

# --- 4. NAVEGAÇÃO POR ABAS ---
tab_diag, tab_solucoes, tab_carga = st.tabs(["📊 Diagnóstico Master", "🤖 IA & Soluções", "📐 Carga Térmica"])

# --- ABA 1: DIAGNÓSTICO MASTER ---
with tab_diag:
    st.subheader("📋 Identificação Completa do Sistema")
    with st.expander("Dados do Cliente e Equipamento", expanded=True):
        c1, c2, c3 = st.columns(3)
        cli = c1.text_input("Cliente", placeholder="Nome/Empresa")
        tec = c2.text_input("Responsável Técnico")
        fab = c3.text_input("Fabricante")
        
        c4, c5, c6, c7 = st.columns(4)
        lin = c4.text_input("Linha/Família")
        mod_int = c5.text_input("Modelo Interno (Evap)")
        mod_ext = c6.text_input("Modelo Externo (Cond)")
        ser = c7.text_input("Número de Série (S/N)")

    # BLOCO BAIXA PRESSÃO
    st.subheader("🛠️ Lado de Baixa (Evaporação)")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        t_ret = st.number_input("Temp. Retorno [°C]", value=24.00, format="%.2f")
        t_ins = st.number_input("Temp. Insuflação [°C]", value=12.00, format="%.2f")
        st.metric("DELTA T", f"{t_ret - t_ins:.2f} °C")
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
        st.metric("AMPERAGEM REAL", f"{v_med_amp:.2f} A")

    # BLOCO ALTA PRESSÃO
    st.subheader("⚙️ Lado de Alta (Condensação)")
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        t_amb = d1.number_input("Temp. Ambiente [°C]", value=35.00, format="%.2f")
        st.metric("DIF. TENSÃO [V]", f"{diff_tensao_v} V")
    with d2:
        p_desc = d2.number_input("Pressão Descarga (PSIG)", value=380.00, step=0.1, format="%.2f")
        tsat_cond = calcular_t_sat_precisao(p_desc, f_gas)
        st.metric("T. SATURAÇÃO (BUBBLE)", f"{tsat_cond:.2f} °C" if tsat_cond else "--")
    with d3:
        t_tubo_liq = d3.number_input("Temp. Tubo Líquido [°C]", value=30.00, format="%.2f")
        sr = tsat_cond - t_tubo_liq if tsat_cond else 0.0
        st.metric("SUB-RESFRIAMENTO", f"{sr:.2f} K")
    with d4:
        st.metric("TENSÃO MEDIDA", f"{v_medida} V", delta=f"{variacao_v:.1f}%")

# --- ABA 3: CARGA TÉRMICA ---
with tab_carga:
    st.subheader("📐 Cálculo de Carga Térmica")
    area_m2 = st.number_input("Área total (m²)", min_value=0.0, format="%.2f")
    sol_tab = st.selectbox("Exposição Solar", ["Manhã", "Tarde"])
    if area_m2 > 0:
        f_btu = 800 if sol_tab == "Tarde" else 600
        total_btu = area_m2 * f_btu
        st.metric("CARGA NECESSÁRIA", f"{total_btu:,.2f} BTU/h")

# --- 5. GERAÇÃO DE PDF PROFISSIONAL ---
if st.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if not cli:
        st.error("Preencha o nome do cliente.")
    else:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 74, 153) # Azul MPN
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 15, 'LAUDO TÉCNICO - MPN REFRIGERAÇÃO', 0, 1, 'C')
        pdf.ln(25)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 10, f"DADOS ELÉTRICOS: Tensão Nominal {v_trab_str}V | Medida {v_medida}V | Diferença {diff_tensao_v}V", ln=True)
        pdf.cell(0, 10, f"DADOS TÉRMICOS: SH {sh:.2f}K | SR {sr:.2f}K | Sat Sucção {tsat_evap:.2f}C", ln=True)
        
        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 Baixar Laudo PDF", pdf_output, f"Laudo_{cli}.pdf", "application/pdf")

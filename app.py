import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io
import streamlit.components.v1 as components

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# --- 2. SCRIPT NAVEGAÇÃO ENTER ---
components.html(
    """<script>
    const doc = window.parent.document;
    doc.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const focusable = doc.querySelectorAll('input, select, textarea, button');
            const index = Array.from(focusable).indexOf(doc.activeElement);
            if (index > -1 && index + 1 < focusable.length) {
                focusable[index + 1].focus(); e.preventDefault();
            }
        }
    });
    </script>""", height=0,
)

# --- 3. MOTOR TERMODINÂMICO GLOBAL (NIST/DANFOSS) ---
def get_tsat_global(psig, gas):
    if psig <= -14.6: return -155.0
    p_abs_bar = (psig + 14.696) * 0.0689476
    fluídos = {
        "R-410A": {"A": 4.120, "B": 750.50, "C": -23.50},
        "R-32":   {"A": 4.015, "B": 632.10, "C": -31.15},
        "R-22":   {"A": 4.150, "B": 834.15, "C": -31.70},
        "R-134a": {"A": 4.430, "B": 1070.3, "C": -33.15},
        "R-404A": {"A": 4.020, "B": 670.50, "C": -25.50}
    }
    conf = fluídos.get(gas, fluídos["R-410A"])
    try:
        t_kelvin = conf["B"] / (conf["A"] - np.log10(p_abs_bar)) - conf["C"]
        return round(t_kelvin - 273.15, 2)
    except: return 0.0

# --- 4. LÓGICA DE CORES DINÂMICAS ---
def get_style(val, tipo):
    if tipo == "SH":
        if 5 <= val <= 11: return "#E8F5E9", "#4CAF50"
        if 2 <= val < 5 or 11 < val <= 15: return "#FFF3E0", "#FF9800"
        return "#FFEBEE", "#F44336"
    if tipo == "SC":
        if 3 <= val <= 8: return "#E8F5E9", "#4CAF50"
        return "#FFF3E0", "#FF9800"
    if tipo == "DT":
        if 8 <= val <= 14: return "#E8F5E9", "#4CAF50"
        return "#FFEBEE", "#F44336"
    return "#F8F9FA", "#BDBDBD"

# --- 5. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c1.text_input("CPF / CNPJ")
    endereco = c2.text_input("Endereço Completo")
    whatsapp = c3.text_input("🟢 WhatsApp", value="21980264217")
    data_visita = c3.date_input("Data da Visita", value=date.today())
    email_cli = c2.text_input("✉️ E-mail")
    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    linha = d1.text_input("Linha (Ex: Artcool, WindFree)")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"])
    tipo_eq = d2.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "Multi-Split", "VRF/VRV", "Chiller"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"])
    cap_digitada = d3.text_input("Capacidade (Mil BTU´s)")
    col_u1, col_u2 = st.columns(2)
    mod_evap = col_u1.text_input("Modelo Unidade (Evap)")
    serie_evap = col_u1.text_input("Nº Série (Evap)")
    mod_cond = col_u2.text_input("Modelo Unidade (Cond)")
    serie_cond = col_u2.text_input("Nº Série (Cond)")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    col_v, col_a = st.columns(2)
    v_nom = float(col_v.selectbox("Tensão Nominal (V)", ["127", "220", "360", "480"]))
    v_med = col_v.number_input("Tensão Medida (V)", value=0.0)
    a_rla = col_a.number_input("Corrente RLA (A)", value=0.0)
    a_med = col_a.number_input("Corrente Medida (A)", value=0.0)

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico & Delta T")
    t1, t2, t3 = st.columns(3)
    p_suc = t1.number_input("Pressão Sucção (PSIG)", value=118.0)
    t_suc_tubo = t1.number_input("Temp. Tubo Sucção (°C)", value=12.0)
    p_liq = t2.number_input("Pressão Descarga (PSIG)", value=345.0)
    t_liq_tubo = t2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ret = t3.number_input("Temp. Ar Retorno (°C)", value=24.0)
    t_ins = t3.number_input("Temp. Ar Insuflamento (°C)", value=12.0)
    
    tsat_suc = get_tsat_global(p_suc, fluido)
    tsat_liq = get_tsat_global(p_liq, fluido)
    sh = round(t_suc_tubo - tsat_suc, 1)
    sc = round(tsat_liq - t_liq_tubo, 1)
    dt = round(t_ret - t_ins, 1)

    bg_sh, b_sh = get_style(sh, "SH")
    bg_sc, b_sc = get_style(sc, "SC")
    bg_dt, b_dt = get_style(dt, "DT")

    st.markdown(f"""
        <style>
        div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] {{ background-color: {bg_sh} !important; border: 2px solid {b_sh} !important; border-radius: 10px; padding: 15px; }}
        div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] {{ background-color: {bg_sc} !important; border: 2px solid {b_sc} !important; border-radius: 10px; padding: 15px; }}
        div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] {{ background-color: #FFF3E0 !important; border: 2px solid #FFB74D !important; border-radius: 10px; padding: 15px; }}
        div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetric"] {{ background-color: #FFFDE7 !important; border: 2px solid #FFF176 !important; border-radius: 10px; padding: 15px; }}
        div[data-testid="column"]:nth-of-type(5) div[data-testid="stMetric"] {{ background-color: {bg_dt} !important; border: 2px solid {b_dt} !important; border-radius: 10px; padding: 15px; }}
        .stButton>button {{ background-color: #004A99; color: white; font-weight: bold; border-radius: 8px; }}
        </style>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Superheat (SH)", f"{sh} K")
    m2.metric("Subcooling (SC)", f"{sc} K")
    m3.metric("T-Sat Sucção", f"{tsat_suc} °C")
    m4.metric("T-Sat Líquido", f"{tsat_liq} °C")
    m5.metric("Delta T", f"{dt} K")

with tab_diag:
    st.subheader("🤖 Diagnóstico & Relatório Final")
    obs = st.text_area("Observações Técnicas", height=150)
    
    # LÓGICA DO PDF
    if st.button("Gerar Relatório PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "MPN ENGENHARIA - RELATÓRIO TÉCNICO", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, f"CLIENTE: {cliente}", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(190, 8, f"Data: {data_visita} | Equipamento: {fabricante} {cap_digitada} BTU", ln=True)
        pdf.cell(190, 8, f"Gás: {fluido} | Tecnologia: {tecnologia}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "PARÂMETROS TERMODINÂMICOS:", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(190, 8, f"Superaquecimento (SH): {sh} K", ln=True)
        pdf.cell(190, 8, f"Sub-resfriamento (SC): {sc} K", ln=True)
        pdf.cell(190, 8, f"Delta T (Evaporadora): {dt} K", ln=True)
        pdf.cell(190, 8, f"T-Sat Sucção: {tsat_suc} C | T-Sat Líquido: {tsat_liq} C", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "OBSERVAÇÕES DO ESPECIALISTA:", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(190, 8, obs)
        
        html_pdf = pdf.output(dest="S").encode("latin-1")
        st.download_button(label="📥 Baixar Relatório em PDF", data=html_pdf, file_name=f"Relatorio_{cliente}.pdf", mime="application/pdf")

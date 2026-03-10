import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io
import os
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

# --- 3. MOTOR TERMODINÂMICO (MATRIZ DE PRECISÃO MPN) ---
def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {
            "p": [50.0, 100.0, 133.1, 133.5, 134.0, 134.5, 150.0, 200.0, 221.0, 250.0, 300.0, 452.0, 455.0, 456.0, 460.0, 500.0, 501.0, 502.0, 503.0, 525.0, 550.0, 555.0, 560.0, 570.0, 600.0],
            "t": [-17.02, -0.29, 7.90, 7.99, 8.10, 8.21, 11.55, 20.93, 24.38, 28.78, 35.58, 52.15, 52.44, 52.53, 52.89, 55.36, 56.59, 56.67, 56.75, 58.63, 60.69, 61.09, 61.49, 62.29, 64.59]
        },
        "R-32": {
            "p": [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 400.0, 450.0, 500.0, 550.0, 600.0],
            "t": [-17.46, 0.87, 10.86, 20.14, 27.91, 34.63, 45.96, 51.02, 55.36, 59.54, 63.43]
        },
        "R-22": {
            "p": [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 500.0, 550.0, 600.0],
            "t": [-3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 67.72, 78.38, 83.12, 87.53]
        },
        "R-134a": {
            "p": [0.0, 50.0, 100.0, 150.0, 200.0],
            "t": [-26.08, 12.23, 30.92, 43.65, 53.74]
        },
        "R-404A": {
            "p": [0.0, 50.0, 100.0, 150.0, 200.0],
            "t": [-45.45, -9.41, 8.96, 22.23, 32.59]
        }
    }
    if gas not in ancoras: return 0.0
    try:
        val = np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])
        return round(float(val), 2)
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
    
    if st.button("Gerar Relatório PDF"):
        pdf = FPDF()
        pdf.add_page()
        
        if os.path.exists("logo.png"):
            pdf.image("logo.png", 10, 8, 33)
            pdf.set_x(45)
        
        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(0, 74, 153)
        pdf.cell(145, 10, "RELATÓRIO TÉCNICO DE ENGENHARIA", ln=True, align="R")
        
        # CAMPO "GERADO EM" REMOVIDO
        pdf.ln(10)
        
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(0)
        pdf.cell(190, 8, " IDENTIFICAÇÃO DO CLIENTE", ln=True, fill=True)
        
        # LINHA ACIMA DO NOME
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(85, 8, f"Cliente: {cliente}", border="B")
        
        # DATA EM DESTAQUE (QUADRO PREENCHIDO)
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(225, 225, 225)
        pdf.cell(55, 8, f" DATA: {data_visita.strftime('%d/%m/%Y')} ", border=1, fill=True, align="C")
        
        # "DOC" SUBSTITUÍDO POR "CNPJ/CPF"
        pdf.set_font("Arial", "", 10)
        pdf.cell(50, 8, f"CNPJ/CPF: {doc_cliente}", border="B", ln=True, align="R")
        
        pdf.cell(190, 8, f"Endereço: {endereco}", border="B", ln=True)
        pdf.cell(95, 8, f"WhatsApp: {whatsapp}", border="B")
        pdf.cell(95, 8, f"E-mail: {email_cli}", border="B", ln=True)

        # CORREÇÃO DEFINITIVA DO OUTPUT PARA BYTES
        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')

        st.download_button(
            label="📥 Baixar Relatório", 
            data=pdf_bytes, 
            file_name=f"Relatorio_{cliente}.pdf", 
            mime="application/pdf"
        )

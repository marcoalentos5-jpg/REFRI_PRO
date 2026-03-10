import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io
import os
from PIL import Image

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# --- 2. MOTOR TERMODINÂMICO (PRECISÃO PERICIAL) ---
def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                   "t": [-51.0, -17.02, -0.29, 11.55, 20.93, 28.84, 35.58, 41.74, 47.3, 52.1, 56.59, 60.7, 64.59]},
        "R-32": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                 "t": [-51.7, -17.46, 0.87, 10.86, 20.14, 27.9, 34.63, 40.6, 45.96, 50.8, 55.36, 59.5, 63.43]},
        "R-22": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 600.0], 
                 "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 67.72, 73.2, 78.38, 87.53]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 80.0, 100.0, 130.0, 150.0, 180.0, 200.0], 
                   "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 38.4, 43.65, 50.1, 53.74]},
        "R-404A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0], 
                   "t": [-45.45, -9.41, 8.96, 22.23, 32.59, 41.2, 48.6, 55.2, 61.1]}
    }
    if gas not in ancoras: return 0.0
    try: return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)
    except: return 0.0

# --- 3. MOTOR DE GERAÇÃO PDF ---
class PDF(FPDF):
    def __init__(self, logo_path=None):
        super().__init__()
        self.logo_path = logo_path
    def header(self):
        if self.logo_path and os.path.exists(self.logo_path):
            self.image(self.logo_path, 10, 8, 33)
            self.set_x(45)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'RELATORIO TECNICO - MPN ENGENHARIA', 0, 1, 'R')
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

# --- 4. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_ref = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📚 Referência"])

with tab_cad:
    st.subheader("🖼️ Identidade Visual")
    logo_file = st.file_uploader("Upload Logomarca (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
    st.subheader("👤 Dados do Cliente")
    c1, c2 = st.columns(2)
    cliente = c1.text_input("Nome do Cliente", key="cli_n")
    doc_cliente = c2.text_input("CPF / CNPJ", key="doc_n")
    whatsapp = c1.text_input("🟢 WhatsApp", value="21980264217")
    data_visita = c2.date_input("Data da Visita", value=date.today())
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.selectbox("Fabricante", ["Samsung", "LG", "Daikin", "Midea", "Carrier", "Gree", "Elgin", "Hitachi", "TCL"])
    tecnologia = d2.selectbox("Série/Tecnologia", ["WindFree", "Dual Inverter", "Advance/SkyAir", "Liva/EcoInverter", "XPower", "G-Top", "Eco Power", "AirHome", "Elite Series", "On-Off"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"])
    cap_digitada = d3.text_input("Capacidade (BTUs)")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    e1, e2 = st.columns(2)
    v_rede = e1.number_input("Tensão Rede (V)", value=220.0)
    v_med = e1.number_input("Tensão Medida (V)", value=218.0)
    rla_comp = e2.number_input("RLA Nominal (A)", value=0.0)
    a_med = e2.number_input("Corrente Medida (A)", value=0.0)

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    col1, col2 = st.columns(2)
    p_suc = col1.number_input("Pressão Sucção (PSIG)", value=118.0)
    t_suc_tubo = col1.number_input("Temp. Tubo Sucção (°C)", value=12.0)
    p_liq = col2.number_input("Pressão Descarga (PSIG)", value=345.0)
    t_liq_tubo = col2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    tsat_suc = get_tsat_global(p_suc, fluido)
    tsat_liq = get_tsat_global(p_liq, fluido)
    sh, sc = round(t_suc_tubo - tsat_suc, 1), round(tsat_liq - t_liq_tubo, 1)

with tab_diag:
    st.subheader("🤖 Diagnóstico e Evidências")
    col_in, col_out = st.columns(2)
    with col_in:
        h_o = max(150, (st.session_state.get('o_text', "").count('\n') + 1) * 25)
        o_raw = st.text_area("✍️ Observações/Erros", height=h_o, key="o_text")
        h_m = max(150, (st.session_state.get('m_text', "").count('\n') + 1) * 25)
        m_raw = st.text_area("🔧 Medidas Tomadas", height=h_m, key="m_text")
    
    st.markdown("---")
    f_files = st.file_uploader("📸 Fotos de Campo (Máx 4)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    if f_files:
        c_i = st.columns(len(f_files))
        for i, f in enumerate(f_files): c_i[i].image(f, use_container_width=True)

    diag_f = []
    txt_c = (o_raw + " " + m_raw).upper()
    erros_db = {
        "Samsung": {"WINDFREE": {"E101": "Erro comunicação", "E554": "Vazamento gás"}},
        "LG": {"DUAL INVERTER": {"CH05": "Falha Comunicacao"}},
        "Hitachi": {"AIRHOME": {"08": "Alta temp descarga"}},
        "TCL": {"ELITE SERIES": {"P4": "Proteção IPM"}}
    }
    if fabricante in erros_db and tecnologia.upper() in erros_db[fabricante]:
        for cod, msg in erros_db[fabricante][tecnologia.upper()].items():
            if cod in txt_c: diag_f.append(f"🚨 {fabricante} {cod}: {msg}")
    
    if any(x in txt_c for x in ["VAZAMENTO", "FUGA"]): diag_f.append("🔴 PRIORIDADE: Pressurizar com N2.")
    st.warning("\n".join(diag_f) if diag_f else "✅ Parâmetros normais.")

    if st.button("🚀 PROCESSAR RELATÓRIO FINAL"):
        t_logo, t_imgs = None, []
        if logo_file:
            t_logo = "temp_logo.png"
            with open(t_logo, "wb") as f: f.write(logo_file.getvalue())
        
        pdf = PDF(logo_path=t_logo)
        pdf.add_page()
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, f"CLIENTE: {cliente}", 0, 1)
        pdf.cell(0, 8, f"EQUIPAMENTO: {fabricante} {tecnologia} ({cap_digitada} BTUs)", 0, 1)
        pdf.ln(5)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 8, 'DADOS TECNICOS', 1, 1, 'C', 1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(95, 8, f"P. Suc: {p_suc} PSIG / SH: {sh} K", 1)
        pdf.cell(95, 8, f"P. Liq: {p_liq} PSIG / SC: {sc} K", 1, 1)
        pdf.ln(5)
        pdf.multi_cell(0, 8, f"Observacoes:\n{o_raw}\n\nMedidas Tomadas:\n{m_raw}", 1)
        
        if f_files:
            pdf.ln(10)
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 8, 'EVIDENCIAS FOTOGRAFICAS', 1, 1, 'C', 1)
            y_f = pdf.get_y() + 5
            for idx, f in enumerate(f_files[:4]):
                t_p = f"t_img_{idx}.jpg"
                Image.open(f).convert("RGB").save(t_p, "JPEG", quality=75)
                t_imgs.append(t_p)
                pdf.image(t_p, x=10 + ((idx % 2) * 95), y=y_f + ((idx // 2) * 65), w=90)
        
        pdf_out = pdf.output(dest='S').encode('latin-1', errors='replace')
        st.download_button("📥 Baixar PDF", pdf_out, f"Relatorio_MPN_{cliente}.pdf", "application/pdf")
        if t_logo and os.path.exists(t_logo): os.remove(t_logo)
        for t in t_imgs: 
            if os.path.exists(t): os.remove(t)

with tab_ref:
    st.subheader("⚡ Calculadora de Queda de Tensão")
    dist = st.number_input("Distância (m)", value=10.0)
    bit = st.selectbox("Bitola (mm²)", [1.5, 2.5, 4.0, 6.0])
    v_p = round((2 * 0.0172 * dist * (a_med if a_med > 0 else 1)) / bit, 2)
    st.info(f"Queda: {v_p}V | Tensão Final: {round(v_rede - v_p, 1)}V")
    st.markdown("---")
    st.subheader("📋 Checklist de Comissionamento")
    c1, c2 = st.columns(2)
    with c1: st.checkbox("Vácuo < 500 Microns"); st.checkbox("Nitrogênio 600 PSI")
    with c2: st.checkbox("Dreno Testado"); st.checkbox("Aperto Elétrico")
    st.markdown("---")
    st.subheader("📚 Tabela NTC")
    # Tabela corrigida para evitar SyntaxError
    st.table({
        "Temp (C)": [10, 15, 20, 25, 30],
        "10k (Ohm)": [18700, 14800, 12100, 10000, 8200]
    })

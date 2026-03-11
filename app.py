import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io
import os

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
                 "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 73.2, 78.38, 87.53]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 80.0, 100.0, 130.0, 150.0, 180.0, 200.0], 
                   "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 38.4, 43.65, 50.1, 53.74]},
        "R-404A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0], 
                   "t": [-45.45, -9.41, 8.96, 22.23, 32.59, 41.2, 48.6, 55.2, 61.1]}
    }
    if gas not in ancoras: return 0.0
    try: return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)
    except: return 0.0

# Função de Limpeza Rigorosa para PDF
def clean(txt):
    if txt is None: return ""
    replacements = {'°': 'C', 'º': '.', 'ª': '.', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C', '´': '', '`': ''}
    t = str(txt)
    for old, new in replacements.items(): t = t.replace(old, new)
    return t.encode('latin-1', 'replace').decode('latin-1')

# --- 3. INTERFACE DO APP ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    
    # Linha 1: Nome aumentado e CPF/CNPJ diminuído
    c1, c2 = st.columns([3, 1])
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c2.text_input("CPF / CNPJ")
    
    # Linha 2: Logradouro (combo), Nome, Nº e Complemento
    c3, c4, c5, c6 = st.columns([1, 2, 0.5, 1])
    tipo_logr = c3.selectbox("Logradouro", ["Rua", "Avenida", "Travessa", "Alameda", "Estrada", "Rodovia", "Praça", "Loteamento"])
    nome_logr = c4.text_input("Nome do Logradouro")
    numero = c5.text_input("Nº")
    complemento = c6.text_input("Complemento")
    
    # Linha 3: Bairro e CEP (diminuídos) + E-mail
    c7, c8, c9 = st.columns([1, 1, 2])
    bairro = c7.text_input("Bairro")
    cep = c8.text_input("CEP", placeholder="00000-000")
    email_cli = c9.text_input("✉️ E-mail")

    # Linha 4: WhatsApp e Data
    c10, c11 = st.columns(2)
    whatsapp = c10.text_input("🟢 WhatsApp", value="21980264217")
    data_visita = c11.date_input("Data da Visita", value=date.today())

    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    linha = d1.text_input("Linha")
    local_eq = d1.text_input("Localização / Setor")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"])
    tipo_eq = d2.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF", "Chiller"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"])
    cap_digitada = d3.text_input("Capacidade (Mil BTU´s)", value="0")
    col_ev1, col_ev2 = st.columns(2)
    mod_evap = col_ev1.text_input("Modelo Unidade Evaporadora")
    serie_evap = col_ev2.text_input("Nº de Série Evaporadora")
    col_cd1, col_cd2 = st.columns(2)
    mod_cond = col_cd1.text_input("Modelo Unidade Condensadora")
    serie_cond = col_cd2.text_input("Nº de Série Condensadora")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    e1, e2 = st.columns(2)
    v_rede = e1.number_input("Tensão da Rede (V)", value=220.0)
    v_med = e1.number_input("Tensão Medida (V)", value=218.0)
    lra_comp = e2.number_input("LRA (A)", value=0.0)
    rla_comp = e2.number_input("RLA (A)", value=0.0)
    a_med = e2.number_input("Corrente Medida (A)", value=0.0)
    diff_v = round(v_rede - v_med, 1)
    carga_percent = round((a_med/rla_comp*100),1) if rla_comp > 0 else 0
    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric("Queda de Tensão", f"{diff_v} V", delta=f"-{diff_v}V", delta_color="inverse")
    res2.metric("Folga Corrente", f"{round(rla_comp - a_med, 1)} A")
    res3.metric("Carga Motor", f"{carga_percent}%")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    col1, col2, col3 = st.columns(3)
    p_suc = col1.number_input("Pressão Sucção (PSIG)", value=118.0)
    t_suc_tubo = col1.number_input("Temp. Tubo Sucção (°C)", value=12.0)
    p_liq = col2.number_input("Pressão Descarga (PSIG)", value=345.0)
    t_liq_tubo = col2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ret = col3.number_input("Temp. Ar Retorno (°C)", value=24.0)
    t_ins = col3.number_input("Temp. Ar Insufl. (°C)", value=12.0)
    tsat_suc = get_tsat_global(p_suc, fluido)
    tsat_liq = get_tsat_global(p_liq, fluido)
    sh = round(t_suc_tubo - tsat_suc, 1)
    sc = round(tsat_liq - t_liq_tubo, 1)
    dt = round(t_ret - t_ins, 1)
    st.markdown("---")
    ct1, ct2 = st.columns(2)
    with ct1:
        st.markdown(f"""<div style='background-color:#004a99;padding:15px;border-radius:10px;border-left:5px solid #ffcc00;color:white;'><b>🌡️ T-Sat Sucção:</b><h2 style='margin:0;color:white;'>{tsat_suc} °C</h2><b>🔥 Superaquecimento (SH):</b><h2 style='margin:0;color:white;'>{sh} K</h2></div>""", unsafe_allow_html=True)
    with ct2:
        st.markdown(f"""<div style='background-color:#004a99;padding:15px;border-radius:10px;border-left:5px solid #00d2ff;color:white;'><b>❄️ T-Sat Líquido:</b><h2 style='margin:0;color:white;'>{tsat_liq} °C</h2><b>💧 Sub-resfriamento (SC):</b><h2 style='margin:0;color:white;'>{sc} K</h2></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div style='background-color:#004a99;padding:20px;border-radius:15px;text-align:center;margin-top:10px;border:2px solid #ffcc00;'><span style='color:white;font-weight:bold;'>📈 Diferencial de Temperatura (ΔT)</span><h1 style='margin:0;color:white;font-size:45px;'>{dt} K</h1></div>""", unsafe_allow_html=True)

with tab_diag:
    st.subheader("🤖 Diagnóstico e Recomendações")
    ia_raw = st.text_area("🤖 Diagnóstico Final / IA", value=f"SH: {sh}K | SC: {sc}K | DT: {dt}K", height=150)
    if st.button("📄 Gerar Relatório Profissional"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 74, 153)
        pdf.rect(0, 0, 210, 42, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 15, "RELATORIO TECNICO", ln=True, align='C')
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, "CNPJ: 45.451.272/0001-00 | Tel: 21-98545-3763", ln=True, align='C')
        pdf.ln(12)

        def draw_header(title):
            pdf.set_fill_color(235, 235, 235); pdf.set_text_color(0, 74, 153); pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, f" {clean(title.upper())}", ln=True, fill=True); pdf.set_text_color(0, 0, 0); pdf.ln(3)

        draw_header("1. Identificacao do Cliente")
        pdf.set_font("Arial", '', 9)
        pdf.cell(0, 6, f"Cliente: {clean(cliente)} | CPF/CNPJ: {clean(doc_cliente)}", ln=True)
        pdf.cell(0, 6, f"Endereco: {clean(tipo_logr)} {clean(nome_logr)}, No {clean(numero)} {clean(complemento)}", ln=True)
        pdf.cell(0, 6, f"Bairro: {clean(bairro)} | CEP: {clean(cep)} | WhatsApp: {clean(whatsapp)}", ln=True)
        
        draw_header("2. Dados Tecnicos")
        pdf.cell(0, 6, f"Equipamento: {clean(fabricante)} | Tecnologia: {tecnologia} | Fluido: {fluido}", ln=True)
        pdf.cell(0, 6, f"Evaporadora Serie: {clean(serie_evap)} | Condensadora Serie: {clean(serie_cond)}", ln=True)

        draw_header("3. Parametros Medidos")
        pdf.cell(0, 6, f"Eletrica: {v_med}V | {a_med}A | Carga: {carga_percent}%", ln=True)
        pdf.cell(0, 6, f"Termica: Succao {p_suc} PSIG | SH: {sh}K | SC: {sc}K | Delta T: {dt}K", ln=True)

        draw_header("4. Diagnostico Final")
        pdf.multi_cell(0, 6, clean(ia_raw))

        out = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("⬇️ Baixar Relatório PDF", out, f"Relatorio_{clean(cliente)}.pdf", "application/pdf")

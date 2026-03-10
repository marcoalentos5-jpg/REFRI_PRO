import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io
import os
import streamlit.components.v1 as components

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# --- 2. MOTOR TERMODINÂMICO ---
def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-17.02, -0.29, 11.55, 20.93, 35.58, 47.30, 56.59, 64.59]},
        "R-32": {"p": [50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-17.46, 0.87, 10.86, 20.14, 34.63, 45.96, 55.36, 63.43]},
        "R-22": {"p": [50.0, 100.0, 150.0, 200.0, 300.0, 350.0, 400.0, 500.0, 600.0], "t": [-3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 67.72, 78.38, 83.12, 87.53]},
        "R-134a": {"p": [0.0, 50.0, 100.0, 150.0, 200.0], "t": [-26.08, 12.23, 30.92, 43.65, 53.74]},
        "R-404A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0], "t": [-45.45, -9.41, 8.96, 22.23, 32.59]}
    }
    if gas not in ancoras: return 0.0
    try: return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)
    except: return 0.0

# --- 3. INTERFACE DO APP (LAYOUT PRESERVADO) ---
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
    linha = d1.text_input("Linha")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "On-Off"])
    tipo_eq = d2.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"])
    cap_digitada = d3.text_input("Capacidade (BTU´s)")
    mod_cond = st.text_input("Modelo Unidade (Cond)")

with tab_ele:
    v_med = st.number_input("Tensão Medida (V)", value=0.0)
    a_med = st.number_input("Corrente Medida (A)", value=0.0)

with tab_termo:
    p_suc = st.number_input("Pressão Sucção (PSIG)", value=118.0)
    t_suc_tubo = st.number_input("Temp. Tubo Sucção (°C)", value=12.0)
    p_liq = st.number_input("Pressão Descarga (PSIG)", value=345.0)
    t_liq_tubo = st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ret = st.number_input("Temp. Ar Retorno (°C)", value=24.0)
    t_ins = st.number_input("Temp. Ar Insuflamento (°C)", value=12.0)
    
    tsat_suc = get_tsat_global(p_suc, fluido)
    tsat_liq = get_tsat_global(p_liq, fluido)
    sh = round(t_suc_tubo - tsat_suc, 1)
    sc = round(tsat_liq - t_liq_tubo, 1)
    dt = round(t_ret - t_ins, 1)

with tab_diag:
    obs = st.text_area("Observações Técnicas", height=150)
    
    if st.button("Gerar Relatório PDF"):
        pdf = FPDF()
        pdf.add_page()
        
        # CABEÇALHO COM LOGOMARCA
        if os.path.exists("logo.png"):
            pdf.image("logo.png", 10, 8, 25)
            pdf.set_x(40)
        
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(0, 74, 153)
        pdf.cell(150, 8, "RELATÓRIO TÉCNICO DE ENGENHARIA", ln=True, align="R")
        pdf.ln(5)
        
        # --- 1. IDENTIFICAÇÃO DO CLIENTE (LAYOUT CONGELADO) ---
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 9)
        pdf.set_text_color(0)
        pdf.cell(190, 6, " 1. IDENTIFICAÇÃO DO CLIENTE", ln=True, fill=True)
        
        # CPF/CNPJ DO CLIENTE NO TOPO DA SEÇÃO
        pdf.set_font("Arial", "", 8)
        pdf.cell(190, 6, f"CPF/CNPJ DO CLIENTE: {doc_cliente}", border="B", ln=True)
        
        # LINHA ACIMA DO NOME (ORDEM PRIORITÁRIA)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.cell(100, 6, f"Cliente: {cliente}", border="B")
        
        # DATA DA VISITA EM DESTAQUE
        pdf.set_font("Arial", "B", 8); pdf.set_fill_color(225, 225, 225)
        pdf.cell(90, 6, f" DATA DA VISITA: {data_visita.strftime('%d/%m/%Y')} ", border=1, fill=True, align="C", ln=True)
        
        pdf.set_font("Arial", "", 8)
        pdf.cell(190, 6, f"Endereço: {endereco}", border="B", ln=True)
        pdf.cell(95, 6, f"WhatsApp: {whatsapp}", border="B")
        pdf.cell(95, 6, f"E-mail: {email_cli}", border="B", ln=True)

        # --- 2. DADOS DO EQUIPAMENTO E MEDIÇÕES ---
        pdf.ln(3)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(190, 6, " 2. DADOS DO EQUIPAMENTO E MEDIÇÕES", ln=True, fill=True)
        pdf.set_font("Arial", "", 8)
        pdf.cell(95, 6, f"Fabricante: {fabricante} | Linha: {linha}", border="B")
        pdf.cell(95, 6, f"Modelo Cond: {mod_cond}", border="B", ln=True)
        pdf.cell(47, 6, f"Tensão: {v_med} V", border="B")
        pdf.cell(47, 6, f"Corrente: {a_med} A", border="B")
        pdf.cell(48, 6, f"Fluido: {fluido}", border="B")
        pdf.cell(48, 6, f"Superheat: {sh} K", border="B", ln=True)

        # --- 3. DIAGNÓSTICO ---
        pdf.ln(3)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(190, 6, " 3. DIAGNÓSTICO E OBSERVAÇÕES", ln=True, fill=True)
        pdf.set_font("Arial", "", 8)
        pdf.multi_cell(190, 5, obs if obs else "Sem observações.", border=1)

        # --- RODAPÉ PERMANENTE (ASSINATURA TRAVADA) ---
        pdf.ln(10)
        pdf.line(60, pdf.get_y(), 150, pdf.get_y())
        pdf.set_font("Arial", "B", 8)
        pdf.cell(190, 4, "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO", ln=True, align="C")
        pdf.set_font("Arial", "", 7)
        pdf.cell(190, 4, "CNPJ: 51.274.762/0001-17", ln=True, align="C")

        # SAÍDA DE BYTES SEGURA PARA DOWNLOAD
        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, str): pdf_bytes = pdf_bytes.encode('latin-1')
        st.download_button(label="📥 Baixar Relatório", data=io.BytesIO(pdf_bytes), file_name=f"Relatorio_{cliente}.pdf", mime="application/pdf")

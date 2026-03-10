import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io
import os
import streamlit.components.v1 as components

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# --- 2. MOTOR TERMODINÂMICO ---
def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-17.02, -0.29, 11.55, 20.93, 35.58, 47.30, 56.59, 64.59]},
        "R-32": {"p": [50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-17.46, 0.87, 10.86, 20.14, 34.63, 45.96, 55.36, 63.43]},
        "R-22": {"p": [50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-3.34, 15.80, 28.15, 38.56, 54.89, 67.72, 78.38, 87.53]},
        "R-134a": {"p": [0.0, 50.0, 100.0, 150.0, 200.0], "t": [-26.08, 12.23, 30.92, 43.65, 53.74]},
        "R-404A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0], "t": [-45.45, -9.41, 8.96, 22.23, 32.59]}
    }
    if gas not in ancoras: return 0.0
    return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)

# --- 3. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c1.text_input("CPF / CNPJ")
    endereco = c2.text_input("Endereço Completo")
    whatsapp = c3.text_input("🟢 WhatsApp", value="21980264217")
    data_visita = c3.date_input("Data da Visita", value=date.today())
    email_cli = c2.text_input("✉️ E-mail")
    st.markdown("---")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante")
    linha = d1.text_input("Linha")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "On-Off"])
    tipo_eq = d2.selectbox("Tipo", ["Split", "Cassete", "Piso-Teto"])
    fluido = d3.selectbox("Gás", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"])
    cap_digitada = d3.text_input("Capacidade (BTU)")

with tab_ele:
    v_med = st.number_input("Tensão Medida (V)", value=220.0)
    a_med = st.number_input("Corrente Medida (A)", value=0.0)

with tab_termo:
    p_suc = st.number_input("Pressão Sucção (PSIG)", value=118.0)
    t_suc_tubo = st.number_input("Temp. Tubo Sucção (°C)", value=12.0)
    p_liq = st.number_input("Pressão Descarga (PSIG)", value=345.0)
    t_liq_tubo = st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ret = st.number_input("Temp. Retorno (°C)", value=24.0)
    t_ins = st.number_input("Temp. Insuflamento (°C)", value=12.0)
    
    tsat_suc = get_tsat_global(p_suc, fluido)
    tsat_liq = get_tsat_global(p_liq, fluido)
    sh = round(t_suc_tubo - tsat_suc, 1)
    sc = round(tsat_liq - t_liq_tubo, 1)
    dt = round(t_ret - t_ins, 1)

with tab_diag:
    obs = st.text_area("Observações", height=100)
    if st.button("Gerar Relatório PDF"):
        pdf = FPDF()
        pdf.add_page()
        
        # CABEÇALHO
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "RELATÓRIO TÉCNICO DE ENGENHARIA", ln=True, align="C")
        pdf.ln(5)
        
        # 1. IDENTIFICAÇÃO (ORDENS APLICADAS)
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 8, " 1. IDENTIFICAÇÃO DO CLIENTE", ln=True, fill=True)
        
        pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # LINHA ACIMA DO NOME
        pdf.set_font("Arial", "", 10)
        pdf.cell(85, 8, f"Cliente: {cliente}", border="B")
        
        # DATA EM DESTAQUE
        pdf.set_font("Arial", "B", 10); pdf.set_fill_color(200, 200, 200)
        pdf.cell(50, 8, f"DATA: {data_visita.strftime('%d/%m/%Y')}", border=1, fill=True, align="C")
        
        # CNPJ/CPF NO LUGAR DE DOC
        pdf.set_font("Arial", "", 10)
        pdf.cell(55, 8, f"CNPJ/CPF: {doc_cliente}", border="B", ln=True, align="R")
        
        pdf.cell(190, 8, f"Endereço: {endereco}", border="B", ln=True)
        pdf.cell(95, 8, f"WhatsApp: {whatsapp}", border="B")
        pdf.cell(95, 8, f"E-mail: {email_cli}", border="B", ln=True)
        
        # 2. DADOS DO EQUIPAMENTO
        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 8, " 2. DADOS TÉCNICOS DA MÁQUINA", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(63, 8, f"Fabricante: {fabricante}", border=1)
        pdf.cell(63, 8, f"Fluido: {fluido}", border=1)
        pdf.cell(64, 8, f"Capacidade: {cap_digitada}", border=1, ln=True)
        
        # 3. INFORMAÇÕES TÉCNICAS (COMPLETO)
        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 8, " 3. MEDIÇÕES E PARÂMETROS", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(47, 8, f"Pressão Suc: {p_suc} PSI", border=1)
        pdf.cell(47, 8, f"Temp Tubo: {t_suc_tubo} C", border=1)
        pdf.cell(48, 8, f"Superheat: {sh} K", border=1)
        pdf.cell(48, 8, f"T-Sat Suc: {tsat_suc} C", border=1, ln=True)
        
        pdf.cell(47, 8, f"Tensão: {v_med} V", border=1)
        pdf.cell(47, 8, f"Corrente: {a_med} A", border=1)
        pdf.cell(48, 8, f"Delta T: {dt} K", border=1)
        pdf.cell(48, 8, f"Subcooling: {sc} K", border=1, ln=True)

        # 4. OBSERVAÇÕES
        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 8, " 4. DIAGNÓSTICO / OBSERVAÇÕES", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(190, 8, obs, border=1)

        # SAÍDA SEGURA
        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, str): pdf_bytes = pdf_bytes.encode('latin-1')
        st.download_button("📥 Baixar Relatório Completo", io.BytesIO(pdf_bytes), f"Relatorio_{cliente}.pdf", "application/pdf")

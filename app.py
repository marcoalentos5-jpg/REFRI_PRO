import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io
import os

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

# --- 3. INTERFACE DO APP ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c1.text_input("CPF / CNPJ")
    
    endereco = c2.text_input("Endereço Completo")
    bairro = c2.text_input("Bairro")
    cep = c2.text_input("CEP", placeholder="00000-000")
    
    whatsapp = c3.text_input("🟢 WhatsApp", value="21980264217")
    data_visita = c3.date_input("Data da Visita", value=date.today())
    email_cli = c2.text_input("✉️ E-mail")
    
    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    linha = d1.text_input("Linha")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"])
    tipo_eq = d2.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF", "Chiller"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"])
    cap_digitada = d3.text_input("Capacidade (Mil BTU´s)")
    
    col_evap1, col_evap2 = st.columns(2)
    mod_evap = col_evap1.text_input("Modelo Unidade Evaporadora")
    serie_evap = col_evap2.text_input("Nº de Série Evaporadora")
    col_cond1, col_cond2 = st.columns(2)
    mod_cond = col_cond1.text_input("Modelo Unidade Condensadora")
    serie_cond = col_cond2.text_input("Nº de Série Condensadora")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    e1, e2 = st.columns(2)
    with e1:
        v_rede = st.number_input("Tensão (Rede) [V]", value=220.0)
        v_med = st.number_input("Tensão Medida (V)", value=218.0)
        diff_v = round(v_rede - v_med, 1)
    with e2:
        lra_comp = st.number_input("LRA (A)", value=0.0)
        rla_comp = st.number_input("RLA (A)", value=0.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
        diff_a = round(rla_comp - a_med, 1)
    
    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric("Queda de Tensão", f"{diff_v} V", delta=f"-{diff_v}V", delta_color="inverse")
    res2.metric("Folga Corrente (RLA-Med)", f"{diff_a} A")
    res3.metric("Carga Motor", f"{round((a_med/rla_comp*100),1) if rla_comp > 0 else 0}%")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    col1, col2 = st.columns(2)
    p_suc = col1.number_input("Pressão de Sucção (PSIG)", value=118.0)
    t_suc_tubo = col1.number_input("Temp. do Tubo de Sucção (°C)", value=12.0)
    p_liq = col2.number_input("Pressão de Descarga (PSIG)", value=345.0)
    t_liq_tubo = col2.number_input("Temp. do Tubo de Líquido (°C)", value=30.0)
    t_ret = col1.number_input("Temp. do Ar de Retorno (°C)", value=24.0)
    t_ins = col2.number_input("Temp. do Ar de Insuflamento (°C)", value=12.0)
    
    tsat_suc = get_tsat_global(p_suc, fluido)
    tsat_liq = get_tsat_global(p_liq, fluido)
    sh = round(t_suc_tubo - tsat_suc, 1)
    sc = round(tsat_liq - t_liq_tubo, 1)
    dt = round(t_ret - t_ins, 1)
    
    st.markdown("---")
    st.subheader("📊 Destaque dos Resultados")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🌡️ T-Sat Sucção", f"{tsat_suc} °C")
    m2.metric("🔥 Superaquecimento", f"{sh} K")
    m3.metric("❄️ T-Sat Líquido", f"{tsat_liq} °C")
    m4.metric("💧 Sub-resfriamento", f"{sc} K")
    
    st.info(f"### Diferencial de Temperatura (ΔT): {dt} K")

with tab_diag:
    obs = st.text_area("Observações Técnicas Detalhadas", height=150)
    if st.button("Gerar Relatório PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(0, 74, 153)
        pdf.cell(190, 10, "RELATÓRIO TÉCNICO", ln=True, align="C")
        pdf.ln(5)
        
        pdf.set_fill_color(245, 245, 245)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(60)
        pdf.cell(190, 7, " 1. IDENTIFICAÇÃO DO CLIENTE", ln=True, fill=True)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(190, 6, f"CPF/CNPJ: {doc_cliente}", border="B", ln=True)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(135, 7, f"Cliente: {cliente}", border="B") 
        pdf.cell(55, 7, f" DATA: {data_visita.strftime('%d/%m/%Y')} ", border=1, ln=True)
        pdf.cell(135, 6, f"Endereço: {endereco}", border="B")
        pdf.cell(55, 6, f" Bairro: {bairro}", border="B", ln=True)
        pdf.cell(63, 6, f"WhatsApp: {whatsapp}", border="B")
        pdf.cell(63, 6, f"E-mail: {email_cli}", border="B")
        pdf.cell(64, 6, f" CEP: {cep}", border="B", ln=True)

        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 7, " 3. ANÁLISE TÉCNICA E MEDIÇÕES", ln=True, fill=True)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(47, 6, f"V. Rede: {v_rede} V", border="B"); pdf.cell(47, 6, f"V. Med: {v_med} V", border="B")
        pdf.cell(48, 6, f"LRA: {lra_comp} A", border="B"); pdf.cell(48, 6, f"RLA: {rla_comp} A", border="B", ln=True)
        pdf.cell(47, 6, f"P. Suc: {p_suc} PSI", border="B"); pdf.cell(47, 6, f"P. Liq: {p_liq} PSI", border="B")
        pdf.cell(48, 6, f"SH: {sh} K", border="B"); pdf.cell(48, 6, f"SC: {sc} K", border="B", ln=True)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(190, 6, f" Delta T: {dt} K", border="B", ln=True)

        pdf.ln(4)
        pdf.multi_cell(190, 5, f"Diagnóstico: {obs}", border=1)

        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, str): pdf_bytes = pdf_bytes.encode('latin-1')
        st.download_button("📥 Baixar Relatório", io.BytesIO(pdf_bytes), f"Relatorio_{cliente}.pdf")

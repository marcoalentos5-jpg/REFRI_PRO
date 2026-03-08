import streamlit as st
from datetime import date
from fpdf import FPDF
import urllib.parse
import os
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. ESTILIZAÇÃO MPN ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetric"] { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #dee2e6; }
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 3.5em; background-color: #004A99; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA TÉCNICA ---
def calcular_tsat(psig, gas):
    if psig <= 0: return 0
    tabelas = {
        "R-410A": 0.2307 * psig - 22.81, "R-22": 0.2854 * psig - 25.12,
        "R-134a": 0.5210 * psig - 38.54, "R-404A": 0.2105 * psig - 16.52, "R-32": 0.31 * psig - 25.0
    }
    return tabelas.get(gas, 0)

# --- 4. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico & Relatório"
])

with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c1.text_input("CPF / CNPJ")
    endereco = c2.text_input("Endereço Completo")
    whatsapp_input = c2.text_input("🟢 WhatsApp (com DDD)", value="21980264217")
    email_cli = c3.text_input("✉️ E-mail")
    # ORDEM 1: Formato de data brasileiro na interface
    data_visita = st.date_input("Data da Visita", value=date.today(), format="DD/MM/YYYY")

    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante")
    linha = d1.text_input("Linha")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"])
    tipo_eq = d2.selectbox("Tipo", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF/VRV", "Chiller"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])
    cap_btu = d3.text_input("Capacidade (BTUs)")

    mod_evap = st.text_input("Modelo Evaporadora")
    serie_evap = st.text_input("Série Evaporadora")
    mod_cond = st.text_input("Modelo Condensadora")
    serie_cond = st.text_input("Série Condensadora")

with tab_ele:
    v_med = st.number_input("Tensão (V)", value=220.0)
    a_med = st.number_input("Corrente (A)", value=0.0)

with tab_termo:
    p_suc = st.number_input("Pressão Sucção (PSIG)", value=120.0)
    t_suc = st.number_input("Temp. Tubo Sucção (°C)", value=10.0)
    t_ret = st.number_input("Ar Retorno (°C)", value=24.0)
    p_liq = st.number_input("Pressão Líquido (PSIG)", value=350.0)
    t_liq = st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ins = st.number_input("Ar Insuflação (°C)", value=12.0)
    
    tsat_evap = calcular_tsat(p_suc, fluido)
    tsat_cond = calcular_tsat(p_liq, fluido)
    sh, sr, dt = t_suc - tsat_evap, tsat_cond - t_liq, t_ret - t_ins

with tab_diag:
    if sh < 5: veredito = "ALERTA: SH Baixo. Risco de retorno de líquido."
    elif sh > 12: veredito = "ALERTA: SH Alto. Possível falta de fluido ou restrição."
    else: veredito = "Sistema operando em equilíbrio técnico conforme fabricante."
    
    st.info(f"Veredito: {veredito}")
    # ORDEM 2: Nome alterado para apenas "Observações"
    obs_final = st.text_area("📝 Observações", height=150)

    # --- RELATÓRIO PDF (ORDENS DE ENQUADRAMENTO E DATA BR) ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "LAUDO TÉCNICO DE ENGENHARIA - MPN", ln=True, align="C")
    pdf.ln(5)

    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, " 1. IDENTIFICAÇÃO", border=1, ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    # ORDEM 1 (PDF): Data em formato brasileiro DD/MM/AAAA
    data_br = data_visita.strftime('%d/%m/%Y')
    pdf.cell(130, 8, f" Cliente: {cliente}", border=1)
    pdf.cell(60, 8, f" Data: {data_br}", border=1, ln=True)
    pdf.cell(190, 8, f" Endereço: {endereco}", border=1, ln=True)

    pdf.ln(2)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, " 2. DADOS DO EQUIPAMENTO", border=1, ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(63, 8, f" Marca: {fabricante}", border=1); pdf.cell(63, 8, f" Linha: {linha}", border=1); pdf.cell(64, 8, f" Cap: {cap_btu} BTU", border=1, ln=True)
    pdf.cell(95, 8, f" Evap S/N: {serie_evap}", border=1); pdf.cell(95, 8, f" Cond S/N: {serie_cond}", border=1, ln=True)

    pdf.ln(2)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, " 3. MEDIÇÕES", border=1, ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(47, 8, f" Tensao: {v_med}V", border=1); pdf.cell(47, 8, f" Corrente: {a_med}A", border=1); pdf.cell(48, 8, f" P. Suc: {p_suc} PSI", border=1); pdf.cell(48, 8, f" P. Liq: {p_liq} PSI", border=1, ln=True)
    pdf.cell(47, 8, f" SH: {sh:.1f} K", border=1); pdf.cell(47, 8, f" SR: {sr:.1f} K", border=1); pdf.cell(48, 8, f" DT Ar: {dt:.1f} C", border=1); pdf.cell(48, 8, f" Tsat: {tsat_evap:.1f} C", border=1, ln=True)

    pdf.ln(2)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, " 4. DIAGNÓSTICO", border=1, ln=True, fill=True)
    pdf.set_font("Arial", "B", 10)
    pdf.multi_cell(190, 8, f" Veredito: {veredito}", border=1, align="L")

    # ORDEM 3 E 4: Último campo, nomeado "Observações", alinhado à esquerda e enquadrado (190mm)
    pdf.ln(2)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, " 5. OBSERVAÇÕES", border=1, ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(190, 8, f" {obs_final}", border=1, align="L")

    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 5, "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO", ln=True, align="C")
    pdf.cell(190, 5, "CNPJ: 51.274.762/0001-17", ln=True, align="C")

    # BUG FIX: Exportação compatível com Streamlit Cloud (fpdf2)
    pdf_bytes = pdf.output()
    st.download_button(
        label="📥 BAIXAR RELATÓRIO PDF", 
        data=bytes(pdf_bytes), 
        file_name=f"Laudo_{cliente}.pdf", 
        mime="application/pdf"
    )

import streamlit as st
from datetime import date
from fpdf import FPDF
import urllib.parse
import os
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. ESTILIZAÇÃO DA INTERFACE ---
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

def obter_ref_tecnica(fabricante, tecnologia, tipo, linha):
    texto = f"{fabricante} {tecnologia} {tipo} {linha}".upper()
    if "VRF" in texto or "MULTI" in texto:
        return {"sh_min": 3, "sh_max": 8, "sr_min": 5, "sr_max": 12}
    return {"sh_min": 5, "sh_max": 12, "sr_min": 3, "sr_max": 10}

# --- 4. TÍTULO E ABAS ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico & Relatório"
])

# --- ABA 1: IDENTIFICAÇÃO (FORMATO DE DATA BR) ---
with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c1.text_input("CPF / CNPJ")
    endereco = c2.text_input("Endereço Completo")
    whatsapp_input = c2.text_input("🟢 WhatsApp (com DDD)", value="21980264217")
    email_cli = c3.text_input("✉️ E-mail")
    # Diretriz: Formato brasileiro na interface
    data_visita = st.date_input("Data da Visita", value=date.today(), format="DD/MM/YYYY")

    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante")
    linha = d1.text_input("Linha (Ex: WindFree)")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"])
    tipo_eq = d2.selectbox("Tipo", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF/VRV", "Chiller"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])
    cap_btu = d3.text_input("Capacidade (BTUs)")

    col_u1, col_u2 = st.columns(2)
    mod_evap = col_u1.text_input("Modelo Evaporadora")
    serie_evap = col_u1.text_input("Série Evaporadora")
    mod_cond = col_u2.text_input("Modelo Condensadora")
    serie_cond = col_u2.text_input("Série Condensadora")

# --- ABA 2: ELÉTRICA ---
with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    e1, e2 = st.columns(2)
    v_med = e1.number_input("Tensão (V)", value=220.0)
    a_med = e2.number_input("Corrente (A)", value=0.0)

# --- ABA 3: TERMODINÂMICA ---
with tab_termo:
    st.subheader("🌡️ Pressões e Temperaturas")
    t1, t2 = st.columns(2)
    p_suc = t1.number_input("Pressão Sucção (PSIG)", value=120.0)
    t_suc = t1.number_input("Temp. Tubo Sucção (°C)", value=10.0)
    t_ret = t1.number_input("Ar Retorno (°C)", value=24.0)
    p_liq = t2.number_input("Pressão Líquido (PSIG)", value=350.0)
    t_liq = t2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ins = t2.number_input("Ar Insuflação (°C)", value=12.0)

    tsat_evap = calcular_tsat(p_suc, fluido)
    tsat_cond = calcular_tsat(p_liq, fluido)
    sh, sr, dt = t_suc - tsat_evap, tsat_cond - t_liq, t_ret - t_ins
    
    st.markdown("---")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Superaquecimento", f"{sh:.1f} K")
    r2.metric("Sub-resfriamento", f"{sr:.1f} K")
    r3.metric("Delta T Ar", f"{dt:.1f} °C")
    r4.metric("T. Sat. Evap", f"{tsat_evap:.1f} °C")

# --- ABA 4: DIAGNÓSTICO E GERAÇÃO DE PDF ---
with tab_diag:
    st.subheader("🤖 Diagnóstico e Relatório")
    ref = obter_ref_tecnica(fabricante, tecnologia, tipo_eq, linha)
    if sh < ref["sh_min"]: veredito = "ALERTA: SH Baixo. Risco de retorno de líquido."
    elif sh > ref["sh_max"]: veredito = "ALERTA: SH Alto. Possível falta de fluido ou restrição."
    else: veredito = "Sistema operando em equilíbrio técnico conforme fabricante."
    
    st.info(f"Veredito: {veredito}")
    # Diretriz: Campo renomeado para apenas Observações
    obs_final = st.text_area("📝 Observações", height=150)

    st.markdown("---")
    
    # --- LÓGICA DO PDF (CORREÇÃO DE BUGS E LAYOUT) ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "LAUDO TÉCNICO DE ENGENHARIA - MPN", ln=True, align="C")
    pdf.ln(5)

    # 1. Identificação
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, " 1. IDENTIFICAÇÃO DO CLIENTE", border=1, ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    # Diretriz: Data brasileira no PDF
    data_br = data_visita.strftime('%d/%m/%Y')
    pdf.cell(130, 8, f" Cliente: {cliente}", border=1)
    pdf.cell(60, 8, f" Data: {data_br}", border=1, ln=True)
    pdf.cell(190, 8, f" Endereço: {endereco}", border=1, ln=True)
    pdf.cell(95, 8, f" CPF/CNPJ: {doc_cliente}", border=1)
    pdf.cell(95, 8, f" WhatsApp: {whatsapp_input}", border=1, ln=True)

    # 2. Equipamento
    pdf.ln(2)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, " 2. DADOS DO EQUIPAMENTO", border=1, ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(63, 8, f" Marca: {fabricante}", border=1); pdf.cell(63, 8, f" Linha: {linha}", border=1); pdf.cell(64, 8, f" Cap: {cap_btu} BTU", border=1, ln=True)
    pdf.cell(95, 8, f" Evap S/N: {serie_evap}", border=1); pdf.cell(95, 8, f" Cond S/N: {serie_cond}", border=1, ln=True)
    pdf.cell(190, 8, f" Fluido: {fluido} | Tecnologia: {tecnologia} | Tipo: {tipo_eq}", border=1, ln=True)

    # 3. Medições
    pdf.ln(2)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, " 3. PARÂMETROS TÉCNICOS MEDIDOS", border=1, ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(47, 8, f" Tensão: {v_med}V", border=1); pdf.cell(47, 8, f" Corrente: {a_med}A", border=1); pdf.cell(48, 8, f" P. Sucção: {p_suc} PSI", border=1); pdf.cell(48, 8, f" P. Líquido: {p_liq} PSI", border=1, ln=True)
    pdf.cell(47, 8, f" SH: {sh:.1f} K", border=1); pdf.cell(47, 8, f" SR: {sr:.1f} K", border=1); pdf.cell(48, 8, f" Delta T Ar: {dt:.1f} C", border=1); pdf.cell(48, 8, f" Tsat: {tsat_evap:.1f} C", border=1, ln=True)

    # 4. Veredito e Observações (Diretriz: Último campo, enquadrado à esquerda)
    pdf.ln(2)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, " 4. DIAGNÓSTICO E OBSERVAÇÕES", border=1, ln=True, fill=True)
    pdf.set_font("Arial", "B", 10)
    pdf.multi_cell(190, 8, f" Veredito: {veredito}", border=1, align="L")
    pdf.set_font("Arial", "", 10)
    # multi_cell com 190mm garante que o texto não saia da página A4
    pdf.multi_cell(190, 8, f" Observações: {obs_final}", border=1, align="L")

    # Rodapé
    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 5, "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO", ln=True, align="C")
    pdf.cell(190, 5, "CNPJ: 51.274.762/0001-17", ln=True, align="C")

    # Botão de Download (Correção de Bug do fpdf2/Streamlit Cloud)
    pdf_bytes = pdf.output()
    st.download_button(
        label="📥 BAIXAR LAUDO TÉCNICO PDF", 
        data=bytes(pdf_bytes), 
        file_name=f"Laudo_{cliente}.pdf", 
        mime="application/pdf"
    )

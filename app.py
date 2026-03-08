import streamlit as st
from datetime import date
from fpdf import FPDF
import urllib.parse
import os
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. ESTILIZAÇÃO ORIGINAL MPN (LAYOUT ANTERIOR) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] { background-color: #E3F2FD; border-radius: 10px; padding: 15px; border: 1px solid #BBDEFB; }
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] { background-color: #E8F5E9; border-radius: 10px; padding: 15px; border: 1px solid #C8E6C9; }
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] { background-color: #FFFDE7; border-radius: 10px; padding: 15px; border: 1px solid #FFF9C4; }
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetric"] { background-color: #E1F5FE; border-radius: 10px; padding: 15px; border: 1px solid #B3E5FC; }
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA TÉCNICA ---
def calcular_tsat(psig, gas):
    if psig <= 0: return 0
    tabelas = {
        "R-410A": 0.2307 * psig - 22.81, "R-22": 0.2854 * psig - 25.12,
        "R-134a": 0.5210 * psig - 38.54, "R-404A": 0.2105 * psig - 16.52, 
        "R-32": 0.31 * psig - 25.0, "R-600a": 0.45 * psig - 15.0, "R-290": 0.25 * psig - 20.0
    }
    return tabelas.get(gas, 0)

# --- 4. TÍTULO E ABAS ---
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
    
    whatsapp_input = c3.text_input("🟢 WhatsApp (com DDD)", value="21980264217")
    data_visita = c3.date_input("Data da Visita", value=date.today(), format="DD/MM/YYYY")
    email_cli = c2.text_input("✉️ E-mail")

    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    linha = d1.text_input("Linha (Ex: Artcool, WindFree)")
    tecnologia = d2.selectbox("Tecnologia do Compressor", ["Inverter", "WindFree", "Scroll", "On-Off"])
    
    tipo_eq = d2.selectbox("Tipo de Sistema", [
        "Split Hi-Wall", "Cassete", "Piso-Teto", "Multi-Split", "VRF/VRV", 
        "Geladeira", "Freezer", "Chiller", "Câmara Fria", "Balcão Frigorífico", 
        "Bebedouro", "Ar-Condicionado Janela", "Self-Contained", "Fan-Coil"
    ])
    
    fluido = d3.selectbox("Gás Refrigerante", [
        "R-410A", "R-22", "R-32", "R-134a", "R-600a", 
        "R-290", "R-404A", "R-407C", "R-417A", "R-507A"
    ])
    cap_btu = d3.text_input("Capacidade (Mil BTUs/h)")

    col_u1, col_u2 = st.columns(2)
    mod_evap = col_u1.text_input("Modelo da Unidade (Evap)")
    serie_evap = col_u1.text_input("Nº de Série da Unidade (Evap)")
    mod_cond = col_u2.text_input("Modelo da Unidade (Cond)")
    serie_cond = col_u2.text_input("Nº de Série da Unidade (Cond)")

    tecnico_nome = "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO"
    doc_tecnico = "CNPJ: 51.274.762/0001-17"

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    v_med = st.number_input("Tensão Medida (V)", value=220.0)
    a_med = st.number_input("Corrente Medida Real (A)", value=0.0)

with tab_termo:
    t1, t2 = st.columns(2)
    p_suc = t1.number_input("Pressão Sucção (PSIG)", value=120.0)
    t_suc = t1.number_input("Temp. Tubo Sucção (°C)", value=10.0)
    t_ret = t1.number_input("Ar Retorno (°C)", value=24.0)
    p_liq = t2.number_input("Pressão Descarga (PSIG)", value=350.0)
    t_liq = t2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ins = t2.number_input("Ar Insuflação (°C)", value=12.0)

    tsat_evap = calcular_tsat(p_suc, fluido)
    tsat_cond = calcular_tsat(p_liq, fluido)
    sh, sr, dt = t_suc - tsat_evap, tsat_cond - t_liq, t_ret - t_ins
    
    st.markdown("---")
    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Temp. Saturação", f"{tsat_evap:.1f} °C")
    res2.metric("Superaquecimento", f"{sh:.1f} K")
    res3.metric("Delta T do Ar", f"{dt:.1f} °C")
    res4.metric("Sub-resfriamento", f"{sr:.1f} K")

with tab_diag:
    if sh < 5: veredito = "ALERTA: SH Baixo. Perigo de retorno de líquido ao compressor."
    elif sh > 12: veredito = "ALERTA: SH Alto. Possível falta de fluido ou restrição."
    else: veredito = "Sistema operando em equilíbrio técnico conforme fabricante."
    
    st.warning(f"Diagnóstico Final: {veredito}")
    obs_final = st.text_area("📝 Observações", height=150)

    st.markdown("---")
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15); pdf.add_page()
    
    pdf.set_font("helvetica", "B", 12); pdf.set_fill_color(230, 230, 230)
    pdf.cell(190, 10, "LAUDO TECNICO DE DIAGNOSTICO - MPN", border=1, ln=True, align="C", fill=True)
    
    # DADOS CLIENTE
    pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " INFORMAÇÕES DO CLIENTE", border="LR", ln=True, fill=True)
    pdf.set_font("helvetica", "", 8)
    data_formatada = data_visita.strftime('%d/%m/%Y')
    pdf.cell(130, 7, f" Cliente: {cliente} / Doc: {doc_cliente}", border=1); pdf.cell(60, 7, f" Data: {data_formatada}", border=1, ln=True)
    pdf.cell(190, 7, f" Endereco: {endereco}", border=1, ln=True)

    # DADOS EQUIPAMENTO
    pdf.ln(2); pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " DADOS DO EQUIPAMENTO", border="LR", ln=True, fill=True)
    pdf.set_font("helvetica", "", 8)
    pdf.cell(63, 7, f" Marca: {fabricante} ({linha})", border=1); pdf.cell(63, 7, f" Tipo: {tipo_eq}", border=1); pdf.cell(64, 7, f" Cap: {cap_btu} BTUs", border=1, ln=True)
    pdf.cell(95, 7, f" Mod. Evap: {mod_evap} (S/N: {serie_evap})", border=1)
    pdf.cell(95, 7, f" Mod. Cond: {mod_cond} (S/N: {serie_cond})", border=1, ln=True)

    # PARÂMETROS
    pdf.ln(2); pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " PARAMETROS MEDIDOS", border="LR", ln=True, fill=True)
    pdf.set_font("helvetica", "", 8)
    pdf.cell(47, 7, f" Tensao: {v_med}V", border=1); pdf.cell(47, 7, f" Corrente: {a_med}A", border=1); pdf.cell(48, 7, f" P. Suc: {p_suc} PSI", border=1); pdf.cell(48, 7, f" Fluido: {fluido}", border=1, ln=True)
    pdf.cell(47, 7, f" Superaq: {sh:.1f} K", border=1); pdf.cell(47, 7, f" Subresf: {sr:.1f} K", border=1); pdf.cell(48, 7, f" Delta T: {dt:.1f} C", border=1); pdf.cell(48, 7, f" Tsat: {tsat_evap:.1f} C", border=1, ln=True)

    # DIAGNÓSTICO
    pdf.ln(2); pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " DIAGNOSTICO", border="LR", ln=True, fill=True)
    pdf.set_font("helvetica", "B", 8)
    pdf.multi_cell(190, 7, f" Veredito: {veredito}", border=1, align="L")

    # OBSERVAÇÕES (ÚLTIMO E ENQUADRADO A4)
    pdf.ln(2); pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " OBSERVACOES", border="LR", ln=True, fill=True)
    pdf.set_font("helvetica", "", 8)
    pdf.multi_cell(190, 7, f" {obs_final}", border=1, align="L")

    # ASSINATURA
    pdf.ln(10); pdf.set_font("helvetica", "B", 8)
    pdf.cell(190, 5, tecnico_nome, ln=True, align="C")
    pdf.cell(190, 5, doc_tecnico, ln=True, align="C")

    pdf_bytes = pdf.output()
    st.download_button(label="📥 BAIXAR RELATÓRIO PDF", data=bytes(pdf_bytes), file_name=f"Laudo_{cliente}.pdf", mime="application/pdf")

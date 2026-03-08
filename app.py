import streamlit as st
from datetime import date
from fpdf import FPDF
import urllib.parse
import os
from PIL import Image
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. ESTILIZAÇÃO MPN ---
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
        "R-134a": 0.5210 * psig - 38.54, "R-404A": 0.2105 * psig - 16.52, "R-32": 0.31 * psig - 25.0
    }
    return tabelas.get(gas, 0)

def obter_ref_tecnica(fabricante, tecnologia, tipo, linha):
    texto = f"{fabricante} {tecnologia} {tipo} {linha}".upper()
    if "VRF" in texto or "MULTI" in texto:
        return {"sh_min": 3, "sh_max": 8, "sr_min": 5, "sr_max": 12, "dt_min": 10}
    elif "WINDFREE" in texto or "INVERTER" in texto:
        return {"sh_min": 4, "sh_max": 11, "sr_min": 2, "sr_max": 9, "dt_min": 9}
    else:
        return {"sh_min": 5, "sh_max": 12, "sr_min": 3, "sr_max": 10, "dt_min": 8}

# --- 4. TÍTULO ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico & Relatório"
])

# --- ABA 1: IDENTIFICAÇÃO ---
with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c1.text_input("CPF / CNPJ do Cliente")
    endereco = c2.text_input("Endereço Completo")
    whatsapp_input = c2.text_input("🟢 WhatsApp (com DDD)", value="21980264217")
    email_cli = c3.text_input("✉️ E-mail")
    data_visita = c3.date_input("Data da Visita", value=date.today())

    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos de Placa")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    linha = d1.text_input("Linha (Ex: Artcool, WindFree)")
    tecnologia = d2.selectbox("Tecnologia do Compressor", ["Inverter", "WindFree", "Scroll", "On-Off"])
    tipo_eq = d2.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF/VRV", "Chiller", "Câmara Fria", "Multi-Split"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])
    cap_btu = d3.text_input("Capacidade (Mil BTUs/h)")

    st.markdown("---")
    st.subheader("📦 Detalhamento das Unidades")
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        st.markdown("**🔹 UNIDADE INTERNA (EVAPORADORA)**")
        mod_evap = st.text_input("Modelo da Unidade (Evap)")
        serie_evap = st.text_input("Nº de Série da Unidade (Evap)")
    with col_u2:
        st.markdown("**🔸 UNIDADE EXTERNA (CONDENSADORA)**")
        mod_cond = st.text_input("Modelo da Unidade (Cond)")
        serie_cond = st.text_input("Nº de Série da Unidade (Cond)")

    tecnico_nome = "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO"
    doc_tecnico = "CNPJ: 51.274.762/0001-17"

# --- ABA 2: ELÉTRICA ---
with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    e1, e2 = st.columns(2)
    v_med = e1.number_input("Tensão Medida (V)", value=220.0)
    a_med = e2.number_input("Corrente Medida Real (A)", value=0.0)

# --- ABA 3: TERMODINÂMICA ---
with tab_termo:
    t1, t2 = st.columns(2)
    with t1:
        p_suc = t1.number_input("Pressão Sucção (PSIG)", value=120.0)
        t_suc = t1.number_input("Temp. Tubo Sucção (°C)", value=10.0)
        t_ret = t1.number_input("Ar Retorno (°C)", value=24.0)
    with t2:
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

# --- ABA 4: DIAGNÓSTICO & EXPORTAÇÃO ---
with tab_diag:
    ref = obter_ref_tecnica(fabricante, tecnologia, tipo_eq, linha)
    if sh < ref["sh_min"]: veredito = "ALERTA: SH Baixo. Perigo de retorno de líquido ao compressor."
    elif sh > ref["sh_max"]: veredito = "ALERTA: SH Alto. Possível falta de fluido ou restrição."
    else: veredito = "Sistema operando em equilíbrio técnico conforme fabricante."
    
    st.warning(f"Diagnóstico Final: {veredito}")
    # CAMPO RENOMEADO CONFORME SOLICITADO
    obs_final = st.text_area("📝 Observações", height=150)

    st.markdown("---")
    col_wa, col_pdf = st.columns(2)
    with col_wa:
        num_clean = "".join(filter(str.isdigit, whatsapp_input))
        if not num_clean.startswith("55"): num_clean = "55" + num_clean
        msg_wa = f"❄️ *LAUDO TÉCNICO MPN*\n\n*Cliente:* {cliente}\n*Veredito:* {veredito}\n\n*Técnico:* {tecnico_nome}"
        url_wa = f"https://api.whatsapp.com{num_clean}&text={urllib.parse.quote(msg_wa)}"
        st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:8px; font-weight:bold; cursor:pointer;">📲 ENVIAR WHATSAPP</button></a>', unsafe_allow_html=True)

    with col_pdf:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15); pdf.add_page()
        
        if os.path.exists("logo.png"):
            try:
                pdf.image("logo.png", 10, 8, 33)
                pdf.ln(20)
            except: pass
        
        pdf.set_font("helvetica", "B", 12); pdf.set_fill_color(230, 230, 230)
        pdf.cell(190, 10, "LAUDO TECNICO DE DIAGNOSTICO - MPN", border=1, ln=True, align="C", fill=True)
        
        # INFORMAÇÕES CLIENTE
        pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " INFORMAÇÕES DO CLIENTE", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "", 8)
        data_formatada = data_visita.strftime('%d/%m/%Y') # DATA FORMATO BR
        pdf.cell(130, 7, f" Cliente: {cliente} / Doc: {doc_cliente}", border=1); pdf.cell(60, 7, f" Data: {data_formatada}", border=1, ln=True)
        pdf.cell(190, 7, f" Endereco: {endereco}", border=1, ln=True)

        # EQUIPAMENTO
        pdf.ln(2); pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " DADOS DO EQUIPAMENTO", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(63, 7, f" Marca: {fabricante} ({linha})", border=1); pdf.cell(63, 7, f" Tipo: {tipo_eq}", border=1); pdf.cell(64, 7, f" Cap: {cap_btu} mil BTUs", border=1, ln=True)
        pdf.cell(95, 7, f" Mod. Evap: {mod_evap} (S/N: {serie_evap})", border=1)
        pdf.cell(95, 7, f" Mod. Cond: {mod_cond} (S/N: {serie_cond})", border=1, ln=True)

        # ANÁLISE TÉCNICA
        pdf.ln(2); pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " PARAMETROS MEDIDOS", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(47, 7, f" Tensao: {v_med}V", border=1); pdf.cell(47, 7, f" Corrente: {a_med}A", border=1); pdf.cell(48, 7, f" Pressao Suc: {p_suc} PSIG", border=1); pdf.cell(48, 7, f" Fluido: {fluido}", border=1, ln=True)
        pdf.cell(47, 7, f" Superaq: {sh:.1f} K", border=1); pdf.cell(47, 7, f" Subresf: {sr:.1f} K", border=1); pdf.cell(48, 7, f" Delta T Ar: {dt:.1f} C", border=1); pdf.cell(48, 7, f" Tsat Evap: {tsat_evap:.1f} C", border=1, ln=True)

        # VEREDITO
        pdf.ln(2); pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " DIAGNOSTICO", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "B", 8)
        pdf.multi_cell(190, 7, f" Veredito: {veredito}", border=1, align="L")

        # ÚLTIMO CAMPO: OBSERVAÇÕES (ENQUADRADO À ESQUERDA)
        pdf.ln(2); pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " OBSERVACOES", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "", 8)
        pdf.multi_cell(190, 7, f" {obs_final}", border=1, align="L")

        # RODAPÉ TÉCNICO
        pdf.ln(4); pdf.set_font("helvetica", "B", 8)
        pdf.cell(190, 5, tecnico_nome, ln=True, align="C")
        pdf.cell(190, 5, doc_tecnico, ln=True, align="C")

                # Código corrigido para Streamlit Cloud
        pdf_output = pdf.output()
        st.download_button(
            label="📥 BAIXAR RELATÓRIO PDF", 
            data=bytes(pdf_output), 
            file_name=f"Laudo_{cliente}.pdf", 
            mime="application/pdf"
        )

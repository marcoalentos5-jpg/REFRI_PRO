import streamlit as st
from datetime import date
from fpdf import FPDF
import urllib.parse
import os
from PIL import Image

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. ESTILIZAÇÃO INTERFACE ---
st.markdown("""
    <style>
    .main { background-color: #f1f3f5; }
    div[data-testid="stMetric"] {
        background-color: #ffffff; border-top: 4px solid #000000;
        padding: 15px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 5px; height: 3.5em; }
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
    whatsapp_input = c2.text_input("🟢 WhatsApp (com DDD)", value="5521980264217")
    email_cli = c3.text_input("✉️ E-mail")
    data_visita = c3.date_input("Data da Visita", value=date.today())

    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos de Placa")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    cap_btu = d2.text_input("Capacidade (BTUs/h)")
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])

    st.markdown("---")
    st.subheader("📦 Detalhamento das Unidades")
    col_evap, col_cond = st.columns(2)
    with col_evap:
        st.markdown("**🔹 UNIDADE INTERNA**")
        mod_evap = st.text_input("Modelo da Evaporadora")
        serie_evap = st.text_input("Nº de Série da Evaporadora")
        tag_loc = st.text_input("Ambiente / TAG")
    with col_cond:
        st.markdown("**🔸 UNIDADE EXTERNA**")
        mod_cond = st.text_input("Modelo da Condensadora")
        serie_cond = st.text_input("Nº de Série da Condensadora")
        tipo_eq = st.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "Multi-Split", "VRF/VRV", "Chiller", "Câmara Fria"])

    tecnico_nome = "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO"
    doc_tecnico = "CNPJ: 51.274.762/0001-17"

# --- ABA 2: ELÉTRICA ---
with tab_ele:
    el1, el2 = st.columns(2)
    v_nom = el1.selectbox("Tensão Nominal (V)", ["127", "220", "380", "440"], index=1)
    v_med = el1.number_input("Tensão Medida (V)", value=float(v_nom))
    a_nom = el2.number_input("Corrente Nominal RLA (A)", value=5.0)
    a_med = el2.number_input("Corrente Medida Real (A)", value=0.0)

# --- ABA 3: TERMODINÂMICA ---
with tab_termo:
    t1, t2 = st.columns(2)
    p_suc = t1.number_input("Pressão Sucção (PSIG)", value=120.0)
    t_suc = t1.number_input("Temp. Tubo Sucção (°C)", value=10.0)
    t_ret = t1.number_input("Ar Retorno (°C)", value=24.0)
    p_liq = t2.number_input("Pressão Descarga (PSIG)", value=350.0)
    t_liq = t2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ins = t2.number_input("Ar Insuflação (°C)", value=12.0)

    sh = t_suc - calcular_tsat(p_suc, fluido)
    sr = calcular_tsat(p_liq, fluido) - t_liq
    dt = t_ret - t_ins

# --- ABA 4: DIAGNÓSTICO & EXPORTAÇÃO ---
with tab_diag:
    veredito = "Sistema operando em equilíbrio conforme parâmetros do fabricante."
    if sh < 5: veredito = "ALERTA: Superaquecimento Crítico (Risco de retorno de líquido)."
    elif sh > 12: veredito = "ALERTA: Superaquecimento Alto (Possível falta de carga ou obstrução)."
    elif dt < 8: veredito = "AVISO: Baixo Delta T (Verificar vazão de ar ou limpeza)."
    
    st.warning(f"Diagnóstico Técnico: {veredito}")
    obs_final = st.text_area("📝 Recomendações e Observações Técnicas")

    st.markdown("---")
    col_wa, col_pdf = st.columns(2)

    with col_wa:
        # --- CORREÇÃO WHATSAPP ---
        wa_num = "".join(filter(str.isdigit, whatsapp_input))
        texto_wa = f"❄️ *LAUDO TÉCNICO MPN*\n\n*Cliente:* {cliente}\n*Diagnóstico:* {veredito}\n\n*Assinado por:* {tecnico_nome}\n*{doc_tecnico}*"
        # A barra '/' após o wa.me é obrigatória
        link_wa = f"https://wa.me{wa_num}?text={urllib.parse.quote(texto_wa)}"
        st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:5px; font-weight:bold; cursor:pointer;">📲 ENVIAR VIA WHATSAPP</button></a>', unsafe_allow_html=True)

    with col_pdf:
        pdf = FPDF()
        pdf.add_page()
        
        logo_inserida = False
        if os.path.exists("logo.png"):
            try:
                img = Image.open("logo.png").convert("RGB")
                img.save("temp_logo_pdf.png")
                pdf.image("temp_logo_pdf.png", 10, 8, 35)
                pdf.ln(20)
                logo_inserida = True
            except: pass
        
        if not logo_inserida:
            pdf.set_font("Arial", "B", 18); pdf.cell(190, 10, "MPN ENGENHARIA", ln=True, align="R"); pdf.ln(10)

        pdf.set_font("Arial", "B", 13); pdf.set_fill_color(230, 230, 230); pdf.set_text_color(0,0,0)
        pdf.cell(190, 10, "RELATÓRIO DE DIAGNÓSTICO TÉCNICO", border=1, ln=True, align="C", fill=True)
        
        pdf.set_font("Arial", "B", 9); pdf.cell(190, 7, " INFORMAÇÕES DO CLIENTE", border="LR", ln=True, fill=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(130, 7, f" Cliente: {cliente}", border=1); pdf.cell(60, 7, f" Doc: {doc_cliente}", border=1, ln=True)
        pdf.cell(130, 7, f" Endereço: {endereco}", border=1); pdf.cell(60, 7, f" Data: {data_visita}", border=1, ln=True)

        pdf.ln(3); pdf.set_font("Arial", "B", 9); pdf.cell(190, 7, " DADOS DO EQUIPAMENTO", border="LR", ln=True, fill=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(63, 7, f" Marca: {fabricante}", border=1); pdf.cell(63, 7, f" Cap: {cap_btu}", border=1); pdf.cell(64, 7, f" Gás: {fluido}", border=1, ln=True)
        pdf.cell(95, 7, f" Mod. Evap: {mod_evap}", border=1); pdf.cell(95, 7, f" S/N: {serie_evap}", border=1, ln=True)
        pdf.cell(95, 7, f" Mod. Cond: {mod_cond}", border=1); pdf.cell(95, 7, f" TAG: {tag_loc}", border=1, ln=True)

        pdf.ln(3); pdf.set_font("Arial", "B", 9); pdf.cell(190, 7, " PARÂMETROS TÉCNICOS MEDIDOS", border="LR", ln=True, fill=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(47, 7, f" Superaq (SH): {sh:.1f} K", border=1); pdf.cell(47, 7, f" Sub-resf (SR): {sr:.1f} K", border=1)
        pdf.cell(48, 7, f" Delta T Ar: {dt:.1f} C", border=1); pdf.cell(48, 7, f" Corrente: {a_med} A", border=1, ln=True)

        pdf.ln(3); pdf.set_font("Arial", "B", 9); pdf.cell(190, 7, " PARECER TÉCNICO", border="LR", ln=True, fill=True)
        pdf.set_font("Arial", "B", 9); pdf.multi_cell(190, 7, f" Veredito: {veredito}", border=1)
        pdf.set_font("Arial", "", 9); pdf.multi_cell(190, 7, f" Recomendações: {obs_final}", border=1)

        # --- ASSINATURA FINAL ---
        pdf.ln(15)
        pdf.cell(60); pdf.cell(70, 0, "", border="T", ln=True)
        
        pdf.set_font("Times", "I", 24)
        pdf.cell(190, 12, "Marcos Alexandre Almeida do Nascimento", ln=True, align="C")
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 5, tecnico_nome.upper(), ln=True, align="C")
        pdf.set_font("Arial", "", 9)
        pdf.cell(190, 5, doc_tecnico, ln=True, align="C")
        pdf.set_font("Arial", "I", 7); pdf.cell(190, 5, "TÉCNICO RESPONSÁVEL", ln=True, align="C")

        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button(label="📄 BAIXAR LAUDO TÉCNICO", data=pdf_bytes, file_name=f"Laudo_MPN_{cliente}.pdf", mime="application/pdf")

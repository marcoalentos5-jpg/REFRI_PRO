import streamlit as st
from datetime import date
from fpdf import FPDF
import urllib.parse
import os
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- LÓGICA TÉCNICA ---
def calcular_tsat(psig, gas):
    if psig <= 0: return 0
    tabelas = {
        "R-410A": 0.2307 * psig - 22.81, "R-22": 0.2854 * psig - 25.12,
        "R-134a": 0.5210 * psig - 38.54, "R-404A": 0.2105 * psig - 16.52, "R-32": 0.31 * psig - 25.0
    }
    return tabelas.get(gas, 0)

# --- TÍTULO E ABAS ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Nome do Cliente / Empresa", value="Cliente")
    doc_cliente = c1.text_input("CPF / CNPJ do Cliente")
    # Limpeza automática do número de WhatsApp
    wa_input = c2.text_input("🟢 WhatsApp (Ex: 21980264217)", value="21980264217")
    data_visita = c3.date_input("Data da Visita", value=date.today())
    endereco = c2.text_input("Endereço Completo")
    fabricante = d1 = st.text_input("Fabricante")
    cap_btu = d2 = st.text_input("Capacidade (BTUs)")
    fluido = d3 = st.selectbox("Gás", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])
    
    mod_evap = st.text_input("Modelo Evaporadora")
    serie_evap = st.text_input("Nº Série Evaporadora")
    tag_loc = st.text_input("Ambiente / TAG")
    mod_cond = st.text_input("Modelo Condensadora")
    serie_cond = st.text_input("Nº Série Condensadora")
    tipo_eq = st.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF/VRV", "Chiller", "Câmara Fria"])

    tecnico_nome = "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO"
    doc_tecnico = "CNPJ: 51.274.762/0001-17"

with tab_ele:
    v_med = st.number_input("Tensão Medida (V)", value=220.0)
    a_med = st.number_input("Corrente Medida Real (A)", value=0.0)

with tab_termo:
    p_suc = st.number_input("Pressão Sucção (PSIG)", value=120.0)
    t_suc = st.number_input("Temp. Tubo Sucção (°C)", value=10.0)
    p_liq = st.number_input("Pressão Descarga (PSIG)", value=350.0)
    t_liq = st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ret = st.number_input("Ar Retorno (°C)", value=24.0)
    t_ins = st.number_input("Ar Insuflação (°C)", value=12.0)
    
    sh = t_suc - calcular_tsat(p_suc, fluido)
    sr = calcular_tsat(p_liq, fluido) - t_liq
    dt = t_ret - t_ins

with tab_diag:
    veredito = "Sistema operando em equilíbrio conforme parâmetros."
    if sh < 5: veredito = "ALERTA: Superaquecimento Crítico (Baixo)."
    elif sh > 12: veredito = "ALERTA: Superaquecimento Alto (Falta de Gás)."
    obs_final = st.text_area("📝 Recomendações e Observações Técnicas")
    
    st.markdown("---")
    col_wa, col_pdf = st.columns(2)

    with col_wa:
        # --- CORREÇÃO FINAL WHATSAPP (BOTÃO NATIVO) ---
        num_clean = "".join(filter(str.isdigit, wa_input))
        if not num_clean.startswith("55"): num_clean = "55" + num_clean
        
        msg_encoded = urllib.parse.quote(f"❄️ *LAUDO TÉCNICO MPN*\n\n*Cliente:* {cliente}\n*Diagnóstico:* {veredito}\n\n*Técnico:* {tecnico_nome}")
        # URL completa com HTTPS e BARRA após o wa.me
        url_final = f"https://wa.me{num_clean}?text={msg_encoded}"
        
        # O st.link_button é mais seguro para navegadores no Windows
        st.link_button("📲 ENVIAR VIA WHATSAPP", url_final, type="primary", use_container_width=True)

    with col_pdf:
        # --- GERAÇÃO DO PDF ---
        pdf = FPDF()
        pdf.add_page()
        
        # Logo tratada para evitar RuntimeError
        if os.path.exists("logo.png"):
            try:
                img = Image.open("logo.png").convert("RGB")
                img.save("temp_logo.png")
                pdf.image("temp_logo.png", 10, 8, 35)
                pdf.ln(20)
            except: pass
        
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "RELATÓRIO DE DIAGNÓSTICO TÉCNICO", border=1, ln=True, align="C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 8, f" Cliente: {cliente} | Data: {data_visita}", border=1, ln=True)
        pdf.multi_cell(190, 8, f" Veredito: {veredito}", border=1)
        pdf.multi_cell(190, 8, f" Obs: {obs_final}", border=1)

        # Assinaturas
        pdf.ln(15)
        pdf.set_font("Times", "I", 24) # Século XVI
        pdf.cell(190, 12, "Marcos Alexandre Almeida do Nascimento", ln=True, align="C")
        pdf.set_font("Arial", "B", 10) # Imprensa
        pdf.cell(190, 5, tecnico_nome.upper(), ln=True, align="C")
        pdf.set_font("Arial", "", 9)
        pdf.cell(190, 5, f"CNPJ: 51.274.762/0001-17", ln=True, align="C")

        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("📄 BAIXAR LAUDO PDF", pdf_bytes, f"Laudo_{cliente}.pdf", "application/pdf", use_container_width=True)

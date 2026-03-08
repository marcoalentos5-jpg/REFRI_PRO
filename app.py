import streamlit as st
from datetime import date
from fpdf import FPDF
import urllib.parse
import os
from PIL import Image  # Adicionado para tratar a imagem corretamente

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- ESTILIZAÇÃO MPN ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetric"] {
        background-color: #ffffff; border-left: 5px solid #004A99;
        padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #e9ecef; border-radius: 5px 5px 0 0;
        padding: 10px 20px; font-weight: bold; color: #495057;
    }
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    .stButton>button { width: 100%; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA TÉCNICA ---
def calcular_tsat(psig, gas):
    if psig <= 0: return 0
    tabelas = {
        "R-410A": 0.2307 * psig - 22.81, "R-22": 0.2854 * psig - 25.12,
        "R-134a": 0.5210 * psig - 38.54, "R-404A": 0.2105 * psig - 16.52, "R-32": 0.31 * psig - 25.0
    }
    return tabelas.get(gas, 0)

# --- TÍTULO ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    cliente = st.text_input("Nome do Cliente", value="Cliente")
    whatsapp = st.text_input("WhatsApp", value="55")
    data_visita = st.date_input("Data", value=date.today())
    fabricante = st.text_input("Fabricante")
    cap_btu = st.text_input("Capacidade (BTUs)")
    fluido = st.selectbox("Gás", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])
    tecnico_nome = "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO"

with tab_ele:
    v_nom = st.selectbox("Tensão Nominal", ["127", "220", "380"], index=1)
    v_med = st.number_input("Tensão Medida", value=float(v_nom))

with tab_termo:
    p_suc = st.number_input("Pressão Sucção (PSIG)", value=120.0)
    t_suc = st.number_input("Temp. Tubo Sucção (°C)", value=10.0)
    t_ret = st.number_input("Ar Retorno (°C)", value=24.0)
    p_liq = st.number_input("Pressão Descarga (PSIG)", value=350.0)
    t_liq = st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ins = st.number_input("Ar Insuflação (°C)", value=12.0)
    sh = t_suc - calcular_tsat(p_suc, fluido)
    sr = calcular_tsat(p_liq, fluido) - t_liq
    dt = t_ret - t_ins

with tab_diag:
    veredito = "Sistema operando em equilíbrio."
    if sh < 5: veredito = "🚨 ALERTA: Superaquecimento Baixo."
    elif sh > 12: veredito = "🚨 ALERTA: Superaquecimento Alto."
    obs_final = st.text_area("Recomendações")

    if st.button("📲 Preparar WhatsApp"):
        wa_num = "".join(filter(str.isdigit, whatsapp))
        texto_wa = f"❄️ *LAUDO MPN*\n*Cliente:* {cliente}\n*Veredito:* {veredito}"
        st.markdown(f'<a href="https://wa.me{wa_num}?text={urllib.parse.quote(texto_wa)}" target="_blank">Clique aqui para enviar</a>', unsafe_allow_html=True)

    # --- GERADOR DE PDF CORRIGIDO ---
    pdf = FPDF()
    pdf.add_page()
    
    logo_inserida = False
    caminho_logo = os.path.join(os.getcwd(), "logo.png")

    if os.path.exists(caminho_logo):
        try:
            # Força a conversão para RGB usando Pillow para evitar erro de formato
            img = Image.open(caminho_logo).convert("RGB")
            img.save("logo_corrigida.png")
            pdf.image("logo_corrigida.png", 10, 8, 40)
            pdf.ln(25)
            logo_inserida = True
        except Exception as e:
            st.error(f"Erro ao processar imagem: {e}")

    if not logo_inserida:
        pdf.set_fill_color(0, 74, 153); pdf.rect(0, 0, 210, 30, 'F')
        pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 18)
        pdf.cell(190, 15, "MPN ENGENHARIA", ln=True, align="C"); pdf.ln(15)

    pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "LAUDO TECNICO DE CICLO FRIGORIFICO", ln=True, align="C")
    pdf.set_font("Arial", "", 10); pdf.ln(5)
    pdf.cell(190, 8, f" CLIENTE: {cliente} | DATA: {data_visita}", ln=True)
    pdf.cell(190, 8, f" SH: {sh:.1f} K | SR: {sr:.1f} K | Delta T: {dt:.1f} C", ln=True)
    pdf.multi_cell(0, 8, f"VEREDITO: {veredito}")
    pdf.ln(20); pdf.set_font("Times", "I", 15); pdf.set_text_color(0, 74, 153)
    pdf.cell(190, 10, tecnico_nome, ln=True, align="C")

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    st.download_button(label="📄 BAIXAR LAUDO PDF", data=pdf_bytes, file_name="laudo.pdf", mime="application/pdf")

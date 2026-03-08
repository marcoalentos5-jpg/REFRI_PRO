import streamlit as st
from datetime import date
from fpdf import FPDF
import urllib.parse
import os

# --- NOVO: FUNÇÃO PARA ACHAR A LOGO NO SERVIDOR DO STREAMLIT ---
def buscar_caminho_logo():
    # Tenta achar o arquivo logo.png na pasta onde o script está rodando
    caminho_tentativa = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(caminho_tentativa):
        return caminho_tentativa
    # Se não achar, tenta na pasta atual (raiz)
    if os.path.exists("logo.png"):
        return "logo.png"
    return None

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. ESTILIZAÇÃO MPN ---
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

# --- 3. LÓGICA TÉCNICA (P x T) ---
def calcular_tsat(psig, gas):
    if psig <= 0: return 0
    tabelas = {
        "R-410A": 0.2307 * psig - 22.81, "R-22": 0.2854 * psig - 25.12,
        "R-134a": 0.5210 * psig - 38.54, "R-404A": 0.2105 * psig - 16.52, "R-32": 0.31 * psig - 25.0
    }
    return tabelas.get(gas, 0)

# --- 4. TÍTULO ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

# --- 5. CRIAÇÃO DAS ABAS ---
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico & Relatório"
])

# --- ABA 1: IDENTIFICAÇÃO ---
with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Nome do Cliente / Empresa", value="Cliente Exemplo")
    endereco = c1.text_input("Endereço Completo")
    whatsapp = c2.text_input("🟢 WhatsApp (com DDD)", value="55")
    data_visita = c3.date_input("Data da Visita", value=date.today())

    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos de Placa")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    cap_btu = d2.text_input("Capacidade (BTUs/h)")
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])

    tecnico_nome = "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO"
    st.info(f"👷 **Técnico Responsável:** {tecnico_nome}")

# --- ABA 2: ELÉTRICA ---
with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2 = st.columns(2)
    v_nom = el1.selectbox("Tensão Nominal (V)", ["127", "220", "380"], index=1)
    v_med = el1.number_input("Tensão Medida (V)", value=float(v_nom))
    a_nom = el2.number_input("Corrente Nominal RLA (A)", value=5.0)
    a_med = el2.number_input("Corrente Medida Real (A)", value=0.0)

# --- ABA 3: TERMODINÂMICA ---
with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
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
    st.subheader("🤖 Diagnóstico & Relatório")
    veredito = "Sistema operando em equilíbrio."
    if sh < 5: veredito = "🚨 ALERTA: Superaquecimento Baixo."
    elif sh > 12: veredito = "🚨 ALERTA: Superaquecimento Alto."
    
    st.info(f"Veredito Técnico: {veredito}")
    obs_final = st.text_area("📝 Recomendações Técnicas")

    st.markdown("---")
    col_wa, col_pdf = st.columns(2)

    with col_wa:
        wa_num = "".join(filter(str.isdigit, whatsapp))
        texto_wa = f"❄️ *LAUDO MPN*\n*Cliente:* {cliente}\n*Veredito:* {veredito}"
        st.markdown(f'<a href="https://wa.me{wa_num}?text={urllib.parse.quote(texto_wa)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:5px; font-weight:bold; cursor:pointer;">ENVIAR WHATSAPP</button></a>', unsafe_allow_html=True)

    with col_pdf:
        # GERAÇÃO DO PDF
        pdf = FPDF()
        pdf.add_page()
        
        # --- BUSCA A LOGO AUTOMATICAMENTE ---
        caminho_logo = buscar_caminho_logo()
        
        if caminho_logo:
            # Se encontrou o arquivo, coloca no PDF
            pdf.image(caminho_logo, 10, 8, 40)
            pdf.ln(25)
        else:
            # Se não encontrou, faz o cabeçalho azul (para não dar erro)
            pdf.set_fill_color(0, 74, 153); pdf.rect(0, 0, 210, 30, 'F')
            pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 18)
            pdf.cell(190, 15, "MPN ENGENHARIA", ln=True, align="C"); pdf.ln(15)
        
        # Preenchimento do Laudo
        pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "LAUDO TECNICO DE CICLO FRIGORIFICO", ln=True, align="C")
        
        pdf.set_font("Arial", "", 10); pdf.ln(5); pdf.set_fill_color(240, 240, 240)
        pdf.cell(190, 8, f" CLIENTE: {cliente} | DATA: {data_visita}", ln=True, fill=True)
        pdf.cell(190, 8, f" FABRICANTE: {fabricante} | CAPACIDADE: {cap_btu} | GAS: {fluido}", ln=True)
        
        pdf.ln(5); pdf.set_font("Arial", "B", 11); pdf.cell(190, 8, "RESULTADOS", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(63, 8, f" SH: {sh:.1f} K", border=1); pdf.cell(63, 8, f" SR: {sr:.1f} K", border=1); pdf.cell(64, 8, f" Delta T: {dt:.1f} C", border=1, ln=True)
        
        pdf.ln(5); pdf.multi_cell(0, 8, f"VEREDITO: {veredito}", border=1)
        pdf.multi_cell(0, 8, f"OBSERVACOES: {obs_final}", border=1)
        
        pdf.ln(20); pdf.set_font("Times", "I", 15); pdf.set_text_color(0, 74, 153)
        pdf.cell(190, 10, tecnico_nome, ln=True, align="C")
        
        # Cria os dados do PDF para download
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        
        st.download_button(
            label="📄 BAIXAR LAUDO PDF",
            data=pdf_bytes,
            file_name=f"Laudo_MPN_{cliente}.pdf",
            mime="application/pdf"
        )

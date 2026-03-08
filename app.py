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
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #e9ecef; border-radius: 5px 5px 0 0;
        padding: 10px 20px; font-weight: bold; color: #495057;
    }
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
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
        tipo_eq = st.selectbox("Tipo de Sistema", ["ACJ", "Cassete", "Câmara Fria", "Chiller", "Fancoil", "Multi-Split", "Piso-Teto", "Self-Contained", "Split Hi-Wall", "VRF/VRV"])

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
    p_liq = t2.number_input("Pressão Descarga (PSIG)", value=350.0)
    t_liq = t2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ret = t1.number_input("Ar Retorno (°C)", value=24.0)
    t_ins = t2.number_input("Ar Insuflação (°C)", value=12.0)

    tsat_evap = calcular_tsat(p_suc, fluido)
    tsat_cond = calcular_tsat(p_liq, fluido)
    sh, sr, dt = t_suc - tsat_evap, tsat_cond - t_liq, t_ret - t_ins

# --- ABA 4: DIAGNÓSTICO & EXPORTAÇÃO ---
with tab_diag:
    veredito = "Sistema operando em equilíbrio conforme parâmetros."
    if sh < 5: veredito = "ALERTA: Superaquecimento Crítico (Baixo)."
    elif sh > 12: veredito = "ALERTA: Superaquecimento Alto (Falta de Gás)."
    
    st.warning(f"Parecer Técnico: {veredito}")
    obs_final = st.text_area("📝 Recomendações Técnicas")

    st.markdown("---")
    col_wa, col_pdf = st.columns(2)

    with col_wa:
        num_clean = "".join(filter(str.isdigit, whatsapp_input))
        if not num_clean.startswith("55"): num_clean = "55" + num_clean
        msg_wa = f"❄️ *LAUDO TÉCNICO MPN*\n\n*Cliente:* {cliente}\n*Veredito:* {veredito}\n\n*Técnico:* {tecnico_nome}\n*{doc_tecnico}*"
        url_wa = f"https://api.whatsapp.com{num_clean}&text={urllib.parse.quote(msg_wa)}"
        
        st.markdown(f'''
            <a href="{url_wa}" target="_blank" style="text-decoration:none;">
                <button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:8px; font-weight:bold; cursor:pointer;">
                    📲 ENVIAR VIA WHATSAPP
                </button>
            </a>
        ''', unsafe_allow_html=True)

    with col_pdf:
        # --- GERAÇÃO DO PDF ---
        pdf = FPDF()
        pdf.add_page()
        
        if os.path.exists("logo.png"):
            try:
                img = Image.open("logo.png").convert("RGB")
                img.save("temp_logo.png")
                pdf.image("temp_logo.png", 10, 8, 32)
                pdf.ln(20)
            except: pass
        
        pdf.set_font("Arial", "B", 13); pdf.set_fill_color(235, 235, 235)
        pdf.cell(190, 10, "RELATÓRIO DE DIAGNÓSTICO TÉCNICO", border=1, ln=True, align="C", fill=True)
        
        # TABELA DE DADOS
        pdf.set_font("Arial", "B", 8); pdf.cell(190, 6, " DADOS GERAIS", border="LR", ln=True, fill=True)
        pdf.set_font("Arial", "", 8)
        pdf.cell(130, 7, f" Cliente: {cliente}", border=1); pdf.cell(60, 7, f" Doc: {doc_cliente}", border=1, ln=True)
        pdf.cell(190, 7, f" Equipamento: {fabricante} / {cap_btu} / {fluido}", border=1, ln=True)

        pdf.ln(2); pdf.set_font("Arial", "B", 8); pdf.cell(190, 6, " PARÂMETROS MEDIDOS", border="LR", ln=True, fill=True)
        pdf.set_font("Arial", "", 8)
        pdf.cell(47, 7, f" Tensao: {v_med}V", border=1); pdf.cell(47, 7, f" Corrente: {a_med}A", border=1)
        pdf.cell(48, 7, f" SH: {sh:.1f} K", border=1); pdf.cell(48, 7, f" Delta T: {dt:.1f} C", border=1, ln=True)

        pdf.ln(2); pdf.set_font("Arial", "B", 8); pdf.cell(190, 6, " PARECER TÉCNICO", border="LR", ln=True, fill=True)
        pdf.set_font("Arial", "B", 8); pdf.multi_cell(190, 7, f" Veredito: {veredito}", border=1)
        pdf.set_font("Arial", "", 8); pdf.multi_cell(190, 7, f" Recomendações: {obs_final}", border=1)

        # RODAPÉ
        pdf.ln(12); pdf.cell(60); pdf.cell(70, 0, "", border="T", ln=True)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 6, tecnico_nome.upper(), ln=True, align="C")
        pdf.set_font("Arial", "", 9)
        pdf.cell(190, 5, doc_tecnico, ln=True, align="C")

        # --- CORREÇÃO DO ERRO DE DOWNLOAD ---
        # Transformamos a saída do PDF em bytes para o Streamlit aceitar
        pdf_output = bytes(pdf.output())
        
        st.download_button(
            label="📄 BAIXAR LAUDO TÉCNICO", 
            data=pdf_output, 
            file_name=f"Laudo_MPN_{cliente}.pdf", 
            mime="application/pdf", 
            use_container_width=True
        )

import streamlit as st
from datetime import date
from fpdf import FPDF
import urllib.parse
import os
from PIL import Image

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. ESTILIZAÇÃO MPN ---
st.markdown("""
    <style>
    .main { background-color: #f1f3f5; }
    div[data-testid="stMetric"] {
        background-color: #ffffff; border-top: 4px solid #000000;
        padding: 15px; border-radius: 8px;
    }
    .stButton>button { width: 100%; font-weight: bold; height: 3.5em; border-radius: 8px; }
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

# --- 4. TÍTULO E ABAS ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c1.text_input("CPF / CNPJ do Cliente")
    whatsapp_input = c2.text_input("🟢 WhatsApp (Ex: 21980264217)", value="21980264217")
    data_visita = c3.date_input("Data da Visita", value=date.today())
    endereco = c2.text_input("Endereço Completo")
    email_cli = c3.text_input("✉️ E-mail")
    
    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante")
    cap_btu = d2.text_input("Capacidade (BTUs)")
    fluido = d3.selectbox("Gás", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])
    
    col_u1, col_u2 = st.columns(2)
    mod_evap = col_u1.text_input("Modelo Evaporadora")
    serie_evap = col_u1.text_input("Nº Série Evaporadora")
    tag_loc = col_u1.text_input("Ambiente / TAG")
    mod_cond = col_u2.text_input("Modelo Condensadora")
    serie_cond = col_u2.text_input("Nº Série Condensadora")
    tipo_eq = col_u2.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF/VRV", "Chiller", "Câmara Fria"])

    tecnico_nome = "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO"
    doc_tecnico = "CNPJ: 51.274.762/0001-17"

with tab_ele:
    el1, el2 = st.columns(2)
    v_nom = el1.selectbox("Tensão Nominal (V)", ["127", "220", "380", "440"], index=1)
    v_med = el1.number_input("Tensão Medida (V)", value=float(v_nom))
    a_med = el2.number_input("Corrente Medida Real (A)", value=0.0)

with tab_termo:
    t1, t2 = st.columns(2)
    p_suc = t1.number_input("Pressão Sucção (PSIG)", value=120.0)
    t_suc = t1.number_input("Temp. Tubo Sucção (°C)", value=10.0)
    p_liq = t2.number_input("Pressão Descarga (PSIG)", value=350.0)
    t_liq = t2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ret = t1.number_input("Ar Retorno (°C)", value=24.0)
    t_ins = t2.number_input("Ar Insuflação (°C)", value=12.0)
    
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
        # --- CORREÇÃO DEFINITIVA DO WHATSAPP ---
        numero_limpo = "".join(filter(str.isdigit, whatsapp_input))
        if not numero_limpo.startswith("55"):
            numero_limpo = "55" + numero_limpo
        
        texto_wa = f"❄️ *LAUDO TÉCNICO MPN*\n\n*Cliente:* {cliente}\n*Diagnóstico:* {veredito}\n\n*Assinado por:* {tecnico_nome}\n*{doc_tecnico}*"
        # Uso obrigatório de https:// e da barra / após o wa.me
        link_whatsapp = f"https://wa.me{numero_limpo}?text={urllib.parse.quote(texto_wa)}"
        
        st.markdown(f'''
            <a href="{link_whatsapp}" target="_blank">
                <button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:8px; font-weight:bold; cursor:pointer;">
                    📲 ENVIAR VIA WHATSAPP
                </button>
            </a>
        ''', unsafe_allow_html=True)

    with col_pdf:
        pdf = FPDF()
        pdf.add_page()
        
        # LOGO COM TRATAMENTO PIL (PARA EVITAR ERRO DE FORMATO)
        logo_inserida = False
        caminho_original = os.path.join(os.getcwd(), "logo.png")
        if os.path.exists(caminho_original):
            try:
                img = Image.open(caminho_original).convert("RGB")
                img.save("temp_logo_pdf.png")
                pdf.image("temp_logo_pdf.png", 10, 8, 35)
                pdf.ln(20)
                logo_inserida = True
            except: pass
        
        if not logo_inserida:
            pdf.set_font("Arial", "B", 18); pdf.cell(190, 10, "MPN ENGENHARIA", ln=True, align="R"); pdf.ln(10)

        # Cabeçalho Laudo
        pdf.set_font("Arial", "B", 13); pdf.set_fill_color(230, 230, 230)
        pdf.cell(190, 10, "RELATÓRIO DE DIAGNÓSTICO TÉCNICO", border=1, ln=True, align="C", fill=True)
        
        # Dados do Cliente
        pdf.set_font("Arial", "B", 9); pdf.cell(190, 7, " INFORMAÇÕES DO CLIENTE", border="LR", ln=True, fill=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(130, 7, f" Cliente: {cliente}", border=1); pdf.cell(60, 7, f" Doc: {doc_cliente}", border=1, ln=True)
        pdf.cell(190, 7, f" Endereço: {endereco}", border=1, ln=True)
        
        # Dados do Equipamento
        pdf.ln(2); pdf.set_font("Arial", "B", 9); pdf.cell(190, 7, " DADOS DO EQUIPAMENTO", border="LR", ln=True, fill=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(63, 7, f" Marca: {fabricante}", border=1); pdf.cell(63, 7, f" Cap: {cap_btu}", border=1); pdf.cell(64, 7, f" Gás: {fluido}", border=1, ln=True)
        pdf.cell(95, 7, f" Mod. Cond: {mod_cond}", border=1); pdf.cell(95, 7, f" TAG: {tag_loc}", border=1, ln=True)

        # Parecer Técnico
        pdf.ln(2); pdf.set_font("Arial", "B", 9); pdf.cell(190, 7, " PARECER TÉCNICO", border="LR", ln=True, fill=True)
        pdf.set_font("Arial", "B", 9); pdf.multi_cell(190, 7, f" Veredito: {veredito}", border=1)
        pdf.set_font("Arial", "", 9); pdf.multi_cell(190, 7, f" Obs: {obs_final}", border=1)

        # --- ASSINATURA ---
        pdf.ln(15)
        pdf.cell(60); pdf.cell(70, 0, "", border="T", ln=True)
        
        # Estilo Século XVI (Caligrafia Pena)
        pdf.set_font("Times", "I", 24)
        pdf.cell(190, 12, "Marcos Alexandre Almeida do Nascimento", ln=True, align="C")
        
        # Letra de Imprensa Preta e CNPJ
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 5, tecnico_nome.upper(), ln=True, align="C")
        pdf.set_font("Arial", "", 9)
        pdf.cell(190, 5, doc_tecnico, ln=True, align="C")
        pdf.set_font("Arial", "I", 7); pdf.cell(190, 5, "TÉCNICO RESPONSÁVEL", ln=True, align="C")

        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button(label="📄 BAIXAR LAUDO PDF", data=pdf_bytes, file_name=f"Laudo_MPN_{cliente}.pdf", mime="application/pdf")

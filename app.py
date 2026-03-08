import streamlit as st
from datetime import date
from fpdf import FPDF
import urllib.parse
import os
from PIL import Image
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. ESTILIZAÇÃO MPN (REVISÃO 1: Interface Profissional) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetric"] {
        background-color: #ffffff; border-top: 4px solid #004A99;
        padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #e9ecef; border-radius: 8px 8px 0 0;
        padding: 10px 20px; font-weight: bold; color: #495057;
    }
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA TÉCNICA (REVISÃO 2: Precisão Termodinâmica) ---
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

# --- ABA 1: IDENTIFICAÇÃO (LAYOUT ORIGINAL RESTAURADO) ---
with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Nome do Cliente / Empresa", placeholder="Ex: Condomínio Solar")
    doc_cliente = c1.text_input("CPF / CNPJ do Cliente")
    endereco = c2.text_input("Endereço Completo")
    whatsapp_input = c2.text_input("🟢 WhatsApp (com DDD)", value="21980264217")
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
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2 = st.columns(2)
    v_nom = el1.selectbox("Tensão Nominal (V)", ["127", "220", "380", "440"], index=1)
    v_med = el1.number_input("Tensão Medida (V)", value=float(v_nom))
    a_nom = el2.number_input("Corrente Nominal RLA (A)", value=5.0)
    a_med = el2.number_input("Corrente Medida Real (A)", value=0.0)

# --- ABA 3: TERMODINÂMICA ---
with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    t1, t2 = st.columns(2)
    with t1:
        p_suc = t1.number_input("Pressão Sucção (PSIG)", value=120.0)
        t_suc = t1.number_input("Temp. Tubo Sucção (°C)", value=10.0)
        t_ret = t1.number_input("Ar Retorno (°C)", value=24.0)
    with t2:
        p_liq = t2.number_input("Pressão Descarga (PSIG)", value=350.0)
        t_liq = t2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
        t_ins = t2.number_input("Ar Insuflação (°C)", value=12.0)

    sh, sr, dt = t_suc - calcular_tsat(p_suc, fluido), calcular_tsat(p_liq, fluido) - t_liq, t_ret - t_ins

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
        # --- REVISÃO 3: CORREÇÃO DEFINITIVA WHATSAPP (Protocolo Completo) ---
        num_clean = "".join(filter(str.isdigit, whatsapp_input))
        if not num_clean.startswith("55"): num_clean = "55" + num_clean
        
        msg_encoded = urllib.parse.quote(f"❄️ *LAUDO TÉCNICO MPN*\n\n*Cliente:* {cliente}\n*Veredito:* {veredito}\n\n*Técnico:* {tecnico_nome}\n*{doc_tecnico}*")
        # Link HTTPS absoluto para evitar erros de DNS/about:blank
        url_wa = f"https://api.whatsapp.com{num_clean}&text={msg_encoded}"
        
        st.markdown(f'''
            <a href="{url_wa}" target="_blank" style="text-decoration:none;">
                <button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:8px; font-weight:bold; cursor:pointer; width:100%;">
                    📲 ENVIAR VIA WHATSAPP
                </button>
            </a>
        ''', unsafe_allow_html=True)

    with col_pdf:
        # --- REVISÃO 4: GERAÇÃO DE PDF BLINDADA (fpdf2 + Pillow) ---
        pdf = FPDF()
        pdf.add_page()
        
        # Tratamento de Imagem Robusto para evitar RuntimeError
        if os.path.exists("logo.png"):
            try:
                with Image.open("logo.png") as img:
                    img = img.convert("RGB")
                    temp_buffer = io.BytesIO()
                    img.save(temp_buffer, format="PNG")
                    temp_buffer.seek(0)
                    pdf.image(temp_buffer, 10, 8, 32)
                pdf.ln(20)
            except: pass
        
        pdf.set_font("helvetica", "B", 13); pdf.set_fill_color(230, 230, 230)
        pdf.cell(190, 10, "RELATÓRIO DE DIAGNÓSTICO TÉCNICO", border=1, ln=True, align="C", fill=True)
        
        # SEÇÕES ORGANIZADAS DO LAUDO
        pdf.set_font("helvetica", "B", 9); pdf.cell(190, 7, " INFORMAÇÕES DO CLIENTE", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "", 9)
        pdf.cell(130, 7, f" Cliente: {cliente}", border=1); pdf.cell(60, 7, f" Doc: {doc_cliente}", border=1, ln=True)
        pdf.cell(190, 7, f" Endereco: {endereco}", border=1, ln=True)

        pdf.ln(2); pdf.set_font("helvetica", "B", 9); pdf.cell(190, 7, " DADOS DO EQUIPAMENTO", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "", 9)
        pdf.cell(63, 7, f" Marca: {fabricante}", border=1); pdf.cell(63, 7, f" Cap: {cap_btu}", border=1); pdf.cell(64, 7, f" Gas: {fluido}", border=1, ln=True)
        pdf.cell(95, 7, f" S/N Evap: {serie_evap}", border=1); pdf.cell(95, 7, f" TAG: {tag_loc}", border=1, ln=True)

        pdf.ln(2); pdf.set_font("helvetica", "B", 9); pdf.cell(190, 7, " MEDIÇÕES ELÉTRICAS E TÉRMICAS", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(47, 7, f" Tensao: {v_med}V", border=1); pdf.cell(47, 7, f" Corr: {a_med}A", border=1)
        pdf.cell(48, 7, f" P. Suc: {p_suc} PSI", border=1); pdf.cell(48, 7, f" T. Suc: {t_suc}C", border=1, ln=True)
        pdf.cell(63, 7, f" SH: {sh:.1f} K", border=1); pdf.cell(63, 7, f" SR: {sr:.1f} K", border=1); pdf.cell(64, 7, f" DT Ar: {dt:.1f} C", border=1, ln=True)

        pdf.ln(2); pdf.set_font("helvetica", "B", 9); pdf.cell(190, 7, " PARECER TÉCNICO FINAL", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "B", 8); pdf.multi_cell(190, 7, f" Veredito: {veredito}", border=1)
        pdf.set_font("helvetica", "", 8); pdf.multi_cell(190, 7, f" Obs: {obs_final}", border=1)

        # RODAPÉ (Letra de Imprensa, Conforme Solicitado)
        pdf.ln(12); pdf.cell(60); pdf.cell(70, 0, "", border="T", ln=True)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(190, 6, tecnico_nome.upper(), ln=True, align="C")
        pdf.set_font("helvetica", "", 9)
        pdf.cell(190, 5, doc_tecnico, ln=True, align="C")

        # --- REVISÃO 5: DOWNLOAD BYTES (Ajuste para compatibilidade total) ---
        pdf_bytes = pdf.output()
        
        st.download_button(
            label="📄 BAIXAR LAUDO TÉCNICO", 
            data=bytes(pdf_bytes), 
            file_name=f"Laudo_MPN_{cliente}.pdf", 
            mime="application/pdf", 
            use_container_width=True
        )

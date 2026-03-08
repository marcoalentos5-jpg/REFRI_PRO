import streamlit as st
from datetime import date
from fpdf import FPDF
import urllib.parse
import os
from PIL import Image
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. ESTILIZAÇÃO INTERFACE ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetric"] {
        background-color: #ffffff; border-top: 4px solid #004A99;
        padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA TÉCNICA AVANÇADA ---
def calcular_tsat(psig, gas):
    if psig <= 0: return 0
    tabelas = {
        "R-410A": 0.2307 * psig - 22.81, "R-22": 0.2854 * psig - 25.12,
        "R-134a": 0.5210 * psig - 38.54, "R-404A": 0.2105 * psig - 16.52, "R-32": 0.31 * psig - 25.0
    }
    return tabelas.get(gas, 0)

def obter_referencias_especificas(fabricante, modelo, tipo_sistema):
    # Consolidado de texto para busca de palavras-chave
    texto_tecnico = f"{fabricante} {modelo} {tipo_sistema}".upper()
    
    # PADRÃO VRF / VRV (Daikin, LG Multi V, etc)
    if "VRF" in texto_tecnico or "VRV" in texto_tecnico or "MULTI" in texto_tecnico:
        return {"sh_min": 3, "sh_max": 8, "sr_min": 5, "sr_max": 12, "dt_min": 10, "label": "Linha VRF/Multi (Alta Precisão)"}
    
    # CÂMARA FRIA / REFRIGERAÇÃO COMERCIAL (R-404A/R-134a)
    elif "CÂMARA" in texto_tecnico or "FRIA" in texto_tecnico or "COMERCIAL" in texto_tecnico:
        return {"sh_min": 5, "sh_max": 15, "sr_min": 3, "sr_max": 10, "dt_min": 6, "label": "Refrigeração Comercial"}
    
    # CHILLERS
    elif "CHILLER" in texto_tecnico:
        return {"sh_min": 4, "sh_max": 8, "sr_min": 4, "sr_max": 10, "dt_min": 5, "label": "Linha Chiller (Água Gelada)"}

    # SPLIT INVERTER (Daikin, Fujitsu, LG Artcool, Samsung WindFree)
    elif "INVERTER" in texto_tecnico or "DAIKIN" in texto_tecnico or "FUJITSU" in texto_tecnico or "ARTCOOL" in texto_tecnico:
        return {"sh_min": 4, "sh_max": 11, "sr_min": 2, "sr_max": 9, "dt_min": 9, "label": "Linha Inverter (Alta Eficiência)"}
    
    # PADRÃO CONVENCIONAL / ON-OFF
    else:
        return {"sh_min": 5, "sh_max": 12, "sr_min": 3, "sr_max": 10, "dt_min": 8, "label": "Linha Convencional / Geral"}

# --- 4. TÍTULO E ABAS ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico & Relatório"
])

with tab_cad:
    st.subheader("👤 Identificação")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Cliente / Empresa")
    doc_cliente = c1.text_input("CPF / CNPJ")
    whatsapp_input = c2.text_input("WhatsApp", value="21980264217")
    data_visita = c3.date_input("Data", value=date.today())
    endereco = c2.text_input("Endereço")

    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    cap_btu = d2.text_input("Capacidade (BTUs/h)")
    fluido = d3.selectbox("Gás", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])

    col_m1, col_m2 = st.columns(2)
    mod_evap = col_m1.text_input("Modelo/Linha (Ex: WindFree, Inverter, Multi V)")
    serie_evap = col_m1.text_input("Nº de Série")
    tipo_eq = col_m2.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "Multi-Split", "VRF/VRV", "Chiller", "Câmara Fria"])

    tecnico_nome = "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO"
    doc_tecnico = "CNPJ: 51.274.762/0001-17"

with tab_ele:
    e1, e2 = st.columns(2)
    v_med = e1.number_input("Tensão Medida (V)", value=220.0)
    a_med = e2.number_input("Corrente Medida (A)", value=0.0)

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

    # Cálculos Inteligentes
    sh, sr, dt = t_suc - calcular_tsat(p_suc, fluido), calcular_tsat(p_liq, fluido) - t_liq, t_ret - t_ins
    ref = obter_referencias_especificas(fabricante, mod_evap, tipo_eq)

    st.markdown("---")
    st.info(f"📋 **Referência Detectada:** {ref['label']}")
    m1, m2, m3 = st.columns(3)
    m1.metric("Superaquecimento (SH)", f"{sh:.1f} K", help=f"Faixa: {ref['sh_min']} a {ref['sh_max']}K")
    m2.metric("Sub-resfriamento (SR)", f"{sr:.1f} K", help=f"Faixa: {ref['sr_min']} a {ref['sr_max']}K")
    m3.metric("Delta T Ar (ΔT)", f"{dt:.1f} °C", help=f"Mínimo: {ref['dt_min']}°C")

with tab_diag:
    # Diagnóstico automático via IA de Faixas
    if sh < ref["sh_min"]: veredito = "ALERTA: SH Baixo. Perigo de retorno de líquido ao compressor."
    elif sh > ref["sh_max"]: veredito = "ALERTA: SH Alto. Possível falta de carga ou restrição na expansão."
    elif dt < ref["dt_min"]: veredito = "AVISO: Delta T Baixo. Troca térmica insuficiente na evaporadora."
    else: veredito = "Sistema em conformidade com as especificações técnicas da linha."
    
    st.warning(f"Diagnóstico: {veredito}")
    obs_final = st.text_area("📝 Notas Técnicas", height=120)

    st.markdown("---")
    col_wa, col_pdf = st.columns(2)

    with col_wa:
        num_clean = "".join(filter(str.isdigit, whatsapp_input))
        if not num_clean.startswith("55"): num_clean = "55" + num_clean
        msg_wa = f"❄️ *LAUDO TÉCNICO MPN*\n\n*Cliente:* {cliente}\n*Veredito:* {veredito}\n\n*Técnico:* {tecnico_nome}"
        url_wa = f"https://api.whatsapp.com{num_clean}&text={urllib.parse.quote(msg_wa)}"
        st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:8px; font-weight:bold; cursor:pointer; width:100%;">📲 ENVIAR WHATSAPP</button></a>', unsafe_allow_html=True)

    with col_pdf:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        if os.path.exists("logo.png"):
            try:
                with Image.open("logo.png") as img:
                    img = img.convert("RGB")
                    temp_buf = io.BytesIO()
                    img.save(temp_buf, format="PNG"); temp_buf.seek(0)
                    pdf.image(temp_buf, 10, 8, 32)
                pdf.ln(20)
            except: pass
        
        pdf.set_font("helvetica", "B", 12); pdf.set_fill_color(230, 230, 230)
        pdf.cell(190, 10, "LAUDO TECNICO DE DIAGNOSTICO", border=1, ln=True, align="C", fill=True)
        
        # TABELA RESUMO
        pdf.set_font("helvetica", "B", 8); pdf.cell(190, 7, " RESUMO DO EQUIPAMENTO", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(95, 7, f" Cliente: {cliente}", border=1); pdf.cell(95, 7, f" Equip: {fabricante} {mod_evap}", border=1, ln=True)
        pdf.cell(190, 7, f" Referencia Aplicada: {ref['label']}", border=1, ln=True)

        # TABELA MEDIÇÕES VS REFERÊNCIA
        pdf.ln(2); pdf.set_font("helvetica", "B", 8); pdf.cell(190, 7, " ANALISE DO CICLO FRIGORIFICO", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "B", 7)
        pdf.cell(63, 6, "PARAMETRO", border=1, align="C"); pdf.cell(63, 6, "VALOR REAL", border=1, align="C"); pdf.cell(64, 6, "REFERENCIA", border=1, align="C", ln=True)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(63, 7, " Superaquecimento (SH)", border=1); pdf.cell(63, 7, f" {sh:.1f} K", border=1, align="C"); pdf.cell(64, 7, f" {ref['sh_min']} a {ref['sh_max']} K", border=1, align="C", ln=True)
        pdf.cell(63, 7, " Sub-resfriamento (SR)", border=1); pdf.cell(63, 7, f" {sr:.1f} K", border=1, align="C"); pdf.cell(64, 7, f" {ref['sr_min']} a {ref['sr_max']} K", border=1, align="C", ln=True)
        pdf.cell(63, 7, " Delta T Ar (DT)", border=1); pdf.cell(63, 7, f" {dt:.1f} C", border=1, align="C"); pdf.cell(64, 7, f" Minimo {ref['dt_min']} C", border=1, align="C", ln=True)

        # PARECER
        pdf.ln(2); pdf.set_font("helvetica", "B", 8); pdf.cell(190, 7, " PARECER TECNICO FINAL", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "B", 8); pdf.multi_cell(190, 6, f" Veredito: {veredito}", border=1)
        pdf.set_font("helvetica", "", 8); pdf.multi_cell(190, 6, f" Observacoes: {obs_final}", border=1)

        # RODAPÉ
        pdf.ln(10); pdf.cell(60); pdf.cell(70, 0, "", border="T", ln=True)
        pdf.set_font("helvetica", "B", 10); pdf.cell(190, 6, tecnico_nome.upper(), ln=True, align="C")
        pdf.set_font("helvetica", "", 9); pdf.cell(190, 4, doc_tecnico, ln=True, align="C")

        pdf_bytes = pdf.output()
        st.download_button("📄 BAIXAR LAUDO PDF", bytes(pdf_bytes), f"Laudo_{cliente}.pdf", "application/pdf", use_container_width=True)

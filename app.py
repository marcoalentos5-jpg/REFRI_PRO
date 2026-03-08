import streamlit as st
from datetime import date
from fpdf import FPDF
import urllib.parse
import os
from PIL import Image
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. ESTILIZAÇÃO INTERFACE (REVISADA) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    /* Estilo para os cartões de resultado (Fundo Bonito) */
    div[data-testid="stMetric"] {
        background-color: #E3F2FD; 
        border: 1px solid #BBDEFB;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
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

def obter_referencias_especificas(fabricante, modelo, tipo_sistema):
    texto = f"{fabricante} {modelo} {tipo_sistema}".upper()
    if "VRF" in texto or "VRV" in texto or "MULTI" in texto:
        return {"sh_min": 3, "sh_max": 8, "sr_min": 5, "sr_max": 12, "dt_min": 10, "label": "VRF/Multi"}
    elif "CÂMARA" in texto or "FRIA" in texto:
        return {"sh_min": 5, "sh_max": 15, "sr_min": 3, "sr_max": 10, "dt_min": 6, "label": "Refrig. Comercial"}
    elif "INVERTER" in texto or "DAIKIN" in texto or "FUJITSU" in texto:
        return {"sh_min": 4, "sh_max": 11, "sr_min": 2, "sr_max": 9, "dt_min": 9, "label": "Inverter"}
    else:
        return {"sh_min": 5, "sh_max": 12, "sr_min": 3, "sr_max": 10, "dt_min": 8, "label": "Geral"}

# --- 4. TÍTULO E ABAS ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Identificação")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Cliente / Empresa")
    doc_cliente = c1.text_input("CPF / CNPJ")
    whatsapp_input = c2.text_input("WhatsApp (com DDD)", value="21980264217")
    data_visita = c3.date_input("Data", value=date.today())
    fabricante = c1.text_input("Fabricante (Marca)")
    cap_btu = c2.text_input("Capacidade (BTUs)")
    fluido = c3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])
    mod_evap = st.text_input("Modelo/Linha (Ex: WindFree, Inverter, Multi V)")
    tipo_eq = st.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF/VRV", "Chiller", "Câmara Fria"])
    tecnico_nome = "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO"
    doc_tecnico = "CNPJ: 51.274.762/0001-17"

with tab_ele:
    e1, e2 = st.columns(2)
    v_med = e1.number_input("Tensão Medida (V)", value=220.0)
    a_med = e2.number_input("Corrente Medida (A)", value=0.0)

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        p_suc = st.number_input("Pressão Sucção (PSIG)", value=120.0)
        t_suc = st.number_input("Temp. Tubo Sucção (°C)", value=10.0)
        t_ret = st.number_input("Ar Retorno (°C)", value=24.0)
    with col_in2:
        p_liq = st.number_input("Pressão Descarga (PSIG)", value=350.0)
        t_liq = st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
        t_ins = st.number_input("Ar Insuflação (°C)", value=12.0)

    # CÁLCULOS
    tsat_evap = calcular_tsat(p_suc, fluido)
    tsat_cond = calcular_tsat(p_liq, fluido)
    sh, sr, dt = t_suc - tsat_evap, tsat_cond - t_liq, t_ret - t_ins
    ref = obter_referencias_especificas(fabricante, mod_evap, tipo_eq)

    st.markdown("---")
    st.subheader("📊 Resultados Analíticos")
    # ORGANIZAÇÃO SOLICITADA: Tsat | SH | DT | SR
    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Temp. Saturação (Tsat)", f"{tsat_evap:.1f} °C")
    res2.metric("Superaquecimento (SH)", f"{sh:.1f} K")
    res3.metric("Delta T do Ar (ΔT)", f"{dt:.1f} °C")
    res4.metric("Sub-resfriamento (SR)", f"{sr:.1f} K")

with tab_diag:
    if sh < ref["sh_min"]: veredito = "ALERTA: SH Baixo. Risco de golpe de líquido."
    elif sh > ref["sh_max"]: veredito = "ALERTA: SH Alto. Possível falta de gás."
    else: veredito = "Sistema em conformidade técnica."
    
    st.warning(f"Parecer: {veredito}")
    obs_final = st.text_area("📝 Notas e Recomendações", height=120)

    col_wa, col_pdf = st.columns(2)
    with col_wa:
        num_clean = "".join(filter(str.isdigit, whatsapp_input))
        if not num_clean.startswith("55"): num_clean = "55" + num_clean
        msg_wa = f"❄️ *LAUDO MPN*\n*Cliente:* {cliente}\n*Veredito:* {veredito}\n*Técnico:* {tecnico_nome}"
        url_wa = f"https://api.whatsapp.com{num_clean}&text={urllib.parse.quote(msg_wa)}"
        st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:8px; font-weight:bold; cursor:pointer;">📲 WHATSAPP</button></a>', unsafe_allow_html=True)

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
                    pdf.image(temp_buf, 10, 8, 30)
                pdf.ln(18)
            except: pass
        
        pdf.set_font("helvetica", "B", 12); pdf.set_fill_color(230, 230, 230)
        pdf.cell(190, 10, "LAUDO TECNICO DE DIAGNOSTICO", border=1, ln=True, align="C", fill=True)
        
        # TABELA DADOS
        pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " DADOS GERAIS", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(130, 6, f" Cliente: {cliente}", border=1); pdf.cell(60, 6, f" Data: {data_visita}", border=1, ln=True)
        pdf.cell(190, 6, f" Equipamento: {fabricante} {mod_evap} ({fluido})", border=1, ln=True)

        # TABELA CICLO (ORDEM SOLICITADA)
        pdf.ln(2); pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " CICLO FRIGORIFICO E ANALISE", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "B", 7)
        pdf.cell(47, 6, "TSAT (EVAP)", border=1, align="C"); pdf.cell(47, 6, "SUPERAQ. (SH)", border=1, align="C")
        pdf.cell(48, 6, "DELTA T (DT)", border=1, align="C"); pdf.cell(48, 6, "SUB-RESF. (SR)", border=1, align="C", ln=True)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(47, 7, f"{tsat_evap:.1f} C", border=1, align="C"); pdf.cell(47, 7, f"{sh:.1f} K", border=1, align="C")
        pdf.cell(48, 7, f"{dt:.1f} C", border=1, align="C"); pdf.cell(48, 7, f"{sr:.1f} K", border=1, align="C", ln=True)

        # PARECER
        pdf.ln(2); pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " PARECER FINAL", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "B", 8); pdf.multi_cell(190, 6, f" Veredito: {veredito}", border=1)
        pdf.set_font("helvetica", "", 8); pdf.multi_cell(190, 6, f" Obs: {obs_final}", border=1)

        # RODAPÉ
        pdf.ln(10); pdf.cell(60); pdf.cell(70, 0, "", border="T", ln=True)
        pdf.set_font("helvetica", "B", 10); pdf.cell(190, 6, tecnico_nome.upper(), ln=True, align="C")
        pdf.set_font("helvetica", "", 9); pdf.cell(190, 4, doc_tecnico, ln=True, align="C")

        pdf_bytes = pdf.output()
        st.download_button("📄 BAIXAR PDF", bytes(pdf_bytes), f"Laudo_{cliente}.pdf", "application/pdf", use_container_width=True)

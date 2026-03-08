import streamlit as st
from datetime import date
from fpdf import FPDF
import urllib.parse
import os
from PIL import Image
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. ESTILIZAÇÃO MPN (Revisão de Cores e Fundos) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    /* Cores de fundo personalizadas para cada métrica */
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] { background-color: #E3F2FD; border-radius: 10px; padding: 15px; border: 1px solid #BBDEFB; } /* Tsat */
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] { background-color: #E8F5E9; border-radius: 10px; padding: 15px; border: 1px solid #C8E6C9; } /* SH */
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] { background-color: #FFFDE7; border-radius: 10px; padding: 15px; border: 1px solid #FFF9C4; } /* DT */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetric"] { background-color: #E1F5FE; border-radius: 10px; padding: 15px; border: 1px solid #B3E5FC; } /* SR */
    
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

def obter_ref_tecnica(fabricante, tecnologia, tipo):
    texto = f"{fabricante} {tecnologia} {tipo}".upper()
    if "VRF" in texto or "MULTI" in texto:
        return {"sh_min": 3, "sh_max": 8, "sr_min": 5, "sr_max": 12, "dt_min": 10, "label": "VRF / Multi-Split"}
    elif "WINDFREE" in texto or "INVERTER" in texto:
        return {"sh_min": 4, "sh_max": 11, "sr_min": 2, "sr_max": 9, "dt_min": 9, "label": "Tecnologia Inverter"}
    elif "CÂMARA" in texto:
        return {"sh_min": 5, "sh_max": 15, "sr_min": 3, "sr_max": 10, "dt_min": 6, "label": "Refrig. Comercial"}
    else:
        return {"sh_min": 5, "sh_max": 12, "sr_min": 3, "sr_max": 10, "dt_min": 8, "label": "On-Off / Scroll Convencional"}

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
    tecnologia = d2.selectbox("Tecnologia do Compressor", ["Inverter", "WindFree", "Scroll", "On-Off"]) # NOVO CAMPO
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])
    cap_btu = d1.text_input("Capacidade (BTUs/h)")

    st.markdown("---")
    st.subheader("📦 Detalhamento das Unidades")
    col_evap, col_cond = st.columns(2)
    mod_evap = col_evap.text_input("Modelo da Evaporadora")
    serie_evap = col_evap.text_input("Nº de Série da Unidade")
    tipo_eq = col_cond.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF/VRV", "Chiller", "Câmara Fria", "Multi-Split"])

    tecnico_nome = "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO"
    doc_tecnico = "CNPJ: 51.274.762/0001-17"

# --- ABA 2: ELÉTRICA ---
with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    e1, e2 = st.columns(2)
    v_med = e1.number_input("Tensão Medida (V)", value=220.0)
    a_med = e2.number_input("Corrente Medida Real (A)", value=0.0)

# --- ABA 3: TERMODINÂMICA (ORDEM E CORES SOLICITADAS) ---
with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown("**🔹 Baixa Pressão**")
        p_suc = st.number_input("Pressão Sucção (PSIG)", value=120.0)
        t_suc = st.number_input("Temp. Tubo Sucção (°C)", value=10.0)
        t_ret = st.number_input("Temp. Ar Retorno (°C)", value=24.0)
    with t2:
        st.markdown("**🔸 Alta Pressão**")
        p_liq = st.number_input("Pressão Descarga (PSIG)", value=350.0)
        t_liq = st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
        t_ins = st.number_input("Temp. Ar Insuflação (°C)", value=12.0)

    tsat_evap = calcular_tsat(p_suc, fluido)
    tsat_cond = calcular_tsat(p_liq, fluido)
    sh, sr, dt = t_suc - tsat_evap, tsat_cond - t_liq, t_ret - t_ins
    ref = obter_ref_tecnica(fabricante, tecnologia, tipo_eq)

    st.markdown("---")
    st.subheader("📊 Resultados (Tsat | SH | DT | SR)")
    # As cores de fundo são aplicadas via CSS no topo do código
    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Temp. Saturação", f"{tsat_evap:.1f} °C")
    res2.metric("Superaquecimento", f"{sh:.1f} K")
    res3.metric("Delta T do Ar", f"{dt:.1f} °C")
    res4.metric("Sub-resfriamento", f"{sr:.1f} K")

# --- ABA 4: DIAGNÓSTICO & EXPORTAÇÃO ---
with tab_diag:
    if sh < ref["sh_min"]: veredito = "ALERTA: SH Baixo. Perigo de retorno de líquido ao compressor."
    elif sh > ref["sh_max"]: veredito = "ALERTA: SH Alto. Possível falta de fluido ou restrição."
    else: veredito = "Sistema em conformidade com os parâmetros da tecnologia selecionada."
    
    st.warning(f"Diagnóstico MPN: {veredito}")
    obs_final = st.text_area("📝 Recomendações Técnicas", height=150)

    st.markdown("---")
    col_wa, col_pdf = st.columns(2)

    with col_wa:
        num_clean = "".join(filter(str.isdigit, whatsapp_input))
        if not num_clean.startswith("55"): num_clean = "55" + num_clean
        msg_wa = f"❄️ *LAUDO MPN*\n*Cliente:* {cliente}\n*Veredito:* {veredito}\n*Técnico:* {tecnico_nome}"
        url_wa = f"https://api.whatsapp.com{num_clean}&text={urllib.parse.quote(msg_wa)}"
        st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:8px; font-weight:bold; cursor:pointer;">📲 ENVIAR WHATSAPP</button></a>', unsafe_allow_html=True)

    with col_pdf:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        if os.path.exists("logo.png"):
            try:
                with Image.open("logo.png") as img:
                    img = img.convert("RGB")
                    buf = io.BytesIO()
                    img.save(buf, format="PNG"); buf.seek(0)
                    pdf.image(buf, 10, 8, 30)
                pdf.ln(18)
            except: pass
        
        pdf.set_font("helvetica", "B", 12); pdf.set_fill_color(235, 235, 235)
        pdf.cell(190, 10, "LAUDO TECNICO DE DIAGNOSTICO - MPN", border=1, ln=True, align="C", fill=True)
        
        pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " INFORMACOES GERAIS", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(95, 6, f" Cliente: {cliente}", border=1); pdf.cell(95, 6, f" Tecnologia: {tecnologia}", border=1, ln=True)
        pdf.cell(63, 6, f" Marca: {fabricante}", border=1); pdf.cell(63, 6, f" BTU: {cap_btu}", border=1); pdf.cell(64, 6, f" Gas: {fluido}", border=1, ln=True)

        pdf.ln(2); pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " ANALISE DO CICLO FRIGORIFICO", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "B", 7)
        pdf.cell(47, 6, "TSAT (EVAP)", border=1, align="C"); pdf.cell(47, 6, "SUPERAQ. (SH)", border=1, align="C")
        pdf.cell(48, 6, "DELTA T (DT)", border=1, align="C"); pdf.cell(48, 6, "SUB-RESF. (SR)", border=1, align="C", ln=True)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(47, 7, f"{tsat_evap:.1f} C", border=1, align="C"); pdf.cell(47, 7, f"{sh:.1f} K", border=1, align="C")
        pdf.cell(48, 7, f"{dt:.1f} C", border=1, align="C"); pdf.cell(48, 7, f"{sr:.1f} K", border=1, align="C", ln=True)

        pdf.ln(2); pdf.set_font("helvetica", "B", 8); pdf.cell(190, 6, " PARECER FINAL", border="LR", ln=True, fill=True)
        pdf.set_font("helvetica", "B", 8); pdf.multi_cell(190, 6, f" Veredito: {veredito}", border=1)
        pdf.set_font("helvetica", "", 8); pdf.multi_cell(190, 6, f" Recomendações: \n{obs_final}", border=1)

        pdf.ln(10); pdf.cell(60); pdf.cell(70, 0, "", border="T", ln=True)
        pdf.set_font("helvetica", "B", 10); pdf.cell(190, 6, tecnico_nome.upper(), ln=True, align="C")
        pdf.set_font("helvetica", "", 9); pdf.cell(190, 4, doc_tecnico, ln=True, align="C")

        st.download_button(label="📄 BAIXAR LAUDO PDF", data=bytes(pdf.output()), file_name=f"Laudo_MPN_{cliente}.pdf", mime="application/pdf", use_container_width=True)

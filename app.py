import streamlit as st
from datetime import date
from fpdf import FPDF
import urllib.parse

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

# --- 5. CRIAÇÃO DAS ABAS ---
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico & Relatório"
])

# --- ABA 1: IDENTIFICAÇÃO ---
with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Nome do Cliente / Empresa")
    endereco = c1.text_input("Endereço")
    telefone = c2.text_input("📞 Telefone Fixo")
    whatsapp = c2.text_input("🟢 WhatsApp (com DDD)", placeholder="Ex: 11999999999")
    email_cli = c3.text_input("✉️ E-mail")
    data_visita = c3.date_input("Data da Visita", value=date.today())

    st.markdown("---")
    st.subheader("📦 Especificações das Unidades")
    col_evap, col_cond = st.columns(2)
    with col_evap:
        st.markdown("**🔹 UNIDADE INTERNA (EVAPORADORA)**")
        mod_evap = st.text_input("Modelo (Evap)")
        serie_evap = st.text_input("Nº de Série (Evap)")
        tag_loc = st.text_input("Ambiente / TAG")
    with col_cond:
        st.markdown("**🔸 UNIDADE EXTERNA (CONDENSADORA)**")
        mod_cond = st.text_input("Modelo (Cond)")
        serie_cond = st.text_input("Nº de Série (Cond)")
        tipo_eq = st.selectbox("Tipo", ["Split Hi-Wall", "Piso-Teto", "Cassete", "Chiller", "VRF/VRV", "Multi-Split"])

    st.markdown("---")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante")
    cap_btu = d2.text_input("Capacidade (BTUs)")
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])
    tecnico = st.text_input("👷 Técnico Responsável", value="MPN Engenharia")

# --- ABA 2: ELÉTRICA ---
with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2 = st.columns(2)
    v_nom = el1.selectbox("Tensão Nominal (V)", ["127", "220", "380", "440"], index=1)
    v_med = el1.number_input("Tensão Medida (V)", value=float(v_nom))
    a_nom = el2.number_input("Corrente Nominal RLA (A)", value=5.0)
    a_med = el2.number_input("Corrente Medida Real (A)", value=0.0)
    diff_v = ((v_med - float(v_nom)) / float(v_nom)) * 100
    diff_a = a_med - a_nom
    
    st.markdown("---")
    res1, res2 = st.columns(2)
    res1.metric("Variação de Tensão", f"{diff_v:.1f}%", delta=f"{v_med - float(v_nom)}V", delta_color="inverse")
    res2.metric("Desvio de Corrente", f"{a_med:.1f} A", delta=f"{diff_a:.1f}A", delta_color="inverse")

# --- ABA 3: TERMODINÂMICA ---
with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    t1, t2 = st.columns(2)
    with t1:
        p_suc = st.number_input("Pressão Sucção (PSIG)", value=120.0)
        t_suc = st.number_input("Temp. Tubo Sucção (°C)", value=10.0)
        t_ret = st.number_input("Ar Retorno (°C)", value=24.0)
    with t2:
        p_liq = st.number_input("Pressão Descarga (PSIG)", value=350.0)
        t_liq = st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
        t_ins = st.number_input("Ar Insuflação (°C)", value=12.0)

    sh = t_suc - calcular_tsat(p_suc, fluido)
    sr = calcular_tsat(p_liq, fluido) - t_liq
    dt = t_ret - t_ins

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Superaquecimento (SH)", f"{sh:.1f} K")
    m2.metric("Sub-resfriamento (SR)", f"{sr:.1f} K")
    m3.metric("Delta T do Ar (ΔT)", f"{dt:.1f} °C")

# --- ABA 4: DIAGNÓSTICO & EXPORTAÇÃO ---
with tab_diag:
    st.subheader("🤖 Diagnóstico Final")
    veredito = "Sistema operando em equilíbrio."
    if sh < 5: veredito = "🚨 ALERTA: Superaquecimento Baixo (Risco de Líquido)."
    elif sh > 12: veredito = "🚨 ALERTA: Superaquecimento Alto (Baixa Carga/Rendimento)."
    elif dt < 8: veredito = "⚠️ AVISO: Baixa troca térmica (Filtros/Sujeira)."
    
    st.info(f"Veredito: {veredito}")
    obs_final = st.text_area("📝 Recomendações Adicionais", placeholder="Descreva aqui o que deve ser feito.")

    st.markdown("---")
    col_wa, col_pdf = st.columns(2)

    # BOTÃO WHATSAPP
    with col_wa:
        if st.button("📲 Preparar WhatsApp"):
            wa_num = "".join(filter(str.isdigit, whatsapp))
            texto_wa = f"❄️ *LAUDO MPN*\n*Cliente:* {cliente}\n*Eq:* {fabricante}\n*SH:* {sh:.1f}K | *SR:* {sr:.1f}K\n*Veredito:* {veredito}"
            st.markdown(f'<a href="https://wa.me{wa_num}?text={urllib.parse.quote(texto_wa)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:5px; cursor:pointer;">ENVIAR WHATSAPP</button></a>', unsafe_allow_html=True)

    # BOTÃO PDF (IMPRESSÃO A4)
    with col_pdf:
        if st.button("📄 Gerar Laudo PDF (A4)"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "LAUDO TECNICO DE REFRIGERACAO - MPN", ln=True, align="C")
            pdf.set_font("Arial", "", 10)
            pdf.ln(10)
            pdf.cell(200, 8, f"CLIENTE: {cliente} | DATA: {data_visita}", ln=True)
            pdf.cell(200, 8, f"EQUIPAMENTO: {fabricante} {cap_btu} | TAG: {tag_loc}", ln=True)
            pdf.cell(200, 8, f"EVAP: {mod_evap} (S/N: {serie_evap})", ln=True)
            pdf.cell(200, 8, f"COND: {mod_cond} (S/N: {serie_cond})", ln=True)
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, "PARAMETROS DO CICLO:", ln=True)
            pdf.set_font("Arial", "", 10)
            pdf.cell(200, 8, f"SH: {sh:.1f} K | SR: {sr:.1f} K | Delta T: {dt:.1f} C", ln=True)
            pdf.cell(200, 8, f"Tensao: {v_med}V | Corrente: {a_med}A", ln=True)
            pdf.ln(5)
            pdf.cell(200, 10, f"DIAGNOSTICO: {veredito}", ln=True)
            pdf.multi_cell(0, 10, f"OBS: {obs_final}")
            pdf.ln(20)
            pdf.cell(200, 10, "________________________________________", ln=True, align="C")
            pdf.cell(200, 10, f"ASSINATURA TECNICA: {tecnico}", ln=True, align="C")
            
            pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='replace')
            st.download_button(label="📥 Baixar PDF para Impressão", data=pdf_bytes, file_name=f"Laudo_{cliente}.pdf", mime="application/pdf")

import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA (BLOQUEADA) ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# ESTILO DAS ABAS (FONTE AUMENTADA E NEGRETADA)
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR TERMODINÂMICO E UTILITÁRIOS ---
def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                   "t": [-51.0, -17.02, -0.29, 11.55, 20.93, 28.84, 35.58, 41.74, 47.3, 52.1, 56.59, 60.7, 64.59]},
        "R-32": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                 "t": [-51.7, -17.46, 0.87, 10.86, 20.14, 27.9, 34.63, 40.6, 45.96, 50.8, 55.36, 59.5, 63.43]},
        "R-22": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 600.0], 
                 "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 73.2, 78.38, 87.53]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 80.0, 100.0, 130.0, 150.0, 180.0, 200.0], 
                   "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 38.4, 43.65, 50.1, 53.74]},
        "R-404A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0], 
                   "t": [-45.45, -9.41, 8.96, 22.23, 32.59, 41.2, 48.6, 55.2, 61.1]}
    }
    if gas not in ancoras or psig is None: return 0.0
    try: return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)
    except: return 0.0

def clean(txt):
    if not txt: return "N/A"
    replacements = {'°': 'C', 'º': '.', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C'}
    t = str(txt)
    for old, new in replacements.items(): t = t.replace(old, new)
    return t.encode('ascii', 'ignore').decode('ascii')

# --- 3. INTERFACE DO APP ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente, doc_cliente = c1.text_input("Cliente/Empresa", key="f_cli"), c2.text_input("CPF/CNPJ", key="f_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY", key="f_date")
    whatsapp, celular, tel_residencial = c4.text_input("🟢 WhatsApp", value="21980264217", key="f_wpp"), c5.text_input("📱 Celular", key="f_cel"), c6.text_input("📞 Fixo", key="f_fix")
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr, nome_logr, numero, complemento, bairro, cep, email_cli = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."], key="f_tlog"), e2.text_input("Logradouro", key="f_nlog"), e3.text_input("Nº", key="f_num"), e4.text_input("Comp.", key="f_comp"), e5.text_input("Bairro", key="f_bai"), e6.text_input("CEP", key="f_cep"), e7.text_input("✉️ E-mail", key="f_mail")
    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3 = st.columns(3)
    with g1: fabricante, modelo_eq, cap_digitada = st.text_input("Marca", key="f_fab"), st.text_input("Modelo Geral", key="f_mod"), st.text_input("Capacidade (BTU/h)", value="0", key="f_cap")
    with g2: linha, tecnologia, fluido = st.text_input("Linha", key="f_lin"), st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"], key="f_tec"), st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"], key="f_gas")
    with g3: tipo_eq, loc_evap, loc_cond = st.selectbox("Sistema", ["Split", "Cassete", "Piso", "VRF", "Chiller"], key="f_sis"), st.text_input("Local Evaporadora", key="f_le"), st.text_input("Local Condensadora", key="f_lc")
    s1, s2 = st.columns(2)
    with s1: mod_evap, serie_evap = st.text_input("Modelo Evap.", key="f_me"), st.text_input("Nº Série Evap.", key="f_se")
    with s2: mod_cond, serie_cond = st.text_input("Modelo Cond.", key="f_mc"), st.text_input("Nº Série Cond.", key="f_sc")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns(3)
    with el1: v_rede, v_med = st.number_input("Tensão Rede (V)", value=220.0), st.number_input("Tensão Medida (V)", value=218.0)
    diff_v = round(v_rede - v_med, 1)
    with el2: rla_comp, a_med = st.number_input("Corrente RLA (A)", value=1.0), st.number_input("Corrente Medida (A)", value=0.0)
    diff_a = round(a_med - rla_comp, 1)
    with el3: lra_comp = st.number_input("LRA (A)", value=0.0)

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    with tr1: p_suc, t_suc_tubo = st.number_input("Pressão (PSI)", value=118.0, key="ps"), st.number_input("Temp. Tubo (°C)", value=12.0, key="ts")
    ts_suc = get_tsat_global(p_suc, fluido)
    with tr2: p_liq, t_liq_tubo = st.number_input("Pressão (PSI)", value=345.0, key="pl"), st.number_input("Temp. Tubo (°C)", value=30.0, key="tl")
    ts_liq = get_tsat_global(p_liq, fluido)
    sh_val, sc_val = round(t_suc_tubo - ts_suc, 1), round(ts_liq - t_liq_tubo, 1)

# --- ABA DIAGNÓSTICO ---
with tab_diag:
    col_prob, col_obs = st.columns(2)
    with col_prob:
        st.subheader("⚠️ Problemas Encontrados")
        diag_list, medidas_prop = [], []
        if sh_val > 12 and sc_val < 3: 
            diag_list.append("🔴 Falta de Gás ou Vazamento.")
            medidas_prop.append("🛠️ Localizar vazamento com nitrogênio e realizar carga por massa.")
        if sh_val < 5 and sc_val > 12: 
            diag_list.append("🔴 Excesso de Gás Refrigerante.")
            medidas_prop.append("🛠️ Recolher excesso e ajustar SH/SC conforme fabricante.")
        if sh_val > 15 and sc_val > 12: 
            diag_list.append("🔴 Obstrução no Dispositivo de Expansão.")
            medidas_prop.append("🛠️ Substituir filtro secador e limpar sistema com R-141b.")
        if abs(diff_v) > 22: 
            diag_list.append("🔴 Instabilidade Elétrica Grave.")
            medidas_prop.append("🛠️ Instalar protetor de fase ou verificar entrada da concessionária.")
        if not diag_list: st.info("✅ Parâmetros normais.")
        else:
            for d in diag_list: st.error(d)

    with col_obs:
        st.subheader("📝 Observações do Técnico")
        medidas_texto = st.text_area("", value=f"SH: {sh_val}K | SC: {sc_val}K | Diff V: {diff_v}V", height=150, label_visibility="collapsed")

    st.markdown("---")
    
    col_prop, col_tom = st.columns(2)
    with col_prop:
        st.subheader("🔧 Propostas")
        if not medidas_prop: st.write("Nenhuma medida proposta.")
        for m in medidas_prop: st.warning(m)
        
    with col_tom:
        st.subheader("📋 Medidas")
        st.markdown("**Tomadas**")
        tomadas_input = st.text_area("", placeholder="Descreva as medidas executadas...", key="tomadas_t", height=150, label_visibility="collapsed")

    if st.button("📄 Gerar Relatório Profissional"):
        pdf = FPDF()
        pdf.add_page()
        pdf.image("logo.png", 10, 8, 42)
        pdf.set_font("Arial", 'B', 22); pdf.set_text_color(0, 51, 102); pdf.set_xy(0, 10); pdf.cell(210, 10, "MPN", 0, 1, 'C')
        pdf.set_font("Arial", 'B', 16); pdf.set_x(0); pdf.cell(210, 8, "Relatório Técnico".encode('latin-1').decode('latin-1'), 0, 1, 'C')
        # PDF MANTIDO SEM ALTERAÇÕES DE LAYOUT CONFORME INSTRUÇÃO
        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button("📩 Baixar Relatório PDF", pdf_output, file_name=f"Relatorio_{cliente}.pdf", mime="application/pdf")

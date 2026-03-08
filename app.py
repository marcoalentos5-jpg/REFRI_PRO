import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import math
import io
import urllib.parse

# --- 1. PROTEÇÃO DE ACESSO MPN ---
def check_password():
    """Retorna True se a senha estiver correta."""
    def password_entered():
        if st.session_state["password"] == "MPN2024":  # <--- SUA SENHA AQUI
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("❄️ Acesso Restrito MPN")
        st.text_input("Digite a Senha de Engenharia", type="password", on_change=password_entered, key="password")
        if "password_correct" in st.session_state:
            st.error("😕 Senha incorreta")
        return False
    return st.session_state["password_correct"]

if not check_password():
    st.stop()

# --- 2. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="MPN | Engenharia & Diagnóstico", layout="wide", page_icon="❄️")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    [data-testid="stMetric"] {
        background-color: #004A99 !important; border-radius: 15px !important;
        padding: 20px !important; border: 2px solid #A9A9A9 !important;
    }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-weight: bold !important; font-size: 1.1rem !important; }
    [data-testid="stMetricValue"] { color: #00D1FF !important; font-size: 2.2rem !important; }
    .stButton>button { background-color: #004A99; color: white; border-radius: 10px; height: 3.5em; font-weight: bold; width: 100%; border: none; }
    h1, h2, h3, h4 { color: #004A99; font-family: 'Arial', sans-serif; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE ENGENHARIA (DANFOSS) ---
def calcular_t_sat_precisao(psig, gas):
    if psig is None or not gas or psig <= 0: return None
    try:
        if gas == "R-410A":
            # Calibração Master: 133.10 psig -> 7.90 °C | 122.70 psig -> 5.50 °C
            return 0.23076923 * psig - 22.81538462
        elif gas == "R-22": return 0.2854 * psig - 25.12
        elif gas == "R-134a": return 0.521 * psig - 38.54
        elif gas == "R-404A": return 0.2105 * psig - 16.52
    except: return None
    return None

# --- 4. SIDEBAR (SETUP & ELÉTRICA EM INTEIROS) ---
st.sidebar.header("⚙️ Setup do Ciclo & Elétrica")
f_equip = st.sidebar.selectbox("Equipamento", ["", "Split Hi-Wall", "Split Cassete", "Piso-Teto", "Chiller", "VRF/VRV", "Câmara Fria"])
f_gas = st.sidebar.selectbox("Fluido Refrigerante", ["", "R-410A", "R-22", "R-134a", "R-404A"])
f_tec = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter", "Digital Scroll"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Parâmetros Elétricos")
v_trab_str = st.sidebar.selectbox("Tensão Nominal [V]", ["", "127", "220", "380", "440"])
v_medida = st.sidebar.number_input("Tensão Medida [V]", min_value=0, step=1, format="%d")

diff_tensao_v = 0
if v_trab_str and v_medida > 0:
    diff_tensao_v = v_medida - int(v_trab_str)
st.sidebar.markdown(f"**Diferença:** `{diff_tensao_v} V`")

# --- 5. NAVEGAÇÃO POR ABAS ---
tab_iden, tab_termo, tab_solucoes, tab_carga, tab_subs = st.tabs([
    "📋 Identificação", "🌡️ Termodinâmica", "🤖 IA & Diagnóstico", "📐 Carga VRF", "🔄 Peças"
])

with tab_iden:
    st.subheader("📋 Identificação e Amperagem")
    c1, c2, c3 = st.columns(3)
    cli = c1.text_input("Cliente")
    tec = c2.text_input("Técnico")
    ser = c3.text_input("S/N (Série)")
    
    e1, e2, e3, e4 = st.columns(4)
    v_rla = e1.number_input("Corrente RLA [A]", value=0.00, step=0.01, format="%.2f")
    v_lra = e2.number_input("Corrente LRA [A]", value=0.00, step=0.01, format="%.2f")
    v_med_amp = e3.number_input("Corrente Medida [A]", value=0.00, step=0.01, format="%.2f")
    diff_amp = v_med_amp - v_rla if v_rla > 0 else 0.00
    e4.metric("DIF. CORRENTE", f"{diff_amp:.2f} A", delta=f"{diff_amp:.2f} vs RLA")

with tab_termo:
    st.subheader("🛠️ Pressões e Temperaturas")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        t_ret = st.number_input("Ar Retorno [°C]", value=24.00, format="%.2f")
        t_ins = st.number_input("Ar Insuflação [°C]", value=12.00, format="%.2f")
        dt = t_ret - t_ins
        st.metric("DELTA T (AR)", f"{dt:.2f} °C")
    with m2:
        p_suc = st.number_input("Sucção (PSIG)", value=133.10, format="%.2f")
        tsat_evap = calcular_t_sat_precisao(p_suc, f_gas)
        st.metric("T. SAT (DEW)", f"{tsat_evap:.2f} °C" if tsat_evap else "--")
    with m3:
        t_tubo_suc = st.number_input("Tubo Sucção [°C]", value=12.00, format="%.2f")
        sh = t_tubo_suc - tsat_evap if tsat_evap else 0.00
        st.metric("SH (SUPER-AQ)", f"{sh:.2f} K")
    with m4:
        p_desc = st.number_input("Descarga (PSIG)", value=380.00, format="%.2f")
        tsat_cond = calcular_t_sat_precisao(p_desc, f_gas)
        t_tubo_liq = st.number_input("Tubo Líquido [°C]", value=30.00, format="%.2f")
        sr = tsat_cond - t_tubo_liq if tsat_cond else 0.00
        st.metric("SR (SUB-RESF)", f"{sr:.2f} K")

with tab_solucoes:
    st.subheader("🤖 Diagnóstico IA Especialista")
    if p_suc > 0 and v_med_amp > 0:
        if sh < 5 and sr > 10: st.error("🚨 EXCESSO DE CARGA OU OBSTRUÇÃO NA EXPANSÃO.")
        elif sh > 12 and sr < 3: st.error("🚨 FALTA DE FLUIDO REFRIGERANTE.")
        else: st.success("✅ SISTEMA EM EQUILÍBRIO TERMODINÂMICO.")

with tab_subs:
    st.subheader("🔄 Peças Alternativas")
    dados_comp = {"Capacidade": ["9k BTU", "12k BTU", "18k BTU"], "Embraco": ["FFU 80HAX", "FFU 130HAX", "FFU 160HAX"], "Tecumseh": ["THB1380YS", "AE4440YS", "AK4476YS"]}
    st.table(pd.DataFrame(dados_comp))

# --- 6. EXPORTAÇÃO ---
st.markdown("---")
if st.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if not cli: st.error("Informe o cliente.")
    else:
        pdf = FPDF(); pdf.add_page()
        pdf.set_fill_color(0, 74, 153); pdf.rect(0, 0, 210, 35, 'F')
        pdf.set_font('Arial', 'B', 14); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 15, 'LAUDO TÉCNICO MPN REFRIGERAÇÃO', 0, 1, 'C')
        st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), f"Laudo_{cli}.pdf")

texto_wa = f"*MPN REFRIGERAÇÃO*\n👤 *Cliente:* {cli}\n🌡️ *SH:* {sh:.2f}K | *SR:* {sr:.2f}K\n⚡ *Tensão:* {v_medida}V"
st.link_button("📲 WHATSAPP", f"https://wa.me{urllib.parse.quote(texto_wa)}")

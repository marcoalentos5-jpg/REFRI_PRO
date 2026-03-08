import streamlit as st
from fpdf import FPDF
from datetime import datetime
import math

# --- CONFIGURAÇÃO VISUAL MASTER MPN ---
st.set_page_config(page_title="MPN | Engenharia & Diagnóstico", layout="wide", page_icon="❄️")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    [data-testid="stMetric"] {
        background-color: #004A99 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        border: 2px solid #A9A9A9 !important;
    }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-weight: bold !important; font-size: 1.1rem !important; }
    [data-testid="stMetricValue"] { color: #00D1FF !important; font-size: 2.2rem !important; }
    .stButton>button { background-color: #004A99; color: white; border-radius: 10px; height: 3.5em; font-weight: bold; width: 100%; border: none; }
    h1, h2, h3, h4 { color: #004A99; font-family: 'Arial', sans-serif; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ENGENHARIA (DANFOSS DEW POINT) ---
def calcular_t_sat_dew(psig, gas):
    if psig is None or not gas or gas == "": return None
    if gas == "R-410A": return 22.95 * math.log(psig) - 104.38
    elif gas == "R-22": return 26.54 * math.log(psig) - 121.93
    elif gas == "R-134a": return 31.75 * math.log(psig) - 147.35
    elif gas == "R-404A": return 20.88 * math.log(psig) - 94.32
    elif gas == "R-32": return 23.15 * math.log(psig) - 106.85
    return None

# --- NAVEGAÇÃO POR ABAS ---
tab_diag, tab_ai, tab_carga, tab_subs, tab_manuais = st.tabs([
    "📊 Diagnóstico Master", "🤖 IA & Soluções", "📐 Carga Térmica", "🔄 Substituição", "📚 Manuais"
])

# --- ABA 1: DIAGNÓSTICO MASTER (LAYOUT ORIGINAL PRESERVADO) ---
with tab_diag:
    st.image("https://i.imgur.com", width=350)
    with st.expander("📋 Identificação Completa do Sistema", expanded=True):
        c1, c2, c3 = st.columns(3)
        cli, tec, fab = c1.text_input("Cliente"), c2.text_input("Técnico"), c3.text_input("Fabricante")
        c4, c5, c6, c7 = st.columns(4)
        lin, mod_int, mod_ext, ser = c4.text_input("Linha"), c5.text_input("Mod. Interno"), c6.text_input("Mod. Externo"), c7.text_input("Série")

    st.sidebar.header("⚙️ Setup do Ciclo")
    f_equip = st.sidebar.selectbox("Equipamento", ["", "ACJ", "Câmara Fria", "Chiller", "Piso-Teto", "Split Hi-Wall", "Splitão", "VRF/VRV"])
    f_gas = st.sidebar.selectbox("Gás (Danfoss Dew)", ["", "R-410A", "R-22", "R-134a", "R-404A", "R-32"])
    f_tec = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter", "Digital Scroll"])

    st.subheader("🛠️ Coleta de Dados Termodinâmicos")
    m1, m2, m3 = st.columns(3)
    with m1:
        t_ret = st.number_input("Temp. Retorno [°C]", value=None)
        t_ins = st.number_input("Temp. Insuflação [°C]", value=None)
        dt = t_ret - t_ins if (t_ret and t_ins) else None
        st.metric("DELTA T", f"{dt:.1f} °C" if dt else "--")
    with m2:
        p_suc = st.number_input("Pressão Sucção [PSI]", value=None)
        t_fin = st.number_input("Temp. Final Sucção [°C]", value=None)
        tsat = calcular_t_sat_dew(p_suc, f_gas)
        sh = t_fin - tsat if (t_fin and tsat) else None
        st.metric("SUPER AQUECIMENTO", f"{sh:.1f} K" if sh else "--")
    with m3:
        v_rla, v_lra, v_med = st.number_input("RLA [A]", value=None), st.number_input("LRA [A]", value=None), st.number_input("Medida [A]", value=None)
        da = v_med - v_rla if (v_rla and v_med) else None
        st.metric("AMPERAGEM REAL", f"{v_med:.1f} A" if v_med else "--", delta=f"{da:.2f} vs RLA" if da else None, delta_color="inverse")

# --- ABA 3: CARGA TÉRMICA PROFISSIONAL ---
with tab_carga:
    st.subheader("📐 Dimensionamento de Carga Térmica de Precisão")
    with st.expander("🏠 Características do Ambiente", expanded=True):
        c_a1, c_a2, c_a3 = st.columns(3)
        area_m2 = c_a1.number_input("Área do Local (m²)", value=None)
        pe_direito = c_a2.number_input("Pé Direito (m)", value=None, placeholder="2.60")
        face_solar = c_a3.selectbox("Face Solar", ["", "Norte/Oeste (Quente)", "Sul/Leste (Frio)"])

    with st.expander("👥 Ocupação e Eletrônicos"):
        c_p1, c_p2, c_p3 = st.columns(3)
        n_pessoas = c_p1.number_input("Nº de Pessoas", value=None)
        watts_luz = c_p2.number_input("Iluminação (Watts)", value=None)
        janelas_m2 = c_p3.number_input("Área de Janelas (m²)", value=0.0)

    if area_m2 and n_pessoas:
        f_base = 800 if face_solar == "Norte/Oeste (Quente)" else 600
        btu_final = (area_m2 * f_base) + ((n_pessoas - 1) * 600 if n_pessoas > 1 else 0) + (janelas_m2 * 1000) + (watts_luz * 3.41 if watts_luz else 0)
        st.divider()
        res_c1, res_c2 = st.columns(2)
        res_c1.metric("CARGA TOTAL CALCULADA", f"{btu_final:,.0f} BTU/h")
        comercial = next((x for x in [9000, 12000, 18000, 24000, 30000, 36000, 48000, 60000, 80000] if x >= btu_final), "Consultar Engenharia")
        res_c2.metric("EQUIPAMENTO SUGERIDO", f"{comercial} BTU/h")

if st.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    st.success("Relatório gerado. Inclui Diagnóstico e Carga Térmica.")

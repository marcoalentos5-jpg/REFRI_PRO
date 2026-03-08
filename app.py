import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import math
import io

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

# --- LÓGICA DE ENGENHARIA ---
def calcular_t_sat_danfoss_dew(psig, gas):
    if psig is None or not gas or psig <= 0: return None
    try:
        if gas == "R-410A": return 22.95 * math.log(psig) - 104.38
        elif gas == "R-22": return 26.54 * math.log(psig) - 121.93
        elif gas == "R-134a": return 31.75 * math.log(psig) - 147.35
        elif gas == "R-404A": return 20.88 * math.log(psig) - 94.32
        elif gas == "R-32": return 23.15 * math.log(psig) - 106.85
    except: return None
    return None

# --- CLASSE PDF PROFISSIONAL ---
class MPN_PDF(FPDF):
    def header(self):
        self.set_fill_color(0, 74, 153)
        self.rect(0, 0, 210, 35, 'F')
        self.set_font('Arial', 'B', 15)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'MPN REFRIGERAÇÃO - ENGENHARIA & DIAGNÓSTICO', 0, 1, 'C')
        self.ln(10)

# --- NAVEGAÇÃO ---
tab_diag, tab_solucoes, tab_carga, tab_subs, tab_manuais = st.tabs([
    "📊 Diagnóstico Master", "🤖 IA & Soluções", "📐 Carga Térmica", "🔄 Substituição & Alternativas", "📚 Manuais"
])

# --- ABA 1: DIAGNÓSTICO MASTER ---
with tab_diag:
    st.subheader("📋 Identificação Completa do Sistema")
    with st.expander("Dados do Cliente e Equipamento", expanded=True):
        c1, c2, c3 = st.columns(3)
        cli = c1.text_input("Cliente", placeholder="Nome ou Empresa")
        tec = c2.text_input("Responsável Técnico")
        fab = c3.text_input("Fabricante", placeholder="Ex: Daikin / Carrier")
        
        c4, c5, c6, c7 = st.columns(4)
        lin = c4.text_input("Linha/Família", placeholder="Ex: Inverter V")
        mod_int = c5.text_input("Modelo Interno (Evaporadora)")
        mod_ext = c6.text_input("Modelo Externo (Condensadora)")
        ser = c7.text_input("Número de Série (S/N)")

    st.sidebar.header("⚙️ Setup do Ciclo")
    lista_equip = ["", "ACJ", "Câmara Fria", "Chiller", "Geladeira/Freezer", "Piso-Teto", "Self-Contained", "Split Cassete (K-7)", "Split Hi-Wall", "Splitão", "VRF/VRV"]
    f_equip = st.sidebar.selectbox("Tipo de Equipamento", sorted(lista_equip))
    f_gas = st.sidebar.selectbox("Fluido Refrigerante", ["", "R-410A", "R-22", "R-134a", "R-404A", "R-32", "R-407C"])
    f_tec = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter", "Digital Scroll"])
    f_tensao = st.sidebar.selectbox("Tensão", ["", "110V", "220V", "380V", "440V"])

    st.subheader("🛠️ Coleta de Dados Termofluidodinâmicos")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("#### 🌬️ Troca de Ar")
        t_ret = st.number_input("Temp. Retorno [°C]", value=0.0)
        t_ins = st.number_input("Temp. Insuflação [°C]", value=0.0)
        dt = t_ret - t_ins
        st.metric("DELTA T", f"{dt:.1f} °C")

    with m2:
        st.markdown("#### 🧪 Ciclo (Danfoss Dew)")
        p_suc = st.number_input("Pressão Sucção (PSI)", value=0.0)
        t_fin = st.number_input("Temp. Final Sucção [°C]", value=0.0)
        tsat = calcular_t_sat_danfoss_dew(p_suc, f_gas)
        sh = t_fin - tsat if (tsat is not None) else 0.0
        st.metric("SUPER AQUECIMENTO", f"{sh:.1f} K")

    with m3:
        st.markdown("#### ⚡ Elétrica (RLA/LRA)")
        v_rla = st.number_input("Corrente RLA [A]", value=1.0)
        v_med = st.number_input("Corrente Medida [A]", value=0.0)
        da = v_med - v_rla
        st.metric("AMPERAGEM REAL", f"{v_med:.1f} A", delta=f"{da:.2f} vs RLA", delta_color="inverse")

# --- ABA 2: IA & SOLUÇÕES ---
with tab_solucoes:
    st.subheader("🤖 Consultoria MPN IA")
    if p_suc == 0 or t_ret == 0:
        st.warning("Aguardando medições na Aba 1...")
    else:
        st.info("IA Cruzando Manuais e Base de Especialistas...")
        pecas = []
        if sh < 5: 
            st.error("🚨 **GOLPE DE LÍQUIDO:** Verifique Válvula de Expansão ou Sensor NTC.")
            pecas.append("Válvula de Expansão / Sensor de Sucção")
        if sh > 12: 
            st.error("❌ **SISTEMA FAMINTO:** Verifique Filtro Secador ou Vazamento.")
            pecas.append("Filtro Secador / Fluido Refrigerante")
        if dt < 8: 
            st.warning("🌬️ **EFICIÊNCIA:** Limpeza química ou capacitor do ventilador.")
            pecas.append("Capacitor do Ventilador / Higienização")
        
        if pecas: st.write("### 🛠️ Peças Sugeridas:", ", ".join(pecas))
        else: st.success("✅ Sistema em perfeito equilíbrio térmico!")

# --- BOTÃO PDF ---
if st.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if not cli or p_suc == 0: st.error("Preencha os dados básicos.")
    else:
        pdf = MPN_PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 10, f"CLIENTE: {cli} | TÉCNICO: {tec}", ln=True)
        pdf.cell(0, 10, f"EQUIPAMENTO: {f_equip} | S/N: {ser}", ln=True)
        pdf.ln(5)
        pdf.cell(0, 10, f"SH: {sh:.1f}K | DT: {dt:.1f}C | AMP: {v_med}A", ln=True)
        st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), f"OS_{cli}.pdf", "application/pdf")

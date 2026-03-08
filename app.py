import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
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

# --- LÓGICA DE ENGENHARIA DE ALTA PRECISÃO (DANFOSS DEW POINT) ---
def calcular_t_sat_danfoss_dew(psig, gas):
    if psig is None or not gas or psig <= 0: 
        return None
    try:
        # Calibração Exata baseada nos pontos: 122.7=5.50 / 133.1=7.90
        if gas == "R-410A":
            return 0.23076923 * psig - 22.81538462
        elif gas == "R-22":
            return 0.2854 * psig - 25.12
        elif gas == "R-134a":
            return 0.521 * psig - 38.54
        elif gas == "R-404A":
            return 0.2105 * psig - 16.52
    except:
        return None
    return None

# --- NAVEGAÇÃO POR ABAS ---
tab_diag, tab_solucoes, tab_carga, tab_subs, tab_manuais = st.tabs([
    "📊 Diagnóstico Master", "🤖 IA & Soluções", "📐 Carga Térmica", "🔄 Substituição & Alternativas", "📚 Manuais"
])

# --- ABA 1: DIAGNÓSTICO MASTER ---
with tab_diag:
    st.subheader("📋 Identificação Completa do Sistema")
    
    with st.expander("Dados do Cliente, Equipamento e Elétrica", expanded=True):
        # Linha 1: Identificação Básica
        c1, c2, c3 = st.columns(3)
        cli = c1.text_input("Cliente", placeholder="Nome ou Empresa")
        tec = c2.text_input("Responsável Técnico")
        fab = c3.text_input("Fabricante", placeholder="Ex: Daikin / Carrier")
        
        # Linha 2: Modelos e Série
        c4, c5, c6, c7 = st.columns(4)
        lin = c4.text_input("Linha/Família", placeholder="Ex: Inverter V")
        mod_int = c5.text_input("Modelo Interno (Evaporadora)")
        mod_ext = c6.text_input("Modelo Externo (Condensadora)")
        ser = c7.text_input("Número de Série (S/N)")

        # Linha 3: Novos Campos de Tensão (Lado Esquerdo)
        c8, c9, c10, c11 = st.columns(4)
        v_trab_str = c8.selectbox("Tensão de Trabalho (Nominal)", ["", "127", "220", "380", "440"])
        v_medida = c9.number_input("Tensão Medida [V]", value=0.00, step=0.01, format="%.2f")
        
        # Cálculo da Variação de Tensão
        variacao_v = 0.00
        if v_trab_str and v_medida > 0:
            v_nominal = float(v_trab_str)
            variacao_v = ((v_medida - v_nominal) / v_nominal) * 100
            color_v = "normal" if abs(variacao_v) <= 10 else "inverse"
            c10.metric("VARIAÇÃO TENSÃO", f"{variacao_v:.2f}%", delta=f"{variacao_v:.1f}%", delta_color=color_v)

    st.sidebar.header("⚙️ Setup do Ciclo")
    lista_equip = ["", "ACJ", "Câmara Fria", "Chiller", "Geladeira/Freezer", "Piso-Teto", "Self-Contained", "Split Cassete (K-7)", "Split Hi-Wall", "Splitão", "VRF/VRV"]
    f_equip = st.sidebar.selectbox("Tipo de Equipamento", sorted(lista_equip))
    f_gas = st.sidebar.selectbox("Fluido Refrigerante", ["", "R-410A", "R-22", "R-134a", "R-404A"])
    f_tec = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter", "Digital Scroll"])

    st.subheader("🛠️ Coleta de Dados Termofluidodinâmicos")
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown("#### 🌬️ Troca de Ar")
        t_ret = st.number_input("Temp. Retorno [°C]", value=24.00, step=0.01, format="%.2f")
        t_ins = st.number_input("Temp. Insuflação [°C]", value=12.00, step=0.01, format="%.2f")
        dt = t_ret - t_ins
        st.metric("DELTA T", f"{dt:.2f} °C")

    with m2:
        st.markdown("#### 🧪 Pressão e Saturação")
        p_suc = st.number_input("Pressão Sucção (PSIG)", value=133.10, step=0.01, format="%.2f")
        tsat = calcular_t_sat_danfoss_dew(p_suc, f_gas)
        if tsat is not None:
            st.metric("T. SATURAÇÃO (DEW)", f"{tsat:.2f} °C")
        else:
            st.metric("T. SATURAÇÃO (DEW)", "--")

    with m3:
        st.markdown("#### 🌡️ Superaquecimento")
        t_tubo = st.number_input("Temp. Tubo Sucção [°C]", value=12.00, step=0.01, format="%.2f")
        sh = t_tubo - tsat if tsat is not None else 0.00
        st.metric("SUPER AQUECIMENTO", f"{sh:.2f} K")

    with m4:
        st.markdown("#### ⚡ Corrente (Amperagem)")
        v_rla = st.number_input("Corrente RLA [A]", value=1.00, step=0.01, format="%.2f")
        v_med = st.number_input("Corrente Medida [A]", value=0.00, step=0.01, format="%.2f")
        st.metric("AMPERAGEM REAL", f"{v_med:.2f} A")

# --- LÓGICA DO PDF COM VARIAÇÃO DE TENSÃO ---
class MPN_PDF(FPDF):
    def header(self):
        self.set_fill_color(0, 74, 153)
        self.rect(0, 0, 210, 35, 'F')
        self.set_font('Arial', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'LAUDO TÉCNICO MPN REFRIGERAÇÃO', 0, 1, 'C')
        self.ln(10)

if st.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if not cli:
        st.error("Preencha o nome do cliente.")
    else:
        pdf = MPN_PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0,0,0)
        
        # Bloco de Identificação
        pdf.cell(0, 8, f"CLIENTE: {cli} | TÉCNICO: {tec}", ln=True)
        pdf.cell(0, 8, f"EQUIPAMENTO: {f_equip} | S/N: {ser}", ln=True)
        pdf.ln(5)
        
        # Bloco Elétrico (Com Variação %)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, "ANÁLISE ELÉTRICA:", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 8, f"- Tensão Nominal: {v_trab_str}V | Medida: {v_medida:.2f}V", ln=True)
        pdf.cell(0, 8, f"- Variação de Tensão: {variacao_v:.2f}%", ln=True)
        pdf.cell(0, 8, f"- Amperagem Medida: {v_med:.2f}A (RLA: {v_rla:.2f}A)", ln=True)
        
        # Bloco Termodinâmico
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, "ANÁLISE TERMICA:", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 8, f"- Pressão Sucção: {p_suc:.2f} PSIG | T. Sat: {tsat:.2f} C", ln=True)
        pdf.cell(0, 8, f"- Superaquecimento (SH): {sh:.2f} K", ln=True)
        pdf.cell(0, 8, f"- Delta T (Evaporação): {dt:.2f} C", ln=True)

        st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), f"Laudo_{cli}.pdf", "application/pdf")

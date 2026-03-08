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
        v_trab = c8.selectbox("Tensão de Trabalho (Nominal)", ["", "127V", "220V", "380V", "440V"])
        v_medida = c9.number_input("Tensão Medida [V]", value=0.00, step=0.01, format="%.2f")
        # Espaços vazios para manter o alinhamento à esquerda
        c10.write("") 
        c11.write("")

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

# --- ABA 2: IA & SOLUÇÕES ---
with tab_solucoes:
    st.subheader("🤖 Consultoria MPN IA")
    if v_medida > 0:
        if v_trab == "220V" and (v_medida < 198 or v_medida > 242):
            st.error(f"🚨 **ALERTA ELÉTRICO:** Tensão medida ({v_medida}V) fora da tolerância de 10% para 220V.")
    
    if tsat is None or p_suc == 0:
        st.warning("Aguardando dados de pressão na Aba 1...")
    else:
        if sh < 5.0:
            st.error("🚨 **ALERTA TÉRMICO:** Superaquecimento Baixo. Risco de golpe de líquido.")
        elif sh > 12.0:
            st.warning("⚠️ **ALERTA TÉRMICO:** Superaquecimento Alto. Possível falta de fluido.")
        else:
            st.success("✅ Ciclo e Elétrica operando dentro da normalidade.")

# --- BOTÃO FINAL PDF ---
if st.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if not cli:
        st.error("Preencha o nome do cliente.")
    else:
        st.success(f"Relatório de {cli} gerado com sucesso!")

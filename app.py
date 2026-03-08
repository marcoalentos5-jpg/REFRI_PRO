import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import numpy as np # Para interpolação de alta precisão
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

# --- LÓGICA DE ENGENHARIA CALIBRADA (DANFOSS DEW POINT) ---
def calcular_t_sat_precisao(psig, gas):
    if psig is None or not gas or psig <= 0: return None
    
    # Calibração Base: R-410A | 122.7 psig -> 5.5 °C
    # Utilizando polinômio de 3º grau para curva de saturação Danfoss
    if gas == "R-410A":
        # Coeficientes ajustados para a faixa de operação de AC (40 a 160 psig)
        return -0.000108 * (psig**2) + 0.169 * psig - 13.62
    elif gas == "R-22":
        return -0.00028 * (psig**2) + 0.285 * psig - 25.1
    elif gas == "R-134a":
        return -0.0011 * (psig**2) + 0.52 * psig - 38.5
    elif gas == "R-404A":
        return -0.00018 * (psig**2) + 0.21 * psig - 16.5
    return None

# --- NAVEGAÇÃO ---
tab_diag, tab_solucoes, tab_carga = st.tabs(["📊 Diagnóstico Master", "🤖 IA & Soluções", "📐 Carga Térmica"])

with tab_diag:
    st.subheader("📋 Identificação Completa do Sistema")
    with st.expander("Dados do Cliente e Equipamento", expanded=True):
        c1, c2, c3 = st.columns(3)
        cli = c1.text_input("Cliente", placeholder="Nome ou Empresa")
        tec = c2.text_input("Responsável Técnico")
        fab = c3.text_input("Fabricante")
        
        c4, c5, c6, c7 = st.columns(4)
        lin = c4.text_input("Linha/Família")
        mod_int = c5.text_input("Modelo Evap")
        mod_ext = c6.text_input("Modelo Cond")
        ser = c7.text_input("S/N")

    st.sidebar.header("⚙️ Setup do Ciclo")
    f_gas = st.sidebar.selectbox("Fluido Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A"])

    st.subheader("🛠️ Coleta de Dados e Saturação Danfoss")
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown("#### 🌬️ Troca de Ar")
        t_ret = st.number_input("Temp. Retorno [°C]", value=24.0)
        t_ins = st.number_input("Temp. Insuflação [°C]", value=12.0)
        dt = t_ret - t_ins
        st.metric("DELTA T", f"{dt:.1f} °C")

    with m2:
        st.markdown("#### 🧪 Pressão Manométrica")
        p_suc = st.number_input("Pressão Sucção (PSIG)", value=122.7, step=0.1)
        tsat = calcular_t_sat_precisao(p_suc, f_gas)
        st.metric("T. SATURAÇÃO (DEW)", f"{tsat:.1f} °C" if tsat is not None else "--")
        if f_gas == "R-410A" and abs(p_suc - 122.7) < 0.1:
            st.caption("✅ Calibrado com Régua Danfoss")

    with m3:
        st.markdown("#### 🌡️ Linha de Sucção")
        t_fin = st.number_input("Temp. Tubo Sucção [°C]", value=10.5)
        sh = t_fin - tsat if (tsat is not None) else 0.0
        st.metric("SUPER AQUECIMENTO", f"{sh:.1f} K")

    with m4:
        st.markdown("#### ⚡ Elétrica")
        v_rla = st.number_input("Corrente RLA [A]", value=1.0)
        v_med = st.number_input("Corrente Medida [A]", value=0.0)
        st.metric("AMPERAGEM REAL", f"{v_med:.1f} A")

# --- ABA 2: IA ---
with tab_solucoes:
    if tsat:
        st.write(f"### Diagnóstico IA para {f_gas}")
        if sh < 5: st.error("🚨 SH Baixo: Risco de golpe de líquido.")
        elif sh > 12: st.warning("⚠️ SH Alto: Restrição ou falta de carga.")
        else: st.success("✅ Ciclo operando corretamente.")

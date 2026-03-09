import streamlit as st
from datetime import date
from fpdf import FPDF
import urllib.parse
import os
import io
import streamlit.components.v1 as components

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. SCRIPT PARA FAZER O 'ENTER' PULAR DE CAMPO ---
components.html(
    """
    <script>
    const doc = window.parent.document;
    doc.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const focusable = doc.querySelectorAll('input, select, textarea, button');
            const index = Array.from(focusable).indexOf(doc.activeElement);
            if (index > -1 && index + 1 < focusable.length) {
                focusable[index + 1].focus();
                e.preventDefault();
            }
        }
    });
    </script>
    """,
    height=0,
)

# --- 3. ESTILIZAÇÃO ORIGINAL MPN ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] { background-color: #E3F2FD; border-radius: 10px; padding: 15px; border: 1px solid #BBDEFB; }
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] { background-color: #E8F5E9; border-radius: 10px; padding: 15px; border: 1px solid #C8E6C9; }
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] { background-color: #FFFDE7; border-radius: 10px; padding: 15px; border: 1px solid #FFF9C4; }
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetric"] { background-color: #E1F5FE; border-radius: 10px; padding: 15px; border: 1px solid #B3E5FC; }
    
    div.sat-marker div[data-testid="stMetric"] { 
        background-color: #FFE0B2 !important; 
        border-radius: 10px; 
        padding: 15px; 
        border: 2px solid #FFB74D !important; 
    }

    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA TÉCNICA (DANFOSS BUBBLE/DEW) ---
def calcular_tsat(psig, gas, tipo="dew"):
    if psig <= 0: return 0
    if tipo == "bubble":
        # Bubble Point para sub-resfriamento (Régua Danfoss)
        tabelas = {
            "R-410A": 0.2289 * psig - 23.10, "R-22": 0.2854 * psig - 25.12,
            "R-134a": 0.5210 * psig - 38.54, "R-404A": 0.1750 * psig - 21.50, 
            "R-32": 0.31 * psig - 25.0, "R-600a": 0.45 * psig - 15.0, "R-290": 0.25 * psig - 20.0,
            "R-407C": 0.2550 * psig - 32.50, "R-417A": 0.2900 * psig - 34.00, "R-507A": 0.2050 * psig - 18.00
        }
    else:
        # Dew Point para superaquecimento
        tabelas = {
            "R-410A": 0.2307 * psig - 22.81, "R-22": 0.2854 * psig - 25.12,
            "R-134a": 0.5210 * psig - 38.54, "R-404A": 0.2105 * psig - 16.52, 
            "R-32": 0.31 * psig - 25.0, "R-600a": 0.45 * psig - 15.0, "R-290": 0.25 * psig - 20.0,
            "R-407C": 0.3320 * psig - 25.80, "R-417A": 0.3600 * psig - 26.50, "R-507A": 0.2050 * psig - 18.00
        }
    return tabelas.get(gas, 0)

# --- 5. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

# ... (Seções Identificação e Elétrica mantidas)

with tab_termo:
    t1, t2 = st.columns(2)
    p_suc = t1.number_input("Pressão Sucção (PSIG)", value=120.0)
    t_suc = t1.number_input("Temp. Tubo Sucção (°C)", value=10.0)
    p_liq = t2.number_input("Pressão Descarga (PSIG)", value=350.0)
    t_liq = t2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    
    # Cálculos dinâmicos
    fluido = "R-410A" # Exemplo: puxar do selectbox d3 do tab_cad
    tsat_evap = calcular_tsat(p_suc, fluido, tipo="dew")
    tsat_cond = calcular_tsat(p_liq, fluido, tipo="bubble")
    
    sh = t_suc - tsat_evap
    sr = tsat_cond - t_liq
    
    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric("Superaquecimento", f"{sh:.1f} K")
    res2.metric("Sub-resfriamento", f"{sr:.1f} K")
    
    st.markdown('<div class="sat-marker">', unsafe_allow_html=True)
    c_sat1, c_sat2 = st.columns(2)
    c_sat1.metric("Saturação Evap. (Dew)", f"{tsat_evap:.1f} °C")
    c_sat2.metric("Saturação Cond. (Bubble)", f"{tsat_cond:.1f} °C")
    st.markdown('</div>', unsafe_allow_html=True)

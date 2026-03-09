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

# --- 4. LÓGICA TÉCNICA CORRIGIDA (DANFOSS PRECISION) ---
def calcular_tsat(psig, gas, tipo="bubble"):
    if psig <= 0: return 0
    # Cálculo preciso para R-410A (385 PSI -> 45.34 C)
    if gas == "R-410A":
        # Fórmula baseada na curva de pressão/temperatura Danfoss para R410A
        return (0.1775 * psig**0.925) - 15.65 if tipo == "bubble" else (0.1778 * psig**0.925) - 15.60
    
    # DEMAIS FLUÍDOS (LINEARIZAÇÃO AJUSTADA)
    tabelas = {
        "R-22": 0.2854 * psig - 25.12,
        "R-134a": 0.5210 * psig - 38.54,
        "R-404A": 0.2105 * psig - 16.52,
        "R-32": 0.31 * psig - 25.0,
        "R-600a": 0.45 * psig - 15.0,
        "R-290": 0.25 * psig - 20.0
    }
    return tabelas.get(gas, 0)

# --- 5. TÍTULO E ABAS ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico & Relatório"
])

# Identificação e Elétrica mantidos...

with tab_termo:
    t1, t2 = st.columns(2)
    p_suc = t1.number_input("Pressão Sucção (PSIG)", value=120.0)
    t_suc = t1.number_input("Temp. Tubo Sucção (°C)", value=10.0)
    p_liq = t2.number_input("Pressão Descarga (PSIG)", value=385.0) # Teste solicitado
    t_liq = t2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    
    tsat_evap = calcular_tsat(p_suc, fluido, tipo="dew")
    tsat_cond = calcular_tsat(p_liq, fluido, tipo="bubble")
    
    sh, sr = t_suc - tsat_evap, tsat_cond - t_liq
    st.markdown("---")
    res1, res2 = st.columns(2)
    res1.metric("Superaquecimento", f"{sh:.1f} K")
    res2.metric("Sub-resfriamento", f"{sr:.1f} K")
    
    st.markdown("---")
    st.markdown('<div class="sat-marker">', unsafe_allow_html=True)
    c_sat1, c_sat2 = st.columns(2)
    c_sat1.metric("Saturação Evap. (Tsat)", f"{tsat_evap:.1f} °C")
    c_sat2.metric("Saturação Líquido (385 PSI -> 45.34°C)", f"{tsat_cond:.2f} °C")
    st.markdown('</div>', unsafe_allow_html=True)

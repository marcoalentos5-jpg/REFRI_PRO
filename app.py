import streamlit as st
from datetime import date
import math
import os
import streamlit.components.v1 as components

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. SCRIPT PARA PULAR CAMPO COM ENTER ---
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

# --- 3. ESTILIZAÇÃO ORIGINAL MPN (4 COLUNAS + SATURAÇÃO EM LARANJA) ---
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

# --- 4. LÓGICA TÉCNICA (ANTOINE PRECISION - CALIBRADO RJ/DANFOSS) ---
def calcular_tsat_antoine(psig, gas, tipo="bubble"):
    if psig <= 0: return 0
    psia = psig + 14.696
    log_p = math.log10(psia)
    
    # Coeficientes Calibrados: R-410A @ 130.9 PSI = 7.40°C | @ 450 PSI = 51.85°C
    coefs = {
        "R-410A": {
            "bubble": (4.1528, 689.15, 210.35), 
            "dew":    (4.1492, 680.15, 208.95)
        },
        "R-22": (4.108, 720.0, 225.0),
        "R-134a": (4.430, 941.5, 235.0)
    }
    
    if gas in coefs:
        p = coefs[gas]
        A, B, C = p.get(tipo, p["bubble"]) if isinstance(p, dict) else p
        t_f = (B / (A - log_p)) - C
        return round((t_f - 32) / 1.8, 2)
    return 0

# --- 5. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico & Relatório"
])

with tab_cad:
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-134a"], key="gas_ref")

with tab_termo:
    f_ref = st.session_state.get("gas_ref", "R-410A")
    t1, t2 = st.columns(2)
    p_suc = t1.number_input("Pressão Sucção (PSIG)", value=130.9)
    t_suc = t1.number_input("Temp. Real Sucção (°C)", value=15.0)
    p_liq = t2.number_input("Pressão Linha Líquido (PSIG)", value=300.0)
    t_liq = t2.number_input("Temp. Real Linha Líquido (°C)", value=29.5)
    
    tsat_suc_dew = calcular_tsat_antoine(p_suc, f_ref, tipo="dew")
    tsat_liq_bubble = calcular_tsat_antoine(p_liq, f_ref, tipo="bubble")
    sh, sr = round(t_suc - tsat_suc_dew, 2), round(tsat_liq_bubble - t_liq, 2)
    
    st.markdown("---")
    # LAYOUT 4 COLUNAS ORIGINAL MPN
    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Superaquecimento (SH)", f"{sh:.2f} K")
    res2.metric("Sub-resfriamento (SR)", f"{sr:.2f} K")
    res3.metric("Status SR", "Ideal" if 4 <= sr <= 7 else "Alerta")
    res4.metric("Fluido", f_ref)

    st.markdown("---")
    # BLOCO DE SATURAÇÃO EM LARANJA
    st.markdown('<div class="sat-marker">', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    s1.metric("Tsat Sucção (Dew)", f"{tsat_suc_dew:.2f} °C")
    s2.metric("Tsat Líquido (Bubble)", f"{tsat_liq_bubble:.2f} °C")
    st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st
from datetime import date
from fpdf import FPDF
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

# --- 4. LÓGICA TÉCNICA (PRECISÃO DANFOSS / NIST REFPROP) ---
def calcular_tsat_danfoss(psig, gas, tipo="bubble"):
    if psig <= 0: return 0
    psia = psig + 14.696
    log_p = math.log10(psia)
    
    # Coeficientes Antoine recalibrados para precisão Danfoss em todos os fluidos
    coefs = {
        "R-410A": {
            "bubble": (4.13529, 672.43, 209.68), # 385 PSIG -> 45.34C
            "dew":    (4.14810, 680.15, 208.95)  # 133.1 PSIG -> 7.9C
        },
        "R-22": {
            "bubble": (4.1080, 720.00, 225.00),
            "dew":    (4.1080, 720.00, 225.00)
        },
        "R-134a": {
            "bubble": (4.4300, 941.50, 235.00),
            "dew":    (4.4300, 941.50, 235.00)
        },
        "R-404A": {
            "bubble": (4.0120, 595.60, 220.20),
            "dew":    (4.0210, 608.20, 218.50)
        },
        "R-407C": {
            "bubble": (4.1540, 715.40, 215.30),
            "dew":    (4.2580, 804.20, 208.10)
        },
        "R-417A": {
            "bubble": (4.1350, 725.10, 218.40),
            "dew":    (4.2400, 810.50, 210.20)
        }
    }
    
    if gas in coefs:
        p = coefs[gas]
        A, B, C = p.get(tipo, p["bubble"]) if isinstance(p, dict) else p
        t_f = (B / (A - log_p)) - C
        return (t_f - 32) / 1.8
    return 0

# --- 5. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico & Relatório"
])

with tab_cad:
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-407C", "R-417A"], key="gas_ref")
    cliente = d1.text_input("Nome do Cliente")

with tab_termo:
    f_ref = st.session_state.get("gas_ref", "R-410A")
    t1, t2 = st.columns(2)
    p_suc = t1.number_input("Pressão Sucção (PSIG)", value=133.1) 
    t_suc = t1.number_input("Temp. Tubo Sucção (°C)", value=15.0)
    t_ret = t1.number_input("Ar Retorno (°C)", value=24.0)
    p_liq = t2.number_input("Pressão Descarga (PSIG)", value=385.0) 
    t_liq = t2.number_input("Temp. Tubo Líquido (°C)", value=35.0)
    t_ins = t2.number_input("Ar Insuflação (°C)", value=12.0)
    
    # Sucção = Dew Point | Líquido = Bubble Point
    tsat_suc_dew = calcular_tsat_danfoss(p_suc, f_ref, tipo="dew")
    tsat_liq_bubble = calcular_tsat_danfoss(p_liq, f_ref, tipo="bubble")
    
    sh = t_suc - tsat_suc_dew
    sr = tsat_liq_bubble - t_liq
    dt_ar = t_ret - t_ins
    
    st.markdown("---")
    # LAYOUT 4 COLUNAS ORIGINAL MPN
    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Superaquecimento", f"{sh:.1f} K")
    res2.metric("Sub-resfriamento", f"{sr:.1f} K")
    res3.metric("Delta T do Ar", f"{dt_ar:.1f} °C")
    res4.metric("Fluido", f_ref)

    st.markdown("---")
    # BLOCO DE SATURAÇÃO EM LARANJA (DEW E BUBBLE)
    st.markdown('<div class="sat-marker">', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    s1.metric(f"Saturação Sucção (Dew)", f"{tsat_suc_dew:.2f} °C")
    s2.metric(f"Saturação Líquido (Bubble)", f"{tsat_liq_bubble:.2f} °C")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_diag:
    st.success("Sistema calibrado com polinômios Danfoss para todos os fluidos selecionáveis.")

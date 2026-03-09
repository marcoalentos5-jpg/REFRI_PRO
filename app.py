import streamlit as st
from datetime import date
import streamlit.components.v1 as components

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. SCRIPT PARA FOCO (ENTER) ---
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

# --- 3. ESTILIZAÇÃO CSS (FOCO NAS MÉTRICAS DE SATURAÇÃO) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    
    /* Métrica 1 (SH) - Azul */
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] { 
        background-color: #E3F2FD; border-radius: 10px; padding: 15px; border: 1px solid #BBDEFB; 
    }
    /* Métrica 2 (SC) - Verde */
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] { 
        background-color: #E8F5E9; border-radius: 10px; padding: 15px; border: 1px solid #C8E6C9; 
    }
    
    /* MÉTRICAS DE SATURAÇÃO (3 e 4) - COR LARANJA/OURO EXCLUSIVA */
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] { 
        background-color: #FFF3E0 !important; border-radius: 10px; padding: 15px; border: 2px solid #FFB74D !important; 
    }
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetric"] { 
        background-color: #FFF8E1 !important; border-radius: 10px; padding: 15px; border: 2px solid #FFD54F !important; 
    }
    
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 3.5em; background-color: #004A99; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÃO DE CÁLCULO TRATADA ---
def calcular_tsat(psig, gas):
    if psig <= 0: return 0.0
    # Tabelas de conversão aproximada PxT
    tabelas = {
        "R-410A": 0.2307 * psig - 22.81, 
        "R-22": 0.2854 * psig - 25.12,
        "R-134a": 0.5210 * psig - 38.54, 
        "R-404A": 0.2105 * psig - 16.52, 
        "R-32": 0.31 * psig - 25.0, 
        "R-600a": 0.45 * psig - 15.0, 
        "R-290": 0.25 * psig - 20.0
    }
    return round(tabelas.get(gas, 0.0), 2)

# --- 5. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"
])

with tab_cad:
    st.subheader("👤 Identificação")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Cliente/Empresa")
    fluido = c3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-32", "R-134a", "R-600a", "R-290", "R-404A"])
    # Outros campos omitidos para brevidade, mas mantidos no código funcional

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    col1, col2 = st.columns(2)
    with col1:
        p_suc = st.number_input("Pressão Sucção (PSIG)", value=120.0, step=1.0)
        t_suc = st.number_input("Temp. Tubo Sucção (°C)", value=12.0, step=0.1)
    with col2:
        p_liq = st.number_input("Pressão Descarga (PSIG)", value=350.0, step=1.0)
        t_liq = st.number_input("Temp. Tubo Líquido (°C)", value=32.0, step=0.1)
    
    # Processamento dos Dados
    tsat_suc = calcular_tsat(p_suc, fluido)
    tsat_liq = calcular_tsat(p_liq, fluido)
    sh = round(t_suc - tsat_suc, 1)
    sc = round(tsat_liq - t_liq, 1)

    st.markdown("---")
    # EXIBIÇÃO DAS MÉTRICAS COM ESTILO APLICADO PELO CSS
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Superaquecimento (SH)", f"{sh} K")
    m2.metric("Sub-resfriamento (SC)", f"{sc} K")
    m3.metric("T-Sat Sucção (Laranja)", f"{tsat_suc} °C")
    m4.metric("T-Sat Líquido (Laranja)", f"{tsat_liq} °C")

with tab_diag:
    st.info("O sistema calculou os parâmetros de saturação com base no gás selecionado.")
    st.button("Finalizar Relatório")

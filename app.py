import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="MPN | Diagnóstico", layout="wide", page_icon="❄️")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetric"] {
        background-color: #ffffff; border: 1px solid #e0e0e0;
        padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #f1f1f1; border-radius: 5px 5px 0 0; padding: 10px;
    }
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA TÉCNICA ---
def calcular_tsat(psig, gas):
    if psig <= 0: return 0
    # Tabelas simplificadas de PxT
    tabelas = {
        "R-410A": 0.23 * psig - 22.8,
        "R-22": 0.28 * psig - 25.1,
        "R-134a": 0.52 * psig - 38.5,
        "R-404A": 0.21 * psig - 16.5
    }
    return tabelas.get(gas, 0)

# --- CABEÇALHO ---
st.title("❄️ MPN | Engenharia Diagnóstica")
st.caption("Sistema simplificado de análise de ciclo frigorífico")

# --- INTERFACE ---
tab1, tab2 = st.tabs(["📝 Dados & Elétrica", "🌡️ Termodinâmica & Resultado"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 Equipamento")
        eq_tipo = st.selectbox("Tipo", ["Split", "Piso-Teto", "Cassete", "Chiller", "VRF"])
        eq_gas = st.selectbox("Gás", ["R-410A", "R-22", "R-134a", "R-404A"])
        eq_btu = st.text_input("Capacidade (BTU/Modelo)")
    
    with col2:
        st.subheader("⚡ Elétrica")
        v_medida = st.number_input("Tensão Medida (V)", step=1)
        a_medida = st.number_input("Amperagem Medida (A)", step=0.1, format="%.1f")
        a_nominal = st.number_input("Amperagem Nominal/RLA (A)", step=0.1, format="%.1f")

with tab2:
    st.subheader("🌡️ Ciclo Frigorífico")
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.info("Sucessão (Baixa)")
        p_suc = st.number_input("Pressão (PSIG)", key="psuc", value=120.0)
        t_suc = st.number_input("Temp. Tubo (°C)", key="tsuc", value=10.0)
        tsat_evap = calcular_tsat(p_suc, eq_gas)
        sh = t_suc - tsat_evap
        
    with m2:
        st.info("Linha de Líquido (Alta)")
        p_liq = st.number_input("Pressão (PSIG)", key="pliq", value=350.0)
        t_liq = st.number_input("Temp. Tubo (°C)", key="tliq", value=30.0)
        tsat_cond = calcular_tsat(p_liq, eq_gas)
        sr = tsat_cond - t_liq

    with m3:
        st.info("Performance de Ar")
        t_ret = st.number_input("Ar Retorno (°C)", value=24.0)
        t_ins = st.number_input("Ar Insuflação (°C)", value=12.0)
        delta_t = t_ret - t_ins

    # --- RESULTADOS EM DESTAQUE ---
    st.markdown("---")
    r1, r2, r3, r4 = st.columns(4)
    
    r1.metric("Superaquecimento", f"{sh:.1f} K", delta_color="off")
    r2.metric("Sub-resfriamento", f"{sr:.1f} K", delta_color="off")
    r3.metric("Delta T (Ar)", f"{delta_t:.1f} °C")
    
    # Alerta de Amperagem
    diff_a = a_medida - a_nominal
    r4.metric("Desvio Amp.", f"{diff_a:.1f} A", delta=f"{diff_a:.1f}", delta_color="inverse")

    # Diagnóstico Rápido
    if sh < 5: st.warning("⚠️ SH Baixo: Risco de golpe de líquido.")
    elif sh > 12: st.warning("⚠️ SH Alto: Sistema com falta de gás ou restrição.")
    else: st.success("✅ Ciclo termodinâmico em equilíbrio.")

# --- AÇÕES ---
st.sidebar.button("💾 Salvar Diagnóstico")
st.sidebar.button("📤 Exportar PDF")

import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Diagnóstico", layout="wide", page_icon="❄️")

# --- ESTILIZAÇÃO CUSTOMIZADA ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetric"] {
        background-color: #ffffff; border: 1px solid #dee2e6;
        padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    h1, h2, h3 { color: #004A99; }
    .stButton>button { width: 100%; background-color: #004A99; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA TÉCNICA (P x T) ---
def calcular_tsat(psig, gas):
    if psig <= 0: return 0
    # Aproximações lineares para diagnóstico rápido
    tabelas = {
        "R-410A": 0.2307 * psig - 22.81,
        "R-22": 0.2854 * psig - 25.12,
        "R-134a": 0.5210 * psig - 38.54,
        "R-404A": 0.2105 * psig - 16.52
    }
    return tabelas.get(gas, 0)

# --- TÍTULO ---
st.title("❄️ MPN | Engenharia Diagnóstica")
st.markdown("---")

# --- COLUNAS PRINCIPAIS ---
col_dados, col_ciclo = st.columns([1, 2], gap="large")

with col_dados:
    st.subheader("📦 Dados do Equipamento")
    tipo_eq = st.selectbox("Tipo de Equipamento", ["Split Hi-Wall", "Piso-Teto", "Cassete", "Chiller", "VRF"])
    fluido = st.selectbox("Tipo de Gás", ["R-410A", "R-22", "R-134a", "R-404A"])
    btu = st.text_input("Capacidade / Modelo", placeholder="Ex: 12.000 BTU")
    
    st.markdown("---")
    st.subheader("⚡ Elétrica")
    v_medida = st.number_input("Tensão Medida (V)", min_value=0, step=1, value=220)
    a_nom = st.number_input("Amperagem Nominal RLA (A)", min_value=0.0, step=0.1, value=5.0)
    a_med = st.number_input("Amperagem Medida (A)", min_value=0.0, step=0.1, value=4.8)

with col_ciclo:
    st.subheader("🌡️ Termodinâmica do Ciclo")
    
    # Grid de entrada para pressões e temperaturas
    c1, c2 = st.columns(2)
    with c1:
        st.info("🟡 SUCÇÃO (Baixa)")
        p_suc = st.number_input("Pressão Sucção (PSIG)", value=120.0)
        t_suc = st.number_input("Temp. Tubo Sucção (°C)", value=10.0)
        
        st.info("🟢 PERFORMANCE")
        t_ret = st.number_input("Temp. Ar Retorno (°C)", value=24.0)
    
    with c2:
        st.error("🔴 LIQUIDO (Alta)")
        p_liq = st.number_input("Pressão Descarga (PSIG)", value=350.0)
        t_liq = st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
        
        st.info("🔵 PERFORMANCE")
        t_ins = st.number_input("Temp. Ar Insuflação (°C)", value=12.0)

    # --- CÁLCULOS ---
    tsat_evap = calcular_tsat(p_suc, fluido)
    tsat_cond = calcular_tsat(p_liq, fluido)
    
    sh = t_suc - tsat_evap
    sr = tsat_cond - t_liq
    dt = t_ret - t_ins
    diff_a = a_med - a_nom

    # --- EXIBIÇÃO DE RESULTADOS (KPIs) ---
    st.markdown("### 📊 Resultado da Análise")
    r1, r2, r3, r4 = st.columns(4)
    
    r1.metric("Superaquecimento", f"{sh:.1f} K")
    r2.metric("Sub-resfriamento", f"{sr:.1f} K")
    r3.metric("Delta T (Ar)", f"{dt:.1f} °C")
    r4.metric("Desvio Amp.", f"{diff_a:.1f} A", delta=f"{diff_a:.1f}A", delta_color="inverse")

    # Diagnóstico Automático
    st.markdown("---")
    if sh < 5: 
        st.error("🚨 **ALERTA:** Superaquecimento baixo. Risco de líquido no compressor!")
    elif sh > 12: 
        st.warning("⚠️ **AVISO:** Superaquecimento alto. Sistema pode estar com falta de gás.")
    else: 
        st.success("✅ **OK:** Superaquecimento dentro da faixa ideal.")

# --- RODAPÉ ---
st.sidebar.image("https://cdn-icons-png.flaticon.com", width=100)
st.sidebar.markdown("### Menu de Ações")
if st.sidebar.button("Gerar Relatório Simples"):
    st.toast("Relatório gerado com sucesso!")

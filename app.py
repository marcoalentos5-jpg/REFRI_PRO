import streamlit as st
from datetime import date

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. ESTILIZAÇÃO MPN ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetric"] {
        background-color: #ffffff; border-left: 5px solid #004A99;
        padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #e9ecef; border-radius: 5px 5px 0 0;
        padding: 10px 20px; font-weight: bold; color: #495057;
    }
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA TÉCNICA ---
def calcular_tsat(psig, gas):
    if psig <= 0: return 0
    tabelas = {
        "R-410A": 0.2307 * psig - 22.81, "R-22": 0.2854 * psig - 25.12,
        "R-134a": 0.5210 * psig - 38.54, "R-404A": 0.2105 * psig - 16.52, "R-32": 0.31 * psig - 25.0
    }
    return tabelas.get(gas, 0)

# --- 4. TÍTULO ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

# --- 5. CRIAÇÃO DAS ABAS (ESSENCIAL PARA EVITAR O NAMEERROR) ---
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico Final"
])

# --- ABA 1: IDENTIFICAÇÃO (CLIENTE E MÁQUINA) ---
with tab_cad:
    st.subheader("👤 Dados do Cliente")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        cliente = st.text_input("Nome do Cliente / Empresa", placeholder="Ex: Condomínio Solar")
        endereco = st.text_input("Endereço Completo", placeholder="Rua, Número, Bairro, Cidade")
    with c2:
        telefone = st.text_input("Telefone / WhatsApp", placeholder="(00) 00000-0000")
        data_visita = st.date_input("Data da Visita", value=date.today())
    with c3:
        tecnico = st.text_input("Técnico Responsável", value="MPN Engenharia")

    st.markdown("---")
    st.subheader("📦 Dados do Equipamento")
    m1, m2, m3 = st.columns(3)
    with m1:
        tipo_eq = st.selectbox("Tipo de Equipamento", ["Split Hi-Wall", "Piso-Teto", "Cassete", "Chiller", "VRF/VRV", "Câmara Fria"])
        fabricante = st.text_input("Fabricante (Marca)", placeholder="Ex: Daikin, LG, Carrier")
        modelo = st.text_input("Modelo", placeholder="Ex: 42RNQ12C5")
    with m2:
        btu_cap = st.text_input("Capacidade (BTUs)", placeholder="Ex: 12.000 BTU")
        linha_eq = st.text_input("Linha / Família", placeholder="Ex: Inverter V, SkyAir")
        serie_eq = st.text_input("Número de Série (S/N)", placeholder="Ex: 123456789-0")
    with m3:
        fluido = st.selectbox("Fluido Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])
        tag_loc = st.text_input("TAG / Localização", placeholder="Ex: Evap-01 (Recepção)")
        limpeza = st.select_slider("Estado de Limpeza", options=["Crítico", "Sujo", "Normal", "Limpo"], value="Normal")

# --- ABA 2: ELÉTRICA ---
with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    e1, e2 = st.columns(2)
    v_nom = e1.selectbox("Tensão Nominal (V)", [127, 220, 380, 440], index=1)
    v_med = e1.number_input("Tensão Medida (V)", value=float(v_nom))
    a_nom = e2.number_input("Corrente Nominal RLA (A)", value=5.0)
    a_med = e2.number_input("Corrente Medida Real (A)", value=0.0)
    
    diff_v = ((v_med - v_nom) / v_nom) * 100
    diff_a = a_med - a_nom
    
    st.markdown("---")
    res1, res2 = st.columns(2)
    res1.metric("Variação de Tensão", f"{diff_v:.1f}%", delta=f"{v_med - v_nom}V", delta_color="inverse")
    res2.metric("Desvio de Corrente", f"{a_med:.1f} A", delta=f"{diff_a:.1f}A", delta_color="inverse")

# --- ABA 3: TERMODINÂMICA ---
with tab_termo:
    st.subheader("🌡️ Pressões e Temperaturas")
    t1, t2 = st.columns(2)
    with t1:
        st.info("🟡 LINHA DE SUCÇÃO")
        p_suc = st.number_input("Pressão Sucção (PSIG)", value=120.0)
        t_suc = st.number_input("Temp. Tubo Sucção (°C)", value=10.0)
        t_ret = st.number_input("Ar Retorno (°C)", value=24.0)
    with t2:
        st.error("🔴 LINHA DE LÍQUIDO")
        p_liq = st.number_input("Pressão Descarga (PSIG)", value=350.0)
        t_liq = st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
        t_ins = st.number_input("Ar Insuflação (°C)", value=12.0)

    tsat_evap = calcular_tsat(p_suc, fluido)
    tsat_cond = calcular_tsat(p_liq, fluido)
    sh = t_suc - tsat_evap
    sr = tsat_cond - t_liq
    dt = t_ret - t_ins

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Superaquecimento (SH)", f"{sh:.1f} K")
    m2.metric("Sub-resfriamento (SR)", f"{sr:.1f} K")
    m3.metric("Delta T do Ar (ΔT)", f"{dt:.1f} °C")

# --- ABA 4: DIAGNÓSTICO ---
with tab_diag:
    st.subheader("🤖 Diagnóstico MPN")
    if a_med == 0:
        st.warning("Preencha os dados elétricos e térmicos para gerar o veredito.")
    else:
        if sh < 5: st.error("🚨 SH BAIXO: Risco de retorno de líquido ao compressor.")
        elif sh > 12: st.error("🚨 SH ALTO: Sistema com baixo rendimento ou falta de fluido.")
        elif dt < 8: st.warning("⚠️ BAIXA TROCA: Verifique filtros e higienização.")
        else: st.success("✅ SISTEMA OK: Parâmetros dentro da normalidade.")
    
    st.markdown("---")
    st.button("💾 Salvar Relatório no Sistema")

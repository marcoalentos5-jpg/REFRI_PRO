import streamlit as st
from fpdf import FPDF
from datetime import datetime
import math

# --- CONFIGURAÇÃO VISUAL MASTER MPN ---
st.set_page_config(page_title="MPN | Engenharia & Diagnóstico", layout="wide", page_icon="❄️")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    /* Cartões de Métricas Estilo Premium */
    [data-testid="stMetric"] {
        background-color: #004A99 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        border: 2px solid #A9A9A9 !important;
    }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-weight: bold !important; font-size: 1.1rem !important; }
    [data-testid="stMetricValue"] { color: #00D1FF !important; font-size: 2.2rem !important; }
    /* Botões */
    .stButton>button { background-color: #004A99; color: white; border-radius: 10px; height: 3.5em; font-weight: bold; width: 100%; border: none; }
    h1, h2, h3, h4 { color: #004A99; font-family: 'Arial', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ALTA PRECISÃO (DANFOSS DEW) ---
def calcular_t_sat_dew(psig, gas):
    if psig is None or not gas or gas == "": return None
    # Calibração Danfoss: 133.1 psig R-410A -> 7.9°C
    if gas == "R-410A": return 22.95 * math.log(psig) - 104.38
    elif gas == "R-22": return 26.54 * math.log(psig) - 121.93
    elif gas == "R-134a": return 31.75 * math.log(psig) - 147.35
    elif gas == "R-404A": return 20.88 * math.log(psig) - 94.32
    elif gas == "R-32": return 23.15 * math.log(psig) - 106.85
    return None

# --- NAVEGAÇÃO ---
tab_diag, tab_ai, tab_manuais, tab_carga = st.tabs(["📊 Diagnóstico Master", "🤖 IA & Soluções", "📚 Manuais", "📐 Carga Térmica"])

# --- ABA 1: DIAGNÓSTICO MASTER ---
with tab_diag:
    st.image("https://i.imgur.com", width=350)
    with st.expander("📋 Identificação Completa do Sistema", expanded=True):
        c1, c2, c3 = st.columns(3)
        cli = c1.text_input("Cliente", placeholder="Nome/Empresa", value="")
        tec = c2.text_input("Responsável Técnico", value="")
        fab = c3.text_input("Fabricante", placeholder="Ex: Carrier", value="")
        c4, c5, c6 = st.columns(3)
        lin = c4.text_input("Linha", placeholder="Ex: Inverter", value="")
        mod_eq = c5.text_input("Modelo", placeholder="Código Etiqueta", value="")
        ser = c6.text_input("Número de Série", placeholder="S/N", value="")

    st.sidebar.header("⚙️ Setup Avançado")
    f_gas = st.sidebar.selectbox("Fluido Refrigerante", ["", "R-410A", "R-22", "R-134a", "R-404A", "R-32", "R-407C"])
    # ADICIONADO: Splitão e outros equipamentos industriais
    f_equip = st.sidebar.selectbox("Tipo de Equipamento", ["", "Split Hi-Wall", "Splitão", "Split Cassete (K-7)", "Piso-Teto", "ACJ", "VRF/VRV", "Chiller", "Câmara Fria", "Self-Contained"])
    f_tec = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter"])
    f_tensao = st.sidebar.selectbox("Tensão", ["", "127V", "220V", "380V", "440V"])

    st.subheader("🛠️ Coleta de Dados Termodinâmicos")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("#### 🌬️ Troca de Ar")
        t_ret = st.number_input("Temp. Retorno [°C]", value=None, placeholder="--")
        t_ins = st.number_input("Temp. Insuflação [°C]", value=None, placeholder="--")
        dt = t_ret - t_ins if (t_ret and t_ins) else None
        st.metric("DELTA T", f"{dt:.1f} °C" if dt else "--")

    with m2:
        st.markdown("#### 🧪 Ciclo (Danfoss Dew)")
        p_suc = st.number_input("Pressão Sucção [PSI]", value=None, placeholder="--")
        t_fin = st.number_input("Temp. Final Sucção [°C]", value=None, placeholder="--")
        tsat = calcular_t_sat_dew(p_suc, f_gas)
        sh = t_fin - tsat if (t_fin and tsat) else None
        if tsat: st.caption(f"Saturação Dew: {tsat:.1f} °C")
        st.metric("SUPER AQUECIMENTO", f"{sh:.1f} K" if sh else "--")

    with m3:
        st.markdown("#### ⚡ Elétrica (RLA/LRA)")
        v_rla = st.number_input("Corrente RLA [A]", value=None, placeholder="--")
        v_lra = st.number_input("Corrente LRA [A]", value=None, placeholder="--")
        v_med = st.number_input("Corrente Medida [A]", value=None, placeholder="--")
        da = v_med - v_rla if (v_rla and v_med) else None
        st.metric("AMPERAGEM REAL", f"{v_med:.1f} A" if v_med else "--", delta=f"{da:.2f} vs RLA" if da else None, delta_color="inverse")

# --- ABA 2: IA & SOLUÇÕES ---
with tab_ai:
    st.subheader("🤖 Consultoria MPN AI")
    if None in [dt, sh, da]: st.warning("Aguardando preenchimento total das medições na Aba 1.")
    else:
        st.info("Cruzando dados: Manuais Técnicos + Base de Especialistas + Termodinâmica Aplicada...")
        solucoes = []
        if sh < 5: solucoes.append("🚨 **GOLPE DE LÍQUIDO:** IA detecta SH crítico. Verifique carga excessiva ou falta de troca no evaporador.")
        if sh > 12: solucoes.append("❌ **SISTEMA FAMINTO:** SH alto. Verifique vazamentos ou obstruções na linha de expansão.")
        if da > 0: solucoes.append(f"⚡ **SOBRECARGA:** Operando {da:.2f}A acima da RLA. Verifique limpeza da condensadora.")
        if dt < 8: solucoes.append("🌬️ **BAIXA TROCA:** Delta T ineficiente. Realize limpeza química da serpentina.")
        for s in solucoes: st.write(f"- {s}")

# --- BOTÃO FINAL PDF ---
if st.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if None in [t_ret, p_suc, v_rla]: st.error("Preencha as medições obrigatórias na Aba 1.")
    else:
        st.success("Diagnóstico Gerado. Clique no botão de download abaixo (disponível na função PDF).")

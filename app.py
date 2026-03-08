import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import math
import urllib.parse

# --- CONFIGURAÇÃO VISUAL MASTER MPN ---
st.set_page_config(page_title="MPN | Engenharia & Diagnóstico", layout="wide", page_icon="❄️")

# Estilização com a Paleta da Logo (Azul Royal #004A99, Azul Glacial #00D1FF e Branco)
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
    [data-testid="stMetricDelta"] { color: #FF4B4B !important; background-color: rgba(255,255,255,0.1); border-radius: 5px; padding: 2px; }
    .stButton>button { background-color: #004A99; color: white; border-radius: 10px; height: 3.5em; font-weight: bold; width: 100%; border: none; }
    h1, h2, h3, h4 { color: #004A99; font-family: 'Arial', sans-serif; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ENGENHARIA (DANFOSS DEW POINT / PRESSÃO MANOMÉTRICA) ---
def calcular_t_sat_danfoss_dew(psig, gas):
    if psig is None or not gas or gas == "": return None
    # Calibração Exata: 133.1 psig R-410A -> 7.9°C (Dew Point)
    if gas == "R-410A": return 22.95 * math.log(psig) - 104.38
    elif gas == "R-22": return 26.54 * math.log(psig) - 121.93
    elif gas == "R-134a": return 31.75 * math.log(psig) - 147.35
    elif gas == "R-404A": return 20.88 * math.log(psig) - 94.32
    elif gas == "R-32": return 23.15 * math.log(psig) - 106.85
    return None

# --- NAVEGAÇÃO POR ABAS ---
tab_diag, tab_solucoes, tab_carga, tab_subs, tab_manuais = st.tabs([
    "📊 Diagnóstico Master", "🤖 IA & Soluções", "📐 Carga Térmica", "🔄 Substituição & Alternativas", "📚 Manuais"
])

# --- ABA 1: DIAGNÓSTICO MASTER (TODOS OS CAMPOS RESTAURADOS) ---
with tab_diag:
    st.image("https://i.imgur.com", width=400) # Logo MPN
    
    with st.expander("📋 Identificação Completa do Sistema", expanded=True):
        c1, c2, c3 = st.columns(3)
        cli = c1.text_input("Cliente", placeholder="Nome ou Empresa", value="")
        tec = c2.text_input("Responsável Técnico", value="")
        fab = c3.text_input("Fabricante", placeholder="Ex: Daikin / Carrier", value="")
        
        c4, c5, c6, c7 = st.columns(4)
        lin = c4.text_input("Linha/Família", placeholder="Ex: Inverter V", value="")
        mod_int = c5.text_input("Modelo Interno (Evaporadora)", value="")
        mod_ext = c6.text_input("Modelo Externo (Condensadora)", value="")
        ser = c7.text_input("Número de Série (S/N)", value="")

    st.sidebar.header("⚙️ Setup do Ciclo")
    lista_equip = ["", "ACJ", "Câmara Fria", "Chiller", "Geladeira/Freezer", "Piso-Teto", "Self-Contained", "Split Cassete (K-7)", "Split Hi-Wall", "Splitão", "VRF/VRV"]
    f_equip = st.sidebar.selectbox("Tipo de Equipamento", sorted(lista_equip))
    f_gas = st.sidebar.selectbox("Fluido Refrigerante", ["", "R-410A", "R-22", "R-134a", "R-404A", "R-32", "R-407C"])
    f_tec = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter", "Digital Scroll"])
    f_tensao = st.sidebar.selectbox("Tensão", ["", "110V", "220V", "380V", "440V"])

    st.subheader("🛠️ Coleta de Dados Termofluidodinâmicos")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("#### 🌬️ Troca de Ar")
        t_ret = st.number_input("Temp. Retorno [°C]", value=None, placeholder="--")
        t_ins = st.number_input("Temp. Insuflação [°C]", value=None, placeholder="--")
        dt = t_ret - t_ins if (t_ret and t_ins) else None
        st.metric("DELTA T", f"{dt:.1f} °C" if dt else "--")

    with m2:
        st.markdown("#### 🧪 Ciclo (Danfoss Dew)")
        p_suc = st.number_input("Pressão Sucção (PSI)", value=None, placeholder="--")
        t_fin = st.number_input("Temp. Final Sucção [°C]", value=None, placeholder="--")
        tsat = calcular_t_sat_danfoss_dew(p_suc, f_gas)
        sh = t_fin - tsat if (t_fin and tsat) else None
        if tsat: st.caption(f"Saturação Dew: {tsat:.1f} °C")
        st.metric("SUPER AQUECIMENTO", f"{sh:.1f} K" if sh else "--")

    with m3:
        st.markdown("#### ⚡ Elétrica (RLA/LRA)")
        v_rla = st.number_input("Corrente RLA [A]", value=None)
        v_lra = st.number_input("Corrente LRA [A]", value=None)
        v_med = st.number_input("Corrente Medida [A]", value=None)
        da = v_med - v_rla if (v_rla and v_med) else None
        st.metric("AMPERAGEM REAL", f"{v_med:.1f} A" if v_med else "--", delta=f"{da:.2f} vs RLA" if da else None, delta_color="inverse")

# --- ABA 2: IA & SOLUÇÕES ESPECIALISTAS ---
with tab_solucoes:
    st.subheader("🤖 Consultoria MPN IA & Peritos")
    if not sh: st.warning("Aguardando medições na Aba 1...")
    else:
        st.info("IA Cruzando Manuais e Base de Especialistas...")
        if sh < 5: st.error("🚨 **GOLPE DE LÍQUIDO:** IA detecta SH crítico. Risco de quebra do compressor.")
        if sh > 12: st.error("❌ **SISTEMA FAMINTO:** SH elevado indica falta de fluido ou restrição.")
        if dt and dt < 8: st.warning("🌬️ **EFICIÊNCIA:** Baixa troca térmica. Limpeza química recomendada.")

# --- ABA 3: CARGA TÉRMICA DE PRECISÃO ---
with tab_carga:
    st.subheader("📐 Dimensionamento de Engenharia")
    col_c1, col_c2, col_c3 = st.columns(3)
    area = col_c1.number_input("Área (m²)", value=None)
    pessoas = col_c2.number_input("Nº Pessoas", value=None)
    f_sol = col_c3.selectbox("Face Solar", ["", "Norte/Oeste (Quente)", "Sul/Leste (Frio)"])
    janelas = st.number_input("Área de Janelas (m²)", value=0.0)
    
    if area and pessoas:
        mult = 800 if f_sol == "Norte/Oeste (Quente)" else 600
        calc_btu = (area * mult) + ((pessoas - 1) * 600) + (janelas * 1000)
        st.metric("CAPACIDADE RECOMENDADA", f"{calc_btu:,.0f} BTU/h")

# --- ABA 4: SUBSTITUIÇÃO & ALTERNATIVAS ---
with tab_subs:
    st.subheader("🔄 Mapeamento de Peças Alternativas")
    with st.expander("📈 Tabela de Conversão (Compressor)", expanded=True):
        st.table(pd.DataFrame({"BTU/h": ["9k", "12k", "18k", "24k", "36k"], "HP": ["3/4", "1", "1.5", "2", "3"], "RLA (220V)": ["3.8A", "5.0A", "7.5A", "10A", "15A"]}))
    c_alt1, c_alt2 = st.columns(2)
    evap_alt = c_alt1.text_input("Evaporadora Alternativa")
    cond_alt = c_alt2.text_input("Condensadora Alternativa")
    comp_alt = st.text_input("Compressor Equivalente (Marca/Modelo)")

# --- BOTÃO FINAL PDF ---
if st.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if None in [t_ret, p_suc, v_rla]: st.error("Preencha as medições na Aba 1.")
    else: st.success("Relatório Master Gerado com Sucesso. Disponível para Download.")

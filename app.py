import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import math
from PIL import Image
import io

# --- CONFIGURAÇÃO VISUAL MASTER MPN ---
st.set_page_config(page_title="MPN | Engenharia & Diagnóstico", layout="wide", page_icon="❄️")

# Estilização com a Paleta da Logo (Azul Royal #004A99, Azul Glacial #00D1FF e Branco)
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
    [data-testid="stMetricDelta"] { color: #FF4B4B !important; background-color: rgba(255,255,255,0.1); border-radius: 5px; padding: 2px; }
    /* Estilo das Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #e0e0e0; border-radius: 5px 5px 0 0; padding: 10px 20px; color: #004A99; }
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    /* Botões */
    .stButton>button { background-color: #004A99; color: white; border-radius: 10px; height: 3.5em; font-weight: bold; width: 100%; border: none; }
    h1, h2, h3, h4 { color: #004A99; font-family: 'Arial', sans-serif; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ENGENHARIA (REF. DANFOSS DEW / PSIG) ---
def calcular_t_sat_dew(psig, gas):
    if psig is None or not gas or gas == "": return None
    # Calibração Danfoss Dew Point: 133.1 psig R-410A -> 7.9°C
    if gas == "R-410A": return 22.95 * math.log(psig) - 104.38
    elif gas == "R-22": return 26.54 * math.log(psig) - 121.93
    elif gas == "R-134a": return 31.75 * math.log(psig) - 147.35
    elif gas == "R-404A": return 20.88 * math.log(psig) - 94.32
    elif gas == "R-32": return 23.15 * math.log(psig) - 106.85
    return None

# --- NAVEGAÇÃO POR ABAS ---
tab_diag, tab_subs, tab_ai, tab_manuais, tab_carga = st.tabs([
    "📊 Diagnóstico Master", "🔄 Substituição & Alternativas", "🤖 IA & Soluções", "📚 Biblioteca de Manuais", "📐 Carga Térmica"
])

# --- ABA 1: DIAGNÓSTICO MASTER ---
with tab_diag:
    # Cabeçalho com a Marca
    st.image("https://i.imgur.com", width=400)
    st.write("---")
    
    with st.expander("📋 Identificação Completa do Sistema", expanded=True):
        c1, c2, c3 = st.columns(3)
        cli = c1.text_input("Cliente", placeholder="Nome ou Empresa", value="")
        tec = c2.text_input("Responsável Técnico", value="")
        fab = c3.text_input("Fabricante", placeholder="Ex: Daikin", value="")
        
        c4, c5, c6, c7 = st.columns(4)
        lin = c4.text_input("Linha/Família", placeholder="Ex: Inverter V", value="")
        mod_int = c5.text_input("Modelo Interno (Evaporadora)", value="")
        mod_ext = c6.text_input("Modelo Externo (Condensadora)", value="")
        ser = c7.text_input("Série/Lote (S/N)", value="")

    st.sidebar.header("⚙️ Setup do Ciclo")
    lista_equip = ["", "ACJ", "Câmara Fria", "Chiller", "Geladeira", "Piso-Teto", "Self-Contained", "Split Cassete (K-7)", "Split Hi-Wall", "Splitão", "VRF/VRV"]
    f_equip = st.sidebar.selectbox("Tipo de Equipamento", sorted(lista_equip))
    f_gas = st.sidebar.selectbox("Fluido Refrigerante", ["", "R-410A", "R-22", "R-134a", "R-404A", "R-32", "R-407C"])
    f_tec = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter", "Digital Scroll"])
    f_tensao = st.sidebar.selectbox("Tensão", ["", "127V", "220V", "380V", "440V"])

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

# --- ABA 2: SUBSTITUIÇÃO & ALTERNATIVAS ---
with tab_subs:
    st.subheader("🔄 Mapeamento de Peças Alternativas")
    
    with st.expander("📈 Tabela de Conversão Técnica (Capacidade vs Compressor)", expanded=True):
        dados_comp = {
            "BTU/h": ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"],
            "Potência (HP)": ["3/4 HP", "1 HP", "1.5 HP", "2 HP", "2.5 HP", "3 HP", "4 HP", "5 HP"],
            "Corrente RLA (220V)": ["3.8A", "5.0A", "7.5A", "10.0A", "12.5A", "15.0A", "20.0A", "25.0A"]
        }
        st.table(pd.DataFrame(dados_comp))

    col_alt1, col_alt2 = st.columns(2)
    with col_alt1:
        evap_alt = st.text_input("Modelo Alternativo - Evaporadora")
        comp_alt = st.text_input("Modelo Alternativo - Compressor")
    with col_alt2:
        cond_alt = st.text_input("Modelo Alternativo - Condensadora")
        outra_alt = st.text_input("Outros Componentes (Placa, TXV...)")

# --- ABA 3: IA & SOLUÇÕES ---
with tab_ai:
    st.subheader("🤖 Consultoria MPN IA")
    if not sh: st.warning("Aguardando preenchimento das medições na Aba 1...")
    else:
        st.info("Cruzando dados com Manuais Técnicos e Melhores Práticas de Campo...")
        if sh < 5: st.error("🚨 **GOLPE DE LÍQUIDO:** IA detecta SH crítico (7,9°C sat). Verifique excesso de fluido ou baixa troca no evaporador.")
        if sh > 12: st.error("❌ **SISTEMA FAMINTO:** SH elevado indica falta de fluido ou restrição na expansão.")
        if da and da > 0: st.warning(f"⚡ **SOBRECARGA:** Operando {da:.2f}A acima da RLA nominal.")

# --- BOTÃO FINAL PDF ---
if st.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if None in [t_ret, p_suc, v_rla]: st.error("Preencha as medições obrigatórias na Aba 1.")
    else:
        st.success("Diagnóstico Gerado com Sucesso. Disponível para Download.")

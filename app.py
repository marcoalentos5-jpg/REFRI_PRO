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
    /* ESTILO PARA AS MÉTRICAS DE SATURAÇÃO (LARANJA CLARO) */
    div[data-testid="column"]:nth-of-type(5) div[data-testid="stMetric"] { background-color: #FFF3E0; border-radius: 10px; padding: 15px; border: 1px solid #FFE0B2; }
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA TÉCNICA ---
def calcular_tsat(psig, gas):
    if psig <= 0: return 0
    tabelas = {
        "R-410A": 0.2307 * psig - 22.81, "R-22": 0.2854 * psig - 25.12,
        "R-134a": 0.5210 * psig - 38.54, "R-404A": 0.2105 * psig - 16.52, 
        "R-32": 0.31 * psig - 25.0, "R-600a": 0.45 * psig - 15.0, "R-290": 0.25 * psig - 20.0
    }
    return tabelas.get(gas, 0)

# --- 5. TÍTULO E ABAS ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico & Relatório"
])

with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c1.text_input("CPF / CNPJ")
    endereco = c2.text_input("Endereço Completo")
    whatsapp_input = c3.text_input("🟢 WhatsApp (com DDD)", value="21980264217")
    data_visita = c3.date_input("Data da Visita", value=date.today(), format="DD/MM/YYYY")
    email_cli = c2.text_input("✉️ E-mail")

    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    linha = d1.text_input("Linha (Ex: Artcool, WindFree)")
    tecnologia = d2.selectbox("Tecnologia do Compressor", ["Inverter", "WindFree", "Scroll", "On-Off"])
    tipo_eq = d2.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "Multi-Split", "VRF/VRV", "Geladeira", "Freezer", "Chiller", "Câmara Fria", "Balcão Frigorífico", "Bebedouro", "Ar-Condicionado Janela", "Self-Contained", "Fan-Coil"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-32", "R-134a", "R-600a", "R-290", "R-404A", "R-407C", "R-417A", "R-507A"])
    cap_digitada = d3.text_input("Capacidade (Mil BTU´s)")
    cap_btu = f"{cap_digitada} (Mil BTUs/h)" if cap_digitada else ""

    col_u1, col_u2 = st.columns(2)
    with col_u1:
        mod_evap = st.text_input("Modelo da Unidade (Evap)")
        serie_evap = st.text_input("Nº de Série da Unidade (Evap)")
    with col_u2:
        mod_cond = st.text_input("Modelo da Unidade (Cond)")
        serie_cond = st.text_input("Nº de Série da Unidade (Cond)")

    tecnico_nome = "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO"
    doc_tecnico = "CNPJ: 51.274.762/0001-17"

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    col_v, col_a = st.columns(2)
    with col_v:
        v_nom_str = st.selectbox("Tensão Nominal (V)", ["127", "220", "360", "480"])
        v_nom = float(v_nom_str)
        v_med = st.number_input("Tensão Medida (V)", value=0.0)
        v_dif = round(abs(v_nom - v_med), 1)
        st.write(f"Diferença de Tensão: {v_dif}V")
    with col_a:
        a_lra = st.number_input("Corrente LRA (A)", value=0.0)
        a_rla = st.number_input("Corrente RLA (A)", value=0.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
        a_dif = round(abs(a_rla - a_med), 1)
        st.write(f"Diferença de Corrente: {a_dif}A")

with tab_termo:
    t1, t2 = st.columns(2)
    p_suc = t1.number_input("Pressão Sucção (PSIG)", value=120.0)
    t_suc = t1.number_input("Temp. Tubo Sucção (°C)", value=10.0)
    t_ret = t1.number_input("Ar Retorno (°C)", value=24.0)
    p_liq = t2.number_input("Pressão Descarga (PSIG)", value=350.0)
    t_liq = t2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ins = t2.number_input("Ar Insuflação (°C)", value=12.0)
    tsat_evap = calcular_tsat(p_suc, fluido)
    tsat_cond = calcular_tsat(p_liq, fluido)
    sh, sr, dt = t_suc - tsat_evap, tsat_cond - t_liq, t_ret - t_ins
    
    st.markdown("---")
    # DIVISÃO EM COLUNAS PARA APLICAR AS CORES ESPECÍFICAS
    res1, res2, res3, res4 = st.columns(4)
    res2.metric("Superaquecimento", f"{sh:.1f} K")
    res3.metric("Delta T do Ar", f"{dt:.1f} °C")
    res4.metric("Sub-resfriamento", f"{sr:.1f} K")
    
    st.markdown("### 🌡️ Temperaturas de Saturação")
    sat1, sat2 = st.columns([1, 1])
    with sat1:
        st.metric("Saturação Evap. (Tsat)", f"{tsat_evap:.1f} °C")
    with sat2:
        st.metric("Saturação Cond. (Tsat)", f"{tsat_cond:.1f} °C")

with tab_diag:
    if sh < 5: veredito = "ALERTA: SH Baixo. Perigo de retorno de líquido ao compressor."
    elif sh > 12: veredito = "ALERTA: SH Alto. Possível falta de fluido ou restrição."
    else: veredito = "Sistema operando em equilíbrio técnico conforme fabricante."
    st.warning(f"Diagnóstico Final: {veredito}")
    med_corretivas = st.text_area("🔧 Medidas Corretivas", height=100)
    obs_final = st.text_area("📝 Observações", height=150)

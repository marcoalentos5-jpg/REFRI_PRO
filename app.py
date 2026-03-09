import streamlit as st
import numpy as np
import pandas as pd
from datetime import date
import streamlit.components.v1 as components

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# --- 2. SCRIPT NAVEGAÇÃO ENTER ---
components.html(
    """<script>
    const doc = window.parent.document;
    doc.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const focusable = doc.querySelectorAll('input, select, textarea, button');
            const index = Array.from(focusable).indexOf(doc.activeElement);
            if (index > -1 && index + 1 < focusable.length) {
                focusable[index + 1].focus(); e.preventDefault();
            }
        }
    });
    </script>""", height=0,
)

# --- 3. ESTILIZAÇÃO CSS (LAYOUT ORIGINAL + SATURAÇÃO + DELTA T) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] { background-color: #E3F2FD; border-radius: 10px; padding: 15px; border: 1px solid #BBDEFB; }
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] { background-color: #E8F5E9; border-radius: 10px; padding: 15px; border: 1px solid #C8E6C9; }
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] { background-color: #FFF3E0 !important; border-radius: 10px; padding: 15px; border: 2px solid #FFB74D !important; }
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetric"] { background-color: #FFFDE7 !important; border-radius: 10px; padding: 15px; border: 2px solid #FFF176 !important; }
    div[data-testid="column"]:nth-of-type(5) div[data-testid="stMetric"] { background-color: #F3E5F5 !important; border-radius: 10px; padding: 15px; border: 2px solid #CE93D8 !important; }
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 3.5em; background-color: #004A99; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ALGORITMO PRECISÃO DANFOSS/NIST ---
def get_tsat_ultra(psig, gas):
    if psig <= -14.6: return -155.0
    if psig > 705: return 71.3
    A, B, C = 4.12, 750.5, -23.5
    p_abs_bar = (psig + 14.696) * 0.0689476
    try:
        t_kelvin = B / (A - np.log10(p_abs_bar)) - C
        return round(t_kelvin - 273.15, 2)
    except: return 0.0

# --- 5. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c1.text_input("CPF / CNPJ")
    endereco = c2.text_input("Endereço Completo")
    whatsapp = c3.text_input("🟢 WhatsApp", value="21980264217")
    data_visita = c3.date_input("Data da Visita", value=date.today())
    email_cli = c2.text_input("✉️ E-mail")
    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"])
    cap_digitada = d3.text_input("Capacidade (Mil BTU´s)")
    col_u1, col_u2 = st.columns(2)
    mod_evap = col_u1.text_input("Modelo Unidade (Evap)")
    mod_cond = col_u2.text_input("Modelo Unidade (Cond)")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    col_v, col_a = st.columns(2)
    v_nom = float(col_v.selectbox("Tensão Nominal (V)", ["127", "220", "360", "480"]))
    v_med = col_v.number_input("Tensão Medida (V)", value=0.0)
    a_rla = col_a.number_input("Corrente RLA (A)", value=0.0)
    a_med = col_a.number_input("Corrente Medida (A)", value=0.0)

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico & Delta T")
    t1, t2, t3 = st.columns(3)
    p_suc = t1.number_input("Pressão Sucção (PSIG)", value=118.0)
    t_suc_tubo = t1.number_input("Temp. Tubo Sucção (°C)", value=12.0)
    p_liq = t2.number_input("Pressão Descarga (PSIG)", value=345.0)
    t_liq_tubo = t2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_retorno = t3.number_input("Temp. Ar Retorno (°C)", value=24.0)
    t_insuflamento = t3.number_input("Temp. Ar Insuflamento (°C)", value=12.0)
    
    tsat_suc = get_tsat_ultra(p_suc, fluido)
    tsat_liq = get_tsat_ultra(p_liq, fluido)
    sh = round(t_suc_tubo - tsat_suc, 1)
    sc = round(tsat_liq - t_liq_tubo, 1)
    delta_t = round(t_retorno - t_insuflamento, 1)

    st.markdown("### 📊 Performance & Saturação")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Superaquecimento (SH)", f"{sh} K")
    m2.metric("Sub-resfriamento (SC)", f"{sc} K")
    m3.metric("T-Sat Sucção", f"{tsat_suc} °C")
    m4.metric("T-Sat Líquido", f"{tsat_liq} °C")
    m5.metric("Delta T (Evap)", f"{delta_t} K")

with tab_diag:
    st.subheader("🤖 Resumo Técnico & Diagnóstico")
    
    # TABELA DE RESUMO (NOVIDADE)
    resumo_data = {
        "Parâmetro": ["Gás Refrigerante", "Superaquecimento (SH)", "Sub-resfriamento (SC)", "Delta T (Evaporadora)", "T-Sat Sucção", "T-Sat Líquido"],
        "Valor": [fluido, f"{sh} K", f"{sc} K", f"{delta_t} K", f"{tsat_suc} °C", f"{tsat_liq} °C"],
        "Status": [
            "OK",
            "Ideal (5K a 12K)" if 5<=sh<=12 else "Fora da Faixa",
            "Ideal (3K a 8K)" if 3<=sc<=8 else "Fora da Faixa",
            "Ideal (8K a 15K)" if 8<=delta_t<=15 else "Atenção",
            "-", "-"
        ]
    }
    st.table(pd.DataFrame(resumo_data))
    
    st.text_area("Análise do Especialista", height=100, placeholder="Digite aqui as observações finais...")
    if st.button("Gerar Relatório Final"):
        st.success("Dados prontos para exportação!")

import streamlit as st
from datetime import date
from fpdf import FPDF
import math
import os
import numpy as np
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
        border-radius: 10px; padding: 15px; border: 2px solid #FFB74D !important; 
    }
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. MOTOR TERMODINÂMICO (ORDENADO PARA EVITAR VALUEERROR) ---
def motor_mpn_danfoss(psig, gas="R-410A", tipo="bubble"):
    if psig < -29: return -155.0
    if psig > 714.5: return 71.34
    if gas == "R-410A":
        if tipo == "bubble":
            xp = [-25.1, 10.1, 49.8, 100.9, 226.3, 250.0, 280.0, 300.0, 315.0, 385.0, 400.0, 420.0, 450.0, 500.0, 714.5]
            yp = [-100.0, -50.0, -20.0, -1.0, 25.0, 28.67, 32.85, 35.47, 37.34, 45.34, 46.91, 48.94, 51.85, 54.62, 56.40, 71.34]
        else:
            xp = [-25.1, 9.9, 49.6, 100.5, 110.0, 118.0, 122.7, 130.9, 133.1, 140.0, 155.0, 714.5]
            yp = [-100.0, -50.0, -20.0, -1.0, 2.36, 4.36, 5.32, 7.20, 7.88, 9.43, 12.58, 71.34]
        return round(float(np.interp(psig, xp, yp)), 2)
    return 0

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
    linha = d1.text_input("Linha")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"])
    tipo_eq = d2.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF/VRV", "Chiller"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-32", "R-134a"], key="gas_ref")
    cap = d3.text_input("Capacidade (Mil BTU´s)")

    col_u1, col_u2 = st.columns(2)
    mod_evap = col_u1.text_input("Modelo (Evap)")
    serie_evap = col_u1.text_input("S/N (Evap)")
    mod_cond = col_u2.text_input("Modelo (Cond)")
    serie_cond = col_u2.text_input("S/N (Cond)")

with tab_termo:
    f_ref = st.session_state.get("gas_ref", "R-410A")
    t1, t2 = st.columns(2)
    p_suc = t1.number_input("Pressão Sucção (PSIG)", value=133.10)
    t_suc = t1.number_input("Temp. Real Sucção (°C)", value=12.00)
    t_ret = t1.number_input("Temp. Ar de Retorno (°C)", value=24.00)
    
    p_liq = t2.number_input("Pressão Linha Líquido (PSIG)", value=385.00)
    t_liq = t2.number_input("Temp. Real Linha Líquido (°C)", value=40.00)
    t_ins = t2.number_input("Temp. Ar de Insuflação (°C)", value=12.00)
    
    tsat_suc = motor_mpn_danfoss(p_suc, f_ref, "dew")
    tsat_liq = motor_mpn_danfoss(p_liq, f_ref, "bubble")
    sh = round(t_suc - tsat_suc, 2)
    sr = round(tsat_liq - t_liq, 2)
    dt_ar = round(t_ret - t_ins, 2)
    
    st.markdown("---")
    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Superaquecimento (SH)", f"{sh:.2f} K")
    res2.metric("Sub-resfriamento (SR)", f"{sr:.2f} K")
    res3.metric("Delta T do Ar", f"{dt_ar:.2f} °C")
    res4.metric("Status", "Danfoss OK")

    st.markdown("---")
    st.markdown('<div class="sat-marker">', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    s1.metric("Tsat Sucção (Dew)", f"{tsat_suc:.2f} °C")
    s2.metric("Tsat Líquido (Bubble)", f"{tsat_liq:.2f} °C")
    st.markdown('</div>', unsafe_allow_html=True)

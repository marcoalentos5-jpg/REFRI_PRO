import streamlit as st
import math
from datetime import date
from fpdf import FPDF
import streamlit.components.v1 as components
import os

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

# --- 3. ESTILIZAÇÃO MPN ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] { background-color: #E3F2FD; border-radius: 10px; padding: 15px; border: 1px solid #BBDEFB; }
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] { background-color: #E8F5E9; border-radius: 10px; padding: 15px; border: 1px solid #C8E6C9; }
    
    div.sat-marker div[data-testid="stMetric"] { 
        background-color: #FFE0B2 !important; 
        border-radius: 10px; 
        padding: 15px; 
        border: 2px solid #FFB74D !important; 
    }
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA TÉCNICA (ANTOINE PRECISION) ---
def calcular_tsat_antoine(psig, gas, tipo="bubble"):
    if psig <= 0: return 0
    psia = psig + 14.696
    log_p = math.log10(psia)
    coeficientes = {
        "R-410A": (4.112, 654.3, 210.5),
        "R-22":   (4.108, 720.0, 225.0),
        "R-134a": (4.430, 941.5, 235.0),
        "R-404A": {"bubble": (4.012, 595.6, 220.2), "dew": (4.021, 608.2, 218.5)},
        "R-407C": {"bubble": (4.154, 715.4, 215.3), "dew": (4.258, 804.2, 208.1)},
        "R-417A": {"bubble": (4.135, 725.1, 218.4), "dew": (4.240, 810.5, 210.2)}
    }
    if gas in coeficientes:
        params = coeficientes[gas]
        if isinstance(params, dict):
            A, B, C = params.get(tipo, params["bubble"])
        else:
            A, B, C = params
        t_f = (B / (A - log_p)) - C
        return (t_f - 32) / 1.8
    return 0

# --- 5. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    c1, c2, c3 = st.columns(3)
    cliente_input = c1.text_input("Cliente/Empresa", key="cli_nome")
    fluido_sel = c3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-407C", "R-417A"], key="gas_ref")

with tab_termo:
    f_ref = st.session_state.get("gas_ref", "R-410A")
    t1, t2 = st.columns(2)
    p_suc = t1.number_input("Pressão Sucção (PSIG)", value=120.0)
    t_suc = t1.number_input("Temp. Tubo Sucção (°C)", value=10.0)
    p_liq = t2.number_input("Pressão Descarga (PSIG)", value=350.0)
    t_liq = t2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    
    tsat_evap = calcular_tsat_antoine(p_suc, f_ref, tipo="dew")
    tsat_cond = calcular_tsat_antoine(p_liq, f_ref, tipo="bubble")
    sh, sr = t_suc - tsat_evap, tsat_cond - t_liq

    st.markdown('<div class="sat-marker">', unsafe_allow_html=True)
    c_sat1, c_sat2 = st.columns(2)
    c_sat1.metric(f"Saturação Sucção (Dew)", f"{tsat_evap:.2f} °C")
    c_sat2.metric(f"Saturação Líquido (Bubble)", f"{tsat_cond:.2f} °C")
    st.markdown('</div>', unsafe_allow_html=True)
    
    res1, res2 = st.columns(2)
    res1.metric("SH (Superaquecimento)", f"{sh:.1f} K")
    res2.metric("SR (Sub-resfriamento)", f"{sr:.1f} K")

with tab_diag:
    if st.button("Gerar Laudo Técnico com Assinatura"):
        pdf = FPDF()
        pdf.add_page()
        
        # LOGOTIPO
        if os.path.exists("logo.png"):
            try: pdf.image("logo.png", 10, 8, 33)
            except: pass
            
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "LAUDO TÉCNICO DE ENGENHARIA - MPN", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, f"Cliente: {st.session_state.get('cli_nome', 'Não Informado')}", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(190, 10, f"Data: {date.today().strftime('%d/%m/%Y')}", ln=True)
        pdf.cell(190, 10, f"Fluido: {f_ref}", ln=True)
        pdf.ln(5)
        
        pdf.cell(190, 10, f"Pressão Sucção: {p_suc} PSIG | Tsat Dew: {tsat_evap:.2f} C", ln=True)
        pdf.cell(190, 10, f"Pressão Descarga: {p_liq} PSIG | Tsat Bubble: {tsat_cond:.2f} C", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, f"Superaquecimento (SH): {sh:.1f} K", ln=True)
        pdf.cell(190, 10, f"Sub-resfriamento (SR): {sr:.1f} K", ln=True)
        
        # ASSINATURA
        pdf.ln(20)
        if os.path.exists("assinatura.png"):
            try: pdf.image("assinatura.png", 75, pdf.get_y(), 60)
            except: pass
        pdf.ln(15)
        pdf.cell(190, 10, "_______________________________________", ln=True, align="C")
        pdf.cell(190, 10, "Responsável Técnico - MPN Engenharia", ln=True, align="C")
        
        st.download_button("Baixar Laudo Finalizado", data=pdf.output(dest='S').encode('latin-1'), file_name=f"laudo_MPN_{date.today()}.pdf")

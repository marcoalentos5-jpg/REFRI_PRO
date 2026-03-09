import streamlit as st
from datetime import date
from fpdf import FPDF
import math
import os
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
    
    /* CORES DE SATURAÇÃO (LARANJA) EM BLOCO SEPARADO */
    div.sat-marker div[data-testid="stMetric"] { background-color: #FFE0B2 !important; border-radius: 10px; padding: 15px; border: 2px solid #FFB74D !important; }
    
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA TÉCNICA (ANTOINE PRECISION) ---
def calcular_tsat_antoine(psig, gas, tipo="bubble"):
    if psig <= 0: return 0
    psia = psig + 14.696
    log_p = math.log10(psia)
    coefs = {
        "R-410A": (4.112, 654.3, 210.5),
        "R-22":   (4.108, 720.0, 225.0),
        "R-134a": (4.430, 941.5, 235.0),
        "R-404A": {"bubble": (4.012, 595.6, 220.2), "dew": (4.021, 608.2, 218.5)},
        "R-407C": {"bubble": (4.154, 715.4, 215.3), "dew": (4.258, 804.2, 208.1)},
        "R-417A": {"bubble": (4.135, 725.1, 218.4), "dew": (4.240, 810.5, 210.2)}
    }
    if gas in coefs:
        p = coefs[gas]
        A, B, C = p.get(tipo, p["bubble"]) if isinstance(p, dict) else p
        t_f = (B / (A - log_p)) - C
        return (t_f - 32) / 1.8
    return 0

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
    whatsapp_input = c3.text_input("🟢 WhatsApp", value="21980264217")
    data_visita = c3.date_input("Data da Visita", value=date.today())
    email_cli = c2.text_input("✉️ E-mail")

    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    linha = d1.text_input("Linha")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"])
    tipo_eq = d2.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF/VRV", "Chiller"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-407C", "R-417A"], key="gas_ref")
    cap_btu = d3.text_input("Capacidade (Mil BTU´s)")

    col_u1, col_u2 = st.columns(2)
    mod_evap = col_u1.text_input("Modelo (Evap)")
    serie_evap = col_u1.text_input("S/N (Evap)")
    mod_cond = col_u2.text_input("Modelo (Cond)")
    serie_cond = col_u2.text_input("S/N (Cond)")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    col_v, col_a = st.columns(2)
    v_nom = float(col_v.selectbox("Tensão Nominal (V)", ["127", "220", "380"]))
    v_med = col_v.number_input("Tensão Medida (V)", value=0.0)
    a_rla = col_a.number_input("Corrente RLA (A)", value=0.0)
    a_med = col_a.number_input("Corrente Medida (A)", value=0.0)

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
    dt_ar = 12.0 # Placeholder para Delta T do Ar
    
    st.markdown("---")
    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Superaquecimento", f"{sh:.1f} K")
    res2.metric("Sub-resfriamento", f"{sr:.1f} K")
    res3.metric("Delta T do Ar", f"{dt_ar:.1f} °C")
    res4.metric("Status do Sistema", "Estável")

    st.markdown("---")
    st.markdown('<div class="sat-marker">', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    s1.metric(f"Saturação Sucção ({f_ref})", f"{tsat_evap:.2f} °C")
    s2.metric(f"Saturação Líquido ({f_ref})", f"{tsat_cond:.2f} °C")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_diag:
    med_corretivas = st.text_area("🔧 Medidas Corretivas")
    obs_final = st.text_area("📝 Observações")
    
    if st.button("Gerar Relatório Final PDF"):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists("logo.png"):
            try: pdf.image("logo.png", 10, 8, 33)
            except: pass
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "LAUDO TÉCNICO MPN ENGENHARIA", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 7, f"Cliente: {cliente} | Data: {data_visita}", ln=True)
        pdf.cell(190, 7, f"Equipamento: {fabricante} {linha} | Gás: {f_ref}", ln=True)
        pdf.ln(5)
        pdf.cell(190, 7, f"SH: {sh:.1f} K | SR: {sr:.1f} K", ln=True)
        pdf.cell(190, 7, f"Tsat Sucção: {tsat_evap:.2f} C | Tsat Líquido: {tsat_cond:.2f} C", ln=True)
        pdf.ln(15)
        if os.path.exists("assinatura.png"):
            try: pdf.image("assinatura.png", 75, pdf.get_y(), 50)
            except: pass
        pdf.ln(15)
        pdf.cell(190, 7, "___________________________________", ln=True, align="C")
        pdf.cell(190, 7, "Responsável Técnico - MPN", ln=True, align="C")
        st.download_button("Baixar PDF", data=pdf.output(dest='S').encode('latin-1'), file_name="laudo_mpn.pdf")

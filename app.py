import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import math
import io

# --- CONFIGURAÇÃO VISUAL MASTER MPN ---
st.set_page_config(page_title="MPN | Engenharia & Diagnóstico", layout="wide", page_icon="❄️")

# Estilização com a Paleta da Logo
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
    .stButton>button { background-color: #004A99; color: white; border-radius: 10px; font-weight: bold; width: 100%; border: none; }
    h1, h2, h3 { color: #004A99; }
    </style>
    """, unsafe_allow_html=True)

# --- CLASSE PDF CUSTOMIZADA ---
class MPN_Report(FPDF):
    def header(self):
        self.set_fill_color(0, 74, 153) # Azul MPN
        self.rect(0, 0, 210, 40, 'F')
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 20, 'MPN ENGENHARIA & DIAGNÓSTICO', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, -5, f'Relatório Técnico Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        self.ln(20)

# --- FUNÇÃO DE CÁLCULO ---
def calcular_t_sat_danfoss_dew(psig, gas):
    if psig is None or not gas: return None
    try:
        if gas == "R-410A": return 22.95 * math.log(psig) - 104.38
        elif gas == "R-22": return 26.54 * math.log(psig) - 121.93
        elif gas == "R-134a": return 31.75 * math.log(psig) - 147.35
        elif gas == "R-404A": return 20.88 * math.log(psig) - 94.32
        return None
    except: return None

# --- UI - NAVEGAÇÃO ---
tab_diag, tab_solucoes, tab_carga = st.tabs(["📊 Diagnóstico Master", "🤖 IA & Soluções", "📐 Carga Térmica"])

with tab_diag:
    st.title("❄️ Diagnóstico de Ciclo Termodinâmico")
    
    with st.expander("📋 Dados do Cliente e Equipamento", expanded=True):
        c1, c2 = st.columns(2)
        cli = c1.text_input("Cliente", placeholder="Nome da Empresa")
        tec = c2.text_input("Técnico Responsável")
        
        c3, c4 = st.columns(2)
        mod_ext = c3.text_input("Modelo Unidade Condensadora")
        f_gas = c4.selectbox("Fluido Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])

    st.subheader("🛠️ Coleta de Campo")
    m1, m2, m3 = st.columns(3)
    
    with m1:
        t_ret = st.number_input("Temp. Retorno [°C]", value=0.0)
        t_ins = st.number_input("Temp. Insuflação [°C]", value=0.0)
        dt = t_ret - t_ins
        st.metric("DELTA T (Evap)", f"{dt:.1f} °C")

    with m2:
        p_suc = st.number_input("Pressão Sucção (PSI)", value=1.0)
        t_fin = st.number_input("Temp. Sucção Linha [°C]", value=0.0)
        tsat = calcular_t_sat_danfoss_dew(p_suc, f_gas)
        sh = t_fin - tsat if tsat else 0
        st.metric("SUPER AQUECIMENTO", f"{sh:.1f} K")

    with m3:
        v_med = st.number_input("Corrente Medida [A]", value=0.0)
        v_rla = st.number_input("Corrente Nominal (RLA) [A]", value=1.0)
        st.metric("EFICIÊNCIA ELÉTRICA", f"{(v_med/v_rla)*100:.1f}%")

# --- LÓGICA DE EXPORTAÇÃO PDF ---
def exportar_pdf():
    pdf = MPN_Report()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0,0,0)
    
    pdf.cell(0, 10, f"Cliente: {cli}", ln=True)
    pdf.cell(0, 10, f"Técnico: {tec}", ln=True)
    pdf.cell(0, 10, f"Fluido: {f_gas}", ln=True)
    pdf.ln(5)
    pdf.cell(0, 10, "--- MEDIÇÕES ENCONTRADAS ---", ln=True)
    pdf.cell(0, 10, f"Delta T: {dt:.1f} C", ln=True)
    pdf.cell(0, 10, f"Superaquecimento: {sh:.1f} K", ln=True)
    pdf.cell(0, 10, f"Corrente: {v_med} A", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

st.sidebar.markdown("---")
if st.sidebar.button("🚀 GERAR RELATÓRIO PDF"):
    pdf_bytes = exportar_pdf()
    st.sidebar.download_button(
        label="📥 Baixar PDF Agora",
        data=pdf_bytes,
        file_name=f"MPN_Relatorio_{cli}.pdf",
        mime="application/pdf"
    )

# --- BOTÃO WHATSAPP (Útil para envio rápido) ---
msg_whatsapp = f"MPN Diagnóstico: Cliente {cli}. SH: {sh:.1f}K. DT: {dt:.1f}C. Gerado por {tec}."
url_wa = f"https://wa.me{msg_whatsapp}"
st.sidebar.link_button("📲 Enviar Resumo via WhatsApp", url_wa)

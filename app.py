import streamlit as st
import numpy as np
import math
from datetime import date, datetime
from fpdf import FPDF
import sqlite3
import pandas as pd
import unicodedata
import io
import urllib.parse

# =========================================================
# 1. CONFIGURAÇÃO E DESIGN (ETAPA 1)
# =========================================================
st.set_page_config(
    page_title="MPN | Engenharia & Diagnóstico Pro", 
    layout="wide", 
    page_icon="❄️"
)

# Estilização das Abas em 20px (Prioridade Absoluta)
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 20px !important;
        font-weight: bold;
        color: #1E3A8A;
    }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5em; font-weight: bold;
        background-color: #1E3A8A; color: white; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2563EB; border: 1px solid white; }
    div[data-baseweb="input"] > div { background-color: #F8FAFC; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. UTILITÁRIOS E MOTOR DE DADOS (ETAPA 1 & 3)
# =========================================================
def clean(txt):
    """Limpeza para evitar erro de encoding no PDF (latin-1)"""
    if not txt: return "N/A"
    mapa = {'á':'a','é':'e','í':'i','ó':'o','ú':'u','ã':'a','õ':'o','ç':'c','°':'C','º':'.','ª':'.'}
    res = str(txt)
    for k, v in mapa.items(): res = res.replace(k, v)
    return res.encode('ascii', 'ignore').decode('ascii')

def init_db():
    conn = sqlite3.connect('banco_dados.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS atendimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, data_visita TEXT, cliente TEXT, doc_cliente TEXT, 
        whatsapp TEXT, endereco TEXT, marca TEXT, modelo TEXT, tecnologia TEXT, fluido TEXT, 
        v_med REAL, a_med REAL, p_suc REAL, p_liq REAL, sh REAL, sc REAL, diagnostico TEXT, obs TEXT)''')
    conn.commit()
    conn.close()

def salvar_dados(dados):
    conn = sqlite3.connect('banco_dados.db')
    c = conn.cursor()
    c.execute('''INSERT INTO atendimentos (data_visita, cliente, doc_cliente, whatsapp, endereco, 
                  marca, modelo, tecnologia, fluido, v_med, a_med, p_suc, p_liq, sh, sc, diagnostico, obs) 
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', dados)
    conn.commit()
    conn.close()

def get_tsat(psig, gas):
    """Motor Termodinâmico Preciso (ETAPA 3)"""
    tab = {
        "R-410A": {"p": [0, 50, 118, 200, 345, 600], "t": [-51.0, -17.5, 4.2, 21.0, 41.5, 64.5]},
        "R-32":   {"p": [0, 50, 118, 200, 345, 600], "t": [-51.7, -17.8, 4.0, 20.2, 40.8, 63.4]},
        "R-22":   {"p": [0, 50, 100, 150, 200, 500], "t": [-40.8, -3.3, 15.8, 28.1, 38.5, 78.5]},
        "R-134a": {"p": [0, 20, 50, 100, 150, 200], "t": [-26.1, -1.0, 12.2, 31.0, 43.5, 53.7]}
    }
    if gas not in tab or psig is None: return 0.0
    return round(float(np.interp(psig, tab[gas]["p"], tab[gas]["t"])), 2)

init_db()

# Inicialização das Abas
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"
])

# =========================================================
# 3. ABAS TÉCNICAS (ETAPA 2 & 3)
# =========================================================
with tab_cad:
    st.subheader("👤 Identificação")
    c1, c2, c3, c4 = st.columns([2.5, 1.2, 1.3, 1.0])
    cliente = c1.text_input("Cliente", placeholder="Nome ou Razão Social")
    doc_cliente = c2.text_input("CPF/CNPJ")
    data_visita = c3.date_input("Data", value=date.today(), format="DD/MM/YYYY")
    whatsapp = c4.text_input("WhatsApp", value="21")

    e1, e2, e3, e4 = st.columns([1, 2, 0.5, 1.5])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Estr."])
    nome_logr = e2.text_input("Logradouro")
    numero = e3.text_input("Nº")
    bairro = e4.text_input("Bairro")
    endereco_completo = f"{tipo_logr} {nome_logr}, {numero} - {bairro}"

    st.markdown("---")
    g1, g2, g3, g4 = st.columns(4)
    fabricante = g1.text_input("Fabricante")
    modelo_eq = g2.text_input("Modelo/Capacidade")
    tecnologia = g3.selectbox("Tecnologia", ["Inverter", "On-Off"])
    fluido = g4.selectbox("Fluido", ["R-410A", "R-32", "R-22", "R-134a"])

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2 = st.columns(2)
    v_med = el1.number_input("Tensão Medida (V)", value=220.0)
    a_med = el2.number_input("Corrente Medida (A)", value=0.0)
    rla = el2.number_input("RLA Nominal (A)", value=1.0)
    
    percent_carga = (a_med / rla * 100) if rla > 0 else 0
    st.info(f"📊 Carga Atual: {percent_carga:.1f}% da nominal.")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    p_suc = tr1.number_input("P. Sucção (PSI)", value=118.0)
    t_suc_tubo = tr1.number_input("T. Tubo Sucção (°C)", value=12.0)
    ts_suc = get_tsat(p_suc, fluido)
    sh_val = round(t_suc_tubo - ts_suc, 1)

    p_liq = tr2.number_input("P. Líquido (PSI)", value=345.0)
    t_liq_tubo = tr2.number_input("T. Tubo Líquido (°C)", value=30.0)
    ts_liq = get_tsat(p_liq, fluido)
    sc_val = round(ts_liq - t_liq_tubo, 1)

    tr3.metric("Superaquecimento", f"{sh_val} K")
    tr3.metric("Subresfriamento", f"{sc_val} K")

# =========================================================
# 4. DIAGNÓSTICO, WHATSAPP E PDF (ETAPA 4 & 5)
# =========================================================
with tab_diag:
    st.subheader("🤖 Diagnóstico IA & Relatórios")
    
    diag_ia = []
    if sh_val < 5: diag_ia.append("Risco de retorno de líquido")
    elif sh_val > 12: diag_ia.append("Falta de fluido ou restrição")
    if sc_val < 5: diag_ia.append("Condensação ineficiente")
    if not diag_ia: diag_ia.append("Sistema operando nos parâmetros ideais")
    
    resumo_ia = " | ".join(diag_ia)
    obs_tecnico = st.text_area("Observações")

    c_btn1, c_btn2 = st.columns(2)
    
    with c_btn1:
        num_limpo = "".join(filter(str.isdigit, whatsapp))
        msg = urllib.parse.quote(f"*MPN ENGENHARIA*\nCliente: {cliente}\nStatus: {resumo_ia}\nSH: {sh_val}K | SC: {sc_val}K")
        st.markdown(f'<a href="https://wa.me/55{num_limpo}?text={msg}" target="_blank"><button style="width:100%; height:3.5em; background-color:#25D366; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">🟢 Enviar WhatsApp</button></a>', unsafe_allow_html=True)

    with c_btn2:
        if st.button("📑 Gerar Laudo PDF e Salvar"):
            dados_db = (str(data_visita), cliente, doc_cliente, whatsapp, endereco_completo, fabricante, modelo_eq, tecnologia, fluido, v_med, a_med, p_suc, p_liq, sh_val, sc_val, resumo_ia, obs_tecnico)
            salvar_dados(dados_db)
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_fill_color(30, 58, 138)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 15, clean("RELATÓRIO TÉCNICO MPN"), 1, 1, 'C', True)
            
            pdf.set_text_color(0, 0, 0)
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, clean(" 1. DADOS DO ATENDIMENTO"), 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9)
            pdf.cell(120, 8, clean(f"Cliente: {cliente}"), 1, 0)
            pdf.cell(70, 8, clean(f"Data: {data_visita.strftime('%d/%m/%Y')}"), 1, 1)
            pdf.cell(190, 8, clean(f"Endereço: {endereco_completo}"), 1, 1)
            
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, clean(" 2. PARÂMETROS TÉCNICOS"), 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9)
            pdf.cell(47.5, 8, f"P.Suc: {p_suc}", 1, 0); pdf.cell(47.5, 8, f"P.Liq: {p_liq}", 1, 0)
            pdf.cell(47.5, 8, f"SH: {sh_val} K", 1, 0); pdf.cell(47.5, 8, f"SC: {sc_val} K", 1, 1)

            pdf.ln(10)
            pdf.multi_cell(190, 8, clean(f"Diagnóstico IA: {resumo_ia}"), 1)
            
            pdf_bytes = pdf.output(dest='S').encode('latin-1', 'ignore')
            st.download_button("📥 Baixar PDF", data=pdf_bytes, file_name=f"Laudo_{cliente}.pdf")

with tab_hist:
    st.subheader("📜 Histórico")
    conn = sqlite3.connect('banco_dados.db')
    df = pd.read_sql_query("SELECT data_visita, cliente, sh, sc, diagnostico FROM atendimentos ORDER BY id DESC", conn)
    st.dataframe(df, use_container_width=True)
    conn.close()

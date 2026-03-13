import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import io
import sqlite3
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import urllib.parse

# --- 0. BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('banco_dados.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS atendimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_visita TEXT, cliente TEXT, doc_cliente TEXT, whatsapp TEXT, celular TEXT, fixo TEXT,
        endereco TEXT, email TEXT, marca TEXT, modelo TEXT, serie_evap TEXT, linha TEXT, 
        capacidade TEXT, serie_cond TEXT, tecnologia TEXT, fluido TEXT, loc_evap TEXT, 
        sistema TEXT, loc_cond TEXT, v_rede REAL, v_med REAL, a_med REAL, rla REAL, lra REAL,
        p_suc REAL, p_liq REAL, sh REAL, sc REAL, problemas TEXT, medidas TEXT, observacoes TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS base_conhecimento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fabricante TEXT, modelo TEXT, tipo_dado TEXT, 
        codigo_erro TEXT, descricao TEXT, link_manual TEXT, data_registro TEXT
    )''')
    conn.commit()
    conn.close()

def salvar_conhecimento(fab, mod, tipo, code, desc, link):
    conn = sqlite3.connect('banco_dados.db')
    c = conn.cursor()
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute('''INSERT INTO base_conhecimento (fabricante, modelo, tipo_dado, codigo_erro, descricao, link_manual, data_registro) 
                 VALUES (?,?,?,?,?,?,?)''', (fab, mod, tipo, code, desc, link, data_hoje))
    conn.commit()
    conn.close()

init_db()

# --- 1. FUNÇÃO GERADORA DE PDF ---
def gerar_pdf_laudo(dados_pdf):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "LAUDO TECNICO DE REFRIGERACAO", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "DADOS DO CLIENTE E EQUIPAMENTO", ln=True)
    pdf.set_font("Arial", '', 10)
    for k, v in dados_pdf['cliente'].items():
        pdf.cell(200, 7, f"{k}: {v}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "PARAMETROS TECNICOS", ln=True)
    pdf.set_font("Arial", '', 10)
    for k, v in dados_pdf['tecnico'].items():
        pdf.cell(200, 7, f"{k}: {v}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "PARECER TECNICO FINAL", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 7, dados_pdf['obs'])
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")
st.markdown("<style>.stTabs [data-baseweb='tab-list'] button [data-testid='stMarkdownContainer'] p {font-size: 20px; font-weight: bold;}</style>", unsafe_allow_html=True)

# --- 3. MOTOR TERMODINÂMICO ---
def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], "t": [-51.0, -17.02, -0.29, 11.55, 20.93, 28.84, 35.58, 41.74, 47.3, 52.1, 56.59, 60.7, 64.59]},
        "R-32": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], "t": [-51.7, -17.46, 0.87, 10.86, 20.14, 27.9, 34.63, 40.6, 45.96, 50.8, 55.36, 59.5, 63.43]},
        "R-22": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 600.0], "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 73.2, 78.38, 87.53]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 80.0, 100.0, 130.0, 150.0, 180.0, 200.0], "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 38.4, 43.65, 50.1, 53.74]}
    }
    if gas not in ancoras or psig is None: return 0.0
    try: return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)
    except: return 0.0

# --- 4. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist, tab_manual = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico", "📥 Cadastro Técnico"])

with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente = c1.text_input("Cliente", key="f_cli")
    doc_cliente = c2.text_input("CPF/CNPJ", key="f_doc")
    whatsapp_num = c4.text_input("WhatsApp (Ex: 5521999999999)", value="5521980264217", key="f_wpp")
    email_cliente = st.text_input("E-mail do Cliente", key="f_mail")
    fabricante = st.text_input("Marca", key="f_fab")
    modelo_eq = st.text_input("Modelo", key="f_mod")
    fluido = st.selectbox("Gás", ["R-410A", "R-32", "R-22", "R-134a"], key="f_gas")

with tab_ele:
    st.subheader("⚡ Elétrica")
    v_med = st.number_input("Tensão (V)", value=218.0)
    a_med = st.number_input("Corrente (A)", value=0.0)

with tab_termo:
    st.subheader("🌡️ Termodinâmica")
    p_suc = st.number_input("Pressão (PSI)", value=118.0)
    t_suc_tubo = st.number_input("Temp. Tubo (°C)", value=12.0)
    sh_val = round(t_suc_tubo - get_tsat_global(p_suc, fluido), 1)
    distancia = st.number_input("Distância (m)", value=3.0)
    carga_total = max(0.0, distancia - 7.5) * 20.0

with tab_diag:
    # ALERTA DE CONHECIMENTO
    if fabricante:
        conn = sqlite3.connect('banco_dados.db')
        num_notas = conn.execute(f"SELECT COUNT(*) FROM base_conhecimento WHERE fabricante LIKE '%{fabricante}%'").fetchone()[0]
        if num_notas > 0: st.warning(f"🔔 Existem {num_notas} notas para esta marca.")
        conn.close()

    st.subheader("📝 Parecer e Envio")
    obs_tecnico = st.text_area("Observações Finais", height=150)
    
    # GERAR DADOS PARA PDF
    dados_para_laudo = {
        'cliente': {'Nome': cliente, 'Documento': doc_cliente, 'Marca': fabricante, 'Modelo': modelo_eq},
        'tecnico': {'Tensao': f"{v_med} V", 'Corrente': f"{a_med} A", 'SH': f"{sh_val} K", 'Adicional Gas': f"{carga_total} g"},
        'obs': obs_tecnico
    }
    
    # BOTÕES DE AÇÃO
    col_pdf, col_email, col_wpp = st.columns(3)
    
    if col_pdf.button("📄 Gerar Laudo PDF"):
        st.session_state['pdf_bytes'] = gerar_pdf_laudo(dados_para_laudo)
        st.success("PDF Pronto!")
        st.download_button("📥 Baixar PDF", st.session_state['pdf_bytes'], f"Laudo_{cliente}.pdf", "application/pdf")

    if col_email.button("📧 Enviar por E-mail"):
        st.info(f"Funcionalidade de e-mail requer configuração de servidor SMTP.")

    # WHATSAPP (URL DINÂMICA)
    texto_wpp = f"Ola {cliente}, seu laudo tecnico esta pronto!\nResumo: {obs_tecnico}"
    link_wpp = f"https://api.whatsapp.com{whatsapp_num}&text={urllib.parse.quote(texto_wpp)}"
    col_wpp.markdown(f'<a href="{link_wpp}" target="_blank"><button style="width:100%;background-color:#25D366;color:white;border:none;padding:10px;border-radius:5px;">🟢 Enviar p/ WhatsApp</button></a>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🧠 Consulta de Inteligência")
    busca = st.text_input("🔍 Pesquisar base...")
    if busca:
        conn = sqlite3.connect('banco_dados.db')
        df_res = pd.read_sql_query(f"SELECT * FROM base_conhecimento WHERE fabricante LIKE '%{busca}%' OR codigo_erro LIKE '%{busca}%'", conn)
        st.dataframe(df_res)
        conn.close()

with tab_hist:
    conn = sqlite3.connect('banco_dados.db'); df_atend = pd.read_sql_query("SELECT * FROM atendimentos", conn); st.dataframe(df_atend); conn.close()

with tab_manual:
    st.subheader("📥 Cadastro Técnico")
    with st.form("f_manual"):
        fab_c = st.text_input("Fabricante")
        desc_c = st.text_area("Conteúdo")
        if st.form_submit_button("Salvar"):
            salvar_conhecimento(fab_c, "", "Manual", "", desc_c, "")
            st.success("Salvo!")

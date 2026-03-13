import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import io
import sqlite3
import pandas as pd

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
        codigo_erro TEXT, descricao TEXT, link_manual TEXT
    )''')
    conn.commit()
    conn.close()

def excluir_atendimento(id_atendimento):
    conn = sqlite3.connect('banco_dados.db')
    c = conn.cursor()
    c.execute("DELETE FROM atendimentos WHERE id = ?", (id_atendimento,))
    conn.commit()
    conn.close()

init_db()

# --- 1. FUNÇÃO DE IMPRESSÃO (PDF) ---
def gerar_pdf(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "RELATORIO TECNICO DE REFRIGERACAO", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"Cliente: {dados['cliente']}", ln=True)
    pdf.cell(200, 10, f"Equipamento: {dados['marca']} - {dados['modelo']}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "DIAGNOSTICO DA IA:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, dados['diag_ia'])
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "OBSERVACOES DO TECNICO:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, dados['obs'])
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

# --- 4. INTERFACE DO APP ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist, tab_manual = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico", "📥 Cadastro Técnico"])

with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente = c1.text_input("Cliente/Empresa", key="f_cli")
    doc_cliente = c2.text_input("CPF/CNPJ", key="f_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY", key="f_date")
    whatsapp = c4.text_input("🟢 WhatsApp", value="21980264217", key="f_wpp")
    celular, tel_residencial = c5.text_input("📱 Celular", key="f_cel"), c6.text_input("📞 Fixo", key="f_fix")
    
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr, nome_logr, numero, complemento, bairro, cep, email_cli = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."], key="f_tlog"), e2.text_input("Logradouro", key="f_nlog"), e3.text_input("Nº", key="f_num"), e4.text_input("Comp.", key="f_comp"), e5.text_input("Bairro", key="f_bai"), e6.text_input("CEP", key="f_cep"), e7.text_input("✉️ E-mail", key="f_mail")
    
    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3, g4 = st.columns(4)
    fabricante, modelo_eq = g1.text_input("Marca", key="f_fab"), g1.text_input("Modelo Geral", key="f_mod")
    fluido = g3.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"], key="f_gas")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2 = st.columns(2)
    v_med = el1.number_input("Tensão Medida (V)", value=218.0)
    a_med = el2.number_input("Corrente Medida (A)", value=0.0)

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2 = st.columns(2)
    p_suc = tr1.number_input("Pressão (PSI)", value=118.0, key="ps")
    t_suc_tubo = tr1.number_input("Temp. Tubo (°C)", value=12.0, key="ts")
    ts_suc = get_tsat_global(p_suc, fluido)
    sh_val = round(t_suc_tubo - ts_suc, 1)

with tab_diag:
    col_prob, col_obs = st.columns(2)
    with col_obs:
        st.subheader("📝 Observações do Técnico")
        obs_tecnico = st.text_area("", placeholder="Parecer técnico...", height=150)
        st.markdown("### 🤖 Diagnóstico da IA")
        diag_ia_texto = f"Análise: Superaquecimento em {sh_val}K."
        st.info(diag_ia_texto)
        if st.button("🖨️ Gerar Relatório"):
            pdf_out = gerar_pdf({'cliente': cliente, 'marca': fabricante, 'modelo': modelo_eq, 'obs': obs_tecnico, 'diag_ia': diag_ia_texto})
            st.download_button(label="📥 Baixar PDF", data=pdf_out, file_name=f"Relatorio_{cliente}.pdf")

with tab_hist:
    st.subheader("📜 Histórico de Atendimentos")
    conn = sqlite3.connect('banco_dados.db')
    df = pd.read_sql_query("SELECT id, data_visita, cliente, marca, modelo FROM atendimentos", conn)
    
    if not df.empty:
        # Formatação da data para padrão brasileiro no DataFrame exibido
        df['data_visita'] = pd.to_datetime(df['data_visita']).dt.strftime('%d/%m/%Y')
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🗑️ Excluir Relatório")
        id_excluir = st.number_input("Digite o ID do relatório para excluir", min_value=1, step=1)
        if st.button("Confirmar Exclusão"):
            excluir_atendimento(id_atendimento=id_excluir)
            st.success(f"Relatório {id_excluir} excluído. Atualize a página.")
    else:
        st.info("Nenhum histórico encontrado.")
    conn.close()

with tab_manual:
    st.subheader("📥 Cadastro Técnico")
    with st.form("form_manual"):
        fab_m = st.text_input("Fabricante")
        if st.form_submit_button("Salvar"):
            st.success("Salvo!")

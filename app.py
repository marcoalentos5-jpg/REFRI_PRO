import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import io
import sqlite3
import pandas as pd
import unicodedata
import time

# --- 0. CONFIGURAÇÃO E CONSTANTES ---
NOME_APP = "MPN | Engenharia & Diagnóstico"
VERSAO = "2.0.4-PRO"

# --- 1. BANCO DE DADOS (ESTRUTURA BLOQUEADA) ---
def init_db():
    """Inicializa o banco de dados com a estrutura definida e imutável."""
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
    conn.commit()
    conn.close()

def salvar_dados(dados):
    """Executa a persistência dos dados de atendimento."""
    try:
        conn = sqlite3.connect('banco_dados.db')
        c = conn.cursor()
        c.execute('''INSERT INTO atendimentos (
            data_visita, cliente, doc_cliente, whatsapp, celular, fixo, endereco, email,
            marca, modelo, serie_evap, linha, capacidade, serie_cond, tecnologia, fluido,
            loc_evap, sistema, loc_cond, v_rede, v_med, a_med, rla, lra, p_suc, p_liq,
            sh, sc, problemas, medidas, observacoes
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', dados)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar no banco: {e}")
        return False

# --- 2. MOTOR TERMODINÂMICO (ÂNCORAS DE SATURAÇÃO) ---
def get_tsat_global(psig, gas):
    """Realiza a interpolação linear para encontrar a temperatura de saturação."""
    ancoras = {
        "R-410A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                   "t": [-51.0, -17.02, -0.29, 11.55, 20.93, 28.84, 35.58, 41.74, 47.3, 52.1, 56.59, 60.7, 64.59]},
        "R-32": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                 "t": [-51.7, -17.46, 0.87, 10.86, 20.14, 27.9, 34.63, 40.6, 45.96, 50.8, 55.36, 59.5, 63.43]},
        "R-22": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 600.0], 
                 "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 73.2, 78.38, 87.53]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 80.0, 100.0, 130.0, 150.0, 180.0, 200.0], 
                   "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 38.4, 43.65, 50.1, 53.74]}
    }
    if gas not in ancoras or psig is None: return 0.0
    try:
        val = float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"]))
        return round(val, 2)
    except:
        return 0.0

# --- 3. UTILITÁRIOS DE STRING E SEGURANÇA ---
def clean(txt):
    """Sanitiza strings para o formato PDF (Latin-1)."""
    if not txt: return "N/A"
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 
                    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C', '°': 'C', 'º': '.'}
    res = str(txt)
    for old, new in replacements.items(): res = res.replace(old, new)
    return res.encode('ascii', 'ignore').decode('ascii')

def seguro(v, padrao=0.0):
    try:
        return float(v) if v is not None else padrao
    except:
        return padrao
st.set_page_config(page_title=NOME_APP, layout="wide", page_icon="❄️")

# CSS para Bloqueio de Layout
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #e1e4e8; border-radius: 5px; height: 50px; width: 100%;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #003366; color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"])

with tab_cad:
    st.subheader("👤 Identificação e Equipamento")
    c1, c2, c3 = st.columns([2, 1, 1])
    cliente = c1.text_input("Cliente/Empresa", key="f_cli")
    doc_cliente = c2.text_input("CPF/CNPJ", key="f_doc")
    data_visita = c3.date_input("📅 DATA", value=date.today(), format="DD/MM/YYYY")

    c4, c5, c6 = st.columns(3)
    whatsapp = c4.text_input("🟢 WhatsApp", value="21980264217")
    celular = c5.text_input("📱 Celular")
    tel_residencial = c6.text_input("📞 Fixo")

    st.markdown("---")
    g1, g2, g3 = st.columns(3)
    with g1:
        fabricante = st.text_input("Marca")
        modelo_eq = st.text_input("Modelo")
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "On-Off", "VRF", "Chiller"])
    with g2:
        linha = st.text_input("Linha")
        cap_digitada = st.text_input("Capacidade (BTU/h)")
        fluido = st.selectbox("Fluido", ["R-410A", "R-32", "R-22", "R-134a"])
    with g3:
        serie_evap = st.text_input("Série Evap.")
        serie_cond = st.text_input("Série Cond.")
        tipo_eq = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto"])

with tab_ele:
    st.subheader("⚡ Parâmetros de Energia")
    el1, el2, el3 = st.columns(3)
    with el1:
        v_rede = st.number_input("Tensão Nominal (V)", value=220.0)
        v_med = st.number_input("Tensão Medida (V)", value=218.0)
        diff_v = round(v_rede - v_med, 1)
        st.metric("Queda de Tensão", f"{diff_v} V")
    with el2:
        rla_comp = st.number_input("Corrente RLA (A)", value=1.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
    with el3:
        lra_comp = st.number_input("Corrente LRA (A)", value=0.0)
init_db()
with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        p_suc = st.number_input("Pressão Sucção (PSI)", value=118.0)
        t_suc_tubo = st.number_input("Temp. Sucção (°C)", value=12.0)
        ts_suc = get_tsat_global(p_suc, fluido)
    with tr2:
        p_liq = st.number_input("Pressão Líquido (PSI)", value=345.0)
        t_liq_tubo = st.number_input("Temp. Líquido (°C)", value=30.0)
        ts_liq = get_tsat_global(p_liq, fluido)
    with tr3:
        sh_val = round(t_suc_tubo - ts_suc, 1)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        st.metric("Superaquecimento", f"{sh_val} K")
        st.metric("Subresfriamento", f"{sc_val} K")

# --- LÓGICA DE DIAGNÓSTICO CRUZADO ---
diagnosticos_ia = []
if sh_val > 12 and sc_val < 3:
    diagnosticos_ia.append("🚩 Alerta: Baixa Carga de Fluido Refrigerante.")
elif sh_val < 4 and sc_val > 12:
    diagnosticos_ia.append("🚩 Alerta: Excesso de Carga/Inundação.")
if abs(diff_v) > (v_rede * 0.1):
    diagnosticos_ia.append("🚩 Alerta: Tensão Fora da Faixa (Risco Elétrico).")

with tab_diag:
    st.subheader("🤖 Diagnóstico Automático e Erros Comuns")
    for d in diagnosticos_ia: st.error(d)
    
    st.markdown("---")
    col_e, col_o = st.columns(2)
    with col_e:
        st.write("**Selecione Erros Identificados:**")
        lista_erros = ["Vazamento", "Capacitor Fraco", "Filtro Obstruído", "Placa Inverter", "Sensor de Degelo", "Motor Travado"]
        selecionados = [e for e in lista_erros if st.checkbox(e)]
    with col_o:
        obs_tecnico = st.text_area("Parecer Técnico Final", height=150)

    # Botão de Finalização
    if st.button("📄 GERAR RELATÓRIO E SALVAR"):
        if not cliente: st.warning("Nome do cliente obrigatório.")
        else:
            res_diag = " | ".join(diagnosticos_ia + selecionados)
            dados = (str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_residencial, "", "", fabricante, modelo_eq, serie_evap, linha, cap_digitada, serie_cond, tecnologia, fluido, "", tipo_eq, "", v_rede, v_med, a_med, rla_comp, lra_comp, p_suc, p_liq, sh_val, sc_val, res_diag, "Executado", obs_tecnico)
            if salvar_dados(dados):
                st.success("Dados salvos! Gerando PDF...")
                # Lógica de PDF simplificada para exemplo
                pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 14)
                pdf.cell(190, 10, clean(f"Relatório: {cliente}"), 0, 1, 'C')
                pdf.set_font("Arial", '', 10)
                pdf.cell(190, 10, clean(f"Diagnóstico: {res_diag}"), 0, 1)
                st.download_button("📥 Baixar Relatório", pdf.output(dest='S').encode('latin-1'), f"{cliente}.pdf")
                with tab_hist:
    st.subheader("📜 Histórico (Padrão DD/MM/YYYY)")
    conn = sqlite3.connect('banco_dados.db')
    df = pd.read_sql_query("SELECT id, data_visita, cliente, sh, sc FROM atendimentos ORDER BY id DESC", conn)
    conn.close()
    if not df.empty:
        df['data_visita'] = pd.to_datetime(df['data_visita']).dt.strftime('%d/%m/%Y')
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum registro encontrado.")

st.markdown(f"<center><small>{NOME_APP} v{VERSAO} | 2026</small></center>", unsafe_allow_html=True)

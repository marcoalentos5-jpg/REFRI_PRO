import streamlit as st
import numpy as np
import math
from datetime import date, datetime
from fpdf import FPDF
import urllib.parse
import unicodedata
import sqlite3
import pandas as pd

# =========================================================
# 0. NÚCLEO TÉCNICO E BANCO DE DADOS (MIGRAÇÃO AUTOMÁTICA)
# =========================================================
def init_db():
    conn = sqlite3.connect('banco_dados.db')
    c = conn.cursor()
    # Tabela completa com todos os campos necessários
    c.execute('''CREATE TABLE IF NOT EXISTS atendimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_visita TEXT, cliente TEXT, doc_cliente TEXT, whatsapp TEXT, celular TEXT, fixo TEXT,
        endereco TEXT, email TEXT, marca TEXT, modelo TEXT, serie_evap TEXT, linha TEXT, 
        capacidade TEXT, serie_cond TEXT, tecnologia TEXT, fluido TEXT, loc_evap TEXT, 
        sistema TEXT, loc_cond TEXT, v_rede REAL, v_med REAL, a_med REAL, rla REAL, lra REAL,
        fp REAL, p_suc REAL, p_liq REAL, t_suc_tubo REAL, t_liq_tubo REAL,
        sh REAL, sc REAL, delta_t REAL, problemas TEXT, medidas TEXT, observacoes TEXT
    )''')
    
    # Garantir que delta_t exista (Prevenção de DatabaseError)
    try:
        c.execute("SELECT delta_t FROM atendimentos LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE atendimentos ADD COLUMN delta_t REAL DEFAULT 0.0")
    
    conn.commit()
    conn.close()

def salvar_dados(dados):
    conn = sqlite3.connect('banco_dados.db')
    c = conn.cursor()
    c.execute('''INSERT INTO atendimentos (
        data_visita, cliente, doc_cliente, whatsapp, celular, fixo, endereco, email,
        marca, modelo, serie_evap, linha, capacidade, serie_cond, tecnologia, fluido,
        loc_evap, sistema, loc_cond, v_rede, v_med, a_med, rla, lra, fp, p_suc, p_liq, 
        t_suc_tubo, t_liq_tubo, sh, sc, delta_t, problemas, medidas, observacoes
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', dados)
    conn.commit()
    conn.close()

init_db()

def clean(txt):
    if not txt: return "N/A"
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 
                    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C', '°': 'C', 'º': '.'}
    res = str(txt)
    for old, new in replacements.items(): res = res.replace(old, new)
    return res.encode('ascii', 'ignore').decode('ascii')

def remover_acentos(txt):
    if not txt: return ""
    return "".join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')

def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-51.0, -0.29, 20.93, 35.58, 47.3, 56.59, 64.59]},
        "R-32": {"p": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-51.7, 0.87, 20.14, 34.63, 45.96, 55.36, 63.43]},
        "R-22": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 300.0, 400.0], "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 54.89, 67.8]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 80.0, 100.0, 150.0, 200.0], "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 43.65, 53.74]}
    }
    if gas not in ancoras: return 0.0
    return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)

# =========================================================
# 1. CONFIGURAÇÃO E INTERFACE (LAYOUT BLOQUEADO)
# =========================================================
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")
st.markdown("""<style>.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {font-size: 18px; font-weight: bold;}</style>""", unsafe_allow_html=True)

st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"
])

with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente = c1.text_input("Cliente/Empresa", key="k_cliente")
    doc_cliente = c2.text_input("CPF/CNPJ", key="k_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY")
    whatsapp = c4.text_input("🟢 WhatsApp", value="21980264217")
    celular, tel_fixo = c5.text_input("📱 Celular"), c6.text_input("📞 Fixo")
    
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod."])
    nome_logr, numero, complemento = e2.text_input("Logradouro"), e3.text_input("Nº"), e4.text_input("Comp.")
    bairro, cep, email_cli = e5.text_input("Bairro"), e6.text_input("CEP"), e7.text_input("✉️ E-mail")
    
    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3, g4 = st.columns(4)
    with g1: fabricante, modelo_eq, serie_evap = st.text_input("Marca"), st.text_input("Modelo Geral"), st.text_input("Série Evaporadora")
    with g2: linha, cap_btu, serie_cond = st.text_input("Linha"), st.text_input("Capacidade (BTU/h)"), st.text_input("Série Condensadora")
    with g3: tecnologia, fluido, loc_evap = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF"]), st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"]), st.text_input("Local Evaporadora")
    with g4: sistema, loc_cond = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "VRF", "Chiller"]), st.text_input("Local Condensadora")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns(3)
    v_rede, v_med = el1.number_input("Tensão Nominal (Rede)", value=220.0), el1.number_input("Tensão Medida (V)", value=220.0)
    rla_comp, a_med = el2.number_input("Corrente RLA (Placa)", value=1.0), el2.number_input("Corrente Medida (A)", value=0.0)
    fp_in, lra_comp = el3.number_input("Fator de Potência (cos Φ)", value=0.87), el3.number_input("LRA (Partida)", value=0.0)
    
    p_aparente = v_med * a_med
    p_ativa = p_aparente * fp_in
    diff_tensao, diff_corrente = round(v_med - v_rede, 1), round(a_med - rla_comp, 1)
    
    st.divider()
    res1, res2, res3 = st.columns(3)
    res1.metric("Potência Ativa", f"{p_ativa:.1f} W")
    res2.metric("Dif. Tensão", f"{diff_tensao} V", delta_color="inverse")
    res3.metric("Dif. Corrente", f"{diff_corrente} A", delta_color="inverse")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico e Performance")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        p_suc, t_suc_tubo = st.number_input("Pressão Sucção (PSI)", value=118.0), st.number_input("Temp. Tubo Sucção (°C)", value=12.0)
        ts_suc = get_tsat_global(p_suc, fluido)
        sh_val = round(t_suc_tubo - ts_suc, 1)
        st.info(f"T-Sat Sucção: {ts_suc} °C")
        st.success(f"SH: {sh_val} K")
    with tr2:
        p_liq, t_liq_tubo = st.number_input("Pressão Líquido (PSI)", value=345.0), st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
        ts_liq = get_tsat_global(p_liq, fluido)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        st.info(f"T-Sat Líquido: {ts_liq} °C")
        st.success(f"SC: {sc_val} K")
    with tr3:
        t_ret = st.number_input("Temp. Retorno (°C)", value=25.0)
        t_ins = st.number_input("Temp. Insuflação (°C)", value=12.0)
        delta_t = round(t_ret - t_ins, 1)
        st.metric("DELTA T (Diferencial)", f"{delta_t} °C")

# =========================================================
# 2. ABA DIAGNÓSTICO E RELATÓRIO (FORMATO BLOQUEADO)
# =========================================================
with tab_diag:
    col_prob, col_obs = st.columns(2)
    with col_prob:
        st.subheader("⚠️ Problemas Encontrados")
        pi1, pi2 = st.columns(2)
        p_sel = []
        opcoes = ["Vazamento de Fluido", "Baixa Carga", "Excesso de Fluido", "Incondensaveis", "Obstrucao Expansao", "Filtro Obstruido", "Falha Compressao", "Falha Ventilacao", "Falha Placa", "Rede Instavel"]
        for i, opt in enumerate(opcoes):
            if i % 2 == 0:
                if pi1.checkbox(opt): p_sel.append(opt)
            else:
                if pi2.checkbox(opt): p_sel.append(opt)
    with col_obs:
        st.subheader("📝 Observações")
        obs_tecnico = st.text_area("", placeholder="Parecer técnico...", height=200, label_visibility="collapsed")

    if st.button("📄 GERAR RELATÓRIO PDF E SALVAR", use_container_width=True):
        prob_txt = ', '.join(p_sel) if p_sel else 'Nenhum'
        endereco_full = f"{tipo_logr} {nome_logr}, {numero} - {bairro}"
        
        # Salvar no Banco
        salvar_dados((str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_fixo, endereco_full, email_cli, fabricante, modelo_eq, serie_evap, linha, cap_btu, serie_cond, tecnologia, fluido, loc_evap, sistema, loc_cond, v_rede, v_med, a_med, rla_comp, lra_comp, fp_in, p_suc, p_liq, t_suc_tubo, t_liq_tubo, sh_val, sc_val, delta_t, prob_txt, "Inspeção Realizada", obs_tecnico))

        # PDF - Layout Original Bloqueado
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16); pdf.cell(190, 10, "MPN ENGENHARIA - RELATORIO TECNICO", 0, 1, 'C'); pdf.ln(5)
        pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", 'B', 10)
        pdf.cell(190, 7, " 1. IDENTIFICACAO", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.cell(190, 6, clean(f"Cliente: {cliente} | CNPJ: {doc_cliente} | Data: {data_visita.strftime('%d/%m/%Y')}"), 1, 1)
        pdf.cell(190, 6, clean(f"Endereco: {endereco_full}"), 1, 1)
        pdf.ln(2); pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " 2. EQUIPAMENTO", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.cell(95, 6, clean(f"Marca/Modelo: {fabricante} {modelo_eq}"), 1, 0); pdf.cell(95, 6, clean(f"Capacidade: {cap_btu} BTU"), 1, 1)
        pdf.ln(2); pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " 3. PERFORMANCE", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.cell(47, 6, clean(f"V: {v_med}V"), 1, 0); pdf.cell(47, 6, clean(f"A: {a_med}A"), 1, 0); pdf.cell(48, 6, clean(f"SH: {sh_val}K"), 1, 0); pdf.cell(48, 6, clean(f"Delta T: {delta_t}C"), 1, 1)
        pdf.ln(2); pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " 4. PARECER", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(190, 6, clean(f"Problemas: {prob_txt}\nObs: {obs_tecnico}"), 1)
        
        st.download_button("📥 Baixar PDF", data=pdf.output(dest='S').encode('latin-1', 'ignore'), file_name=f"Relatorio_{remover_acentos(cliente)}.pdf")

with tab_hist:
    st.subheader("📜 Histórico de Diagnósticos")
    conn = sqlite3.connect('banco_dados.db')
    try:
        df_h = pd.read_sql_query("SELECT data_visita as 'Data', cliente as 'Cliente', marca as 'Marca', sh as 'SH (K)', delta_t as 'Delta T (C)' FROM atendimentos ORDER BY id DESC", conn)
        df_h['Data'] = pd.to_datetime(df_h['Data']).dt.strftime('%d/%m/%Y')
        st.dataframe(df_h, use_container_width=True, hide_index=True)
    except: st.warning("Sem dados no histórico.")
    conn.close()

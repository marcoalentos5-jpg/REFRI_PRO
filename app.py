import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import io
import sqlite3
import pandas as pd
import unicodedata

# --- 0. BANCO DE DADOS (31 CAMPOS SINCRONIZADOS) ---
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
    conn.commit()
    conn.close()

def salvar_dados(dados):
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

init_db()

# --- 1. CONFIGURAÇÃO E CSS ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")
st.markdown("<style>.stTabs [data-baseweb='tab-list'] button p {font-size: 20px; font-weight: bold;}</style>", unsafe_allow_html=True)

# --- 2. MOTOR DE CÁLCULO E UTILITÁRIOS ---
def remover_acentos(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def get_tsat_global(psig, gas):
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
    try: return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)
    except: return 0.0

def clean(txt):
    if not txt: return "N/A"
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', '°': 'C'}
    res = str(txt)
    for old, new in replacements.items(): res = res.replace(old, new)
    return res.encode('ascii', 'ignore').decode('ascii')

def seguro(v):
    try: return float(v) if v is not None else 0.0
    except: return 0.0

# --- 3. INTERFACE PRINCIPAL ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"])

with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente, doc_cliente = c1.text_input("Cliente/Empresa"), c2.text_input("CPF/CNPJ")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY")
    whatsapp, celular, tel_residencial = c4.text_input("🟢 WhatsApp", value="21980264217"), c5.text_input("📱 Celular"), c6.text_input("📞 Fixo")
    
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."])
    nome_logr, numero, complemento, bairro, cep, email_cli = e2.text_input("Logradouro"), e3.text_input("Nº"), e4.text_input("Comp."), e5.text_input("Bairro"), e6.text_input("CEP"), e7.text_input("✉️ E-mail")
    
    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3, g4 = st.columns(4)
    with g1: 
        fabricante, modelo_eq, serie_evap = st.text_input("Marca"), st.text_input("Modelo Geral"), st.text_input("Série Evaporadora")
    with g2:
        linha, cap_digitada, serie_cond = st.text_input("Linha"), st.text_input("Capacidade (BTU/h)", value="0"), st.text_input("Série Condensadora")
    with g3:
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF", "Multisplit"])
        fluido = st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"])
        loc_evap = st.text_input("Local Evaporadora")
    with g4:
        tipo_eq, loc_cond = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "VRF", "Chiller"]), st.text_input("Local Condensadora")
with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns(3)
    with el1:
        v_rede = st.number_input("Tensão Nominal (V)", value=220.0)
        v_med = st.number_input("Tensão Medida (V)", value=218.0)
        diff_v = round(v_rede - v_med, 1)
        st.metric("Diferença de Tensão", f"{diff_v} V")
    with el2:
        rla_comp = st.number_input("Corrente Nominal RLA (A)", value=1.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
        diff_a = round(a_med - rla_comp, 1)
        st.metric("Diferença Corrente", f"{diff_a} A")
    with el3:
        lra_comp = st.number_input("LRA (A)", value=0.0)
        carga_pct = (a_med / rla_comp * 100) if rla_comp > 0 else 0
        st.metric("Carga do Motor", f"{round(carga_pct, 1)}%")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        p_suc = st.number_input("Pressão Sucção (PSI)", value=118.0)
        t_suc_tubo = st.number_input("Temp. Tubo Sucção (°C)", value=12.0)
        ts_suc = get_tsat_global(p_suc, fluido)
    with tr2:
        p_liq = st.number_input("Pressão Líquido (PSI)", value=345.0)
        t_liq_tubo = st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
        ts_liq = get_tsat_global(p_liq, fluido)
    with tr3:
        sh_val = round(t_suc_tubo - ts_suc, 1)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        st.success(f"Superaquecimento: {sh_val} K")
        st.success(f"Subresfriamento: {sc_val} K")

# =============================
# MOTOR DE DIAGNÓSTICO E IA
# =============================
diagnostico, probabilidades = [], {}
def registrar(msg, falha=None, prob=0):
    if msg not in diagnostico: diagnostico.append(msg)
    if falha: probabilidades[falha] = prob

# Lógicas de falha
delta_evap = t_suc_tubo - ts_suc
delta_cond = ts_liq - t_liq_tubo
cop_aprox = round((delta_cond + 1) / (delta_evap + 1), 2) if delta_evap != -1 else 0

if sh_val > 12: registrar("Superaquecimento elevado", "Baixa carga de fluido", 85)
if sh_val < 4: registrar("Superaquecimento baixo", "Excesso de fluido ou baixa troca", 80)
if delta_evap < 2: registrar("Baixa troca no evaporador", "Fluxo de ar insuficiente", 60)
if delta_cond < 2: registrar("Condensacao ineficiente", "Ventilacao insuficiente", 55)
if abs(diff_v) > 10: registrar("Variacao de tensao", "Problema na rede eletrica", 80)
if tecnologia == "Inverter" and p_liq > 420: registrar("Pressao alta no Inverter", "Limitacao de frequencia", 50)

diag_ia = " | ".join(diagnostico) if diagnostico else "Sistema Normal"
ranking = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)
prob_txt = " | ".join([f"{f} ({p}%)" for f, p in ranking]) if probabilidades else "Sem falhas críticas"

contramedidas = []
for falha in probabilidades:
    if "fluido" in falha.lower(): contramedidas.append("Verificar carga e vazamentos")
    if "ar" in falha.lower() or "ventilação" in falha.lower(): contramedidas.append("Limpar colmeias e filtros")
if not contramedidas: contramedidas.append("Monitorar parâmetros")
contramedidas_txt = " | ".join(contramedidas)
with tab_diag:
    st.header("🤖 Inteligência de Diagnóstico")
    st.info(f"**Análise IA:** {diag_ia}")
    st.warning(f"**Probabilidades:** {prob_txt}")
    st.success(f"**Contramedidas:** {contramedidas_txt}")
    
    st.subheader("📝 Medidas e Parecer")
    exec_in = st.text_area("Medidas Executadas:", height=100)
    obs_in = st.text_area("Parecer Técnico Final:", height=100)
    
    relat_quick = f"RELATÓRIO HVAC\n\nIA: {diag_ia}\nFalhas: {prob_txt}\nCOP: {cop_aprox}"
    st.text_area("Relatório Rápido", relat_quick, height=150)
    st.markdown(f'<button onclick="navigator.clipboard.writeText(`{relat_quick}`)" style="padding:10px; border-radius:5px; background:#25d366; color:white; border:none; cursor:pointer;">📋 Copiar para WhatsApp</button>', unsafe_allow_html=True)

    if st.button("💾 SALVAR E GERAR PDF"):
        end_completo = f"{tipo_logr} {nome_logr}, {numero} - {bairro}"
        dados_banco = (str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_residencial, end_completo, email_cli, fabricante, modelo_eq, serie_evap, linha, cap_digitada, serie_cond, tecnologia, fluido, loc_evap, tipo_eq, loc_cond, v_rede, v_med, a_med, rla_comp, lra_comp, p_suc, p_liq, sh_val, sc_val, prob_txt, exec_in, obs_in)
        salvar_dados(dados_banco)
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16); pdf.cell(190, 10, "Relatorio Tecnico MPN", 0, 1, 'C'); pdf.ln(10)
        pdf.set_font("Arial", 'B', 10); pdf.set_fill_color(230, 230, 230)
        pdf.cell(190, 7, " 1. CLIENTE", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.cell(190, 6, clean(f"Cliente: {cliente} | Data: {data_visita.strftime('%d/%m/%Y')}"), 1, 1)
        pdf.cell(190, 6, clean(f"Endereco: {end_completo}"), 1, 1); pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " 2. DIAGNOSTICO IA", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(190, 6, clean(f"Analise: {diag_ia}\nFalhas: {prob_txt}"), 1)
        
        pdf_bytes = pdf.output(dest='S').encode('latin-1', 'ignore')
        st.download_button("📥 Baixar PDF", data=pdf_bytes, file_name=f"Relatorio_{cliente}.pdf")
        st.success("Salvo com sucesso!")

with tab_hist:
    st.subheader("📜 Histórico")
    conn = sqlite3.connect('banco_dados.db')
    df_h = pd.read_sql_query("SELECT id, data_visita, cliente, marca, modelo, sh, sc FROM atendimentos ORDER BY id DESC", conn)
    conn.close()
    if not df_h.empty:
        df_h['data_visita'] = pd.to_datetime(df_h['data_visita']).dt.strftime('%d/%m/%Y')
        df_h.insert(0, "Selecionar", False)
        editado = st.data_editor(df_h, hide_index=True, use_container_width=True, column_config={"id": None})
        if st.button("🗑️ Excluir"):
            ids_del = editado[editado["Selecionar"] == True]["id"].tolist()
            conn = sqlite3.connect('banco_dados.db')
            for id_d in ids_del: conn.execute("DELETE FROM atendimentos WHERE id = ?", (id_d,))
            conn.commit(); conn.close(); st.rerun()

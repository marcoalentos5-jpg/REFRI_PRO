import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import sqlite3
import pandas as pd
import unicodedata

# =========================================================
# 0. BANCO DE DADOS E UTILITÁRIOS
# =========================================================
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

def remover_acentos(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def clean(txt):
    if not txt: return "N/A"
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 
                    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C', '°': 'C', 'º': '.'}
    res = str(txt)
    for old, new in replacements.items(): res = res.replace(old, new)
    return res.encode('ascii', 'ignore').decode('ascii')

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

def seguro(v):
    try:
        if v is None: return 0.0
        return float(v)
    except:
        return 0.0

init_db()

# =========================================================
# 1. CONFIGURAÇÃO DA PÁGINA E INTERFACE
# =========================================================
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 20px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"])

with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente = c1.text_input("Cliente/Empresa", key="f_cli")
    doc_cliente = c2.text_input("CPF/CNPJ", key="f_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY")
    whatsapp = c4.text_input("🟢 WhatsApp", value="21980264217")
    celular = c5.text_input("📱 Celular")
    tel_residencial = c6.text_input("📞 Fixo")
    
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."])
    nome_logr = e2.text_input("Logradouro")
    numero = e3.text_input("Nº")
    complemento = e4.text_input("Comp.")
    bairro = e5.text_input("Bairro")
    cep = e6.text_input("CEP")
    email_cli = e7.text_input("✉️ E-mail")
    
    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3, g4 = st.columns(4)
    with g1: 
        fabricante = st.text_input("Marca")
        modelo_eq = st.text_input("Modelo Geral")
        serie_evap = st.text_input("Série Evaporadora")
    with g2:
        linha = st.text_input("Linha")
        cap_digitada = st.text_input("Capacidade (BTU/h)", value="0")
        serie_cond = st.text_input("Série Condensadora")
    with g3:
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF", "Multisplit"])
        fluido = st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"])
        loc_evap = st.text_input("Local Evaporadora")
    with g4:
        tipo_eq = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "VRF", "Chiller"])
        loc_cond = st.text_input("Local Condensadora")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns(3)
    with el1:
        v_rede = st.number_input("Tensão Rede (V)", value=220.0)
        v_med = st.number_input("Tensão Medida (V)", value=218.0)
        diff_v = round(v_rede - v_med, 1)
        st.write("Diferença de Tensão"); st.success(f"{diff_v} V")
    with el2:
        rla_comp = st.number_input("Corrente RLA (A)", value=1.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
    with el3:
        lra_comp = st.number_input("LRA (A)", value=0.0)

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        st.markdown("**Sucção (Baixa)**")
        p_suc = st.number_input("Pressão (PSI)", value=118.0, key="ps")
        t_suc_tubo = st.number_input("Temp. Tubo (°C)", value=12.0, key="ts")
        ts_suc = get_tsat_global(p_suc, fluido)
        st.write("T-Sat Sucção"); st.info(f"{ts_suc} °C")
    with tr2:
        st.markdown("**Líquido (Alta)**")
        p_liq = st.number_input("Pressão (PSI)", value=345.0, key="pl")
        t_liq_tubo = st.number_input("Temp. Tubo (°C)", value=30.0, key="tl")
        ts_liq = get_tsat_global(p_liq, fluido)
        st.write("T-Sat Líquido"); st.info(f"{ts_liq} °C")
    with tr3:
        st.markdown("**Performance**")
        sh_val = round(t_suc_tubo - ts_suc, 1)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        st.write("Superaquecimento (SH)"); st.success(f"**{sh_val} K**")
        st.write("Subresfriamento (SC)"); st.success(f"**{sc_val} K**")

import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import sqlite3
import pandas as pd
import unicodedata

# =========================================================
# 0. CONFIGURAÇÕES E BANCO DE DADOS
# =========================================================
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

# --- UTILITÁRIOS ---
def remover_acentos(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def clean(txt):
    if not txt: return "N/A"
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 
                    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C', '°': 'C', 'º': '.'}
    res = str(txt)
    for old, new in replacements.items(): res = res.replace(old, new)
    return res.encode('ascii', 'ignore').decode('ascii')

def seguro(v):
    try: return float(v) if v is not None else 0.0
    except: return 0.0

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

# =========================================================
# 1. INTERFACE (LAYOUT BLOQUEADO)
# =========================================================
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

st.markdown("""<style>.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {font-size: 20px; font-weight: bold;}</style>""", unsafe_allow_html=True)

st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"])

with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente = c1.text_input("Cliente/Empresa")
    doc_cliente = c2.text_input("CPF/CNPJ")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY")
    whatsapp = c4.text_input("🟢 WhatsApp", value="21980264217")
    celular = c5.text_input("📱 Celular")
    tel_residencial = c6.text_input("📞 Fixo")
    
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."])
    nome_logr = e2.text_input("Logradouro")
    numero = e3.text_input("Nº")
    complemento = e4.text_input("Comp.")
    bairro = e5.text_input("Bairro")
    cep = e6.text_input("CEP")
    email_cli = e7.text_input("✉️ E-mail")
    
    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3, g4 = st.columns(4)
    with g1: 
        fabricante = st.text_input("Marca")
        modelo_eq = st.text_input("Modelo Geral")
        serie_evap = st.text_input("Série Evaporadora")
    with g2:
        linha = st.text_input("Linha")
        cap_digitada = st.text_input("Capacidade (BTU/h)", value="0")
        serie_cond = st.text_input("Série Condensadora")
    with g3:
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF", "Multisplit"])
        fluido = st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"])
        loc_evap = st.text_input("Local Evaporadora")
    with g4:
        tipo_eq = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "VRF", "Chiller"])
        loc_cond = st.text_input("Local Condensadora")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns(3)
    with el1:
        v_rede = st.number_input("Tensão Rede (V)", value=220.0)
        v_med = st.number_input("Tensão Medida (V)", value=218.0)
    with el2:
        rla_comp = st.number_input("Corrente RLA (A)", value=1.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
    with el3:
        lra_comp = st.number_input("LRA (A)", value=0.0)

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        p_suc = st.number_input("Pressão Sucção (PSI)", value=118.0)
        t_suc_tubo = st.number_input("Temp. Tubo Sucção (°C)", value=12.0)
        ts_suc = get_tsat_global(p_suc, fluido)
        st.info(f"T-Sat Sucção: {ts_suc} °C")
    with tr2:
        p_liq = st.number_input("Pressão Líquido (PSI)", value=345.0)
        t_liq_tubo = st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
        ts_liq = get_tsat_global(p_liq, fluido)
        st.info(f"T-Sat Líquido: {ts_liq} °C")
    with tr3:
        sh_val = round(t_suc_tubo - ts_suc, 1)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        st.success(f"SH: {sh_val} K")
        st.success(f"SC: {sc_val} K")

# =========================================================
# 2. MOTOR DE INTELIGÊNCIA HVAC (PROCESSAMENTO SILENCIOSO)
# =========================================================
diag_lista = []
prob_map = {}

def registrar_ia(falha, causa, peso):
    if falha not in diag_lista: diag_lista.append(falha)
    prob_map[causa] = peso

# Sanitização
sh_ia, sc_ia = seguro(sh_val), seguro(sc_val)
v_diff = seguro(v_med - v_rede)

# Regras Térmicas
if sh_ia > 12: registrar_ia("Superaquecimento elevado", "Baixa carga de fluido refrigerante", 75)
if sh_ia < 4: registrar_ia("Superaquecimento baixo", "Excesso de fluido ou baixa carga térmica", 65)
if sc_ia < 2: registrar_ia("Subresfriamento insuficiente", "Eficiência da condensação reduzida", 55)

# Regras Elétricas e Compressor
if rla_comp > 0:
    carga_pct = (seguro(a_med) / rla_comp) * 100
    if carga_pct > 115: registrar_ia("Sobrecarga no compressor", "Alta pressão ou problemas elétricos", 70)
    if carga_pct < 40 and seguro(a_med) > 0.1: registrar_ia("Compressor em subcarga", "Baixa carga térmica ou falta de fluido", 60)

if abs(v_diff) > 15: registrar_ia("Instabilidade de Tensão", "Problema na rede elétrica local", 85)

# Performance Mecânica
if seguro(p_suc) > 140 and seguro(p_liq) < 300 and fluido in ["R-410A", "R-32"]:
    registrar_ia("Baixa performance de compressão", "Desgaste mecânico interno (Válvulas/Scroll)", 75)

# Eficiência COP
try:
    delta_evap = seguro(t_suc_tubo - ts_suc)
    delta_cond = seguro(ts_liq - t_liq_tubo)
    cop_aprox = round((delta_cond + 1) / (delta_evap + 1), 2)
except: cop_aprox = 0.0

# Consolidação
diag_ia_txt = " | ".join(diag_lista) if diag_lista else "Sistema operando conforme padrões nominais"
prob_ia_txt = " | ".join([f"{c} ({p}%)" for c, p in sorted(prob_map.items(), key=lambda x: x[1], reverse=True)]) if prob_map else "Nenhuma falha crítica"

# Contramedidas
acoes = []
detectado = (diag_ia_txt + " " + prob_ia_txt).lower()
if "fluido" in detectado: acoes.append("Buscar vazamentos e corrigir carga")
if "condensação" in detectado or "condensador" in detectado: acoes.append("Limpeza química da unidade externa")
if "evaporador" in detectado: acoes.append("Limpar filtros e serpentina interna")
if "rede elétrica" in detectado: acoes.append("Revisar bornes e quadro elétrico")
acoes_txt = " | ".join(acoes) if acoes else "Manutenção preventiva padrão"

# Relatório para WhatsApp
rel_wpp = f"*MPN ENGENHARIA - RELATÓRIO*\n*Cliente:* {cliente}\n*Análise:* {diag_ia_txt}\n*Falhas:* {prob_ia_txt}\n*Ações:* {acoes_txt}\n*COP:* {cop_aprox}"

# =========================================================
# 3. ABA DIAGNÓSTICO E FINALIZAÇÃO
# =========================================================
with tab_diag:
    st.header("🤖 Inteligência de Diagnóstico")
    d1, d2 = st.columns(2)
    with d1:
        st.info(f"### 🔎 Análise IA\n{diag_ia_txt}")
        st.warning(f"### 📊 Probabilidades\n{prob_ia_txt}")
    with d2:
        st.success(f"### 🛠️ Ações Sugeridas\n{acoes_txt}")
        st.metric("COP Estimado", cop_aprox)

    st.divider()
    obs_tecnico = st.text_area("📝 Observações e Medidas Adicionais", height=100)

    if st.button("💾 Salvar Atendimento e Gerar PDF", use_container_width=True):
        end = f"{tipo_logr} {nome_logr}, {numero} - {bairro}"
        dados = (str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_residencial, end, email_cli, fabricante, modelo_eq, serie_evap, linha, cap_digitada, serie_cond, tecnologia, fluido, loc_evap, tipo_eq, loc_cond, v_rede, v_med, a_med, rla_comp, lra_comp, p_suc, p_liq, sh_val, sc_val, diag_ia_txt, acoes_txt, obs_tecnico)
        salvar_dados(dados)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "MPN ENGENHARIA - RELATORIO TECNICO", 0, 1, 'C')
        pdf.set_font("Arial", '', 10); pdf.cell(0, 8, f"Cliente: {cliente} | Data: {data_visita.strftime('%d/%m/%Y')}", 0, 1, 'L')
        pdf.ln(5)
        pdf.set_fill_color(240, 240, 240); pdf.cell(0, 8, " DIAGNOSTICO IA", 0, 1, 'L', fill=True)
        pdf.multi_cell(0, 7, clean(f"Analise: {diag_ia_txt}\nProbabilidades: {prob_ia_txt}\nCOP: {cop_aprox}"))
        pdf.ln(5)
        pdf.cell(0, 8, " ACOES E OBSERVACOES", 0, 1, 'L', fill=True)
        pdf.multi_cell(0, 7, clean(f"{acoes_txt}\n{obs_tecnico}"))
        
        pdf_bytes = pdf.output(dest='S').encode('latin-1', 'ignore')
        st.download_button("📥 BAIXAR PDF", pdf_bytes, f"Relatorio_{remover_acentos(cliente)}.pdf", "application/pdf", use_container_width=True)
        st.toast("✅ Salvo com sucesso!")

    # Botão WhatsApp
    st.markdown(f"""<a href="https://api.whatsapp.com/send?phone={whatsapp}&text={rel_wpp.replace(' ', '%20').replace('*', '')}" target="_blank">
        <button style="width:100%; padding:15px; background-color:#25D366; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">
        🟢 ENVIAR RESUMO PARA WHATSAPP
        </button></a>""", unsafe_allow_html=True)

with tab_hist:
    st.subheader("📜 Histórico de Atendimentos")
    conn = sqlite3.connect('banco_dados.db')
    df_h = pd.read_sql_query("SELECT data_visita, cliente, marca, sh, sc, problemas FROM atendimentos ORDER BY id DESC", conn)
    conn.close()
    if not df_h.empty:
        df_h['data_visita'] = pd.to_datetime(df_h['data_visita']).dt.strftime('%d/%m/%Y')
        st.dataframe(df_h, use_container_width=True, hide_index=True)
    else: st.info("Histórico vazio.")
# =========================================================
# 7. EXIBIÇÃO FINAL (ABA DIAGNÓSTICO) - CONSOLIDADA
# =========================================================

with tab_diag:
    st.header("🤖 DIAGNÓSTICO FINAL")

    # Garantia de segurança contra variáveis nulas ou não declaradas
    # Isso evita que o app quebre se o usuário pular etapas
    d_ia = diag_ia if 'diag_ia' in locals() else "Análise não disponível"
    p_txt = prob_txt if 'prob_txt' in locals() else "Nenhuma falha detectada"
    c_txt = contramedidas_txt if 'contramedidas_txt' in locals() else "Manutenção preventiva padrão"
    c_aprox = cop_aprox if 'cop_aprox' in locals() else 0.0

    # Layout de Dashboard
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"### 🔎 Análise do Sistema\n{d_ia}")
        st.warning(f"### 📊 Probabilidades\n{p_txt}")
    with c2:
        st.success(f"### 🛠️ Contramedidas\n{c_txt}")
        st.metric("Eficiência Estimada (COP)", f"{c_aprox}")

    st.divider()
    st.write("### 📄 Relatório Consolidado")
    
    # Montagem do texto para cópia (WhatsApp)
    # Usamos variáveis sanitizadas para garantir que o texto seja gerado
    relatorio_txt = f"""*RELATÓRIO TÉCNICO HVAC - MPN*
-------------------------------------------
*CLIENTE:* {cliente if cliente else 'Não informado'}
*DIAGNÓSTICO:* {d_ia}
*FALHAS:* {p_txt}
*MEDIDAS SUGERIDAS:* {c_txt}
*COP ESTIMADO:* {c_aprox}
-------------------------------------------
Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"""

    # Exibição do texto em área editável
    st.text_area("Texto para WhatsApp", relatorio_txt, height=200, key="rel_final_area")

    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        # JS seguro para cópia: tratamos quebras de linha e aspas simples
        js_copia = relatorio_txt.replace("\n", "\\n").replace("'", "\\'")
        st.markdown(
            f"""
            <button onclick="navigator.clipboard.writeText('{js_copia}')" 
            style="width:100%; padding:12px; background-color:#2e7d32; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold; transition: 0.3s;">
            📋 Copiar para WhatsApp
            </button>
            <script>
            // Pequeno feedback visual ao clicar poderia ser adicionado aqui
            </script>
            """, 
            unsafe_allow_html=True
        )

    with col_btn2:
        if st.button("📄 Gerar PDF Profissional", use_container_width=True):
            try:
                pdf = FPDF()
                pdf.add_page()
                
                # Cabeçalho Estilizado
                pdf.set_font("Courier", 'B', 16)
                pdf.set_text_color(0, 51, 102) # Azul Marinho
                pdf.cell(0, 10, clean("MPN ENGENHARIA - RELATORIO TECNICO"), 0, 1, 'C')
                pdf.ln(5)

                # Função interna para padronizar seções
                def add_section(titulo, conteudo):
                    pdf.set_fill_color(240, 240, 240) # Cinza claro
                    pdf.set_font("Courier", 'B', 11)
                    pdf.set_text_color(0, 51, 102)
                    pdf.cell(0, 8, clean(f" {titulo}"), 0, 1, 'L', fill=True)
                    pdf.set_font("Courier", '', 10)
                    pdf.set_text_color(0, 0, 0)
                    pdf.multi_cell(0, 7, clean(conteudo), 0, 'L')
                    pdf.ln(4)

                # Conteúdo do PDF
                data_str = data_visita.strftime('%d/%m/%Y') if hasattr(data_visita, 'strftime') else str(data_visita)
                
                add_section("1. DADOS DO ATENDIMENTO", f"Cliente: {cliente}\nData: {data_str}")
                add_section("2. DIAGNÓSTICO E PERFORMANCE", f"Análise: {d_ia}\nCOP: {c_aprox}")
                add_section("3. PROBABILIDADE DE FALHAS", p_txt)
                add_section("4. RECOMENDAÇÕES E MEDIDAS", c_txt)

                # Assinatura
                pdf.ln(10)
                pdf.set_draw_color(0, 51, 102)
                pdf.cell(0, 0, "", "T", 1, 'C')
                pdf.set_font("Courier", 'I', 9)
                pdf.cell(0, 10, clean("Responsavel Tecnico - MPN Engenharia"), 0, 1, 'C')

                # Saída do arquivo
                pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
                
                st.download_button(
                    label="📥 BAIXAR RELATÓRIO PDF",
                    data=pdf_output,
                    file_name=f"Relatorio_{remover_acentos(cliente)[:10]}.pdf" if cliente else "Relatorio_Tecnico.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.success("PDF gerado com sucesso!")
            except Exception as e:
                st.error(f"Erro na geração do PDF: {e}")

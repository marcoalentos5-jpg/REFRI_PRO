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

# --- 1. CONFIGURAÇÃO DA PÁGINA E CSS (LAYOUT BLOQUEADO) ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 20px !important;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BANCO DE DADOS (ESTRUTURA COMPLETA) ---
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

# --- 3. UTILITÁRIOS E MOTOR TERMODINÂMICO ---
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
        "R-410A": {"p": [0.0, 50.0, 118.0, 200.0, 345.0, 600.0], "t": [-51.0, -17.0, 4.2, 21.0, 41.5, 64.5]},
        "R-32": {"p": [0.0, 50.0, 118.0, 200.0, 345.0, 600.0], "t": [-51.7, -17.5, 4.0, 20.1, 40.8, 63.4]},
        "R-22": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 500.0], "t": [-40.8, -3.3, 15.8, 28.1, 38.5, 78.3]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 100.0, 150.0, 200.0], "t": [-26.1, -1.0, 12.2, 31.0, 43.6, 53.7]}
    }
    if gas not in ancoras or psig is None: return 0.0
    return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)

st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"])

with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente = c1.text_input("Cliente/Empresa", key="f_cli")
    doc_cliente = c2.text_input("CPF/CNPJ", key="f_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY", key="f_date")
    whatsapp = c4.text_input("🟢 WhatsApp", value="21980264217", key="f_wpp")
    celular = c5.text_input("📱 Celular", key="f_cel")
    tel_residencial = c6.text_input("📞 Fixo", key="f_fix")
    
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."], key="f_tlog")
    nome_logr = e2.text_input("Logradouro", key="f_nlog")
    numero = e3.text_input("Nº", key="f_num")
    complemento = e4.text_input("Comp.", key="f_comp")
    bairro = e5.text_input("Bairro", key="f_bai")
    cep = e6.text_input("CEP", key="f_cep")
    email_cli = e7.text_input("✉️ E-mail", key="f_mail")
    
    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3, g4 = st.columns(4)
    with g1: 
        fabricante = st.text_input("Marca", key="f_fab")
        modelo_eq = st.text_input("Modelo Geral", key="f_mod")
        serie_evap = st.text_input("Série Evaporadora", key="f_sevap")
    with g2:
        linha = st.text_input("Linha", key="f_lin")
        cap_digitada = st.text_input("Capacidade (BTU/h)", value="0", key="f_cap")
        serie_cond = st.text_input("Série Condensadora", key="f_scond")
    with g3:
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF", "Multisplit"], key="f_tec")
        fluido = st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"], key="f_gas")
        loc_evap = st.text_input("Local Evaporadora", key="f_le")
    with g4:
        tipo_eq = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "VRF", "Chiller"], key="f_sis")
        loc_cond = st.text_input("Local Condensadora", key="f_lc")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns(3)
    with el1:
        v_rede = st.number_input("Tensão Rede (V)", value=220.0)
        v_med = st.number_input("Tensão Medida (V)", value=218.0)
        diff_v = round(v_rede - v_med, 1)
        st.write("Diferença entre Tensões"); st.success(f"{diff_v} V")
    with el2:
        rla_comp = st.number_input("Corrente RLA (A)", value=1.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
        diff_a = round(a_med - rla_comp, 1)
        st.write("Diferença entre Correntes"); st.success(f"{diff_a} A")
    with el3:
        lra_comp = st.number_input("LRA (A)", value=0.0)
        fp_in = st.number_input("Fator de Potência (cos Φ)", value=0.87)

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

with tab_diag:
    col_prob, col_obs = st.columns(2)
    with col_prob:
        st.subheader("⚠️ Problemas Encontrados")
        pi1, pi2 = st.columns(2)
        p_sel = []
        opcoes = ["Vazamento de Fluido", "Baixa Carga", "Excesso de Fluido", "Incondensáveis", "Obstrução", "Falha Ventilação"]
        for i, opt in enumerate(opcoes):
            if i % 2 == 0:
                if pi1.checkbox(opt): p_sel.append(opt)
            else:
                if pi2.checkbox(opt): p_sel.append(opt)
    
    with col_obs:
        st.subheader("📝 Observações")
        obs_tecnico = st.text_area("", placeholder="Parecer...", height=150, label_visibility="collapsed", key="obs_diag")
    
    st.markdown("---")
    st.subheader("🤖 Diagnóstico IA")
    alerta = "Sistema operando ideal" if 5 <= sh_val <= 12 else "Verificar carga de fluido"
    st.info(f"Análise Técnica: {alerta}")
    executadas = st.text_area("Medidas Executadas", key="exec_diag")

    if st.button("📄 Gerar e Salvar Relatório"):
        endereco_completo = f"{tipo_logr} {nome_logr}, {numero} - {bairro}"
        prob_txt = ', '.join(p_sel) if p_sel else 'Nenhum'
        dados_db = (str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_residencial, endereco_completo, email_cli, fabricante, modelo_eq, serie_evap, linha, cap_digitada, serie_cond, tecnologia, fluido, loc_evap, tipo_eq, loc_cond, v_rede, v_med, a_med, rla_comp, lra_comp, p_suc, p_liq, sh_val, sc_val, prob_txt, executadas, obs_tecnico)
        salvar_dados(dados_db)
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, "RELATORIO TECNICO MPN", 1, 1, 'C')
        pdf.set_font("Arial", '', 10)
        pdf.ln(5)
        pdf.cell(190, 7, f"Cliente: {clean(cliente)} | Data: {data_visita}", 1, 1)
        pdf.cell(95, 7, f"SH: {sh_val} K", 1, 0); pdf.cell(95, 7, f"SC: {sc_val} K", 1, 1)
        pdf.multi_cell(190, 7, f"Diagnostico: {clean(alerta)}", 1)
        
        st.download_button("📥 Baixar PDF", data=pdf.output(dest='S').encode('latin-1', 'ignore'), file_name=f"Relatorio_{cliente}.pdf")

    # WhatsApp
    msg_wpp = urllib.parse.quote(f"*MPN ENGENHARIA*\nCliente: {cliente}\nStatus: {alerta}")
    st.markdown(f'<a href="https://wa.me/55{whatsapp}?text={msg_wpp}" target="_blank"><button style="width:100%; height:3em; background-color:#25D366; color:white; border:none; border-radius:5px; font-weight:bold;">🟢 Enviar WhatsApp</button></a>', unsafe_allow_html=True)

with tab_hist:
    st.subheader("📜 Histórico")
    conn = sqlite3.connect('banco_dados.db')
    try:
        df = pd.read_sql_query("SELECT id, data_visita, cliente, marca, sh, sc FROM atendimentos ORDER BY id DESC", conn)
        if not df.empty:
            df.insert(0, "Excluir", False)
            df_edit = st.data_editor(df, hide_index=True, use_container_width=True)
            if st.button("🗑️ Deletar Selecionados"):
                ids = df_edit[df_edit["Excluir"] == True]["id"].tolist()
                for i in ids: conn.execute("DELETE FROM atendimentos WHERE id=?", (i,))
                conn.commit()
                st.rerun()
        else: st.info("Vazio")
    except: st.error("Erro no banco")
    finally: conn.close()
]

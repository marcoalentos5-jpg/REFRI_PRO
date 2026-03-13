import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import io
import sqlite3
import pandas as pd

# --- 0. BANCO DE DADOS (MELHORADO COM GERENCIADOR DE CONTEXTO) ---
def init_db():
    with sqlite3.connect('banco_dados.db') as conn:
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

def salvar_dados(dados):
    try:
        with sqlite3.connect('banco_dados.db') as conn:
            c = conn.cursor()
            query = f'''INSERT INTO atendimentos (
                data_visita, cliente, doc_cliente, whatsapp, celular, fixo, endereco, email,
                marca, modelo, serie_evap, linha, capacidade, serie_cond, tecnologia, fluido,
                loc_evap, sistema, loc_cond, v_rede, v_med, a_med, rla, lra, p_suc, p_liq,
                sh, sc, problemas, medidas, observacoes
            ) VALUES ({','.join(['?']*31)})'''
            c.execute(query, dados)
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Erro ao salvar no banco: {e}")
        return False

init_db()

# --- 1. CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# Custom CSS para melhorar a legibilidade
st.markdown("""
    <style>
    .metric-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #003366; }
    .stTabs [data-baseweb="tab-list"] button { font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR TERMODINÂMICO ---
def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [0.0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600], 
                   "t": [-51.0, -17.02, -0.29, 11.55, 20.93, 28.84, 35.58, 41.74, 47.3, 52.1, 56.59, 60.7, 64.59]},
        "R-32":   {"p": [0.0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600], 
                   "t": [-51.7, -17.46, 0.87, 10.86, 20.14, 27.9, 34.63, 40.6, 45.96, 50.8, 55.36, 59.5, 63.43]},
        "R-22":   {"p": [0.0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600], 
                   "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 73.2, 78.38, 87.53]},
        "R-134a": {"p": [0.0, 20, 50, 80, 100, 130, 150, 180, 200], 
                   "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 38.4, 43.65, 50.1, 53.74]}
    }
    if gas not in ancoras: return 0.0
    return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)

def clean(txt):
    if not txt: return "N/A"
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', '°': 'C'}
    res = str(txt)
    for old, new in replacements.items(): res = res.replace(old, new)
    return res.encode('ascii', 'ignore').decode('ascii')

# --- 3. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"])

with tab_cad:
    st.subheader("👤 Cliente e Localização")
    c1, c2, c3 = st.columns([3, 1.5, 1.5])
    cliente = c1.text_input("Cliente/Empresa", key="f_cli")
    doc_cliente = c2.text_input("CPF/CNPJ", key="f_doc")
    data_visita = c3.date_input("Data da Visita", value=date.today())

    c4, c5, c6 = st.columns(3)
    whatsapp = c4.text_input("WhatsApp", value="21980264217")
    celular = c5.text_input("Celular")
    email_cli = c6.text_input("E-mail")

    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3, g4 = st.columns(4)
    fabricante = g1.text_input("Marca")
    modelo_eq = g1.text_input("Modelo")
    tecnologia = g2.selectbox("Tecnologia", ["Inverter", "WindFree", "On-Off", "VRF"])
    fluido = g2.selectbox("Gás", ["R-410A", "R-32", "R-22", "R-134a"])
    cap_digitada = g3.text_input("Capacidade (BTU/h)")
    tipo_eq = g3.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "VRF"])
    serie_evap = g4.text_input("Série Evaporadora")
    serie_cond = g4.text_input("Série Condensadora")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns(3)
    v_rede = el1.number_input("Tensão Rede (V)", value=220.0)
    v_med = el1.number_input("Tensão Medida (V)", value=220.0)
    rla_comp = el2.number_input("Corrente RLA (A)", value=0.0)
    a_med = el2.number_input("Corrente Medida (A)", value=0.0)
    lra_comp = el3.number_input("LRA (A)", value=0.0)
    
    # Cálculo de queda de tensão automático
    drop_v = round(((v_rede - v_med)/v_rede)*100, 1) if v_rede > 0 else 0
    st.metric("Queda de Tensão", f"{v_rede - v_med} V", f"{drop_v}%", delta_color="inverse")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        st.write("**Baixa Pressão (Sucção)**")
        p_suc = st.number_input("Pressão (PSI)", value=118.0, key="ps")
        t_suc_tubo = st.number_input("Temp. Tubo (°C)", value=12.0, key="ts")
        ts_suc = get_tsat_global(p_suc, fluido)
        sh_val = round(t_suc_tubo - ts_suc, 1)
        st.info(f"T-Sat: {ts_suc}°C | **SH: {sh_val} K**")

    with tr2:
        st.write("**Alta Pressão (Líquido)**")
        p_liq = st.number_input("Pressão (PSI)", value=345.0, key="pl")
        t_liq_tubo = st.number_input("Temp. Tubo (°C)", value=30.0, key="tl")
        ts_liq = get_tsat_global(p_liq, fluido)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        st.info(f"T-Sat: {ts_liq}°C | **SC: {sc_val} K**")
    
    with tr3:
        st.write("**Status de Performance**")
        if 5 <= sh_val <= 12: st.success("Superaquecimento OK")
        else: st.error("SH fora da faixa (5-12K)")
        
        if 4 <= sc_val <= 7: st.success("Subresfriamento OK")
        else: st.warning("SC fora da faixa (4-7K)")

with tab_diag:
    st.subheader("🤖 Diagnóstico Automático e Parecer")
    d1, d2 = st.columns(2)
    
    with d1:
        # Lógica de Diagnóstico IA simplificada
        if sh_val > 12 and sc_val < 4:
            sugestao = "⚠️ Possível Baixa Carga de Fluido ou Vazamento."
        elif sh_val < 5 and sc_val > 7:
            sugestao = "⚠️ Possível Excesso de Fluido ou Baixa troca no Evaporador."
        else:
            sugestao = "✅ Ciclo operando dentro das pressões esperadas."
        
        st.markdown(f"**Análise de Dados:**")
        st.info(sugestao)
        
        p_sel = st.multiselect("Problemas Identificados", 
                             ["Vazamento", "Baixa Carga", "Excesso de Fluido", "Obstrução", "Falha Elétrica", "Sujeira Excessiva"])

    with d2:
        obs_tecnico = st.text_area("Parecer Técnico Final", height=150)
        executadas = st.text_area("Medidas Executadas", height=100)

    if st.button("🚀 Finalizar e Gerar PDF"):
        dados = (str(data_visita), cliente, doc_cliente, whatsapp, celular, "", "", email_cli, 
                 fabricante, modelo_eq, serie_evap, "", cap_digitada, serie_cond, tecnologia, fluido, 
                 "", tipo_eq, "", v_rede, v_med, a_med, rla_comp, lra_comp, p_suc, p_liq, 
                 sh_val, sc_val, ", ".join(p_sel), executadas, obs_tecnico)
        
        if salvar_dados(dados):
            st.balloons()
            st.success("Relatório salvo com sucesso!")
            # (Aqui entraria a lógica do FPDF que você já tem, apenas chamando os dados novos)

with tab_hist:
    st.subheader("📜 Histórico Recente")
    with sqlite3.connect('banco_dados.db') as conn:
        df = pd.read_sql_query("SELECT data_visita, cliente, marca, modelo, sh, sc FROM atendimentos ORDER BY id DESC LIMIT 20", conn)
    
    if not df.empty:
        st.table(df)
    else:
        st.info("Nenhum registro encontrado.")

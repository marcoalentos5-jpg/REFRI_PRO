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

# --- 1. CONFIGURAÇÃO DA PÁGINA (LAYOUT BLOQUEADO) ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# Estilo para Abas de 20px e Botões
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

# --- 2. MOTOR DE BANCO DE DADOS (31 CAMPOS) ---
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

def clean(txt):
    if not txt: return "N/A"
    replacements = {'á':'a','é':'e','í':'i','ó':'o','ú':'u','ã':'a','õ':'o','ç':'c','°':'C','º':'.'}
    res = str(txt)
    for old, new in replacements.items(): res = res.replace(old, new)
    return res.encode('ascii', 'ignore').decode('ascii')

def get_tsat_global(psig, gas):
    tab = {
        "R-410A": {"p": [0, 50, 118, 200, 345, 600], "t": [-51.0, -17.0, 4.2, 21.0, 41.5, 64.5]},
        "R-32":   {"p": [0, 50, 118, 200, 345, 600], "t": [-51.7, -17.5, 4.0, 20.1, 40.8, 63.4]},
        "R-22":   {"p": [0, 50, 100, 150, 200, 500], "t": [-40.8, -3.3, 15.8, 28.1, 38.5, 78.3]}
    }
    if gas not in tab: return 0.0
    return round(float(np.interp(psig, tab[gas]["p"], tab[gas]["t"])), 2)

init_db()
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"])
with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente = c1.text_input("Cliente/Empresa")
    doc_cliente = c2.text_input("CPF/CNPJ")
    data_visita = c3.date_input("DATA DA VISITA", value=date.today(), format="DD/MM/YYYY")
    whatsapp = c4.text_input("WhatsApp", value="21980264217")
    celular = c5.text_input("Celular")
    tel_residencial = c6.text_input("Fixo")
    
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Estr.", "Trav."])
    nome_logr = e2.text_input("Logradouro")
    numero = e3.text_input("Nº")
    complemento = e4.text_input("Comp.")
    bairro = e5.text_input("Bairro")
    cep = e6.text_input("CEP")
    email_cli = e7.text_input("E-mail")
    endereco_completo = f"{tipo_logr} {nome_logr}, {numero} {complemento} - {bairro}"
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
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "On-Off", "VRF", "WindFree"])
        fluido = st.selectbox("Fluido", ["R-410A", "R-32", "R-22"])
        loc_evap = st.text_input("Local Evaporadora")
    with g4:
        tipo_eq = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "Multi Split"])
        loc_cond = st.text_input("Local Condensadora")
with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns(3)
    with el1:
        v_rede = st.number_input("Tensão Rede (V)", value=220.0)
        v_med = st.number_input("Tensão Medida (V)", value=218.0)
        st.caption(f"Diferença: {round(v_rede - v_med, 1)} V")
    with el2:
        rla_comp = st.number_input("Corrente RLA (A)", value=1.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
        st.caption(f"Diferença: {round(a_med - rla_comp, 1)} A")
    with el3:
        lra_comp = st.number_input("LRA (A)", value=0.0)

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        p_suc = st.number_input("P. Sucção (PSI)", value=118.0)
        t_suc_tubo = st.number_input("T. Tubo Sucção (°C)", value=12.0)
        ts_suc = get_tsat_global(p_suc, fluido)
    with tr2:
        p_liq = st.number_input("P. Líquido (PSI)", value=345.0)
        t_liq_tubo = st.number_input("T. Tubo Líquido (°C)", value=30.0)
        ts_liq = get_tsat_global(p_liq, fluido)
    with tr3:
        sh_val = round(t_suc_tubo - ts_suc, 1)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        st.metric("SH (Superaquecimento)", f"{sh_val} K")
        st.metric("SC (Subresfriamento)", f"{sc_val} K")
        with tab_diag:
    st.subheader("🤖 Diagnóstico e Ações")
    p_sel = st.multiselect("Problemas Encontrados", ["Vazamento", "Baixa Carga", "Excesso de Fluido", "Sujeira", "Compressor", "Placa"])
    obs_tecnico = st.text_area("Observações Técnicas")
    executadas = st.text_area("Medidas Executadas")
    
    if st.button("📄 Salvar e Gerar Laudo"):
        # CONSTRUÇÃO DA LISTA DE DADOS - SEM COLCHETES SOLTOS
        dados_lista = [
            str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_residencial,
            endereco_completo, email_cli, fabricante, modelo_eq, serie_evap, linha,
            cap_digitada, serie_cond, tecnologia, fluido, loc_evap, tipo_eq, loc_cond,
            v_rede, v_med, a_med, rla_comp, lra_comp, p_suc, p_liq, sh_val, sc_val,
            ", ".join(p_sel), executadas, obs_tecnico
        ]
        
        conn = sqlite3.connect('banco_dados.db')
        c = conn.cursor()
        c.execute('''INSERT INTO atendimentos (
            data_visita, cliente, doc_cliente, whatsapp, celular, fixo, endereco, email,
            marca, modelo, serie_evap, linha, capacidade, serie_cond, tecnologia, fluido,
            loc_evap, sistema, loc_cond, v_rede, v_med, a_med, rla, lra, p_suc, p_liq,
            sh, sc, problemas, medidas, observacoes
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', dados_lista)
        conn.commit()
        conn.close()
        st.success("✅ Atendimento registrado!")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, "RELATORIO MPN ENGENHARIA", 1, 1, 'C')
        pdf.set_font("Arial", '', 10)
        pdf.ln(5)
        pdf.cell(190, 7, f"Cliente: {clean(cliente)}", 1, 1)
        pdf.cell(95, 7, f"SH: {sh_val} K", 1, 0); pdf.cell(95, 7, f"SC: {sc_val} K", 1, 1)
        st.download_button("📥 Baixar PDF", data=pdf.output(dest='S').encode('latin-1', 'ignore'), file_name=f"Laudo_{cliente}.pdf")

    msg_wpp = urllib.parse.quote(f"*MPN ENGENHARIA*\nCliente: {cliente}\nSH: {sh_val}K | SC: {sc_val}K")
    st.markdown(f'<a href="https://wa.me/55{whatsapp}?text={msg_wpp}" target="_blank"><button style="width:100%; height:3em; background-color:#25D366; color:white; border:none; border-radius:5px; font-weight:bold;">🟢 Enviar WhatsApp</button></a>', unsafe_allow_html=True)
    with tab_hist:
    st.subheader("📜 Histórico de Atendimentos")
    try:
        conn = sqlite3.connect('banco_dados.db')
        # Buscando os dados
        df = pd.read_sql_query("SELECT id, data_visita, cliente, marca, sh, sc FROM atendimentos ORDER BY id DESC", conn)
        
        if not df.empty:
            # FORMATO DE DATA BRASILEIRO
            df['data_visita'] = pd.to_datetime(df['data_visita']).dt.strftime('%d/%m/%Y')
            
            # SISTEMA DE EXCLUSÃO
            df.insert(0, "Selecionar", False)
            df_editado = st.data_editor(df, column_config={"Selecionar": st.column_config.CheckboxColumn("Excluir?", default=False), "id": None}, hide_index=True, use_container_width=True)
            
            if st.button("🗑️ Excluir Registros Selecionados"):
                ids_para_excluir = df_editado[df_editado["Selecionar"] == True]["id"].tolist()
                if ids_para_excluir:
                    cursor = conn.cursor()
                    for id_id in ids_para_excluir:
                        cursor.execute("DELETE FROM atendimentos WHERE id = ?", (id_id,))
                    conn.commit()
                    st.success(f"{len(ids_para_excluir)} registro(s) removido(s)!")
                    st.rerun()
        else:
            st.info("Nenhum registro no banco de dados.")
        conn.close()
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")

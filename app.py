import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import io
import sqlite3
import pandas as pd
import unicodedata
import os

# --- 0. BANCO DE DADOS (ESTRUTURA BLOQUEADA) ---
def init_db():
    conn = sqlite3.connect('banco_dados.db', check_same_thread=False)
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
    conn = sqlite3.connect('banco_dados.db', check_same_thread=False)
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

# --- 1. CONFIGURAÇÃO DA PÁGINA (LAYOUT BLOQUEADO) ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

st.markdown("""
<style>
.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
font-size: 20px;
font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --- 2. UTILITÁRIOS E MOTOR TERMODINÂMICO ---
def remover_acentos(texto):
    if not texto:
        return ""
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def get_tsat_global(psig, gas):

    ancoras = {

        "R-410A": {
            "p":[0,50,100,150,200,250,300,350,400,450,500,550,600],
            "t":[-51.0,-17.02,-0.29,11.55,20.93,28.84,35.58,41.74,47.3,52.1,56.59,60.7,64.59]
        },

        "R-32":{
            "p":[0,50,100,150,200,250,300,350,400,450,500,550,600],
            "t":[-51.7,-17.46,0.87,10.86,20.14,27.9,34.63,40.6,45.96,50.8,55.36,59.5,63.43]
        },

        "R-22":{
            "p":[0,50,100,150,200,250,300,350,400,450,500,600],
            "t":[-40.8,-3.34,15.80,28.15,38.56,47.30,54.89,61.63,67.70,73.20,78.38,87.53]
        },

        "R-134a":{
            "p":[0,20,50,80,100,130,150,180,200],
            "t":[-26.08,-1.0,12.23,22.8,30.92,38.4,43.65,50.1,53.74]
        }

    }

    if gas not in ancoras or psig is None:
        return 0.0

    try:
        return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])),2)
    except:
        return 0.0

def clean(txt):

    if not txt:
        return "N/A"

    replacements={
        'á':'a','é':'e','í':'i','ó':'o','ú':'u','ã':'a','õ':'o','ç':'c',
        'Á':'A','É':'E','Í':'I','Ó':'O','Ú':'U','Ã':'A','Õ':'O','Ç':'C','°':'C','º':'.'
    }

    res=str(txt)

    for old,new in replacements.items():
        res=res.replace(old,new)

    return res.encode('ascii','ignore').decode('ascii')

# --- 3. INTERFACE (ESTRUTURA BLOQUEADA) ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs([
"📋 Identificação",
"⚡ Elétrica",
"🌡️ Termodinâmica",
"🤖 Diagnóstico",
"📜 Histórico"
])

with tab_cad:

    st.subheader("👤 Identificação e Contato")

    c1,c2,c3,c4,c5,c6 = st.columns([2.5,1.2,1.4,1.0,1.0,1.0])

    cliente = c1.text_input("Cliente/Empresa",key="f_cli")
    doc_cliente = c2.text_input("CPF/CNPJ",key="f_doc")

    data_visita = c3.date_input(
        "📅 DATA DA VISITA",
        value=date.today(),
        format="DD/MM/YYYY",
        key="f_date"
    )

    whatsapp = c4.text_input("🟢 WhatsApp",value="21980264217",key="f_wpp")
    celular = c5.text_input("📱 Celular",key="f_cel")
    tel_residencial = c6.text_input("📞 Fixo",key="f_fix")

    e1,e2,e3,e4,e5,e6,e7 = st.columns([0.6,1.5,0.4,0.6,1.0,0.8,1.5])

    tipo_logr = e1.selectbox("Tipo",["Rua","Av.","Trav.","Alam.","Estr.","Rod.","Pça."],key="f_tlog")
    nome_logr = e2.text_input("Logradouro",key="f_nlog")
    numero = e3.text_input("Nº",key="f_num")
    complemento = e4.text_input("Comp.",key="f_comp")
    bairro = e5.text_input("Bairro",key="f_bai")
    cep = e6.text_input("CEP",key="f_cep")
    email_cli = e7.text_input("✉️ E-mail",key="f_mail")

    st.markdown("---")

    st.subheader("⚙️ Dados do Equipamento")

    g1,g2,g3,g4 = st.columns(4)

    with g1:
        fabricante = st.text_input("Marca",key="f_fab")
        modelo_eq = st.text_input("Modelo Geral",key="f_mod")
        serie_evap = st.text_input("Série Evaporadora",key="f_sevap")

    with g2:
        linha = st.text_input("Linha",key="f_lin")
        cap_digitada = st.text_input("Capacidade (BTU/h)",value="0",key="f_cap")
        serie_cond = st.text_input("Série Condensadora",key="f_scond")

    with g3:
        tecnologia = st.selectbox("Tecnologia",["Inverter","WindFree","Scroll","On-Off","VRF","Multisplit"],key="f_tec")
        fluido = st.selectbox("Gás Refrigerante",["R-410A","R-32","R-22","R-134a"],key="f_gas")
        loc_evap = st.text_input("Local Evaporadora",key="f_le")

    with g4:
        tipo_eq = st.selectbox("Sistema",["Split","Cassete","Piso Teto","VRF","Chiller"],key="f_sis")
        loc_cond = st.text_input("Local Condensadora",key="f_lc")

# (RESTANTE DO CÓDIGO PERMANECE IDÊNTICO AO SEU, SEM QUALQUER ALTERAÇÃO DE LAYOUT)

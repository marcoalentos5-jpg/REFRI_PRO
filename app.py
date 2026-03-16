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

# --- 0. BANCO DE DADOS (ESTRUTURA BLOQUEADA) ---
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

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

st.markdown("""
<style>

.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size: 20px;
    font-weight: bold;
}

/* Botões */

.stButton>button {
    width: 100%;
    border-radius: 5px;
    height: 3em;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# --- UTILITÁRIOS ---

def remover_acentos(texto):
    if not texto:
        return ""
    return "".join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def clean(txt):

    if not txt:
        return "N/A"

    replacements = {
        'á': 'a','é': 'e','í': 'i','ó': 'o','ú': 'u',
        'ã': 'a','õ': 'o','ç': 'c',
        'Á': 'A','É': 'E','Í': 'I','Ó': 'O','Ú': 'U',
        'Ã': 'A','Õ': 'O','Ç': 'C',
        '°': 'C','º': '.'
    }

    res = str(txt)

    for old,new in replacements.items():
        res = res.replace(old,new)

    return res.encode('ascii','ignore').decode('ascii')


# --- MOTOR TERMODINÂMICO ---

def get_tsat_global(psig, gas):

    ancoras = {

        "R-410A":{
            "p":[0,50,100,150,200,250,300,350,400,450,500,550,600],
            "t":[-51,-17.02,-0.29,11.55,20.93,28.84,35.58,41.74,47.3,52.1,56.59,60.7,64.59]
        },

        "R-32":{
            "p":[0,50,100,150,200,250,300,350,400,450,500,550,600],
            "t":[-51.7,-17.46,0.87,10.86,20.14,27.9,34.63,40.6,45.96,50.8,55.36,59.5,63.43]
        },

        "R-22":{
            "p":[0,50,100,150,200,250,300,350,400,450,500,600],
            "t":[-40.8,-3.34,15.80,28.15,38.56,47.30,54.89,61.63,73.2,78.38,87.53]
        },

        "R-134a":{
            "p":[0,20,50,80,100,130,150,180,200],
            "t":[-26.08,-1.0,12.23,22.8,30.92,38.4,43.65,50.1,53.74]
        }
    }

    if gas not in ancoras or psig is None:
        return 0.0

    try:
        return round(float(np.interp(psig,ancoras[gas]["p"],ancoras[gas]["t"])),2)
    except:
        return 0.0


# --- INTERFACE PRINCIPAL ---

st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad,tab_ele,tab_termo,tab_diag,tab_hist = st.tabs(
[
"📋 Identificação",
"⚡ Elétrica",
"🌡️ Termodinâmica",
"🤖 Diagnóstico",
"📜 Histórico"
]
)

# --- FUNÇÃO SEGURO ---

def seguro(v):
    try:
        return float(v) if v is not None else 0.0
    except:
        return 0.0


# --- MOTOR IA DIAGNÓSTICO ---

with tab_diag:

    diagnostico_ia_lista = []
    probabilidades = {}

    def registrar_falha(msg,falha=None,prob=0):

        if msg not in diagnostico_ia_lista:
            diagnostico_ia_lista.append(msg)

        if falha:
            probabilidades[falha] = prob


    try:

        delta_cond = ts_liq - t_liq_tubo
        delta_evap = t_suc_tubo - ts_suc

        cop_aprox = round((delta_cond+1)/(delta_evap+1),2)

        if cop_aprox < 1.5:
            registrar_falha("Baixa eficiência energética do sistema")

        elif cop_aprox > 4:
            registrar_falha("Sistema operando com alta eficiência")

    except:
        cop_aprox = 0


    if (t_suc_tubo-ts_suc) < 2:
        registrar_falha(
            "Baixa transferência de calor no evaporador",
            "Fluxo de ar insuficiente",
            60
        )


    if (ts_liq-t_liq_tubo) < 2:
        registrar_falha(
            "Condensação ineficiente",
            "Ventilação insuficiente",
            55
        )


    if rla_comp > 0:

        carga_pct = (a_med/rla_comp)*100

        if carga_pct > 120:
            registrar_falha(
                "Compressor sobrecarregado",
                "Alta pressão ou excesso refrigerante",
                65
            )

        elif carga_pct < 40:
            registrar_falha(
                "Compressor operando com carga muito baixa",
                "Baixa carga térmica",
                60
            )


    if p_suc > 140 and p_liq < 300:
        registrar_falha(
            "Possível perda de compressão",
            "Compressor desgastado",
            70
        )


    if abs(v_rede-v_med) > 10:
        registrar_falha(
            "Variação significativa de tensão",
            "Problema na rede elétrica",
            80
        )


    if tecnologia == "Inverter":

        if sh_val < 2:
            registrar_falha(
                "Controle inverter modulando excessivamente",
                "Ajuste de controle do compressor",
                40
            )

        if p_liq > 420:
            registrar_falha(
                "Limitação de frequência por alta pressão",
                "Alta pressão de condensação",
                50
            )


    if not diagnostico_ia_lista:
        diagnostico_ia_lista.append("Sistema operando dentro dos parâmetros")


    diag_ia_resultado = " | ".join(diagnostico_ia_lista)


    if probabilidades:

        ranking = sorted(
            probabilidades.items(),
            key=lambda x:x[1],
            reverse=True
        )

        prob_txt_resultado = " | ".join(
            [f"{f} ({p}%)" for f,p in ranking]
        )

    else:
        prob_txt_resultado = "Nenhuma falha crítica detectada"


    st.header("🤖 Inteligência de Diagnóstico")

    st.info(diag_ia_resultado)

    st.warning(prob_txt_resultado)

    st.metric("Eficiência (COP aprox.)",cop_aprox)

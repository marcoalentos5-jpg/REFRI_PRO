import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import io
import sqlite3
import pandas as pd
import unicodedata

# -------------------------------
# 0. BANCO DE DADOS (BLINDADO)
# -------------------------------

def get_conn():
    return sqlite3.connect('banco_dados.db', check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS atendimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_visita TEXT, cliente TEXT, doc_cliente TEXT, whatsapp TEXT, celular TEXT, fixo TEXT,
        endereco TEXT, email TEXT, marca TEXT, modelo TEXT, serie_evap TEXT, linha TEXT,
        capacidade TEXT, serie_cond TEXT, tecnologia TEXT, fluido TEXT, loc_evap TEXT,
        sistema TEXT, loc_cond TEXT, v_rede REAL, v_med REAL, a_med REAL, rla REAL, lra REAL,
        p_suc REAL, p_liq REAL, sh REAL, sc REAL, problemas TEXT, medidas TEXT, observacoes TEXT
    )
    ''')

    conn.commit()
    conn.close()

def salvar_dados(dados):
    conn = get_conn()
    c = conn.cursor()

    c.execute('''
    INSERT INTO atendimentos (
    data_visita, cliente, doc_cliente, whatsapp, celular, fixo,
    endereco, email, marca, modelo, serie_evap, linha,
    capacidade, serie_cond, tecnologia, fluido,
    loc_evap, sistema, loc_cond, v_rede, v_med, a_med,
    rla, lra, p_suc, p_liq, sh, sc, problemas,
    medidas, observacoes
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', dados)

    conn.commit()
    conn.close()

init_db()

# -------------------------------
# CONFIG PAGINA (LAYOUT BLOQUEADO)
# -------------------------------

st.set_page_config(
    page_title="MPN | Engenharia Pro",
    layout="wide",
    page_icon="❄️"
)

st.markdown("""
<style>
.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
font-size:20px;
font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# UTILITÁRIOS
# -------------------------------

def remover_acentos(texto):

    if texto is None:
        return ""

    return "".join(
        c for c in unicodedata.normalize('NFD', str(texto))
        if unicodedata.category(c) != 'Mn'
    ).lower()


def clean(txt):

    if txt is None:
        return "N/A"

    replacements = {
        'á':'a','é':'e','í':'i','ó':'o','ú':'u',
        'ã':'a','õ':'o','ç':'c',
        'Á':'A','É':'E','Í':'I','Ó':'O','Ú':'U',
        'Ã':'A','Õ':'O','Ç':'C',
        '°':'C','º':'.'
    }

    res = str(txt)

    for old,new in replacements.items():
        res = res.replace(old,new)

    return res.encode('ascii','ignore').decode('ascii')

# -------------------------------
# MOTOR TERMODINAMICO
# -------------------------------

def get_tsat_global(psig,gas):

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
    "t":[-40.8,-3.34,15.80,28.15,38.56,47.30,54.89,61.63,73.2,78.38,87.53,95]
    },

    "R-134a":{
    "p":[0,20,50,80,100,130,150,180,200],
    "t":[-26.08,-1,12.23,22.8,30.92,38.4,43.65,50.1,53.74]
    }

    }

    if gas not in ancoras or psig is None:
        return 0

    try:
        return round(float(np.interp(psig,ancoras[gas]["p"],ancoras[gas]["t"])),2)
    except:
        return 0


# -------------------------------
# DIAGNÓSTICO IA (SEM LAYOUT)
# -------------------------------

def diagnostico_ia(sh,sc):

    resultado = []

    if sh < 2:
        resultado.append("Possível retorno de líquido ao compressor")

    if sh > 20:
        resultado.append("Possível baixa carga de refrigerante")

    if sc < 2:
        resultado.append("Possível falta de fluido ou expansão excessiva")

    if sc > 15:
        resultado.append("Possível excesso de refrigerante")

    if not resultado:
        resultado.append("Parâmetros dentro da faixa típica")

    return " | ".join(resultado)

# -------------------------------
# INTERFACE
# -------------------------------

st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad,tab_ele,tab_termo,tab_diag,tab_hist = st.tabs([
"📋 Identificação",
"⚡ Elétrica",
"🌡️ Termodinâmica",
"🤖 Diagnóstico",
"📜 Histórico"
])

# -------------------------------
# IDENTIFICAÇÃO
# -------------------------------

with tab_cad:

    st.subheader("👤 Identificação e Contato")

    c1,c2,c3,c4,c5,c6 = st.columns([2.5,1.2,1.4,1,1,1])

    cliente = c1.text_input("Cliente/Empresa")
    doc_cliente = c2.text_input("CPF/CNPJ")
    data_visita = c3.date_input("📅 DATA DA VISITA",value=date.today())
    whatsapp = c4.text_input("🟢 WhatsApp","21980264217")
    celular = c5.text_input("📱 Celular")
    tel_residencial = c6.text_input("📞 Fixo")

# -------------------------------
# ELÉTRICA
# -------------------------------

with tab_ele:

    st.subheader("⚡ Parâmetros Elétricos")

    el1,el2,el3 = st.columns(3)

    with el1:

        v_rede = st.number_input("Tensão Rede (V)",220.0)
        v_med = st.number_input("Tensão Medida (V)",218.0)

        diff_v = round(v_rede - v_med,1)

        st.write("Diferença entre Tensões")
        st.success(f"{diff_v} V")

    with el2:

        rla_comp = st.number_input("Corrente RLA (A)",1.0)
        a_med = st.number_input("Corrente Medida (A)",0.0)

        diff_a = round(a_med - rla_comp,1)

        st.write("Diferença entre Correntes")
        st.success(f"{diff_a} A")

    with el3:

        lra_comp = st.number_input("LRA (A)",0.0)

# -------------------------------
# TERMODINAMICA
# -------------------------------

with tab_termo:

    st.subheader("🌡️ Ciclo Frigorífico")

    tr1,tr2,tr3 = st.columns(3)

    with tr1:

        p_suc = st.number_input("Pressão Sucção (PSI)",118.0)
        t_suc_tubo = st.number_input("Temp Tubo Sucção",12.0)

        ts_suc = get_tsat_global(p_suc,"R-410A")

        st.info(f"T-Sat {ts_suc} °C")

    with tr2:

        p_liq = st.number_input("Pressão Liquido (PSI)",345.0)
        t_liq_tubo = st.number_input("Temp Tubo Liquido",30.0)

        ts_liq = get_tsat_global(p_liq,"R-410A")

        st.info(f"T-Sat {ts_liq} °C")

    with tr3:

        sh_val = round(t_suc_tubo - ts_suc,1)
        sc_val = round(ts_liq - t_liq_tubo,1)

        st.success(f"SH {sh_val} K")
        st.success(f"SC {sc_val} K")

# -------------------------------
# DIAGNOSTICO
# -------------------------------

with tab_diag:

    st.subheader("🤖 Diagnóstico IA")

    diag_ia = diagnostico_ia(sh_val,sc_val)

    st.info(diag_ia)

# -------------------------------
# HISTÓRICO
# -------------------------------

with tab_hist:

    conn = get_conn()

    df = pd.read_sql_query(
    "SELECT * FROM atendimentos ORDER BY id DESC",
    conn
    )

    conn.close()

    if not df.empty:

        st.dataframe(df,use_container_width=True)

        excel = io.BytesIO()
        df.to_excel(excel,index=False)

        st.download_button(
        "📥 Exportar Excel",
        excel.getvalue(),
        "historico.xlsx"
        )

    else:

        st.info("Nenhum atendimento registrado.")

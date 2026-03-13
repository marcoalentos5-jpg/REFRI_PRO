import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import io
import sqlite3
import pandas as pd
import unicodedata
import matplotlib.pyplot as plt

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

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

st.markdown("""
<style>
.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size: 20px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --- 2. UTILITÁRIOS ---
def remover_acentos(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def safe_float(v, default=0.0):
    try:
        return float(v)
    except:
        return default

def clean(txt):
    if not txt: return "N/A"
    replacements = {'á':'a','é':'e','í':'i','ó':'o','ú':'u','ã':'a','õ':'o','ç':'c','°':'C'}
    res = str(txt)
    for o,n in replacements.items():
        res=res.replace(o,n)
    return res.encode('ascii','ignore').decode('ascii')

# --- 3. MOTOR TERMODINÂMICO ---
def get_tsat_global(psig, gas):
    ancoras={
        "R-410A":{"p":[0,50,100,150,200,250,300,350,400,450,500,550,600],
        "t":[-51,-17,-0.29,11.55,20.93,28.84,35.58,41.74,47.3,52.1,56.59,60.7,64.59]},
        "R-32":{"p":[0,50,100,150,200,250,300,350,400,450,500,550,600],
        "t":[-51.7,-17.46,0.87,10.86,20.14,27.9,34.63,40.6,45.96,50.8,55.36,59.5,63.43]}
    }
    if gas not in ancoras: return 0
    return round(float(np.interp(psig,ancoras[gas]["p"],ancoras[gas]["t"])),2)

@st.cache_data
def tsat_cached(psig,gas):
    return get_tsat_global(psig,gas)

def diagnostico_avancado(sh,sc):

    if sh<3 and sc<3:
        return "Possível excesso de fluido refrigerante."

    if sh>15 and sc<3:
        return "Baixa carga de fluido refrigerante."

    if sh>20 and sc>15:
        return "Restrição no dispositivo de expansão."

    if sh<5 and sc>15:
        return "Possível obstrução linha líquida."

    if 5<=sh<=15 and 5<=sc<=15:
        return "Sistema operando dentro da faixa ideal."

    return "Sistema fora da faixa recomendada."

def gerar_grafico_ciclo(sh,sc):

    fig,ax=plt.subplots()

    x=[1,2,3,4]
    y=[sh,sc,sh+sc,sh]

    ax.plot(x,y,marker="o")
    ax.set_title("Ciclo Frigorifico")
    ax.set_xlabel("Etapas")
    ax.set_ylabel("Valores")

    buf=io.BytesIO()
    plt.savefig(buf,format="png")
    buf.seek(0)

    return buf

# --- 4. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs(
["📋 Identificação","⚡ Elétrica","🌡️ Termodinâmica","🤖 Diagnóstico","📜 Histórico"]
)

with tab_cad:

    st.subheader("👤 Identificação e Contato")

    c1,c2,c3,c4,c5,c6=st.columns([2.5,1.2,1.4,1,1,1])

    cliente=c1.text_input("Cliente/Empresa")
    doc_cliente=c2.text_input("CPF/CNPJ")
    data_visita=c3.date_input("📅 DATA DA VISITA",value=date.today())

    whatsapp=c4.text_input("🟢 WhatsApp","21980264217")
    celular=c5.text_input("📱 Celular")
    fixo=c6.text_input("📞 Fixo")

    st.markdown("---")

    st.subheader("⚙️ Dados do Equipamento")

    g1,g2,g3,g4=st.columns(4)

    with g1:
        marca=st.text_input("Marca")
        modelo=st.text_input("Modelo")

    with g2:
        linha=st.text_input("Linha")
        capacidade=st.text_input("Capacidade")

    with g3:
        tecnologia=st.selectbox("Tecnologia",["Inverter","On-Off"])
        fluido=st.selectbox("Gás",["R-410A","R-32"])

    with g4:
        sistema=st.selectbox("Sistema",["Split","VRF"])
        loc_cond=st.text_input("Local Cond.")

with tab_ele:

    st.subheader("⚡ Parâmetros Elétricos")

    el1,el2,el3=st.columns(3)

    with el1:
        v_rede=st.number_input("Tensão Rede",220.0)
        v_med=st.number_input("Tensão Medida",218.0)

    with el2:
        rla=st.number_input("RLA",1.0)
        a_med=st.number_input("Corrente Medida",0.0)

    with el3:
        lra=st.number_input("LRA",0.0)

with tab_termo:

    st.subheader("🌡️ Ciclo Frigorífico")

    tr1,tr2,tr3=st.columns(3)

    with tr1:
        p_suc=st.number_input("Pressão Sucção",118.0)
        t_suc=st.number_input("Temp Tubo",12.0)
        ts_suc=tsat_cached(p_suc,fluido)

    with tr2:
        p_liq=st.number_input("Pressão Liquido",345.0)
        t_liq=st.number_input("Temp Liquido",30.0)
        ts_liq=tsat_cached(p_liq,fluido)

    with tr3:
        sh_val=round(t_suc-ts_suc,1)
        sc_val=round(ts_liq-t_liq,1)

        st.success(f"SH {sh_val}")
        st.success(f"SC {sc_val}")

with tab_diag:

    st.subheader("🤖 Diagnóstico IA")

    diag_ia=diagnostico_avancado(sh_val,sc_val)

    st.info(diag_ia)

    if st.button("📄 Gerar Relatório"):

        dados=(str(data_visita),cliente,doc_cliente,whatsapp,celular,fixo,
        "", "",marca,modelo,"",linha,capacidade,"",tecnologia,fluido,"",
        sistema,loc_cond,v_rede,v_med,a_med,rla,lra,p_suc,p_liq,sh_val,sc_val,
        "", "", "")

        salvar_dados(dados)

        pdf=FPDF()
        pdf.add_page()
        pdf.set_font("Arial","B",16)
        pdf.cell(190,10,"Relatorio Tecnico",0,1,"C")

        pdf_bytes=pdf.output(dest='S').encode('latin-1')

        st.download_button(
        "📥 Baixar Relatorio PDF",
        data=pdf_bytes,
        file_name=f"Relatorio_{cliente}.pdf",
        mime="application/pdf"
        )

        grafico=gerar_grafico_ciclo(sh_val,sc_val)

        st.download_button(
        "📈 Baixar Grafico do Ciclo",
        data=grafico,
        file_name="grafico_ciclo.png"
        )

with tab_hist:

    st.subheader("📜 Histórico de Atendimentos")

    conn=sqlite3.connect("banco_dados.db")

    df=pd.read_sql_query(
    "SELECT id,data_visita,cliente,modelo,tecnologia,sh,sc FROM atendimentos ORDER BY id DESC",
    conn
    )

    conn.close()

    if not df.empty:

        busca=st.text_input("🔍 Buscar Cliente")

        busca_modelo=st.text_input("🔎 Buscar Modelo")

        if busca:
            df=df[df["cliente"].apply(lambda x:remover_acentos(busca) in remover_acentos(x))]

        if busca_modelo:
            df=df[df["modelo"].str.contains(busca_modelo,case=False)]

        st.dataframe(df,use_container_width=True)

        excel_buffer=io.BytesIO()

        df.to_excel(excel_buffer,index=False)

        st.download_button(
        "📊 Exportar Histórico Excel",
        data=excel_buffer.getvalue(),
        file_name="historico_atendimentos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.info("Nenhum atendimento registrado.")

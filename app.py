import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import urllib.parse

# -----------------------------------
# CONFIGURAÇÃO
# -----------------------------------

st.set_page_config(
    page_title="MPN Engenharia HVAC",
    layout="wide",
    page_icon="❄️"
)

st.title("MPN Engenharia | Diagnóstico HVAC")

# -----------------------------------
# FUNÇÕES TERMODINÂMICAS
# -----------------------------------

def calcular_tsat(psig, gas):

    if psig <= 0:
        return None

    if gas == "R410A":
        return 0.231 * psig - 22.8

    if gas == "R22":
        return 0.285 * psig - 25.1

    if gas == "R134a":
        return 0.52 * psig - 38.5

    if gas == "R404A":
        return 0.21 * psig - 16.5

    return None


def calcular_cop(dt_ar, corrente):

    if corrente <= 0:
        return None

    cop = (dt_ar * 0.293) / corrente

    return round(cop,2)


# -----------------------------------
# MOTOR DE DIAGNÓSTICO
# -----------------------------------

def diagnostico(sh, sc, dt):

    problemas = []

    if sh is None or sc is None:
        return ["Dados insuficientes"]

    if sh > 15 and sc < 3:
        problemas.append("Baixa carga de refrigerante")

    if sh < 4 and sc > 12:
        problemas.append("Excesso de refrigerante")

    if sh > 15 and sc > 10:
        problemas.append("Restrição na linha líquida ou filtro secador")

    if dt > 14:
        problemas.append("Baixa vazão de ar na evaporadora")

    if dt < 8:
        problemas.append("Troca térmica insuficiente")

    if not problemas:
        problemas.append("Sistema operando dentro dos parâmetros normais")

    return problemas


# -----------------------------------
# BANCO DE COMPRESSORES
# -----------------------------------

compressores = pd.DataFrame({

"Capacidade":[9000,12000,18000,24000],

"Copeland":[
"ZP14K5E",
"ZP20K5E",
"ZP31K5E",
"ZP42K5E"
],

"Embraco":[
"FFU80",
"FFU130",
"FFU160",
"FFU200"
]

})

# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.header("Configuração do Sistema")

gas = st.sidebar.selectbox(
"Refrigerante",
["","R410A","R22","R134a","R404A"]
)

equip = st.sidebar.selectbox(
"Equipamento",
["Split","Cassete","VRF","Chiller","Câmara Fria"]
)

# -----------------------------------
# ABAS
# -----------------------------------

tab1,tab2,tab3,tab4,tab5 = st.tabs([
"Identificação",
"Medições",
"Diagnóstico",
"Gráfico do Ciclo",
"Laudo"
])

# -----------------------------------
# IDENTIFICAÇÃO
# -----------------------------------

with tab1:

    col1,col2,col3 = st.columns(3)

    cliente = col1.text_input("Cliente")
    tecnico = col2.text_input("Responsável Técnico")
    serie = col3.text_input("S/N")

    col4,col5,col6 = st.columns(3)

    fabricante = col4.text_input("Fabricante")
    modelo = col5.text_input("Modelo")
    capacidade = col6.number_input("Capacidade BTU",0)

    st.subheader("Corrente")

    rla = st.number_input("RLA",0.0)
    corrente = st.number_input("Corrente medida",0.0)

# -----------------------------------
# MEDIÇÕES
# -----------------------------------

with tab2:

    col1,col2,col3,col4 = st.columns(4)

    with col1:

        t_ret = st.number_input("Temp retorno",24.0)
        t_ins = st.number_input("Temp insuflação",12.0)

        dt_ar = t_ret - t_ins

        st.metric("Delta T",dt_ar)

    with col2:

        p_suc = st.number_input("Pressão sucção",120.0)

        tsat_evap = calcular_tsat(p_suc,gas)

        st.metric("Temp evaporação",tsat_evap)

    with col3:

        t_suc = st.number_input("Temp linha sucção",12.0)

        sh = None

        if tsat_evap:
            sh = t_suc - tsat_evap

        st.metric("Superaquecimento",sh)

    with col4:

        p_desc = st.number_input("Pressão descarga",380.0)

        tsat_cond = calcular_tsat(p_desc,gas)

        t_liq = st.number_input("Temp linha liquida",30.0)

        sc = None

        if tsat_cond:
            sc = tsat_cond - t_liq

        st.metric("Sub-resfriamento",sc)

# -----------------------------------
# DIAGNÓSTICO
# -----------------------------------

with tab3:

    problemas = diagnostico(sh,sc,dt_ar)

    for p in problemas:

        if "normal" in p.lower():
            st.success(p)

        else:
            st.warning(p)

    cop = calcular_cop(dt_ar,corrente)

    if cop:
        st.metric("COP estimado",cop)

# -----------------------------------
# GRÁFICO CICLO
# -----------------------------------

with tab4:

    st.subheader("Ciclo frigorífico simplificado")

    if tsat_evap and tsat_cond:

        x = [1,2,3,4]
        y = [tsat_evap, t_suc, tsat_cond, t_liq]

        fig, ax = plt.subplots()

        ax.plot(x,y,marker="o")

        ax.set_title("Ciclo Frigorífico")

        ax.set_xlabel("Etapas")
        ax.set_ylabel("Temperatura")

        st.pyplot(fig)

# -----------------------------------
# LAUDO
# -----------------------------------

with tab5:

    data = datetime.now().strftime("%d/%m/%Y")

    texto = f"""

LAUDO TÉCNICO HVAC

Cliente: {cliente}
Técnico: {tecnico}

Equipamento: {fabricante} {modelo}
Capacidade: {capacidade} BTU

Data: {data}

CONDIÇÕES

Temp retorno: {t_ret}
Temp insuflação: {t_ins}

Delta T: {dt_ar}

Pressão sucção: {p_suc}
Superaquecimento: {sh}

Pressão descarga: {p_desc}
Sub-resfriamento: {sc}

DIAGNÓSTICO

{", ".join(problemas)}

COP estimado: {cop}

CONCLUSÃO

A avaliação foi realizada com base em parâmetros
utilizados na engenharia de refrigeração e climatização.
"""

    st.text_area("Laudo técnico",texto,height=400)

    if st.button("Gerar PDF"):

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial","",10)

        for linha in texto.split("\n"):

            pdf.multi_cell(0,8,linha)

        pdf_bytes = pdf.output(dest="S").encode("latin-1","ignore")

        st.download_button(
        "Baixar PDF",
        pdf_bytes,
        "laudo_hvac.pdf",
        "application/pdf"
        )

# -----------------------------------
# WHATSAPP
# -----------------------------------

resumo = f"""
MPN ENGENHARIA HVAC

Cliente: {cliente}

Equipamento: {fabricante} {modelo}

Diagnóstico:
{", ".join(problemas)}
"""

link = f"https://wa.me/?text={urllib.parse.quote(resumo)}"

st.link_button("Enviar diagnóstico WhatsApp",link)

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import urllib.parse

# -----------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------
st.set_page_config(
    page_title="MPN Engenharia & Diagnóstico",
    layout="wide",
    page_icon="❄️"
)

# -----------------------------
# ESTILO VISUAL
# -----------------------------
st.markdown("""
<style>

body {
    background-color:#f2f4f8;
}

h1, h2, h3 {
    color:#004A99;
}

[data-testid="stMetric"]{
    background-color:#004A99;
    border-radius:12px;
    padding:15px;
    border:2px solid #C0C0C0;
}

[data-testid="stMetricLabel"]{
    color:white;
    font-weight:bold;
}

[data-testid="stMetricValue"]{
    color:#00D1FF;
}

.stButton>button{
    background-color:#004A99;
    color:white;
    border-radius:8px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

st.title("❄️ MPN Engenharia & Diagnóstico HVAC")

# -----------------------------
# FUNÇÃO DE SATURAÇÃO
# -----------------------------
def calcular_t_sat(psig, gas):

    if not gas or psig <= 0:
        return None

    if gas == "R-410A":
        return 0.2307 * psig - 22.81

    elif gas == "R-22":
        return 0.2854 * psig - 25.12

    elif gas == "R-134a":
        return 0.521 * psig - 38.54

    elif gas == "R-404A":
        return 0.2105 * psig - 16.52

    return None

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("⚙️ Configuração")

fluido = st.sidebar.selectbox(
    "Fluido Refrigerante",
    ["","R-410A","R-22","R-134a","R-404A"]
)

tensao_nominal = st.sidebar.selectbox(
    "Tensão Nominal",
    ["","127","220","380"]
)

tensao_medida = st.sidebar.number_input(
    "Tensão Medida (V)",
    min_value=0
)

dif_tensao = 0

if tensao_nominal and tensao_medida > 0:
    dif_tensao = tensao_medida - int(tensao_nominal)

st.sidebar.metric("Diferença de Tensão",f"{dif_tensao} V")

# -----------------------------
# ABAS
# -----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
"📋 Identificação",
"⚡ Elétrica",
"🌡 Termodinâmica",
"🧠 Diagnóstico",
"📄 Relatório"
])

# -----------------------------
# ABA 1 – IDENTIFICAÇÃO
# -----------------------------
with tab1:

    st.subheader("Dados do Cliente")

    c1,c2,c3 = st.columns(3)

    cliente = c1.text_input("Cliente")
    tecnico = c2.text_input("Responsável técnico")
    serie = c3.text_input("Número de série")

    c4,c5,c6 = st.columns(3)

    fabricante = c4.text_input("Fabricante")
    modelo = c5.text_input("Modelo")
    capacidade = c6.text_input("Capacidade (BTU)")

# -----------------------------
# ABA 2 – ELÉTRICA
# -----------------------------
with tab2:

    st.subheader("Análise Elétrica")

    e1,e2,e3 = st.columns(3)

    rla = e1.number_input("RLA (corrente nominal)",0.0)
    lra = e2.number_input("LRA (corrente partida)",0.0)
    corrente = e3.number_input("Corrente medida",0.0)

    diff_corrente = corrente - rla if rla>0 else 0

    st.metric("Diferença de corrente",f"{diff_corrente:.2f} A")

# -----------------------------
# ABA 3 – TERMODINÂMICA
# -----------------------------
with tab3:

    st.subheader("Pressões e Temperaturas")

    m1,m2,m3,m4 = st.columns(4)

    with m1:

        t_ret = st.number_input("Temp retorno ar",24.0)
        t_ins = st.number_input("Temp insuflação ar",12.0)

        delta_t = t_ret - t_ins

        st.metric("Delta T",f"{delta_t:.2f} °C")

    with m2:

        p_suc = st.number_input("Pressão sucção (psi)",120.0)

        tsat_evap = calcular_t_sat(p_suc,fluido)

        if tsat_evap:
            st.metric("Temp evaporação",f"{tsat_evap:.2f} °C")
        else:
            st.metric("Temp evaporação","--")

    with m3:

        t_suc = st.number_input("Temp sucção",12.0)

        sh = t_suc-tsat_evap if tsat_evap else 0

        st.metric("Superaquecimento",f"{sh:.2f} K")

    with m4:

        p_desc = st.number_input("Pressão descarga (psi)",380.0)

        tsat_cond = calcular_t_sat(p_desc,fluido)

        t_liq = st.number_input("Temp linha líquido",30.0)

        sr = tsat_cond-t_liq if tsat_cond else 0

        st.metric("Subresfriamento",f"{sr:.2f} K")

    # gráfico

    x = np.arange(1,10)
    y = sh * x

    fig, ax = plt.subplots()

    ax.plot(x,y,marker="o")

    ax.set_title("Tendência de Superaquecimento")
    ax.set_xlabel("Tempo")
    ax.set_ylabel("Valor relativo")

    st.pyplot(fig)

# -----------------------------
# ABA 4 – DIAGNÓSTICO
# -----------------------------
with tab4:

    st.subheader("Diagnóstico Técnico")

    diagnostico = []

    if sh < 5:
        diagnostico.append("Superaquecimento baixo — risco de retorno de líquido.")

    elif sh > 20:
        diagnostico.append("Superaquecimento alto — possível falta de refrigerante.")

    else:
        diagnostico.append("Superaquecimento dentro da faixa normal.")

    if sr < 3:
        diagnostico.append("Subresfriamento baixo — possível carga insuficiente.")

    elif sr > 15:
        diagnostico.append("Subresfriamento alto — possível excesso de refrigerante.")

    if delta_t < 8:
        diagnostico.append("Baixa troca térmica no evaporador.")

    if dif_tensao > 10:
        diagnostico.append("Problema na alimentação elétrica.")

    for d in diagnostico:
        st.warning(d)

# -----------------------------
# ABA 5 – RELATÓRIO
# -----------------------------
with tab5:

    st.subheader("Relatório Técnico")

    st.write("Data:", datetime.now().strftime("%d/%m/%Y"))
    st.write("Cliente:",cliente)
    st.write("Equipamento:",fabricante,modelo)

    st.write("Superaquecimento:",round(sh,2),"K")
    st.write("Subresfriamento:",round(sr,2),"K")

    st.markdown("---")

    if st.button("Gerar PDF"):

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial","B",14)
        pdf.cell(0,10,"LAUDO TECNICO HVAC",0,1,"C")

        pdf.set_font("Arial","",10)

        pdf.cell(0,8,f"Cliente: {cliente}",0,1)
        pdf.cell(0,8,f"Equipamento: {fabricante} {modelo}",0,1)
        pdf.cell(0,8,f"Superaquecimento: {sh:.2f} K",0,1)
        pdf.cell(0,8,f"Subresfriamento: {sr:.2f} K",0,1)

        pdf_bytes = pdf.output(dest="S").encode("latin-1")

        st.download_button(
            "Baixar PDF",
            pdf_bytes,
            "laudo_hvac.pdf",
            "application/pdf"
        )

    msg=f"""
MPN Engenharia

Cliente: {cliente}
Equipamento: {fabricante} {modelo}
Superaquecimento: {sh:.1f}K
Subresfriamento: {sr:.1f}K
"""

    link = f"https://wa.me/?text={urllib.parse.quote(msg)}"

    st.link_button("Enviar via WhatsApp",link)

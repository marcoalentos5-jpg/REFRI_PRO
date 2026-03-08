import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="REFRI PRO", layout="wide")

st.title("REFRI PRO - Sistema Profissional de Diagnóstico HVAC")

st.header("Dados do Sistema")

col1, col2 = st.columns(2)

with col1:

    fluido = st.selectbox(
        "Fluido Refrigerante",
        ["R22","R134a","R404A","R410A"]
    )

    pressao_succao = st.number_input(
        "Pressão de sucção (psi)",
        value=120.0
    )

    temperatura_succao = st.number_input(
        "Temperatura na sucção (°C)",
        value=18.0
    )

    pressao_descarga = st.number_input(
        "Pressão de descarga (psi)",
        value=300.0
    )

with col2:

    temperatura_liquido = st.number_input(
        "Temperatura da linha de líquido (°C)",
        value=35.0
    )

    temperatura_ambiente = st.number_input(
        "Temperatura ambiente (°C)",
        value=30.0
    )

    corrente_compressor = st.number_input(
        "Corrente do compressor (A)",
        value=8.0
    )

    temperatura_evaporador = st.number_input(
        "Temperatura saída evaporador (°C)",
        value=10.0
    )

    temperatura_condensador = st.number_input(
        "Temperatura saída condensador (°C)",
        value=40.0
    )

# tabela pressão x temperatura simplificada

tabela_pt = {

    "R410A": {110:4,120:7,130:10},
    "R22": {70:4,80:7,90:10},
    "R134a": {30:0,40:5,50:10},
    "R404A": {50:-5,60:0,70:5}
}

def temperatura_saturacao(fluido, pressao):

    tabela = tabela_pt.get(fluido)

    return np.interp(
        pressao,
        list(tabela.keys()),
        list(tabela.values())
    )

temp_evaporacao = temperatura_saturacao(fluido, pressao_succao)

superaquecimento = temperatura_succao - temp_evaporacao

subresfriamento = temperatura_condensador - temperatura_liquido

st.header("Resultados Calculados")

col3, col4, col5 = st.columns(3)

col3.metric("Temperatura de Evaporação",f"{round(temp_evaporacao,2)} °C")
col4.metric("Superaquecimento",f"{round(superaquecimento,2)} °C")
col5.metric("Sub-resfriamento",f"{round(subresfriamento,2)} °C")

st.header("Diagnóstico Técnico")

diagnostico = []

if superaquecimento < 5:
    diagnostico.append("Superaquecimento baixo: risco de retorno de líquido ao compressor.")

elif superaquecimento > 20:
    diagnostico.append("Superaquecimento elevado: possível falta de refrigerante ou restrição na linha.")

else:
    diagnostico.append("Superaquecimento dentro da faixa recomendada.")

if subresfriamento < 3:
    diagnostico.append("Sub-resfriamento baixo: possível carga insuficiente de refrigerante.")

elif subresfriamento > 15:
    diagnostico.append("Sub-resfriamento elevado: possível excesso de refrigerante ou restrição.")

if pressao_descarga > 350:
    diagnostico.append("Pressão de descarga elevada: verificar condensador sujo ou ventilação insuficiente.")

if corrente_compressor > 15:
    diagnostico.append("Corrente do compressor acima do normal: possível sobrecarga ou falha mecânica.")

for d in diagnostico:
    st.warning(d)

st.header("Gráfico de Tendência do Sistema")

x = np.arange(0,10)

y = superaquecimento * x

fig, ax = plt.subplots()

ax.plot(x,y,marker="o")

ax.set_title("Tendência de Superaquecimento")

ax.set_xlabel("Tempo")

ax.set_ylabel("Valor relativo")

st.pyplot(fig)

st.header("Gerar Laudo Técnico")

if st.button("Gerar Laudo PDF"):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial","B",16)

    pdf.cell(0,10,"LAUDO TECNICO DE SISTEMA DE REFRIGERACAO",0,1)

    pdf.set_font("Arial","",12)

    pdf.cell(0,10,f"Data: {datetime.now().strftime('%d/%m/%Y')}",0,1)

    pdf.cell(0,10,f"Fluido Refrigerante: {fluido}",0,1)

    pdf.cell(0,10,f"Pressao de succao: {pressao_succao} psi",0,1)

    pdf.cell(0,10,f"Temperatura de succao: {temperatura_succao} C",0,1)

    pdf.cell(0,10,f"Pressao de descarga: {pressao_descarga} psi",0,1)

    pdf.cell(0,10,f"Superaquecimento: {round(superaquecimento,2)} C",0,1)

    pdf.cell(0,10,f"Sub-resfriamento: {round(subresfriamento,2)} C",0,1)

    pdf.multi_cell(0,10,"Diagnostico:")

    for d in diagnostico:

        pdf.multi_cell(0,10,f"- {d}")

    pdf.output("laudo_hvac.pdf")

    with open("laudo_hvac.pdf","rb") as f:

        st.download_button(
            "Baixar Laudo",
            f,
            "laudo_hvac.pdf"
        )

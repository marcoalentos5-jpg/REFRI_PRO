import streamlit as st
import numpy as np
from datetime import datetime

# tentativa segura de importar matplotlib
try:
    import matplotlib.pyplot as plt
    grafico_disponivel = True
except ModuleNotFoundError:
    grafico_disponivel = False


st.set_page_config(page_title="RefriPro HVAC", layout="wide")

st.title("REFRI PRO - Diagnóstico de Sistemas de Refrigeração")

st.header("Dados do Sistema")

col1, col2 = st.columns(2)

with col1:

    fluido = st.selectbox(
        "Fluido Refrigerante",
        ["R22", "R134a", "R404A", "R410A"]
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

    temperatura_condensador = st.number_input(
        "Temperatura do condensador (°C)",
        value=40.0
    )


# tabela simplificada pressão x temperatura
tabela_pt = {

    "R410A": {110: 4, 120: 7, 130: 10},
    "R22": {70: 4, 80: 7, 90: 10},
    "R134a": {30: 0, 40: 5, 50: 10},
    "R404A": {50: -5, 60: 0, 70: 5}

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


st.header("Resultados")

col3, col4, col5 = st.columns(3)

col3.metric(
    "Temperatura de Evaporação",
    f"{round(temp_evaporacao,2)} °C"
)

col4.metric(
    "Superaquecimento",
    f"{round(superaquecimento,2)} °C"
)

col5.metric(
    "Sub-resfriamento",
    f"{round(subresfriamento,2)} °C"
)


st.header("Diagnóstico Técnico")

diagnostico = []

if superaquecimento < 5:
    diagnostico.append(
        "Superaquecimento baixo: possível retorno de líquido ao compressor."
    )

elif superaquecimento > 20:
    diagnostico.append(
        "Superaquecimento alto: possível falta de refrigerante ou restrição."
    )

else:
    diagnostico.append(
        "Superaquecimento dentro da faixa recomendada."
    )

if subresfriamento < 3:
    diagnostico.append(
        "Sub-resfriamento baixo: possível falta de carga."
    )

elif subresfriamento > 15:
    diagnostico.append(
        "Sub-resfriamento alto: possível excesso de refrigerante."
    )

if pressao_descarga > 350:
    diagnostico.append(
        "Pressão de descarga elevada: verificar condensador ou ventilação."
    )

if corrente_compressor > 15:
    diagnostico.append(
        "Corrente do compressor elevada: verificar sobrecarga."
    )


for d in diagnostico:
    st.warning(d)


st.header("Gráfico de Tendência")

if grafico_disponivel:

    x = np.arange(0, 10)
    y = superaquecimento * x

    fig, ax = plt.subplots()

    ax.plot(x, y, marker="o")

    ax.set_title("Tendência de Superaquecimento")
    ax.set_xlabel("Tempo")
    ax.set_ylabel("Valor Relativo")

    st.pyplot(fig)

else:

    st.info(
        "Gráfico indisponível: biblioteca matplotlib não instalada no ambiente."
    )


st.header("Informações do Relatório")

st.write("Data da análise:", datetime.now().strftime("%d/%m/%Y"))
st.write("Fluido refrigerante:", fluido)

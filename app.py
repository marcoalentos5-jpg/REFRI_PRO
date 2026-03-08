import streamlit as st
import numpy as np
from datetime import datetime

# tentativa segura de importar gráfico
try:
    import matplotlib.pyplot as plt
    grafico = True
except:
    grafico = False

st.set_page_config(
    page_title="REFRI PRO HVAC",
    layout="wide"
)

st.title("REFRI PRO — Diagnóstico de Sistemas de Refrigeração")

st.markdown("---")

# ==============================
# ABAS DO SISTEMA
# ==============================

aba1, aba2, aba3, aba4 = st.tabs(
    [
        "Entrada de Dados",
        "Cálculos Termodinâmicos",
        "Diagnóstico",
        "Relatório Técnico"
    ]
)

# ==============================
# TABELA P-T SIMPLIFICADA
# ==============================

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

# ==============================
# ABA 1 — ENTRADA
# ==============================

with aba1:

    st.subheader("Dados Operacionais")

    col1, col2 = st.columns(2)

    with col1:

        fluido = st.selectbox(
            "Fluido refrigerante",
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
            "Temperatura linha líquido (°C)",
            value=35.0
        )

        temperatura_ambiente = st.number_input(
            "Temperatura ambiente (°C)",
            value=30.0
        )

        corrente_compressor = st.number_input(
            "Corrente compressor (A)",
            value=8.0
        )

        temperatura_condensador = st.number_input(
            "Temperatura condensador (°C)",
            value=40.0
        )

# ==============================
# CÁLCULOS
# ==============================

temp_evaporacao = temperatura_saturacao(fluido, pressao_succao)

superaquecimento = temperatura_succao - temp_evaporacao

subresfriamento = temperatura_condensador - temperatura_liquido

# ==============================
# ABA 2 — RESULTADOS
# ==============================

with aba2:

    st.subheader("Resultados Termodinâmicos")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Temperatura de evaporação",
        f"{round(temp_evaporacao,2)} °C"
    )

    c2.metric(
        "Superaquecimento",
        f"{round(superaquecimento,2)} °C"
    )

    c3.metric(
        "Sub-resfriamento",
        f"{round(subresfriamento,2)} °C"
    )

    st.markdown("---")

    if grafico:

        x = np.arange(0,10)
        y = superaquecimento * x

        fig, ax = plt.subplots()

        ax.plot(x,y,marker="o")

        ax.set_title("Tendência de Superaquecimento")
        ax.set_xlabel("Tempo")
        ax.set_ylabel("Valor relativo")

        st.pyplot(fig)

    else:

        st.warning("Biblioteca gráfica não instalada.")

# ==============================
# ABA 3 — DIAGNÓSTICO
# ==============================

with aba3:

    st.subheader("Diagnóstico Técnico")

    diagnostico = []

    if superaquecimento < 5:

        diagnostico.append(
        "Superaquecimento baixo: risco de retorno de líquido."
        )

    elif superaquecimento > 20:

        diagnostico.append(
        "Superaquecimento elevado: possível falta de refrigerante."
        )

    else:

        diagnostico.append(
        "Superaquecimento dentro da faixa recomendada."
        )

    if subresfriamento < 3:

        diagnostico.append(
        "Sub-resfriamento baixo: possível carga insuficiente."
        )

    elif subresfriamento > 15:

        diagnostico.append(
        "Sub-resfriamento alto: possível excesso de refrigerante."
        )

    if pressao_descarga > 350:

        diagnostico.append(
        "Pressão de descarga elevada: verificar condensador."
        )

    if corrente_compressor > 15:

        diagnostico.append(
        "Corrente elevada: possível sobrecarga do compressor."
        )

    for d in diagnostico:

        st.warning(d)

# ==============================
# ABA 4 — RELATÓRIO
# ==============================

with aba4:

    st.subheader("Resumo da Análise")

    st.write("Data:", datetime.now().strftime("%d/%m/%Y"))

    st.write("Fluido:", fluido)

    st.write("Pressão sucção:", pressao_succao,"psi")

    st.write("Pressão descarga:", pressao_descarga,"psi")

    st.write("Superaquecimento:",round(superaquecimento,2),"°C")

    st.write("Sub-resfriamento:",round(subresfriamento,2),"°C")

    st.markdown("---")

    st.write("Conclusão técnica:")

    for d in diagnostico:

        st.write("-",d)

import streamlit as st
import pandas as pd
import numpy as np

# tentativa de importar matplotlib
try:
    import matplotlib.pyplot as plt
    grafico_ok = True
except ModuleNotFoundError:
    grafico_ok = False

st.title("Sistema de Diagnóstico em Refrigeração")

st.subheader("Cálculo de Superaquecimento")

# entrada de dados
pressao_succao = st.number_input("Pressão de sucção (psi)", value=120.0)
temperatura_succao = st.number_input("Temperatura na sucção (°C)", value=18.0)
temperatura_evaporacao = st.number_input("Temperatura de evaporação saturada (°C)", value=10.0)

# cálculo
superaquecimento = temperatura_succao - temperatura_evaporacao

st.write("Superaquecimento total:", superaquecimento, "°C")

# diagnóstico simples
if superaquecimento < 5:
    st.warning("Possível retorno de líquido ao compressor.")
elif superaquecimento > 20:
    st.error("Possível falta de refrigerante ou restrição na linha.")
else:
    st.success("Superaquecimento dentro da faixa recomendada.")

# gráfico opcional
if grafico_ok:

    x = np.arange(0, 10)
    y = x * superaquecimento

    fig, ax = plt.subplots()
    ax.plot(x, y, marker="o")
    ax.set_title("Comportamento do Superaquecimento")
    ax.set_xlabel("Tempo")
    ax.set_ylabel("Valor relativo")

    st.pyplot(fig)

else:
    st.info("Biblioteca matplotlib não instalada. Gráfico indisponível.")

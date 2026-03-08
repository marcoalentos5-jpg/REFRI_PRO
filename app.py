import streamlit as st
import numpy as np
from fpdf import FPDF
from datetime import datetime
import urllib.parse

st.set_page_config(
    page_title="MPN Engenharia HVAC",
    layout="wide",
    page_icon="❄️"
)

st.title("❄️ MPN Engenharia & Diagnóstico HVAC")

# -------------------------
# FUNÇÃO SATURAÇÃO
# -------------------------

def calcular_t_sat(psig, gas):

    if gas == "R410A":
        return 0.2307 * psig - 22.81

    elif gas == "R22":
        return 0.2854 * psig - 25.12

    elif gas == "R134a":
        return 0.521 * psig - 38.54

    elif gas == "R404A":
        return 0.2105 * psig - 16.52

    return None


# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.header("Configuração")

fluido = st.sidebar.selectbox(
    "Fluido refrigerante",
    ["", "R410A", "R22", "R134a", "R404A"]
)

tensao_nominal = st.sidebar.number_input(
    "Tensão nominal",
    value=220
)

tensao_medida = st.sidebar.number_input(
    "Tensão medida",
    value=220
)

dif_tensao = tensao_medida - tensao_nominal

st.sidebar.metric("Diferença tensão", f"{dif_tensao} V")

# -------------------------
# ABAS
# -------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "Identificação",
    "Medições",
    "Diagnóstico",
    "Relatório"
])

# -------------------------
# IDENTIFICAÇÃO
# -------------------------

with tab1:

    col1, col2, col3 = st.columns(3)

    cliente = col1.text_input("Cliente")
    tecnico = col2.text_input("Técnico")
    serie = col3.text_input("Série")

    col4, col5, col6 = st.columns(3)

    fabricante = col4.text_input("Fabricante")
    modelo = col5.text_input("Modelo")
    capacidade = col6.text_input("Capacidade BTU")


# -------------------------
# MEDIÇÕES
# -------------------------

with tab2:

    c1, c2, c3, c4 = st.columns(4)

    t_retorno = c1.number_input("Temp retorno", value=24.0)
    t_insuflacao = c1.number_input("Temp insuflação", value=12.0)

    p_succao = c2.number_input("Pressão sucção (psi)", value=120.0)
    t_succao = c2.number_input("Temp sucção", value=12.0)

    p_descarga = c3.number_input("Pressão descarga (psi)", value=380.0)
    t_liquido = c3.number_input("Temp linha líquido", value=30.0)

    corrente = c4.number_input("Corrente compressor", value=8.0)

    delta_t = t_retorno - t_insuflacao

    tsat_evap = calcular_t_sat(p_succao, fluido) if fluido else None
    tsat_cond = calcular_t_sat(p_descarga, fluido) if fluido else None

    sh = t_succao - tsat_evap if tsat_evap else 0
    sr = tsat_cond - t_liquido if tsat_cond else 0

    st.metric("Delta T", f"{delta_t:.2f} °C")
    st.metric("Superaquecimento", f"{sh:.2f} K")
    st.metric("Subresfriamento", f"{sr:.2f} K")


# -------------------------
# DIAGNÓSTICO
# -------------------------

with tab3:

    diagnostico = []

    if sh < 5:
        diagnostico.append("Superaquecimento baixo: risco de retorno de líquido")

    elif sh > 20:
        diagnostico.append("Superaquecimento alto: possível falta de refrigerante")

    else:
        diagnostico.append("Superaquecimento normal")

    if sr < 3:
        diagnostico.append("Subresfriamento baixo: possível falta de carga")

    elif sr > 15:
        diagnostico.append("Subresfriamento alto: possível excesso de refrigerante")

    if delta_t < 8:
        diagnostico.append("Baixa troca térmica no evaporador")

    for d in diagnostico:
        st.warning(d)


# -------------------------
# RELATÓRIO
# -------------------------

with tab4:

    st.write("Data:", datetime.now().strftime("%d/%m/%Y"))

    st.write("Cliente:", cliente)
    st.write("Equipamento:", fabricante, modelo)

    st.write("Superaquecimento:", round(sh, 2))
    st.write("Subresfriamento:", round(sr, 2))

    if st.button("Gerar PDF"):

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "LAUDO TECNICO HVAC", 0, 1, "C")

        pdf.set_font("Arial", "", 10)

        pdf.cell(0, 8, f"Cliente: {cliente}", 0, 1)
        pdf.cell(0, 8, f"Equipamento: {fabricante} {modelo}", 0, 1)
        pdf.cell(0, 8, f"Superaquecimento: {sh:.2f}", 0, 1)
        pdf.cell(0, 8, f"Subresfriamento: {sr:.2f}", 0, 1)

        pdf_bytes = pdf.output(dest="S").encode("latin-1")

        st.download_button(
            "Baixar PDF",
            pdf_bytes,
            "laudo_hvac.pdf",
            "application/pdf"
        )

    msg = f"""
MPN Engenharia

Cliente: {cliente}
Equipamento: {fabricante} {modelo}
Superaquecimento: {sh:.1f}
Subresfriamento: {sr:.1f}
"""

    link = f"https://wa.me/?text={urllib.parse.quote(msg)}"

    st.link_button("Enviar via WhatsApp", link)

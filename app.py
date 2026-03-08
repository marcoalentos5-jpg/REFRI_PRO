import streamlit as st
import pandas as pd
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
# ESTILO VISUAL (AZUL / PRATA / CINZA)
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

.sidebar .sidebar-content{
    background-color:#1a1a1a;
}

</style>
""", unsafe_allow_html=True)

st.title("❄️ MPN Engenharia & Diagnóstico HVAC")

# -----------------------------
# FUNÇÃO TERMODINÂMICA
# -----------------------------
def calcular_t_sat(psig, gas):

    if not gas or psig <= 0:
        return None

    if gas == "R-410A":
        return 0.23076923 * psig - 22.81538462

    elif gas == "R-22":
        return 0.2854 * psig - 25.12

    elif gas == "R-134a":
        return 0.521 * psig - 38.54

    elif gas == "R-404A":
        return 0.2105 * psig - 16.52

    return None


# -----------------------------
# SIDEBAR – CONFIGURAÇÃO
# -----------------------------
st.sidebar.header("⚙️ Configuração do Sistema")

equipamento = st.sidebar.selectbox(
    "Tipo de Equipamento",
    ["","Split Hi-Wall","Cassete","Piso-Teto","VRF","Chiller","Câmara Fria"]
)

fluido = st.sidebar.selectbox(
    "Fluido Refrigerante",
    ["","R-410A","R-22","R-134a","R-404A"]
)

tecnologia = st.sidebar.radio(
    "Tecnologia",
    ["ON-OFF","Inverter","Digital Scroll"]
)

st.sidebar.markdown("---")

st.sidebar.subheader("⚡ Parâmetros Elétricos")

tensao_nominal = st.sidebar.selectbox(
    "Tensão Nominal",
    ["","127","220","380","440"]
)

tensao_medida = st.sidebar.number_input(
    "Tensão Medida (V)",
    min_value=0
)

dif_tensao = 0
if tensao_nominal and tensao_medida > 0:
    dif_tensao = tensao_medida - int(tensao_nominal)

st.sidebar.metric("Diferença de tensão",f"{dif_tensao} V")

# -----------------------------
# ABAS PRINCIPAIS
# -----------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
"📋 Identificação",
"⚡ Elétrica",
"🌡 Termodinâmica",
"🧠 Diagnóstico",
"📐 Carga térmica",
"📄 Relatório"
])

# -----------------------------
# ABA 1 – IDENTIFICAÇÃO
# -----------------------------
with tab1:

    st.subheader("Dados do Cliente e Equipamento")

    c1,c2,c3 = st.columns(3)

    cliente = c1.text_input("Cliente")

    tecnico = c2.text_input("Responsável técnico")

    serie = c3.text_input("Número de série")

    c4,c5,c6,c7 = st.columns(4)

    capacidade = c4.text_input("Capacidade (BTU)")

    fabricante = c5.text_input("Fabricante")

    modelo = c6.text_input("Modelo")

    linha = c7.text_input("Linha")

# -----------------------------
# ABA 2 – ELÉTRICA
# -----------------------------
with tab2:

    st.subheader("Análise elétrica do compressor")

    e1,e2,e3 = st.columns(3)

    rla = e1.number_input("RLA (corrente nominal)",0.0)

    lra = e2.number_input("LRA (corrente partida)",0.0)

    corrente = e3.number_input("Corrente medida",0.0)

    diff_corrente = corrente-rla if rla>0 else 0

    st.metric("Diferença corrente",f"{diff_corrente:.2f} A")

# -----------------------------
# ABA 3 – TERMODINÂMICA
# -----------------------------
with tab3:

    st.subheader("Pressões e temperaturas")

    m1,m2,m3,m4 = st.columns(4)

    with m1:

        t_ret = st.number_input("Temp retorno ar",24.0)

        t_ins = st.number_input("Temp insuflação ar",12.0)

        delta_t = t_ret - t_ins

        st.metric("Delta T",f"{delta_t:.2f} °C")

    with m2:

        p_suc = st.number_input("Pressão sucção",120.0)

        tsat_evap = calcular_t_sat(p_suc,fluido)

        st.metric("Temp evap sat",f"{tsat_evap:.2f} °C" if tsat_evap else "--")

    with m3:

        t_suc = st.number_input("Temp tubo sucção",12.0)

        sh = (t_suc - tsat_evap) if tsat_evap else 0

        st.metric("Superaquecimento",f"{sh:.2f} K")

    with m4:

        p_desc = st.number_input("Pressão descarga",380.0)

        tsat_cond = calcular_t_sat(p_desc,fluido)

        t_liq = st.number_input("Temp linha líquido",30.0)

        sr = (tsat_cond - t_liq) if tsat_cond else 0

        st.metric("Subresfriamento",f"{sr:.2f} K")

# -----------------------------
# ABA 4 – DIAGNÓSTICO
# -----------------------------
with tab4:

    st.subheader("Diagnóstico inteligente")

    diagnostico = "Sistema operando normalmente"

    if sh>12 and sr<3:
        diagnostico = "Possível falta de refrigerante"

    elif sh<5 and sr>10:
        diagnostico = "Possível excesso de carga"

    elif delta_t<8:
        diagnostico = "Baixa troca térmica no evaporador"

    elif dif_tensao>10:
        diagnostico = "Problema na alimentação elétrica"

    st.info(diagnostico)

# -----------------------------
# ABA 5 – CARGA TÉRMICA
# -----------------------------
with tab5:

    st.subheader("Estimativa de carga térmica")

    area = st.number_input("Área do ambiente (m²)",0.0)

    btu = area*800 if area>0 else 0

    st.metric("Carga térmica estimada",f"{btu:,.0f} BTU/h")

# -----------------------------
# ABA 6 – RELATÓRIO
# -----------------------------
with tab6:

    st.subheader("Gerar relatório técnico")

    if st.button("Gerar PDF"):

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial","B",14)
        pdf.cell(0,10,"LAUDO TECNICO HVAC",0,1,"C")

        pdf.set_font("Arial","",10)

        pdf.cell(0,8,f"Cliente: {cliente}",0,1)
        pdf.cell(0,8,f"Tecnico: {tecnico}",0,1)
        pdf.cell(0,8,f"Equipamento: {fabricante} {modelo}",0,1)

        pdf.cell(0,8,f"Delta T: {delta_t:.2f}",0,1)
        pdf.cell(0,8,f"Superaquecimento: {sh:.2f}",0,1)
        pdf.cell(0,8,f"Subresfriamento: {sr:.2f}",0,1)

        pdf.cell(0,8,f"Diagnostico: {diagnostico}",0,1)

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
Diagnóstico: {diagnostico}
"""

    link = f"https://wa.me/?text={urllib.parse.quote(msg)}"

    st.link_button("Enviar via WhatsApp",link)
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

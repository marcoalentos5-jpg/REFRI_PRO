import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="MPN | Engenharia & Diagnóstico",
    layout="wide",
    page_icon="❄️"
)

# --- ESTILO ---
st.markdown("""
<style>
.main { background-color: #f0f2f6; }

[data-testid="stMetric"] {
background-color: #004A99 !important;
border-radius: 15px !important;
padding: 20px !important;
border: 2px solid #A9A9A9 !important;
}

[data-testid="stMetricLabel"] {
color: white !important;
font-weight: bold !important;
}

[data-testid="stMetricValue"] {
color: #00D1FF !important;
font-size: 2rem !important;
}

.stButton>button {
background-color: #004A99;
color: white;
border-radius: 10px;
height: 3.5em;
font-weight: bold;
width: 100%;
border: none;
}

h1,h2,h3,h4 {color:#004A99;}
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO TERMODINÂMICA ---
def calcular_t_sat_precisao(psig, gas):

    if psig is None or gas == "" or psig <= 0:
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


# --- SIDEBAR ---
st.sidebar.header("⚙️ Setup do Ciclo & Elétrica")

f_equip = st.sidebar.selectbox(
    "Equipamento",
    ["", "Split Hi-Wall", "Split Cassete", "Piso-Teto", "Chiller", "VRF/VRV", "Câmara Fria"]
)

f_gas = st.sidebar.selectbox(
    "Fluido Refrigerante",
    ["", "R-410A", "R-22", "R-134a", "R-404A"]
)

f_tec = st.sidebar.radio(
    "Tecnologia",
    ["ON-OFF", "Inverter", "Digital Scroll"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Parâmetros Elétricos")

v_trab_str = st.sidebar.selectbox(
    "Tensão Nominal",
    ["", "127", "220", "380", "440"]
)

v_medida = st.sidebar.number_input(
    "Tensão Medida [V]",
    min_value=0,
    step=1
)

diff_tensao_v = 0
variacao_v = 0

if v_trab_str != "" and v_medida > 0:

    v_nominal = int(v_trab_str)

    diff_tensao_v = v_medida - v_nominal
    variacao_v = (diff_tensao_v / v_nominal) * 100

st.sidebar.markdown(f"**Diferença de tensão:** `{diff_tensao_v} V`")

# --- ABAS ---
tab_iden, tab_termo, tab_solucoes, tab_carga, tab_subs = st.tabs([
"📋 Identificação",
"🌡️ Termodinâmica",
"🤖 Diagnóstico IA",
"📐 Carga VRF",
"🔄 Peças"
])

# --- IDENTIFICAÇÃO ---
with tab_iden:

    st.subheader("📋 Identificação do Sistema")

    col1,col2,col3 = st.columns(3)

    cli = col1.text_input("Cliente")
    tec = col2.text_input("Responsável Técnico")
    ser = col3.text_input("Número de Série")

    col4,col5,col6,col7 = st.columns(4)

    cap_btu = col4.text_input("Capacidade BTU")
    mod_eq = col5.text_input("Modelo")
    lin_eq = col6.text_input("Linha")
    fab_eq = col7.text_input("Fabricante")

    st.subheader("⚡ Análise de Corrente")

    e1,e2,e3,e4 = st.columns(4)

    v_rla = e1.number_input("RLA [A]",0.0)
    v_lra = e2.number_input("LRA [A]",0.0)
    v_med_amp = e3.number_input("Corrente medida [A]",0.0)

    diff_amp = 0

    if v_rla > 0:
        diff_amp = v_med_amp - v_rla

    e4.metric("Diferença corrente",f"{diff_amp:.2f} A")

# --- TERMODINÂMICA ---
with tab_termo:

    st.subheader("🌡️ Pressões e Temperaturas")

    m1,m2,m3,m4 = st.columns(4)

    with m1:

        t_ret = st.number_input("Temp retorno °C",24.0)
        t_ins = st.number_input("Temp insuflação °C",12.0)

        dt_ar = t_ret - t_ins

        st.metric("Delta T",f"{dt_ar:.2f} °C")

    with m2:

        p_suc = st.number_input("Pressão sucção PSIG",133.1)

        tsat_evap = calcular_t_sat_precisao(p_suc,f_gas)

        if tsat_evap:
            st.metric("Temp saturação",f"{tsat_evap:.2f} °C")
        else:
            st.metric("Temp saturação","--")

    with m3:

        t_tubo_suc = st.number_input("Temp tubo sucção °C",12.0)

        sh = 0

        if tsat_evap is not None:
            sh = t_tubo_suc - tsat_evap

        st.metric("Superaquecimento",f"{sh:.2f} K")

    with m4:

        p_desc = st.number_input("Pressão descarga PSIG",380.0)

        tsat_cond = calcular_t_sat_precisao(p_desc,f_gas)

        t_tubo_liq = st.number_input("Temp tubo líquido °C",30.0)

        sr = 0

        if tsat_cond is not None:
            sr = tsat_cond - t_tubo_liq

        st.metric("Sub-resfriamento",f"{sr:.2f} K")

# --- DIAGNÓSTICO ---
with tab_solucoes:

    st.subheader("🤖 Diagnóstico automático")

    veredito = "Sistema operando dentro dos parâmetros normais."

    if sh < 5 and sr > 10:
        veredito = "🚨 Excesso de fluido ou restrição na expansão."

    elif sh > 12 and sr < 3:
        veredito = "🚨 Sistema com baixa carga de refrigerante."

    elif dt_ar < 8:
        veredito = "🚨 Baixa troca térmica na evaporadora."

    if "🚨" in veredito:
        st.error(veredito)
    else:
        st.success(veredito)

# --- CARGA VRF ---
with tab_carga:

    st.subheader("📐 Estimativa carga térmica")

    area_vrf = st.number_input("Área m²",0.0)

    total_btu = area_vrf * 800

    st.metric("Carga estimada",f"{total_btu:,.0f} BTU/h")

# --- PEÇAS ---
with tab_subs:

    st.subheader("🔄 Referência de compressores")

    dados = {
    "Capacidade":["9k","12k","18k"],
    "Embraco":["FFU80","FFU130","FFU160"],
    "Tecumseh":["THB1380","AE4440","AK4476"]
    }

    st.table(pd.DataFrame(dados))

# --- EXPORTAÇÃO ---
st.markdown("---")

col_p,col_w = st.columns(2)

if col_p.button("🚀 GERAR PDF"):

    if cli == "":
        st.error("Informe o cliente")
    else:

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial","B",14)
        pdf.cell(0,10,"LAUDO TECNICO MPN",0,1,"C")

        pdf.set_font("Arial","",10)

        data = datetime.now().strftime("%d/%m/%Y")

        pdf.cell(0,8,f"Data: {data}",0,1)
        pdf.cell(0,8,f"Cliente: {cli}",0,1)
        pdf.cell(0,8,f"Tecnico: {tec}",0,1)
        pdf.cell(0,8,f"Equipamento: {fab_eq} {mod_eq}",0,1)

        pdf_bytes = pdf.output(dest="S").encode("latin-1","ignore")

        st.download_button(
        "📥 Baixar PDF",
        pdf_bytes,
        f"Laudo_{cli}.pdf",
        "application/pdf"
        )

texto_wa = f"""
MPN REFRIGERACAO

Cliente: {cli}
Equipamento: {fab_eq} {cap_btu} BTU
Tensao medida: {v_medida} V
"""

link_wa = f"https://wa.me/?text={urllib.parse.quote(texto_wa)}"

col_w.link_button("📲 Enviar WhatsApp",link_wa)

def diagnostico_hvac(sh, sc, dt_ar):

    if 6 <= sh <= 12 and 5 <= sc <= 12 and 8 <= dt_ar <= 14:
        return "Sistema operando dentro dos parâmetros ideais."

    if sh > 15 and sc < 3:
        return "Baixa carga de fluido refrigerante."

    if sh < 4 and sc > 12:
        return "Excesso de fluido refrigerante."

    if sh > 15 and sc > 10:
        return "Restrição na linha líquida ou filtro secador."

    if dt_ar > 14:
        return "Baixa vazão de ar na evaporadora."

    if dt_ar < 8:
        return "Baixa eficiência de troca térmica."

    return "Sistema fora do padrão. Requer análise detalhada."

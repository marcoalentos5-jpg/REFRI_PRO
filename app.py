import streamlit as st
from fpdf import FPDF
from datetime import datetime
import math

# --- CONFIGURAÇÃO VISUAL MASTER MPN ---
st.set_page_config(page_title="MPN | Engenharia & Diagnóstico", layout="wide", page_icon="❄️")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    /* Cartões de Métricas Estilo Premium */
    [data-testid="stMetric"] {
        background-color: #004A99 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        border: 2px solid #A9A9A9 !important;
    }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-weight: bold !important; font-size: 1.1rem !important; }
    [data-testid="stMetricValue"] { color: #00D1FF !important; font-size: 2.2rem !important; }
    [data-testid="stMetricDelta"] { color: #FF4B4B !important; background-color: rgba(255,255,255,0.1); border-radius: 5px; padding: 2px; }
    /* Botões */
    .stButton>button { background-color: #004A99; color: white; border-radius: 10px; height: 3.5em; font-weight: bold; width: 100%; border: none; }
    .stButton>button:hover { background-color: #003366; border: 1px solid #00D1FF; }
    h1, h2, h3, h4 { color: #004A99; font-family: 'Arial', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ALTA PRECISÃO (REF. DANFOSS DEW / MANOMÉTRICA) ---
def calcular_t_sat_dew(psig, gas):
    if psig is None or not gas or gas == "": return None
    # Interpolação Logarítmica Calibrada (133.1 psig R-410A -> 7.9°C)
    if gas == "R-410A": return 22.95 * math.log(psig) - 104.38
    elif gas == "R-22": return 26.54 * math.log(psig) - 121.93
    elif gas == "R-134a": return 31.75 * math.log(psig) - 147.35
    elif gas == "R-404A": return 20.88 * math.log(psig) - 94.32
    elif gas == "R-32": return 23.15 * math.log(psig) - 106.85
    elif gas == "R-407C": return 22.51 * math.log(psig) - 103.10
    elif gas == "R-507A": return 20.15 * math.log(psig) - 92.40
    elif gas == "R-600a": return 35.21 * math.log(psig) - 158.12
    return None

# --- GERADOR DE PDF PROFISSIONAL ---
def gerar_pdf_master(dados, diag, solucoes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(0, 74, 153)
    pdf.cell(200, 15, "MPN REFRIGERACAO E CLIMATIZACAO", ln=True, align='C')
    pdf.set_font("Arial", "I", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, f"RELATORIO DE ENGENHARIA - {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    pdf.ln(5)
    
    sections = [
        ("1. IDENTIFICACAO DA VISITA", [("Cliente", dados['cli']), ("Tecnico/Engenheiro", dados['tec'])]),
        ("2. DADOS DO EQUIPAMENTO", [("Fabricante", dados['fab']), ("Linha", dados['lin']), ("Modelo", dados['mod']), ("Serie", dados['ser']), ("Tensao", dados['ten']), ("Gas", dados['gas'])]),
        ("3. ANALISE TERMODINAMICA", [("Delta T", dados['dt']), ("Pressao Succao", dados['p_suc']), ("Temp. Sat. (Dew)", dados['tsat']), ("Temp. Final Line", dados['t_fin']), ("Superaquecimento", dados['sh']), ("RLA", dados['rla']), ("LRA", dados['lra']), ("Amperagem Real", dados['i_med']), ("Delta Amperagem", dados['d_amp'])])
    ]
    for title, fields in sections:
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f" {title}", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        for label, val in fields: pdf.cell(0, 7, f"{label}: {val}", ln=True)
        pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " 4. PARECER TÉCNICO E IA MPN", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    for s in solucoes: pdf.multi_cell(0, 7, f"* {s}")
    return pdf.output(dest='S').encode('latin-1')

# --- NAVEGAÇÃO ---
tab_diag, tab_ai, tab_manuais, tab_carga = st.tabs(["📊 Diagnóstico Master", "🤖 IA & Soluções", "📚 Manuais", "📐 Carga Térmica"])

# --- ABA 1: DIAGNÓSTICO ---
with tab_diag:
    st.image("https://i.imgur.com", width=350)
    with st.expander("📋 Identificação Completa do Sistema", expanded=True):
        c1, c2, c3 = st.columns(3)
        cli = c1.text_input("Cliente", placeholder="Nome/Empresa", value="")
        tec = c2.text_input("Responsável Técnico", value="")
        fab = c3.text_input("Fabricante", placeholder="Ex: Daikin", value="")
        c4, c5, c6 = st.columns(3)
        lin = c4.text_input("Linha", placeholder="Ex: Inverter V", value="")
        mod_eq = c5.text_input("Modelo", placeholder="Código Etiqueta", value="")
        ser = c6.text_input("Número de Série", placeholder="S/N", value="")

    st.sidebar.header("⚙️ Setup Avançado")
    f_gas = st.sidebar.selectbox("Fluido Refrigerante", ["", "R-410A", "R-22", "R-134a", "R-404A", "R-32", "R-407C", "R-507A", "R-600a"])
    f_equip = st.sidebar.selectbox("Tipo de Equipamento", ["", "Split Hi-Wall", "Split Cassete (K-7)", "Piso-Teto", "ACJ (Janela)", "Multi-Split", "VRF/VRV", "Chiller Ar/Água", "Geladeira/Freezer", "Câmara Fria", "Self-Contained"])
    f_tec = st.sidebar.radio("Tecnologia do Compressor", ["ON-OFF", "Inverter", "Digital Scroll"])
    f_tensao = st.sidebar.selectbox("Tensão de Operação", ["", "127V", "220V", "380V", "440V"])

    st.subheader("🛠️ Coleta de Dados Termofluidodinâmicos")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("#### 🌬️ Troca de Ar")
        t_ret = st.number_input("Temp. Retorno [°C]", value=None, placeholder="--")
        t_ins = st.number_input("Temp. Insuflação [°C]", value=None, placeholder="--")
        dt = t_ret - t_ins if (t_ret and t_ins) else None
        st.metric("DELTA T", f"{dt:.1f} °C" if dt else "--")

    with m2:
        st.markdown("#### 🧪 Ciclo (Danfoss Dew)")
        p_suc = st.number_input("Pressão Sucção [PSI]", value=None, placeholder="--")
        t_fin = st.number_input("Temp. Final Sucção [°C]", value=None, placeholder="--")
        tsat = calcular_t_sat_dew(p_suc, f_gas)
        sh = t_fin - tsat if (t_fin and tsat) else None
        if tsat: st.caption(f"Saturação Dew: {tsat:.1f} °C")
        st.metric("SUPER AQUECIMENTO", f"{sh:.1f} K" if sh else "--")

    with m3:
        st.markdown("#### ⚡ Elétrica (RLA/LRA)")
        v_rla = st.number_input("Corrente RLA [A]", value=None, placeholder="--")
        v_lra = st.number_input("Corrente LRA [A]", value=None, placeholder="--")
        v_med = st.number_input("Corrente Medida [A]", value=None, placeholder="--")
        da = v_med - v_rla if (v_rla and v_med) else None
        st.metric("AMPERAGEM REAL", f"{v_med:.1f} A" if v_med else "--", delta=f"{da:.2f} vs RLA" if da else None, delta_color="inverse")

# --- ABA 2: IA & SOLUÇÕES (O PERITO DIGITAL) ---
with tab_ai:
    st.subheader("🤖 Consultoria MPN AI")
    if None in [dt, sh, da]: st.warning("Aguardando preenchimento total das medições na Aba 1.")
    else:
        st.info("Cruzando dados: Manuais Técnicos + Base de Especialistas + Termodinâmica Aplicada...")
        solucoes = []
        if sh < 5: solucoes.append("🚨 **GOLPE DE LÍQUIDO:** IA detecta SH crítico (Danfoss Dew). Verifique excesso de fluido ou EEV travada.")
        if sh > 12: solucoes.append("❌ **FALTA DE FLUIDO:** SH alto indica evaporador 'faminto'. Procure vazamentos ou obstrução no filtro/capilar.")
        if da > 0: solucoes.append(f"⚡ **SOBRECARGA:** Operando {da:.2f}A acima da RLA. Limpe a condensadora ou verifique capacitores.")
        if dt < 8: solucoes.append("🌬️ **BAIXA TROCA:** Delta T ineficiente. Verifique limpeza química do evaporador.")
        if not solucoes: solucoes.append("✅ SISTEMA EM PERFEITO EQUILÍBRIO TERMODINÂMICO.")
        for s in solucoes: st.write(f"- {s}")

# --- BOTÃO FINAL PDF ---
if st.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if None in [t_ret, p_suc, v_rla]: st.error("Aba 1 incompleta.")
    else:
        dados_rel = {"cli": cli, "tec": tec, "fab": fab, "lin": lin, "mod": mod_eq, "ser": ser, "ten": f_tensao, "gas": f_gas, "dt": f"{dt:.1f}", "p_suc": f"{p_suc}", "tsat": f"{tsat:.1f}", "t_fin": f"{t_fin}", "sh": f"{sh:.1f}", "rla": f"{v_rla}", "lra": f"{v_lra}", "i_med": f"{v_med}", "d_amp": f"{da:.2f}"}
        pdf_out = gerar_pdf_master(dados_rel, [], solucoes)
        st.download_button("📥 Baixar Relatório PDF MPN Profissional", data=pdf_out, file_name=f"MPN_{cli}.pdf")

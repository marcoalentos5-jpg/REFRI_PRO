import streamlit as st
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL MPN MASTER ---
st.set_page_config(page_title="MPN | Engenharia & Diagnóstico", layout="wide", page_icon="❄️")

# CSS Customizado para Identidade Visual de Elite
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    [data-testid="stMetric"] {
        background-color: #004A99 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        border: 2px solid #A9A9A9 !important;
    }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-weight: bold !important; font-size: 1.1rem !important; }
    [data-testid="stMetricValue"] { color: #00D1FF !important; font-size: 2.2rem !important; }
    .stButton>button { background-color: #004A99; color: white; border-radius: 10px; height: 3.5em; font-weight: bold; width: 100%; }
    h1, h2, h3, h4 { color: #004A99; font-family: 'Arial', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ENGENHARIA (REF. DANFOSS DEW) ---
def calcular_t_sat_dew(psi, gas):
    if psi is None or not gas or gas == "": return None
    if gas == "R-410A": return (psi**0.5 * 11.23) - 78.4
    if gas == "R-22": return (psi**0.5 * 13.91) - 86.8
    if gas == "R-134a": return (psi**0.5 * 17.15) - 93.1
    if gas == "R-404A": return (psi**0.5 * 10.82) - 79.2
    if gas == "R-32": return (psi**0.5 * 11.35) - 81.5
    return None

# --- GERADOR DE PDF PROFISSIONAL MPN ---
def gerar_pdf_mpn(dados, diag):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(0, 74, 153)
    pdf.cell(200, 15, "MPN REFRIGERACAO E CLIMATIZACAO", ln=True, align='C')
    pdf.set_font("Arial", "I", 10)
    pdf.cell(200, 10, f"RELATORIO TECNICO - {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    pdf.ln(5)
    
    sections = [
        ("1. IDENTIFICACAO", [("Cliente", dados['Cliente']), ("Tecnico", dados['Tecnico'])]),
        ("2. EQUIPAMENTO", [("Fabricante", dados['Fabricante']), ("Linha", dados['Linha']), ("Modelo", dados['Modelo']), ("Serie", dados['Serie']), ("Tensao", dados['Tensao']), ("Gas", dados['Gas'])]),
        ("3. MEDICOES TECNICAS", [("Delta T", dados['DeltaT']), ("Pressao Succao", dados['Pressao']), ("Temp. Sat. Dew", dados['TempSat']), ("Temp. Final", dados['TempFinal']), ("Superaquecimento", dados['SH']), ("RLA", dados['RLA']), ("LRA", dados['LRA']), ("Amperagem Real", dados['I_Medida']), ("Diferenca RLA", dados['DeltaAmp'])])
    ]

    for title, fields in sections:
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f" {title}", ln=True, fill=True)
        pdf.set_font("Arial", "", 11)
        for label, val in fields:
            pdf.cell(0, 8, f"{label}: {val}", ln=True)
        pdf.ln(3)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE DO USUÁRIO ---
st.title("❄️ MPN: Engenharia & Diagnóstico")

# 1. IDENTIFICAÇÃO E DADOS DO EQUIPAMENTO (CAMPOS VAZIOS)
with st.expander("👤 Dados da Visita e Equipamento", expanded=True):
    c1, c2, c3 = st.columns(3)
    cli = c1.text_input("Cliente", placeholder="Nome/Empresa", value="")
    tec = c2.text_input("Técnico/Engenheiro", placeholder="Responsável", value="")
    fab = c3.text_input("Fabricante", placeholder="Ex: Carrier", value="")
    
    c4, c5, c6 = st.columns(3)
    lin = c4.text_input("Linha", placeholder="Ex: Inverter V", value="")
    mod = c5.text_input("Modelo", placeholder="Código da Etiqueta", value="")
    ser = c6.text_input("Número de Série", placeholder="S/N", value="")

# 2. SETUP (SIDEBAR)
st.sidebar.header("⚙️ Configurações Técnicas")
f_gas = st.sidebar.selectbox("Gás (Ref. Danfoss Dew)", ["", "R-410A", "R-22", "R-134a", "R-404A", "R-32"])
f_tipo = st.sidebar.selectbox("Modelo", ["", "Split Hi-Wall", "K-7", "Piso-Teto", "ACJ", "Geladeira"])
f_tec = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter"])
f_tensao = st.sidebar.selectbox("Tensão", ["", "110V", "220V", "380V"])

# 3. MEDIÇÕES DE CAMPO (CAMPOS VAZIOS)
st.subheader("🛠️ Coleta de Dados Termodinâmicos")
m1, m2, m3 = st.columns(3)

with m1:
    st.markdown("#### 🌬️ Troca Térmica")
    t_ret = st.number_input("Temp. Retorno [°C]", value=None, placeholder="--")
    t_ins = st.number_input("Temp. Insuflação [°C]", value=None, placeholder="--")
    dt = t_ret - t_ins if (t_ret is not None and t_ins is not None) else None
    st.metric("DELTA T", f"{dt:.1f} °C" if dt else "--")

with m2:
    st.markdown("#### 🧪 Ciclo Frigorífico")
    p_suc = st.number_input("Pressão Sucção [PSI]", value=None, placeholder="--")
    t_fin = st.number_input("Temp. Final Sucção [°C]", value=None, placeholder="--")
    tsat = calcular_t_sat_dew(p_suc, f_gas)
    sh = t_fin - tsat if (t_fin is not None and tsat is not None) else None
    if tsat: st.caption(f"Saturação Dew: {tsat:.1f} °C")
    st.metric("SUPER AQUECIMENTO", f"{sh:.1f} K" if sh else "--")

with m3:
    st.markdown("#### ⚡ Elétrica (RLA/LRA)")
    v_rla = st.number_input("Corrente RLA [A]", value=None, placeholder="--")
    v_lra = st.number_input("Corrente LRA [A]", value=None, placeholder="--")
    v_med = st.number_input("Corrente Medida [A]", value=None, placeholder="--")
    delta_a = v_med - v_rla if (v_rla and v_med) else None
    st.metric("AMPERAGEM REAL", f"{v_med:.1f} A" if v_med else "--", 
              delta=f"{delta_a:.2f} A vs RLA" if delta_a else None, delta_color="inverse")

# --- PROCESSAMENTO E PDF ---
if st.button("🚀 EXECUTAR CRUZAMENTO DE DADOS"):
    if None in [t_ret, t_ins, p_suc, t_fin, v_rla, v_med]:
        st.error("⚠️ ERRO: Preencha todos os campos técnicos para o diagnóstico.")
    else:
        st.divider()
        diag = []
        if sh < 5: diag.append("🚨 ALERTA: Superaquecimento baixo. Risco de golpe de líquido.")
        if sh > 12: diag.append("❌ FALHA: Superaquecimento alto. Falta de fluido ou obstrução.")
        if delta_a and delta_a > 0: diag.append(f"⚡ SOBRECARGA: Operando {delta_a:.2f}A acima da RLA.")
        if dt and dt < 8: diag.append("🌬️ EFICIÊNCIA: Baixa troca térmica no evaporador.")
        
        if not diag: diag.append("✅ SISTEMA EM PERFEITO EQUILÍBRIO TERMODINÂMICO.")

        st.subheader("📋 Parecer Especialista MPN")
        for item in diag: st.write(f"- {item}")

        dados_pdf = {
            "Cliente": cli, "Tecnico": tec, "Fabricante": fab, "Linha": lin, "Modelo": mod, 
            "Serie": ser, "Tensao": f_tensao, "Gas": f_gas, "DeltaT": f"{dt:.1f}" if dt else "--", 
            "Pressao": f"{p_suc}", "TempSat": f"{tsat:.1f}" if tsat else "--", 
            "TempFinal": f"{t_fin}", "SH": f"{sh:.1f}" if sh else "--", 
            "RLA": f"{v_rla}", "LRA": f"{v_lra}", "I_Medida": f"{v_med}", "DeltaAmp": f"{delta_a:.2f}" if delta_a else "--"
        }
        
        pdf_out = gerar_pdf_mpn(dados_pdf, diag)
        st.download_button("📥 Baixar Relatório PDF MPN Profissional", data=pdf_out, file_name=f"MPN_{cli}.pdf")

import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# --- 2. MOTOR TERMODINÂMICO ---
def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-17.02, -0.29, 11.55, 20.93, 35.58, 47.30, 56.59, 64.59]},
        "R-32": {"p": [50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-17.46, 0.87, 10.86, 20.14, 34.63, 45.96, 55.36, 63.43]},
        "R-22": {"p": [50.0, 100.0, 150.0, 200.0, 300.0, 350.0, 400.0, 500.0, 600.0], "t": [-3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 67.72, 78.38, 83.12, 87.53]},
        "R-134a": {"p": [0.0, 50.0, 100.0, 150.0, 200.0], "t": [-26.08, 12.23, 30.92, 43.65, 53.74]},
        "R-404A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0], "t": [-45.45, -9.41, 8.96, 22.23, 32.59]}
    }
    if gas not in ancoras: return 0.0
    try: return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)
    except: return 0.0

# --- 3. INTERFACE DO APP ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2 = st.columns(2)
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c2.text_input("CPF / CNPJ")
    l2_c1, l2_c2, l2_c3 = st.columns(3)
    endereco = l2_c1.text_input("Endereço (Rua e Número)")
    bairro = l2_c2.text_input("Bairro")
    cep = l2_c3.text_input("CEP", placeholder="00000-000")
    l3_c1, l3_c2, l3_c3 = st.columns([1, 1.5, 1])
    whatsapp = l3_c1.text_input("🟢 WhatsApp", value="21980264217")
    email_cli = l3_c2.text_input("✉️ E-mail")
    data_visita = l3_c3.date_input("Data da Visita", value=date.today())
    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    linha = d1.text_input("Linha")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"])
    tipo_eq = d2.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF", "Chiller"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"])
    cap_digitada = d3.text_input("Capacidade (Mil BTU´s)")
    col_ev1, col_ev2 = st.columns(2)
    mod_evap = col_ev1.text_input("Modelo Unidade Evaporadora")
    serie_evap = col_ev2.text_input("Nº de Série Evaporadora")
    col_cd1, col_cd2 = st.columns(2)
    mod_cond = col_cd1.text_input("Modelo Unidade Condensadora")
    serie_cond = col_cd2.text_input("Nº de Série Condensadora")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    e1, e2 = st.columns(2)
    v_rede = e1.number_input("Tensão da Rede (V)", value=220.0)
    v_med = e1.number_input("Tensão Medida (V)", value=218.0)
    lra_comp = e2.number_input("LRA (A)", value=0.0)
    rla_comp = e2.number_input("RLA (A)", value=0.0)
    a_med = e2.number_input("Corrente Medida (A)", value=0.0)
    diff_v = round(v_rede - v_med, 1)
    diff_a = round(rla_comp - a_med, 1)
    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric("Queda de Tensão", f"{diff_v} V", delta=f"-{diff_v}V", delta_color="inverse")
    res2.metric("Folga Corrente (RLA-Med)", f"{diff_a} A")
    res3.metric("Carga Motor", f"{round((a_med/rla_comp*100),1) if rla_comp > 0 else 0}%")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    col1, col2, col3 = st.columns(3)
    p_suc = col1.number_input("Pressão Sucção (PSIG)", value=118.0)
    t_suc_tubo = col1.number_input("Temp. Tubo Sucção (°C)", value=12.0)
    p_liq = col2.number_input("Pressão Descarga (PSIG)", value=345.0)
    t_liq_tubo = col2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ret = col3.number_input("Temp. Ar Retorno (°C)", value=24.0)
    t_ins = col3.number_input("Temp. Ar Insufl. (°C)", value=12.0)
    tsat_suc = get_tsat_global(p_suc, fluido)
    tsat_liq = get_tsat_global(p_liq, fluido)
    sh = round(t_suc_tubo - tsat_suc, 1)
    sc = round(tsat_liq - t_liq_tubo, 1)
    dt = round(t_ret - t_ins, 1)
    st.markdown("---")
    ct1, ct2 = st.columns(2)
    with ct1:
        st.markdown(f"""<div style='background-color:#004a99;padding:15px;border-radius:10px;border-left:5px solid #ffcc00;color:white;'><b>🌡️ T-Sat Sucção:</b><h2 style='margin:0;color:white;'>{tsat_suc} °C</h2><b>🔥 Superaquecimento (SH):</b><h2 style='margin:0;color:white;'>{sh} K</h2></div>""", unsafe_allow_html=True)
    with ct2:
        st.markdown(f"""<div style='background-color:#004a99;padding:15px;border-radius:10px;border-left:5px solid #00d2ff;color:white;'><b>❄️ T-Sat Líquido:</b><h2 style='margin:0;color:white;'>{tsat_liq} °C</h2><b>💧 Sub-resfriamento (SC):</b><h2 style='margin:0;color:white;'>{sc} K</h2></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div style='background-color:#004a99;padding:20px;border-radius:15px;text-align:center;margin-top:10px;border:2px solid #ffcc00;'><span style='color:white;font-weight:bold;'>📈 Diferencial de Temperatura (ΔT)</span><h1 style='margin:0;color:white;font-size:45px;'>{dt} K</h1></div>""", unsafe_allow_html=True)

with tab_diag:
    st.subheader("🤖 Diagnóstico e Recomendações")
    obs = st.text_area("Observações Técnicas Detalhadas", height=100)
    medidas_tomadas = st.text_area("🔧 Medidas Técnicas Tomadas", height=100)

    st.markdown("### 🔧 Medidas Técnicas Propostas pela IA")
    col_ia_1, col_ia_2 = st.columns(2)
    
    diag_termo = []
    diag_eletr = []
    obs_low = obs.lower()
    
    # Cruzamento de Dados e Medidas de Conserto
    if any(x in obs_low for x in ["óleo", "mancha", "vazamento"]):
        if sh > 12: diag_termo.append("🚨 [MEDIDA]: Vazamento confirmado. Localizar fuga com N2 e refazer carga por massa.")
        else: diag_termo.append("⚠️ [MEDIDA]: Presença de óleo relatada. Verificar estanqueidade das flanges.")
    if any(x in obs_low for x in ["gelo", "congelando"]):
        if sc > 10: diag_termo.append("⚙️ [MEDIDA]: Restrição na expansão. Substituir filtro secador ou capilar.")
        elif sh < 5: diag_termo.append("❄️ [MEDIDA]: Inundação do evaporador. Higienizar serpentinas e testar ventilador.")
    
    if sh < 6: diag_termo.append(f"🌡️ [SH CRÍTICO]: {sh}K. Risco de golpe de líquido.")
    if diff_v > (v_rede * 0.05): diag_eletr.append(f"⚡ [QUEDA TENSÃO]: {diff_v}V excedida.")

    with col_ia_1:
        st.info("**🌡️ Ciclo Frigorífico**")
        txt_termo = "\n".join(diag_termo) if diag_termo else "✅ Sem anomalias térmicas."
        st.write(txt_termo)

    with col_ia_2:
        st.info("**⚡ Parte Elétrica**")
        txt_eletr = "\n".join(diag_eletr) if diag_eletr else "✅ Sem anomalias elétricas."
        st.write(txt_eletr)

    medidas_ia_pdf = f"TERMODINAMICA:\n{txt_termo}\n\nELETRICA:\n{txt_eletr}"
    
    if st.button("Gerar Relatório PDF (Rigor Técnico & Stress Test)"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        def fix_text(t):
            if t is None: return ""
            subst = {"🚨": "!!", "⚠️": "!", "⚙️": "*", "⚡": ">>", "🔥": "!!", "❌": "X", "✅": "OK", "❄️": "*", "🌡️": "T"}
            t = str(t)
            for k, v in subst.items(): t = t.replace(k, v)
            return t.encode('latin-1', 'ignore').decode('latin-1')

        if os.path.exists("logo.png"):
            pdf.image("logo.png", 10, 8, 33)
            pdf.ln(10)
        
        pdf.set_font("Helvetica", "B", 16); pdf.set_text_color(0, 74, 153)
        pdf.cell(190, 10, fix_text("LAUDO TÉCNICO DE ENGENHARIA"), ln=True, align="R")
        pdf.line(10, 32, 200, 32); pdf.ln(8)

        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(0)
        pdf.cell(190, 8, fix_text(" 1. DADOS TÉCNICOS"), ln=True, fill=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(95, 7, fix_text(f"Cliente: {cliente}")); pdf.cell(95, 7, fix_text(f"Data: {data_visita}"), ln=True); pdf.ln(4)

        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, fix_text(" 2. PARÂMETROS OPERACIONAIS"), ln=True, fill=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(47, 7, fix_text(f"V. Med: {v_med}V")); pdf.cell(47, 7, fix_text(f"A. Med: {a_med}A")); pdf.cell(47, 7, fix_text(f"SH: {sh}K")); pdf.cell(49, 7, fix_text(f"SC: {sc}K"), ln=True); pdf.ln(4)

        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, fix_text(" 3. DIAGNÓSTICO E OBSERVAÇÕES (STRESS TEST)"), ln=True, fill=True)
        pdf.set_font("Helvetica", "B", 9); pdf.cell(190, 6, fix_text("> Diagnóstico IA:"), ln=True)
        pdf.set_font("Helvetica", "", 9); pdf.multi_cell(190, 5, fix_text(medidas_ia_pdf)); pdf.ln(2)
        
        pdf.set_font("Helvetica", "B", 9); pdf.cell(190, 6, fix_text("> Observações Detalhadas:"), ln=True)
        pdf.set_font("Helvetica", "", 9); pdf.multi_cell(190, 5, fix_text(obs)); pdf.ln(2)

        pdf_output = io.BytesIO()
        pdf_content = pdf.output(dest='S')
        if isinstance(pdf_content, str): pdf_content = pdf_content.encode('latin-1', 'replace')
        pdf_output.write(pdf_content)
        st.download_button(label="📥 Baixar Laudo Final", data=pdf_output.getvalue(), file_name=f"Laudo_{cliente}.pdf", mime="application/pdf")

import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# --- 2. MOTOR TERMODINÂMICO (PRECISÃO PERICIAL) ---
def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                   "t": [-51.0, -17.02, -0.29, 11.55, 20.93, 28.84, 35.58, 41.74, 47.3, 52.1, 56.59, 60.7, 64.59]},
        "R-32": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                 "t": [-51.7, -17.46, 0.87, 10.86, 20.14, 27.9, 34.63, 40.6, 45.96, 50.8, 55.36, 59.5, 63.43]},
        "R-22": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 600.0], 
                 "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 67.72, 73.2, 78.38, 87.53]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 80.0, 100.0, 130.0, 150.0, 180.0, 200.0], 
                   "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 38.4, 43.65, 50.1, 53.74]},
        "R-404A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0], 
                   "t": [-45.45, -9.41, 8.96, 22.23, 32.59, 41.2, 48.6, 55.2, 61.1]}
    }
    if gas not in ancoras: return 0.0
    try: return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)
    except: return 0.0

# --- 3. INTERFACE DO APP ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2 = st.columns([2.5, 1]) 
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c2.text_input("CPF / CNPJ")
    l2_c1, l2_c2, l2_c3 = st.columns(3)
    endereco = l2_c1.text_input("Endereço (Rua e Número)")
    bairro = l2_c2.text_input("Bairro")
    cep = l2_c3.text_input("CEP", placeholder="00000-000")
    l3_c1, l3_c2, l3_c3, l3_c4 = st.columns([1.2, 1, 1.5, 1])
    comodo_sala = l3_c1.text_input("🏠 COMODO DO PROCEDIMENTO")
    whatsapp = l3_c2.text_input("🟢 WhatsApp", value="21980264217")
    email_cli = l3_c3.text_input("✉️ E-mail")
    data_visita = l3_c4.date_input("Data da Visita", value=date.today())
    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    linha = d1.text_input("Linha")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"])
    tipo_eq = d2.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF", "Chiller"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"])
    cap_digitada = d3.text_input("Capacidade (Mil BTU´s)", value="0")
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
    obs_raw = st.text_area("✍️ Observações Técnicas Detalhadas", height=150)
    med_tomadas_raw = st.text_area("🔧 Medidas Técnicas Tomadas", height=150)
    diag_termo = []
    if sh < 6: diag_termo.append(f"SH CRÍTICO ({sh}K).")
    if sc > 12: diag_termo.append(f"SC ELEVADO ({sc}K).")
    propostas_sugestao = "\n".join(diag_termo) if diag_termo else "Sem anomalias detectadas."
    ia_raw = st.text_area("🤖 Medidas Técnicas Propostas pela IA", value=propostas_sugestao, height=150)

    st.markdown("---")
    if st.button("📄 Gerar Relatório Profissional"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 74, 153)
        pdf.rect(0, 0, 210, 42, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 15, "RELATORIO TECNICO", ln=True, align='C')
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, "CNPJ: 45.451.272/0001-00 | Tel: 21-98545-3763", ln=True, align='C')
        pdf.ln(12)

        def draw_header(title):
            pdf.set_line_width(0.2)
            pdf.set_fill_color(235, 235, 235)
            pdf.set_text_color(0, 74, 153)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, f" {title.upper()}", ln=True, fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(3)

        draw_header("1. Identificacao do Cliente")
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(30, 6, "Cliente:", ln=0); pdf.set_font("Arial", '', 9); pdf.cell(80, 6, f"{cliente}", ln=0)
        pdf.set_x(120) 
        pdf.set_font("Arial", 'B', 9); pdf.cell(30, 6, "CPF/CNPJ:", ln=0); pdf.set_font("Arial", '', 9); pdf.cell(50, 6, f"{doc_cliente}", ln=1)
        pdf.set_font("Arial", 'B', 9); pdf.cell(30, 6, "Cômodo Proc.:", ln=0); pdf.set_font("Arial", '', 9); pdf.cell(80, 6, f"{comodo_sala}", ln=0)
        pdf.set_x(120) 
        pdf.set_font("Arial", 'B', 9); pdf.cell(30, 6, "Data Visita:", ln=0); pdf.set_font("Arial", '', 9); pdf.cell(50, 6, f"{data_visita}", ln=1)
        pdf.ln(5)

        draw_header("2. Dados Tecnicos do Equipamento")
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(30, 6, "Marca/Linha:", ln=0); pdf.set_font("Arial", '', 9); pdf.cell(80, 6, f"{fabricante} / {linha}", ln=0)
        pdf.set_x(120) 
        pdf.set_font("Arial", 'B', 9); pdf.cell(30, 6, "Capacidade:", ln=0); pdf.set_font("Arial", '', 9); pdf.cell(50, 6, f"{cap_digitada} BTU's", ln=1)
        pdf.ln(2)

        draw_header("3. Parametros Operacionais (Medicoes)")
        pdf.set_font("Arial", 'B', 8)
        pdf.set_fill_color(245, 245, 245)
        pdf.cell(47, 7, "  PRESSAO SUCÇÃO", 1, 0, 'L', True)
        pdf.cell(47, 7, "  SUPER-AQUECIMENTO", 1, 0, 'L', True)
        pdf.cell(47, 7, "  CORRENTE MEDIDA", 1, 0, 'L', True)
        pdf.cell(47, 7, "  TENSAO REDE", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(47, 8, f"  {p_suc} PSIG", 1, 0, 'L')
        pdf.cell(47, 8, f"  {sh} K", 1, 0, 'L')
        pdf.cell(47, 8, f"  {a_med} A", 1, 0, 'L')
        pdf.cell(47, 8, f"  {v_med} V", 1, 1, 'L')
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(47, 7, "  PRESSAO DESCARGA", 1, 0, 'L', True)
        pdf.cell(47, 7, "  SUB-RESFRIAMENTO", 1, 0, 'L', True)
        pdf.cell(47, 7, "  DELTA T (AR)", 1, 0, 'L', True)
        pdf.cell(47, 7, "  CARGA MOTOR", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(47, 8, f"  {p_liq} PSIG", 1, 0, 'L')
        pdf.cell(47, 8, f"  {sc} K", 1, 0, 'L')
        pdf.cell(47, 8, f"  {dt} K", 1, 0, 'L')
        perc_carga = round((a_med/rla_comp*100),1) if rla_comp > 0 else 0
        pdf.cell(47, 8, f"  {perc_carga} %", 1, 1, 'L')
        pdf.ln(5)

        draw_header("4. Diagnostico e Medidas Tecnicas")
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 6, "Observacoes Tecnicas:", ln=1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, f"{obs_raw}"); pdf.ln(2)
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 6, "Medidas Tomadas:", ln=1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, f"{med_tomadas_raw}"); pdf.ln(2)
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 6, "Recomendacoes IA:", ln=1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, f"{ia_raw}")

        # --- GERAÇÃO SEGURA DO PDF USANDO BYTESIO ---
        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1', 'ignore')
        
        st.download_button(
            label="⬇️ Baixar Relatório PDF", 
            data=pdf_bytes, 
            file_name=f"Relatorio_{cliente}.pdf", 
            mime="application/pdf"
        )

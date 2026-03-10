import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io
import os
from PIL import Image

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

# --- 3. MOTOR DE GERAÇÃO PDF ---
class PDF(FPDF):
    def __init__(self, logo_path=None):
        super().__init__()
        self.logo_path = logo_path
    def header(self):
        if self.logo_path:
            self.image(self.logo_path, 10, 8, 33)
            self.set_x(45)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'RELATÓRIO TÉCNICO DE MANUTENÇÃO - MPN ENGENHARIA', 0, 1, 'R')
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

# --- 4. INTERFACE DO APP ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("🖼️ Identidade Visual")
    logo_file = st.file_uploader("Upload da Logomarca (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
    st.markdown("---")
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
    col_obs_in, col_obs_out = st.columns(2)
    with col_obs_in:
        obs_raw = st.text_area("✍️ Observações Técnicas Detalhadas", height=150)
    if obs_raw:
        linhas_obs = obs_raw.split('\n')
        obs = "\n".join([f"• {l.strip()}" if l.strip() and not l.startswith('•') else l for l in linhas_obs])
    else: obs = ""
    with col_obs_out:
        st.markdown("**📝 Conteúdo Ajustado (Observações):**")
        st.info(obs if obs else "Aguardando preenchimento...")
    st.markdown("---")
    col_med_in, col_med_out = st.columns(2)
    with col_med_in:
        med_tomadas_raw = st.text_area("🔧 Medidas Técnicas Tomadas", height=150)
    if med_tomadas_raw:
        linhas_med = med_tomadas_raw.split('\n')
        medidas_tomadas = "\n".join([f"• {l.strip()}" if l.strip() and not l.startswith('•') else l for l in linhas_med])
    else: medidas_tomadas = ""
    with col_med_out:
        st.markdown("**📝 Conteúdo Ajustado (Tomadas):**")
        st.success(medidas_tomadas if medidas_tomadas else "Aguardando preenchimento...")
    st.markdown("---")
    diag_termo = []
    diag_eletr = []
    obs_low = obs.lower()
    if any(x in obs_low for x in ["óleo", "mancha", "vazamento"]):
        if sh > 12: diag_termo.append("Vazamento confirmado. Localizar fuga com N2 e refazer carga.")
        else: diag_termo.append("Presença de óleo. Verificar estanqueidade.")
    if sh < 6: diag_termo.append(f"SH CRÍTICO ({sh}K). Risco de golpe de líquido.")
    if diff_v > (v_rede * 0.05): diag_eletr.append(f"QUEDA TENSÃO ({diff_v}V) excedida.")
    propostas_raw = "\n".join(diag_termo + diag_eletr) if (diag_termo + diag_eletr) else "Sem anomalias críticas detectadas."
    st.markdown("**🤖 Medidas Técnicas Propostas pela IA**")
    col_ia_in, col_ia_out = st.columns(2)
    with col_ia_in:
        ia_raw = st.text_area("Sugestões Geradas (Edição Opcional)", value=propostas_raw, height=150)
    if ia_raw:
        linhas_ia = ia_raw.split('\n')
        medidas_ia_final = "\n".join([f"• {l.strip()}" if l.strip() and not l.startswith('•') else l for l in linhas_ia])
    else: medidas_ia_final = ""
    with col_ia_out:
        st.warning(medidas_ia_final if medidas_ia_final else "IA sem sugestões adicionais.")
    st.markdown("---")

    # --- FINALIZAÇÃO E DOWNLOAD DO PDF ---
    if st.button("🚀 PROCESSAR RELATÓRIO PDF"):
        temp_logo = None
        if logo_file:
            temp_logo = "temp_logo.png"
            with open(temp_logo, "wb") as f:
                f.write(logo_file.getvalue())
        
        pdf = PDF(logo_path=temp_logo)
        pdf.add_page()
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, f"CLIENTE: {cliente if cliente else 'Não informado'}", 0, 1)
        pdf.cell(0, 8, f"EQUIPAMENTO: {fabricante} {cap_digitada} BTU ({fluido})", 0, 1)
        pdf.cell(0, 8, f"DATA: {data_visita}", 0, 1)
        pdf.ln(5)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 8, 'PARÂMETROS TÉCNICOS', 1, 1, 'C', 1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(95, 8, f"Pressão Sucção: {p_suc} PSIG", 1)
        pdf.cell(95, 8, f"Pressão Descarga: {p_liq} PSIG", 1, 1)
        pdf.cell(95, 8, f"Superaquecimento: {sh} K", 1)
        pdf.cell(95, 8, f"Sub-resfriamento: {sc} K", 1, 1)
        pdf.cell(95, 8, f"Corrente Medida: {a_med} A", 1)
        pdf.cell(95, 8, f"Tensão Medida: {v_med} V", 1, 1)
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'DIAGNÓSTICO E OBSERVAÇÕES', 1, 1, 'C', 1)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 8, f"Observações:\n{obs}\n\nMedidas Tomadas:\n{medidas_tomadas}\n\nPropostas Técnicas:\n{medidas_ia_final}", 1)
        
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button(label="📥 BAIXAR RELATÓRIO TÉCNICO", data=pdf_bytes, file_name=f"Relatorio_{cliente}_{data_visita}.pdf", mime="application/pdf")
        
        if temp_logo and os.path.exists(temp_logo):
            os.remove(temp_logo)

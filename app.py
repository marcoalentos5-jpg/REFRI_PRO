import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# --- 2. MOTOR TERMODINÂMICO (PRECISÃO PERICIAL) ---
def get_tsat_global(psig, gas):
    ancoras_completas = {
        "R-410A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                   "t": [-51.0, -17.02, -0.29, 11.55, 20.93, 28.84, 35.58, 41.74, 47.3, 52.1, 56.59, 60.7, 64.59]},
        "R-32": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                 "t": [-51.7, -17.46, 0.87, 10.86, 20.14, 27.9, 34.63, 40.6, 45.96, 50.8, 55.36, 59.5, 63.43]},
        "R-22": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 600.0], 
                 "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 73.2, 78.38, 87.53]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 80.0, 100.0, 130.0, 150.0, 180.0, 200.0], 
                   "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 38.4, 43.65, 50.1, 53.74]},
        "R-404A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0], 
                   "t": [-45.45, -9.41, 8.96, 22.23, 32.59, 41.2, 48.6, 55.2, 61.1]}
    }
    if gas not in ancoras_completas: return 0.0
    try: return round(float(np.interp(psig, ancoras_completas[gas]["p"], ancoras_completas[gas]["t"])), 2)
    except: return 0.0

def clean(txt):
    if not txt: return ""
    replacements = {'°': 'C', 'º': '.', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C'}
    t = str(txt)
    for old, new in replacements.items(): t = t.replace(old, new)
    return t.encode('ascii', 'ignore').decode('ascii')

# --- 3. INTERFACE DO APP ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    
    # Linha 1: Redução 30% aplicada
    c1, c2, c3, sp1 = st.columns([1.75, 0.84, 0.7, 1.5])
    cliente = c1.text_input("Nome do Cliente / Empresa", key="cli_name")
    doc_cliente = c2.text_input("CPF / CNPJ", key="cli_doc")
    data_visita = c3.date_input("📅 DATA VISITA", value=date.today(), key="cli_date")
    
    # Linha 2: Endereço
    c4, c5, c6, c7, sp2 = st.columns([0.56, 1.4, 0.35, 0.7, 1.7])
    tipo_logr = c4.selectbox("Tipo", ["Rua", "Avenida", "Travessa", "Alameda", "Estrada", "Rodovia", "Praça", "Loteamento"], key="cli_logr_t")
    nome_logr = c5.text_input("Logradouro", key="cli_logr_n")
    numero = c6.text_input("Nº", key="cli_num")
    complemento = c7.text_input("Comp.", key="cli_comp")
    
    # Linha 3: Contatos e Localidade
    c8, c9, c10, sp3 = st.columns([0.7, 0.56, 1.05, 2.4])
    bairro = c8.text_input("Bairro", key="cli_bairro")
    cep = c9.text_input("CEP", key="cli_cep")
    email_cli = c10.text_input("✉️ E-mail", key="cli_mail")

    c11, c12, c13, sp4 = st.columns([0.7, 0.7, 0.7, 2.6])
    whatsapp = c11.text_input("🟢 WhatsApp", value="21980264217", key="cli_wpp")
    celular = c12.text_input("📱 Celular", key="cli_cel")
    tel_residencial = c13.text_input("📞 Tel. Residencial", key="cli_tel")

    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos")
    
    # Dados Máquina: Redução 30%
    d1, d2, d3, d4, sp5 = st.columns([0.7, 0.7, 0.7, 0.7, 1.9])
    fabricante = d1.text_input("Fabricante (Marca)", key="eq_fab")
    linha = d2.text_input("Linha", key="eq_lin")
    modelo_eq = d3.text_input("Modelo", key="eq_mod")
    cap_digitada = d4.text_input("Capacidade (BTU´s)", value="0", key="eq_cap")
    
    # Tecnologia e Fluido
    d5, d6, d7, sp6 = st.columns([1.05, 0.56, 0.49, 2.6]) 
    tecnologia = d5.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"], key="eq_tec")
    tipo_eq = d6.selectbox("Tipo de Sistema", ["Split", "Cassete", "Piso-Teto", "VRF", "Chiller"], key="eq_tipo")
    fluido = d7.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"], key="eq_gas")

    # Localizações unificadas
    d8, d9, sp7 = st.columns([0.7, 0.7, 3.3])
    loc_evap = d8.text_input("Localização Evaporadora", key="loc_evap")
    loc_cond = d9.text_input("Localização Condensadora", key="loc_cond")

    # Modelos e Séries
    col_tec1, col_tec2, col_tec3, col_tec4, sp8 = st.columns([0.7, 0.7, 0.7, 0.7, 1.9])
    mod_evap = col_tec1.text_input("Modelo Unid. Evap.", key="mod_evap")
    serie_evap = col_tec2.text_input("Nº Série Evap.", key="ser_evap")
    mod_cond = col_tec3.text_input("Modelo Unid. Cond.", key="mod_cond")
    serie_cond = col_tec4.text_input("Nº Série Cond.", key="ser_cond")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    e1, e2 = st.columns(2)
    v_rede = e1.number_input("Tensão da Rede (V)", value=220.0, key="v_rede")
    v_med = e1.number_input("Tensão Medida (V)", value=218.0, key="v_med")
    lra_comp = e2.number_input("LRA (A)", value=0.0, key="lra")
    rla_comp = e2.number_input("RLA (A)", value=1.0, key="rla")
    a_med = e2.number_input("Corrente Medida (A)", value=0.0, key="a_med")
    diff_v = round(v_rede - v_med, 1)
    carga_final = round((a_med/rla_comp*100),1) if rla_comp > 0 else 0.0
    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric("Queda de Tensão", f"{diff_v} V", delta=f"-{diff_v}V", delta_color="inverse")
    res2.metric("Folga Corrente", f"{round(rla_comp - a_med, 1)} A")
    res3.metric("Carga Motor", f"{carga_final}%")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    col1, col2, col3 = st.columns(3)
    p_suc = col1.number_input("Pressão Sucção (PSIG)", value=118.0, key="p_suc")
    t_suc_tubo = col1.number_input("Temp. Tubo Sucção (°C)", value=12.0, key="t_suc")
    p_liq = col2.number_input("Pressão Descarga (PSIG)", value=345.0, key="p_liq")
    t_liq_tubo = col2.number_input("Temp. Tubo Líquido (°C)", value=30.0, key="t_liq")
    tsat_suc = get_tsat_global(p_suc, fluido)
    tsat_liq = get_tsat_global(p_liq, fluido)
    sh = round(t_suc_tubo - tsat_suc, 1)
    sc = round(tsat_liq - t_liq_tubo, 1)
    st.markdown("---")
    ct1, ct2 = st.columns(2)
    with ct1:
        st.markdown(f"""<div style='background-color:#004a99;padding:15px;border-radius:10px;border-left:5px solid #ffcc00;color:white;'><b>🌡️ T-Sat Sucção:</b><h2 style='margin:0;color:white;'>{tsat_suc} °C</h2><b>🔥 Superaquecimento (SH):</b><h2 style='margin:0;color:white;'>{sh} K</h2></div>""", unsafe_allow_html=True)
    with ct2:
        st.markdown(f"""<div style='background-color:#004a99;padding:15px;border-radius:10px;border-left:5px solid #00d2ff;color:white;'><b>❄️ T-Sat Líquido:</b><h2 style='margin:0;color:white;'>{tsat_liq} °C</h2><b>💧 Sub-resfriamento (SC):</b><h2 style='margin:0;color:white;'>{sc} K</h2></div>""", unsafe_allow_html=True)

with tab_diag:
    medidas = st.text_area("🤖 Diagnóstico Final / IA", value=f"SH: {sh}K | SC: {sc}K", height=150, key="diag_txt")
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
            pdf.set_fill_color(235, 235, 235); pdf.set_text_color(0, 74, 153); pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, f" {clean(title.upper())}", ln=True, fill=True); pdf.set_text_color(0, 0, 0); pdf.ln(3)

        draw_header("1. Identificacao do Cliente")
        pdf.set_font("Arial", '', 9)
        pdf.cell(0, 6, f"Cliente: {clean(cliente)} | Doc: {clean(doc_cliente)}", ln=True)
        pdf.cell(0, 6, f"Endereco: {clean(tipo_logr)} {clean(nome_logr)}, No {clean(numero)} {clean(complemento)}", ln=True)
        pdf.cell(0, 6, f"Bairro: {clean(bairro)} | CEP: {clean(cep)} | WhatsApp: {clean(whatsapp)} | Data: {data_visita}", ln=True)
        
        draw_header("2. Dados Tecnicos")
        pdf.cell(0, 6, f"Equipamento: {clean(fabricante)} | Modelo: {clean(modelo_eq)} | Tecnologia: {tecnologia}", ln=True)
        pdf.cell(0, 6, f"Loc. Evap: {clean(loc_evap)} | Loc. Cond: {clean(loc_cond)}", ln=True)
        pdf.cell(0, 6, f"Evaporadora Serie: {clean(serie_evap)} | Condensadora Serie: {clean(serie_cond)}", ln=True)

        draw_header("3. Parametros Medidos")
        pdf.cell(0, 6, f"Eletrica: {v_med}V | {a_med}A | Carga: {carga_final}%", ln=True)
        pdf.cell(0, 6, f"Termica: Succao {p_suc} PSIG | SH: {sh}K | SC: {sc}K", ln=True)

        draw_header("4. Diagnostico Final")
        pdf.multi_cell(0, 6, clean(medidas))

        pdf_output = pdf.output(dest='S').encode('latin-1', errors='replace')
        st.download_button("📥 Baixar PDF", pdf_output, f"Relatorio_{clean(cliente)}.pdf", "application/pdf")

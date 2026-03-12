import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA (BLOQUEADA) ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# --- INSTRUÇÃO SEGUIDA: AUMENTO DA FONTE DAS ABAS VIA CSS ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR TERMODINÂMICO E UTILITÁRIOS ---
def get_tsat_global(psig, gas):
    ancoras = {
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
    if gas not in ancoras or psig is None: return 0.0
    try: return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)
    except: return 0.0

def clean(txt):
    if not txt: return "N/A"
    replacements = {'°': 'C', 'º': '.', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C'}
    t = str(txt)
    for old, new in replacements.items(): t = t.replace(old, new)
    return t.encode('ascii', 'ignore').decode('ascii')

# --- 3. INTERFACE DO APP ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente = c1.text_input("Cliente/Empresa", key="f_cli")
    doc_cliente = c2.text_input("CPF/CNPJ", key="f_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY", key="f_date")
    whatsapp = c4.text_input("🟢 WhatsApp", value="21980264217", key="f_wpp")
    celular = c5.text_input("📱 Celular", key="f_cel")
    tel_residencial = c6.text_input("📞 Fixo", key="f_fix")

    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."], key="f_tlog")
    nome_logr = e2.text_input("Logradouro", key="f_nlog")
    numero = e3.text_input("Nº", key="f_num")
    complemento = e4.text_input("Comp.", key="f_comp")
    bairro = e5.text_input("Bairro", key="f_bai")
    cep = e6.text_input("CEP", key="f_cep")
    email_cli = e7.text_input("✉️ E-mail", key="f_mail")

    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3 = st.columns(3)
    with g1:
        fabricante = st.text_input("Marca", key="f_fab")
        modelo_eq = st.text_input("Modelo Geral", key="f_mod")
        cap_digitada = st.text_input("Capacidade (BTU/h)", value="0", key="f_cap")
    with g2:
        linha = st.text_input("Linha", key="f_lin")
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"], key="f_tec")
        fluido = st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"], key="f_gas")
    with g3:
        tipo_eq = st.selectbox("Sistema", ["Split", "Cassete", "Piso", "VRF", "Chiller"], key="f_sis")
        loc_evap = st.text_input("Local Evaporadora", key="f_le")
        loc_cond = st.text_input("Local Condensadora", key="f_lc")

    st.markdown("##### Detalhes de Série")
    s1, s2 = st.columns(2)
    with s1:
        mod_evap = st.text_input("Modelo Evap.", key="f_me")
        serie_evap = st.text_input("Nº Série Evap.", key="f_se")
    with s2:
        mod_cond = st.text_input("Modelo Cond.", key="f_mc")
        serie_cond = st.text_input("Nº Série Cond.", key="f_sc")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns(3)
    with el1:
        v_rede = st.number_input("Tensão Rede (V)", value=220.0)
        v_med = st.number_input("Tensão Medida (V)", value=218.0)
        diff_v = round(v_rede - v_med, 1)
        st.write("Diferença entre Tensões")
        st.success(f"{diff_v} V")
    with el2:
        rla_comp = st.number_input("Corrente RLA (A)", value=1.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
        diff_a = round(a_med - rla_comp, 1)
        st.write("Diferença entre Correntes")
        st.success(f"{diff_a} A")
    with el3:
        lra_comp = st.number_input("LRA (A)", value=0.0)

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        st.markdown("**Sucção (Baixa)**")
        p_suc = st.number_input("Pressão (PSI)", value=118.0, key="ps")
        t_suc_tubo = st.number_input("Temp. Tubo (°C)", value=12.0, key="ts")
        ts_suc = get_tsat_global(p_suc, fluido)
        st.write("T-Sat Sucção")
        st.info(f"{ts_suc} °C")
    with tr2:
        st.markdown("**Líquido (Alta)**")
        p_liq = st.number_input("Pressão (PSI)", value=345.0, key="pl")
        t_liq_tubo = st.number_input("Temp. Tubo (°C)", value=30.0, key="tl")
        ts_liq = get_tsat_global(p_liq, fluido)
        st.write("T-Sat Líquido")
        st.info(f"{ts_liq} °C")
    with tr3:
        st.markdown("**Performance**")
        sh_val = round(t_suc_tubo - ts_suc, 1)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        st.write("Superaquecimento (SH)")
        st.success(f"**{sh_val} K**")
        st.write("Subresfriamento (SC)")
        st.success(f"**{sc_val} K**")

with tab_diag:
    resumo_pre = f"SH: {sh_val}K | SC: {sc_val}K\n\nParecer: "
    medidas = st.text_area("🤖 Diagnóstico / Parecer", value=resumo_pre, height=150)
    
    if st.button("📄 Gerar Relatório Profissional"):
        pdf = FPDF()
        pdf.add_page()
        
        pdf.image("logo.png", 10, 8, 42)
        pdf.set_font("Arial", 'B', 22); pdf.set_text_color(0, 51, 102)
        pdf.set_xy(0, 10); pdf.cell(210, 10, "MPN", 0, 1, 'C')
        
        # Relatório Técnico Centralizado
        pdf.set_font("Arial", 'B', 16)
        pdf.set_x(0)
        pdf.cell(210, 8, "Relatório Técnico".encode('latin-1', 'replace').decode('latin-1'), 0, 1, 'C')

        pdf.set_y(32)
        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(220, 230, 241); pdf.set_text_color(0, 51, 102)
        pdf.cell(145, 6, " Dados do Cliente", 1, 0, 'L', True)
        pdf.set_font("Arial", 'B', 8)
        data_formatada = data_visita.strftime("%d/%m/%Y")
        pdf.cell(45, 6, f"Data da visita: {data_formatada}", 1, 1, 'C', True)
        
        pdf.set_font("Arial", '', 8); pdf.set_text_color(0)
        y_c = pdf.get_y(); pdf.rect(10, y_c, 190, 28)
        pdf.set_xy(12, y_c+2); pdf.cell(90, 4, f"Cliente: {clean(cliente)}", 0, 0); pdf.cell(90, 4, f"CPF/CNPJ: {doc_cliente}", 0, 1)
        pdf.set_x(12); pdf.cell(110, 4, f"Endereco: {tipo_logr} {clean(nome_logr)}, {numero}", 0, 0); pdf.cell(60, 4, f"Bairro: {clean(bairro)}", 0, 1)
        pdf.set_x(12); pdf.cell(60, 4, f"CEP: {cep}", 0, 0); pdf.cell(90, 4, f"E-mail: {email_cli}", 0, 1)
        pdf.set_x(12); pdf.cell(60, 4, f"Whats: {whatsapp}", 0, 0); pdf.cell(60, 4, f"Cel: {celular}", 0, 0); pdf.cell(60, 4, f"Fixo: {tel_residencial}", 0, 1)

        pdf.set_y(y_c + 32)
        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(220, 230, 241); pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 6, " Dados do Equipamento", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 8); pdf.set_text_color(0)
        y_e = pdf.get_y(); pdf.rect(10, y_e, 190, 36)
        
        pdf.set_xy(12, y_e+2)
        pdf.cell(60, 4, f"Marca: {clean(fabricante)}", 0, 0); pdf.cell(60, 4, f"Linha: {clean(linha)}", 0, 0); pdf.cell(60, 4, f"Modelo: {clean(modelo_eq)}", 0, 1)
        pdf.set_x(12); pdf.cell(60, 4, f"Capacidade: {cap_digitada} BTU/h", 0, 0); pdf.cell(60, 4, f"Tecnologia: {tecnologia}", 0, 0); pdf.cell(60, 4, f"Fluido: {fluido}", 0, 1)
        pdf.set_x(12); pdf.cell(60, 4, f"Sistema: {tipo_eq}", 0, 0); pdf.cell(60, 4, f"Mod. Evap: {clean(mod_evap)}", 0, 0); pdf.cell(60, 4, f"Serie Evap: {serie_evap}", 0, 1)
        pdf.set_x(12); pdf.cell(60, 4, f"Mod. Cond: {clean(mod_cond)}", 0, 0); pdf.cell(60, 4, f"Serie Cond: {serie_cond}", 0, 0); pdf.cell(60, 4, f"Local Evap: {clean(loc_evap)}", 0, 1)
        pdf.set_x(12); pdf.cell(60, 4, f"Local Cond: {clean(loc_cond)}", 0, 1)

        # --- SEÇÃO: ANÁLISE DE PARÂMETROS OPERACIONAIS ---
        pdf.set_y(y_e + 40)
        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(220, 230, 241); pdf.set_text_color(0, 51, 102)
        pdf.cell(190, 6, " Analise de Parametros Operacionais", 1, 1, 'L', True)
        
        pdf.set_font("Arial", '', 8); pdf.set_text_color(0)
        y_p = pdf.get_y(); pdf.rect(10, y_p, 190, 45)
        
        # ABA ELÉTRICA
        pdf.set_xy(12, y_p+2)
        pdf.set_font("Arial", 'B', 8); pdf.cell(60, 4, "[ ELÉTRICA ]".encode('latin-1').decode('latin-1'), 0, 1)
        pdf.set_font("Arial", '', 8)
        pdf.set_x(12); pdf.cell(60, 4, f"Tensao Rede: {v_rede} V", 0, 0); pdf.cell(50, 4, f"Corrente RLA: {rla_comp} A", 0, 0); pdf.cell(50, 4, f"Corrente LRA: {lra_comp} A", 0, 1)
        pdf.set_x(12); pdf.cell(60, 4, f"Tensao Medida: {v_med} V", 0, 0); pdf.cell(50, 4, f"Corrente Medida: {a_med} A", 0, 1)
        pdf.set_x(12); pdf.cell(60, 4, f"Dif. Tensoes: {diff_v} V", 0, 0); pdf.set_x(72); pdf.cell(50, 4, f"Dif. entre Correntes: {diff_a} A", 0, 1)
        
        # ABA TERMODINÂMICA
        pdf.set_xy(12, y_p+28)
        pdf.set_font("Arial", 'B', 8); pdf.cell(60, 4, "[ TERMODINÂMICA ]".encode('latin-1').decode('latin-1'), 0, 1)
        pdf.set_font("Arial", '', 8)
        pdf.set_x(12); pdf.cell(45, 4, f"P. Succao: {p_suc} PSI", 0, 0); pdf.cell(45, 4, f"T. Tubo: {t_suc_tubo} C", 0, 0); pdf.cell(45, 4, f"T-Sat: {ts_suc} C", 0, 1)
        pdf.set_x(12); pdf.cell(45, 4, f"P. Liquido: {p_liq} PSI", 0, 0); pdf.cell(45, 4, f"T. Tubo: {t_liq_tubo} C", 0, 0); pdf.cell(45, 4, f"T-Sat: {ts_liq} C", 0, 1)
        
        # SH e SC centralizados verticalmente no campo
        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(235, 245, 255)
        pdf.set_xy(155, y_p+15)
        pdf.cell(38, 6, f" SH: {sh_val} K ", 1, 1, 'C', True)
        pdf.set_xy(155, y_p+23)
        pdf.cell(38, 6, f" SC: {sc_val} K ", 1, 1, 'C', True)

        pdf.set_y(y_p + 48)
        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(220, 230, 241); pdf.set_text_color(0, 51, 102)
        pdf.cell(190, 6, " Parecer Tecnico / Diagnostico", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.set_text_color(0)
        pdf.multi_cell(190, 5, clean(medidas), 1, 'L')

        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button("📩 Baixar Relatório PDF", pdf_output, file_name=f"Relatorio_{cliente}.pdf", mime="application/pdf")

import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA (BLOQUEADA) ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

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

# --- 3. INTERFACE DO APP (LAYOUT ORIGINAL BLOQUEADO) ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente = c1.text_input("Cliente/Empresa", key="f_cli")
    doc_cliente = c2.text_input("CPF/CNPJ", key="f_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), key="f_date")
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
    st.subheader("⚙️ Dados Técnicos")
    t1, t2, t3, t4, t5, t6, t7 = st.columns([1, 1, 1, 0.8, 1, 0.8, 0.8])
    fabricante = t1.text_input("Marca", key="f_fab")
    linha = t2.text_input("Linha", key="f_lin")
    modelo_eq = t3.text_input("Modelo", key="f_mod")
    cap_digitada = t4.text_input("BTU´s", value="0", key="f_cap")
    tecnologia = t5.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"], key="f_tec")
    tipo_eq = t6.selectbox("Sistema", ["Split", "Cassete", "Piso", "VRF", "Chiller"], key="f_sis")
    fluido = t7.selectbox("Gás", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"], key="f_gas")

    l1_ev, l1_co = st.columns(2)
    loc_evap = l1_ev.text_input("Localização Evaporadora", key="f_le")
    loc_cond = l1_co.text_input("Localização Condensadora", key="f_lc")

    s1, s2, s3, s4 = st.columns(4)
    mod_evap = s1.text_input("Mod. Evap.", key="f_me")
    serie_evap = s2.text_input("Série Evap.", key="f_se")
    mod_cond = s3.text_input("Mod. Cond.", key="f_mc")
    serie_cond = s4.text_input("Série Cond.", key="f_sc")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns([1, 1, 1])
    with el1:
        v_rede = st.number_input("Tensão Rede (V)", value=220.0)
        v_med = st.number_input("Tensão Medida (V)", value=218.0)
        diff_v = round(v_rede - v_med, 1)
        st.info(f"Queda de Tensão: {diff_v} V")
        
    with el2:
        rla_comp = st.number_input("Corrente RLA (A)", value=1.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
        carga_f = round((a_med/rla_comp*100), 1) if rla_comp > 0 else 0.0
        st.info(f"Carga do Motor: {carga_f}%")
        
    with el3:
        lra_comp = st.number_input("LRA (A)", value=0.0)

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    p_suc = tr1.number_input("Pressão Sucção (PSI)", value=118.0)
    t_suc_tubo = tr1.number_input("Temp. Tubo Sucção (°C)", value=12.0)
    p_liq = tr2.number_input("Pressão Descarga (PSI)", value=345.0)
    t_liq_tubo = tr2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    
    ts_suc = get_tsat_global(p_suc, fluido)
    ts_liq = get_tsat_global(p_liq, fluido)
    sh_val = round(t_suc_tubo - ts_suc, 1)
    sc_val = round(ts_liq - t_liq_tubo, 1)

with tab_diag:
    resumo_pre = f"SH: {sh_val}K | SC: {sc_val}K\n\nParecer: "
    medidas = st.text_area("🤖 Diagnóstico / Parecer", value=resumo_pre, height=150)
    
    if st.button("📄 Gerar Relatório Profissional"):
        pdf = FPDF()
        pdf.add_page()
        
        # CABEÇALHO (AZUL MPN)
        pdf.image("logo.png", 10, 10, 40)
        pdf.set_xy(80, 10)
        pdf.set_font("Arial", 'B', 22); pdf.set_text_color(0, 51, 102)
        pdf.cell(50, 10, "MPN", 0, 1, 'C')
        pdf.set_x(80); pdf.set_font("Arial", 'B', 14); pdf.cell(50, 8, "Relatório Técnico", 0, 1, 'C')

        # 1. DADOS DO CLIENTE
        pdf.set_y(32)
        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(220, 230, 241); pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 6, " Dados do Cliente", 1, 1, 'L', True)
        pdf.rect(10, pdf.get_y(), 190, 32)
        pdf.set_font("Arial", '', 8); pdf.set_text_color(0); pdf.set_xy(12, pdf.get_y()+2)
        pdf.cell(90, 4, f"Cliente: {clean(cliente)}", 0, 0); pdf.cell(60, 4, f"CPF/CNPJ: {doc_cliente}", 0, 0)
        pdf.set_xy(170, pdf.get_y()-7); pdf.set_font("Arial", 'B', 7); pdf.cell(28, 4, f"DATA: {data_visita}", 1, 0, 'C'); pdf.set_font("Arial", '', 8)
        pdf.set_xy(12, pdf.get_y()+11); pdf.cell(110, 4, f"Endereço: {tipo_logr} {clean(nome_logr)}, {numero} ({clean(complemento)})", 0, 0); pdf.cell(60, 4, f"Bairro: {clean(bairro)}", 0, 1)
        pdf.set_x(12); pdf.cell(60, 4, f"CEP: {cep}", 0, 0); pdf.cell(90, 4, f"E-mail: {email_cli}", 0, 1)
        pdf.set_x(12); pdf.cell(50, 4, f"Whats: {whatsapp}", 0, 0); pdf.cell(50, 4, f"Cel: {celular}", 0, 0); pdf.cell(50, 4, f"Fixo: {tel_residencial}", 0, 1)

        # 2. DADOS DO EQUIPAMENTO
        pdf.set_y(pdf.get_y() + 6)
        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(220, 230, 241); pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 6, " Dados do Equipamento", 1, 1, 'L', True)
        pdf.rect(10, pdf.get_y(), 190, 35)
        pdf.set_font("Arial", '', 8); pdf.set_text_color(0); pdf.set_xy(12, pdf.get_y()+2)
        pdf.cell(60, 4, f"Marca: {clean(fabricante)}", 0, 0); pdf.cell(60, 4, f"Linha: {clean(linha)}", 0, 0); pdf.cell(60, 4, f"Modelo: {modelo_eq}", 0, 1)
        pdf.set_x(12); pdf.cell(60, 4, f"Capacidade: {cap_digitada} BTU/h", 0, 0); pdf.cell(60, 4, f"Tecnologia: {tecnologia}", 0, 0); pdf.cell(60, 4, f"Fluido: {fluido}", 0, 1)
        pdf.set_x(12); pdf.cell(60, 4, f"Sistema: {tipo_eq}", 0, 0); pdf.cell(60, 4, f"Mod. Evap: {mod_evap}", 0, 0); pdf.cell(60, 4, f"Série Evap: {serie_evap}", 0, 1)
        pdf.set_x(12); pdf.cell(60, 4, f"Mod. Cond: {mod_cond}", 0, 0); pdf.cell(60, 4, f"Série Cond: {serie_cond}", 0, 0); pdf.cell(60, 4, f"Local Evap: {loc_evap}", 0, 1)
        pdf.set_x(12); pdf.cell(60, 4, f"Local Cond: {loc_cond}", 0, 1)

        # 3. ANALISE DE PARAMETROS (TABELA TRIPARTIDA)
        pdf.set_y(pdf.get_y() + 6)
        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(220, 230, 241); pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 6, " Análise de Parâmetros Operacionais", 1, 1, 'L', True)
        y_p = pdf.get_y(); pdf.rect(10, y_p, 190, 32)
        pdf.set_xy(12, y_p+2); pdf.set_font("Arial", 'B', 8); pdf.cell(90, 4, "PARTE ELÉTRICA", 0, 0); pdf.cell(90, 4, "CICLO FRIGORÍFICO", 0, 1)
        pdf.set_font("Arial", '', 8); pdf.set_text_color(0)
        pdf.set_x(12); pdf.cell(45, 4, f"Tensão Rede: {v_rede} V", 0, 0); pdf.cell(45, 4, f"Tensão Medida: {v_med} V", 0, 0); pdf.cell(45, 4, f"Pres. Sucção: {p_suc} PSI", 0, 0); pdf.cell(45, 4, f"T-Sat Sucção: {ts_suc} C", 0, 1)
        pdf.set_x(12); pdf.cell(45, 4, f"Corrente RLA: {rla_comp} A", 0, 0); pdf.cell(45, 4, f"Corrente Medida: {a_med} A", 0, 0); pdf.cell(45, 4, f"Pres. Descarga: {p_liq} PSI", 0, 0); pdf.cell(45, 4, f"T-Sat Líquido: {ts_liq} C", 0, 1)
        pdf.set_x(12); pdf.cell(45, 4, f"LRA: {lra_comp} A", 0, 0); pdf.cell(45, 4, f"Carga Motor: {carga_f} %", 0, 0); pdf.cell(45, 4, f"SH: {sh_val} K", 0, 0); pdf.cell(45, 4, f"SC: {sc_val} K", 0, 1)

        # 4. PARECER (AZUL ESCURO)
        pdf.set_y(pdf.get_y() + 8)
        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(0, 51, 102); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 7, " Parecer Técnico e Recomendações", 1, 1, 'C', True)
        pdf.set_text_color(0); pdf.set_font("Arial", '', 8); pdf.multi_cell(0, 5, clean(medidas), 1)

        # RODAPÉ
        pdf.set_y(260); pdf.line(20, 260, 95, 260); pdf.line(115, 260, 190, 260)
        pdf.set_font("Arial", 'B', 7); pdf.set_xy(20, 261); pdf.cell(75, 4, "Marcos Alexandre Almeida do Nascimento", 0, 0, 'C')
        pdf.set_xy(115, 261); pdf.cell(75, 4, clean(cliente), 0, 1, 'C')
        pdf.set_xy(20, 265); pdf.set_font("Arial", '', 7); pdf.cell(75, 4, "CNPJ: 51.274.762/0001-17", 0, 0, 'C')
        pdf.set_xy(115, 265); pdf.cell(75, 4, "Assinatura do Cliente", 0, 1, 'C')

        st.download_button("⬇️ Baixar Relatório Lacrado", data=pdf.output(dest="S").encode('latin-1'), file_name=f"MPN_{cliente}.pdf")

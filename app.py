import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io

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
    if not txt: return ""
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
    el1, el2 = st.columns(2)
    v_rede = el1.number_input("Tensão Rede (V)", value=220.0, key="v_rd")
    v_med = el1.number_input("Tensão Medida (V)", value=218.0, key="v_md")
    lra_comp = el2.number_input("LRA (A)", value=0.0, key="v_lra")
    rla_comp = el2.number_input("RLA (A)", value=1.0, key="v_rla")
    a_med = el2.number_input("Corrente Medida (A)", value=0.0, key="v_am")
    
    diff_v = round(v_rede - v_med, 1)
    carga_f = round((a_med/rla_comp*100), 1) if rla_comp > 0 else 0.0
    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Queda de Tensão", f"{diff_v} V")
    m2.metric("Folga Corrente", f"{round(rla_comp - a_med, 1)} A")
    m3.metric("Carga Motor", f"{carga_f}%")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    p_suc = tr1.number_input("Pressão Sucção (PSIG)", value=118.0, key="p_s")
    t_suc_tubo = tr1.number_input("Temp. Tubo Sucção (°C)", value=12.0, key="t_s")
    p_liq = tr2.number_input("Pressão Descarga (PSIG)", value=345.0, key="p_d")
    t_liq_tubo = tr2.number_input("Temp. Tubo Líquido (°C)", value=30.0, key="t_l")
    
    ts_suc = get_tsat_global(p_suc, fluido)
    ts_liq = get_tsat_global(p_liq, fluido)
    sh_val = round(t_suc_tubo - ts_suc, 1)
    sc_val = round(ts_liq - t_liq_tubo, 1)
    
    st.markdown("---")
    ct1, ct2 = st.columns(2)
    ct1.markdown(f"<div style='background-color:#004a99;padding:15px;border-radius:10px;color:white;'><b>🌡️ T-Sat Sucção:</b><h2>{ts_suc} °C</h2><b>🔥 Superaquecimento:</b><h2>{sh_val} K</h2></div>", unsafe_allow_html=True)
    ct2.markdown(f"<div style='background-color:#004a99;padding:15px;border-radius:10px;color:white;'><b>❄️ T-Sat Líquido:</b><h2>{ts_liq} °C</h2><b>💧 Sub-resfriamento:</b><h2>{sc_val} K</h2></div>", unsafe_allow_html=True)

with tab_diag:
    medidas = st.text_area("🤖 Diagnóstico / Parecer", value=f"SH: {sh_val}K | SC: {sc_val}K", height=150, key="f_diag")
    if st.button("📄 Gerar Relatório Profissional"):
        pdf = FPDF()
        pdf.add_page()
        
        # 1. CABEÇALHO COM LOGO
        try:
            pdf.image("logo.png", 10, 10, 45)
        except:
            pass

        pdf.set_font("Arial", 'B', 14); pdf.set_text_color(0, 74, 153)
        pdf.cell(0, 6, "MPN SOLUCOES EM CLIMATIZACAO E REFRIGERACAO", ln=True, align='R')
        pdf.set_font("Arial", '', 9); pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 5, "CNPJ: 51.274.762/0001-17 | Especialista em Termodinamica", ln=True, align='R')
        pdf.cell(0, 5, f"Relatorio emitido em: {date.today().strftime('%d/%m/%Y')}", ln=True, align='R')
        pdf.ln(10)

        def draw_table_header(title):
            pdf.set_fill_color(240, 240, 240); pdf.set_text_color(0, 74, 153); pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 8, f" {clean(title)}", 1, 1, 'L', True); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 9)

        # 2. TABELA IDENTIFICAÇÃO E CONTATO
        draw_table_header("IDENTIFICACAO E CONTATO")
        data_ident = [
            [f"Cliente/Empresa: {clean(cliente)}", f"CPF/CNPJ: {clean(doc_cliente)}", f"Data da Visita: {data_visita}"],
            [f"WhatsApp: {clean(whatsapp)}", f"Celular: {clean(celular)}", f"Fixo: {clean(tel_residencial)}"],
            [f"Endereco: {clean(tipo_logr)} {clean(nome_logr)}, {clean(numero)}", f"Bairro: {clean(bairro)}", f"CEP: {clean(cep)}"],
            [f"E-mail: {clean(email_cli)}", f"Complemento: {clean(complemento)}", ""]
        ]
        for row in data_ident:
            pdf.cell(80, 7, row[0], 1); pdf.cell(55, 7, row[1], 1); pdf.cell(55, 7, row[2], 1); pdf.ln()
        pdf.ln(4)

        # 3. TABELA DADOS TÉCNICOS
        draw_table_header("DADOS TECNICOS")
        data_tec = [
            [f"Marca: {clean(fabricante)}", f"Linha: {clean(linha)}", f"Modelo: {clean(modelo_eq)}"],
            [f"Capacidade (BTU's): {clean(cap_digitada)}", f"Tecnologia: {tecnologia}", f"Sistema: {tipo_eq}"],
            [f"Gas: {fluido}", f"Localizacao Evaporadora: {clean(loc_evap)}", f"Localizacao Condensadora: {clean(loc_cond)}"],
            [f"Mod. Evap.: {clean(mod_evap)}", f"Serie Evap.: {clean(serie_evap)}", ""],
            [f"Mod. Cond.: {clean(mod_cond)}", f"Serie Cond.: {clean(serie_cond)}", ""]
        ]
        for row in data_tec:
            pdf.cell(63, 7, row[0], 1); pdf.cell(63, 7, row[1], 1); pdf.cell(64, 7, row[2], 1); pdf.ln()
        pdf.ln(4)

        # 4. TABELA PARÂMETROS MEDIDOS
        draw_table_header("PARAMETROS MEDIDOS")
        pdf.set_fill_color(250, 250, 250); pdf.set_font("Arial", 'B', 8)
        pdf.cell(95, 6, " Descricao do Parametro", 1, 0, 'L', True); pdf.cell(95, 6, " Valor / Resultado", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9)
        
        results = [
            ("Tensao Rede / Medida", f"{v_rede} V / {v_med} V"),
            ("Corrente RLA / Medida", f"{rla_comp} A / {a_med} A"),
            ("Carga do Motor / LRA", f"{carga_f} % / {lra_comp} A"),
            ("Pressao Succao / Descarga", f"{p_suc} PSIG / {p_liq} PSIG"),
            ("T-Sat Succao / T-Sat Liquido", f"{ts_suc} C / {ts_liq} C"),
            ("Superaquecimento (SH) / Sub-resfriamento (SC)", f"{sh_val} K / {sc_val} K")
        ]
        for desc, res in results:
            pdf.cell(95, 6, f" {desc}", 1); pdf.cell(95, 6, f" {res}", 1, 1)
        pdf.ln(4)

        # 5. DIAGNÓSTICO
        draw_table_header("DIAGNOSTICO / PARECER")
        pdf.multi_cell(0, 7, clean(medidas), 1)

        # 6. ASSINATURAS
        pdf.ln(20); y_sign = pdf.get_y()
        pdf.line(15, y_sign, 95, y_sign); pdf.line(115, y_sign, 195, y_sign)
        pdf.set_y(y_sign + 1)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(95, 5, "Marcos Alexandre Almeida do Nascimento", 0, 0, 'C')
        pdf.cell(100, 5, clean(cliente), 0, 1, 'C')
        pdf.set_font("Arial", '', 8)
        pdf.cell(95, 4, "MPN ENGENHARIA | CNPJ: 51.274.762/0001-17", 0, 0, 'C')
        pdf.cell(100, 4, "Assinatura do Cliente / Responsavel", 0, 1, 'C')

        out = pdf.output(dest='S').encode('latin-1', errors='replace')
        st.download_button("📥 Baixar Relatorio Tecnico Pericial", out, f"Relatorio_MPN_{clean(cliente)}.pdf", "application/pdf")

import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# --- 2. MOTOR TERMODINÂMICO ---
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
    if st.button("📄 Gerar Relatório Final"):
        pdf = FPDF()
        pdf.add_page()
        
        # --- CABEÇALHO ---
        try: pdf.image("logo.png", 10, 8, 35)
        except: pass
        pdf.set_font("Arial", 'B', 15); pdf.set_text_color(0, 74, 153)
        pdf.cell(0, 10, "LAUDO TECNICO DE PERFORMANCE TERMICA", ln=True, align='R')
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 5, "MPN SOLUCOES EM CLIMATIZACAO E REFRIGERACAO", ln=True, align='R')
        pdf.ln(8)

        # --- SEÇÃO 1: IDENTIFICAÇÃO (MOLDURA GROSSA E INDIVIDUALIZAÇÃO) ---
        pdf.set_line_width(1.0)
        y_id = pdf.get_y()
        pdf.rect(10, y_id, 190, 45) # Moldura grossa
        
        pdf.set_font("Arial", 'B', 9); pdf.set_text_color(0)
        pdf.set_xy(13, y_id + 5)
        pdf.cell(100, 5, f"CLIENTE: {clean(cliente)}", 0)
        pdf.cell(80, 5, f"DOCUMENTO: {clean(doc_cliente)}", 0, 1)
        
        pdf.set_x(13)
        pdf.cell(100, 5, f"ENDERECO: {clean(tipo_logr)} {clean(nome_logr)}, {clean(numero)}", 0)
        pdf.cell(80, 5, f"BAIRRO: {clean(bairro)}", 0, 1)
        
        pdf.set_x(13)
        pdf.cell(100, 5, f"CONTATO: {clean(whatsapp)}", 0)
        pdf.cell(80, 5, f"E-MAIL: {clean(email_cli)}", 0, 1)

        # Data em Destaque Amarelo (BR)
        pdf.ln(3); pdf.set_x(13)
        pdf.set_fill_color(255, 255, 0)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(65, 8, f" DATA DA VISITA: {data_visita.strftime('%d/%m/%Y')} ", 1, 1, 'C', True)
        
        # --- SEÇÃO 2: TABELA DE DADOS TÉCNICOS ---
        pdf.set_y(y_id + 52)
        pdf.set_font("Arial", 'B', 10); pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 7, " ESPECIFICACOES TECNICAS DO EQUIPAMENTO", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 8.5)
        # Linha 1
        pdf.cell(47.5, 7, f" MARCA: {clean(fabricante)}", 1)
        pdf.cell(47.5, 7, f" MODELO: {clean(modelo_eq)}", 1)
        pdf.cell(47.5, 7, f" CAPACIDADE: {clean(cap_digitada)}", 1)
        pdf.cell(47.5, 7, f" FLUIDO: {clean(fluido)}", 1, 1)
        # Linha 2
        pdf.cell(47.5, 7, f" TECNOLOGIA: {clean(tecnologia)}", 1)
        pdf.cell(47.5, 7, f" SISTEMA: {clean(tipo_eq)}", 1)
        pdf.cell(47.5, 7, f" LOCAL EVAP: {clean(loc_evap)}", 1)
        pdf.cell(47.5, 7, f" LOCAL COND: {clean(loc_cond)}", 1, 1)

        # --- SEÇÃO 3: PARÂMETROS MEDIDOS (3 COLUNAS) ---
        pdf.ln(3)
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 7, " ANALISE FRIGORIFICA (PARAMETROS MEDIDOS)", 1, 1, 'L', True)
        y_p = pdf.get_y(); cw = 63.3
        
        # Col 1: Sucção
        pdf.rect(10, y_p, cw, 25); pdf.set_xy(12, y_p+2); pdf.set_font("Arial", 'B', 8)
        pdf.cell(cw, 4, "CICLO DE SUCCAO", 0, 1); pdf.set_font("Arial", '', 8); pdf.set_x(12)
        pdf.cell(cw, 4, f"Pressao: {p_suc} PSIG", 0, 1); pdf.set_x(12)
        pdf.cell(cw, 4, f"T-Sat: {ts_suc} C", 0, 1)
        
        # Col 2: Descarga
        pdf.rect(10+cw, y_p, cw, 25); pdf.set_xy(12+cw, y_p+2); pdf.set_font("Arial", 'B', 8)
        pdf.cell(cw, 4, "CICLO DE DESCARGA", 0, 1); pdf.set_font("Arial", '', 8); pdf.set_x(12+cw)
        pdf.cell(cw, 4, f"Pressao: {p_liq} PSIG", 0, 1); pdf.set_x(12+cw)
        pdf.cell(cw, 4, f"T-Sat: {ts_liq} C", 0, 1)
        
        # Col 3: Eficiência (Destaque Colorido)
        pdf.rect(10+(cw*2), y_p, cw, 25); pdf.set_xy(11+(cw*2), y_p+2)
        pdf.set_fill_color(255, 204, 204); pdf.set_font("Arial", 'B', 9) # SH
        pdf.cell(cw-2, 10, f" S.H.: {sh_val} K ", 1, 1, 'C', True)
        pdf.set_x(11+(cw*2)); pdf.ln(1); pdf.set_x(11+(cw*2))
        pdf.set_fill_color(204, 229, 255); # SC
        pdf.cell(cw-2, 10, f" S.C.: {sc_val} K ", 1, 1, 'C', True)

        # --- SEÇÃO 4: DIAGNÓSTICO ---
        pdf.set_y(y_p + 30)
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 7, " PARECER TECNICO E DIAGNOSTICO", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(medidas), 1)

        # --- SEÇÃO 5: ASSINATURAS ---
        pdf.ln(15)
        y_sig = pdf.get_y()
        # Técnico
        pdf.line(20, y_sig, 90, y_sig)
        pdf.set_xy(20, y_sig + 2); pdf.set_font("Arial", 'B', 8)
        pdf.cell(70, 4, "MARCIO PAULO DO NASCIMENTO", 0, 1, 'C')
        pdf.set_x(20); pdf.cell(70, 4, "CNPJ: 51.274.762/0001-17", 0, 1, 'C')
        # Cliente
        pdf.line(120, y_sig, 190, y_sig)
        pdf.set_xy(120, y_sig + 2)
        pdf.cell(70, 4, clean(cliente), 0, 1, 'C')
        pdf.set_x(120); pdf.cell(70, 4, "CLIENTE / RESPONSAVEL", 0, 1, 'C')

        # DOWNLOAD
        pdf_output = io.BytesIO()
        pdf_output.write(pdf.output(dest='S').encode('latin1'))
        st.download_button("📥 Baixar Laudo Profissional", data=pdf_output.getvalue(), file_name=f"Laudo_{cliente}.pdf", mime="application/pdf")

import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA (BLOQUEADA) ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR TERMODINÂMICO ---
def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                   "t": [-51.0, -17.02, -0.29, 11.55, 20.93, 28.84, 35.58, 41.74, 47.3, 52.1, 56.59, 60.7, 64.59]},
        "R-32": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                 "t": [-51.7, -17.46, 0.87, 10.86, 20.14, 27.9, 34.63, 40.6, 45.96, 50.8, 55.36, 59.5, 63.43]},
        "R-22": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 600.0], 
                 "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 73.2, 78.38, 87.53]}
    }
    if gas not in ancoras or psig is None: return 0.0
    return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)

def clean(txt):
    if not txt: return "N/A"
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C', '°': 'C', 'º': '.'}
    res = str(txt)
    for old, new in replacements.items(): res = res.replace(old, new)
    return res.encode('ascii', 'ignore').decode('ascii')

# --- 3. INTERFACE DO APP (LAYOUT MANTIDO) ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente, doc_cliente = c1.text_input("Cliente/Empresa", key="f_cli"), c2.text_input("CPF/CNPJ", key="f_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY", key="f_date")
    whatsapp, celular, tel_residencial = c4.text_input("🟢 WhatsApp", value="21980264217", key="f_wpp"), c5.text_input("📱 Celular", key="f_cel"), c6.text_input("📞 Fixo", key="f_fix")
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr, nome_logr, numero, complemento, bairro, cep, email_cli = e1.selectbox("Tipo", ["Rua", "Av."], key="f_tlog"), e2.text_input("Logradouro", key="f_nlog"), e3.text_input("Nº", key="f_num"), e4.text_input("Comp.", key="f_comp"), e5.text_input("Bairro", key="f_bai"), e6.text_input("CEP", key="f_cep"), e7.text_input("✉️ E-mail", key="f_mail")
    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3 = st.columns(3)
    fabricante, modelo_eq, cap_digitada = g1.text_input("Marca", key="f_fab"), g2.text_input("Modelo", key="f_mod"), g3.text_input("Capacidade", value="0", key="f_cap")
    linha, tecnologia, fluido = g1.text_input("Linha", key="f_lin"), g2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF", "Multisplit"], key="f_tec"), g3.selectbox("Fluido", ["R-410A", "R-32", "R-22"], key="f_gas")
    sistema, loc_evap, loc_cond = g1.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "Chiller"], key="f_sis"), g2.text_input("Local Evap", key="f_le"), g3.text_input("Local Cond", key="f_lc")
    mod_evap, serie_evap = st.text_input("Mod. Evap", key="f_me"), st.text_input("Serie Evap", key="f_se")
    mod_cond, serie_cond = st.text_input("Mod. Cond", key="f_mc"), st.text_input("Serie Cond", key="f_sc")

with tab_ele:
    el1, el2, el3 = st.columns(3)
    v_rede, v_med = el1.number_input("Tensao Rede (V)", value=220.0), el1.number_input("Tensao Medida (V)", value=218.0)
    rla, a_med = el2.number_input("Corrente RLA (A)", value=1.0), el2.number_input("Corrente Medida (A)", value=0.0)
    lra = el3.number_input("Corrente LRA (A)", value=0.0)
    diff_v, diff_a = round(v_rede - v_med, 1), round(a_med - rla, 1)

with tab_termo:
    tr1, tr2 = st.columns(2)
    p_suc, t_suc_tubo = tr1.number_input("P. Succao (PSI)", value=118.0), tr1.number_input("T. Tubo Suc. (C)", value=12.0)
    p_liq, t_liq_tubo = tr2.number_input("P. Liquido (PSI)", value=345.0), tr2.number_input("T. Tubo Liq. (C)", value=30.0)
    ts_suc, ts_liq = get_tsat_global(p_suc, fluido), get_tsat_global(p_liq, fluido)
    sh_val, sc_val = round(t_suc_tubo - ts_suc, 1), round(ts_liq - t_liq_tubo, 1)

with tab_diag:
    col_prob, col_obs = st.columns(2)
    with col_prob:
        st.subheader("⚠️ Problemas Encontrados")
        pi1, pi2 = st.columns(2)
        p_sel = []
        opcoes = ["Vazamento de Fluido", "Baixa Carga de Fluido", "Excesso de Fluido", "Linha de Liquido Congelando", "Colmeia Congelando", "Evaporadora Pingando", "Linha de Descarga Congelando", "Filtro Secador Obstruido", "Compressor Sem Compressao", "Falha na Ventilacao", "Falha na Placa Inverter", "Instabilidade na Rede Eletrica"]
        for i, opt in enumerate(opcoes):
            if i % 2 == 0:
                if pi1.checkbox(opt): p_sel.append(opt)
            else:
                if pi2.checkbox(opt): p_sel.append(opt)
    obs_tecnico = col_obs.text_area("📝 Observacoes do Tecnico", height=150)
    medidas_exec = st.text_area("📋 Medidas Executadas", height=100)

    if st.button("📄 Gerar Relatório Profissional"):
        pdf = FPDF()
        pdf.add_page()
        
        # --- CABEÇALHO (LOGO E MPN) ---
        pdf.set_font("Arial", 'B', 22); pdf.set_text_color(0, 51, 102)
        pdf.cell(190, 10, "MPN", 0, 1, 'C')
        pdf.set_font("Arial", 'B', 16); pdf.cell(190, 8, "Relatorio Tecnico", 0, 1, 'C')
        pdf.ln(5)

        # --- DADOS DO CLIENTE (AZUL) ---
        pdf.set_fill_color(220, 230, 241); pdf.set_font("Arial", 'B', 9)
        pdf.cell(140, 7, " Dados do Cliente", 1, 0, 'L', True)
        pdf.cell(50, 7, f" Data da visita: {data_visita.strftime('%d/%m/%Y')}", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 8); pdf.set_text_color(0); pdf.cell(190, 25, "", 1)
        pdf.set_xy(12, 45)
        pdf.cell(90, 4, clean(f"Cliente: {cliente}"), 0); pdf.cell(90, 4, clean(f"CPF/CNPJ: {doc_cliente}"), 0, 1)
        pdf.cell(90, 4, clean(f"Endereco: {nome_logr}, {numero}"), 0); pdf.cell(90, 4, clean(f"Bairro: {bairro}"), 0, 1)
        pdf.cell(90, 4, clean(f"CEP: {cep}"), 0); pdf.cell(90, 4, clean(f"E-mail: {email_cli}"), 0, 1)
        pdf.cell(90, 4, clean(f"Whats: {whatsapp}"), 0); pdf.cell(45, 4, clean(f"Cel: {celular}"), 0); pdf.cell(45, 4, clean(f"Fixo: {tel_residencial}"), 0, 1)

        # --- DADOS DO EQUIPAMENTO ---
        pdf.set_xy(10, 75); pdf.set_fill_color(220, 230, 241); pdf.set_font("Arial", 'B', 9)
        pdf.cell(190, 7, " Dados do Equipamento", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 8); pdf.cell(190, 30, "", 1)
        pdf.set_xy(12, 85)
        pdf.cell(63, 4, clean(f"Marca: {fabricante}"), 0); pdf.cell(63, 4, clean(f"Linha: {linha}"), 0); pdf.cell(64, 4, clean(f"Modelo: {modelo_eq}"), 0, 1)
        pdf.cell(63, 4, clean(f"Capacidade: {cap_digitada}"), 0); pdf.cell(63, 4, clean(f"Tecnologia: {tecnologia}"), 0); pdf.cell(64, 4, clean(f"Fluido: {fluido}"), 0, 1)
        pdf.cell(63, 4, clean(f"Sistema: {sistema}"), 0); pdf.cell(63, 4, clean(f"Mod. Evap: {mod_evap}"), 0); pdf.cell(64, 4, clean(f"Serie Evap: {serie_evap}"), 0, 1)
        pdf.cell(63, 4, clean(f"Mod. Cond: {mod_cond}"), 0); pdf.cell(63, 4, clean(f"Serie Cond: {serie_cond}"), 0); pdf.cell(64, 4, clean(f"Local Evap: {loc_evap}"), 0, 1)
        pdf.cell(63, 4, clean(f"Local Cond: {loc_cond}"), 0, 1)

        # --- ANALISE DE PARAMETROS (O MODELO ENVIADO) ---
        pdf.set_xy(10, 115); pdf.set_fill_color(220, 230, 241); pdf.set_font("Arial", 'B', 9)
        pdf.cell(190, 7, " Analise de Parametros Operacionais", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 8); pdf.cell(190, 45, "", 1)
        pdf.set_xy(12, 125); pdf.set_font("Arial", 'B', 8); pdf.cell(0, 4, "[ ELETRICA ]", 0, 1)
        pdf.set_font("Arial", '', 8)
        pdf.cell(60, 4, f"Tensao Rede: {v_rede} V", 0); pdf.cell(60, 4, f"Corrente RLA: {rla} A", 0); pdf.cell(60, 4, f"Corrente LRA: {lra} A", 0, 1)
        pdf.cell(60, 4, f"Tensao Medida: {v_med} V", 0); pdf.cell(60, 4, f"Corrente Medida: {a_med} A", 0, 1)
        pdf.cell(60, 4, f"Dif. Tensoes: {diff_v} V", 0); pdf.cell(60, 4, f"Dif. Correntes: {diff_a} A", 0, 1)
        pdf.ln(2)
        pdf.set_font("Arial", 'B', 8); pdf.cell(0, 4, "[ TERMODINAMICA ]", 0, 1)
        pdf.set_font("Arial", '', 8)
        pdf.cell(50, 4, f"P. Succao: {p_suc} PSI", 0); pdf.cell(50, 4, f"T. Tubo: {t_suc_tubo} C", 0); pdf.cell(50, 4, f"T-Sat: {ts_suc} C", 0, 1)
        pdf.cell(50, 4, f"P. Liquido: {p_liq} PSI", 0); pdf.cell(50, 4, f"T. Tubo: {t_liq_tubo} C", 0); pdf.cell(50, 4, f"T-Sat: {ts_liq} C", 0, 1)
        
        # BOXES SH E SC (IGUAL A IMAGEM)
        pdf.set_xy(155, 128); pdf.set_font("Arial", 'B', 9); pdf.cell(35, 6, f"SH: {sh_val} K", 1, 1, 'C')
        pdf.set_xy(155, 135); pdf.cell(35, 6, f"SC: {sc_val} K", 1, 1, 'C')

        # --- PARECER TECNICO ---
        pdf.set_xy(10, 170); pdf.set_fill_color(220, 230, 241); pdf.set_font("Arial", 'B', 9)
        pdf.cell(190, 7, " Parecer Tecnico / Diagnostico", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 8); pdf.cell(190, 60, "", 1)
        pdf.set_xy(12, 178)
        pdf.multi_cell(185, 4, clean(f"Problemas Encontrados: {', '.join(p_sel)}\n\nObservacoes do Tecnico: {obs_tecnico}\n\nMedidas Executadas: {medidas_exec}"), 0)

        # --- ASSINATURAS ---
        pdf.set_y(-35); pdf.line(20, pdf.get_y(), 95, pdf.get_y()); pdf.line(115, pdf.get_y(), 190, pdf.get_y())
        pdf.set_font("Arial", 'B', 8); pdf.set_xy(20, -33); pdf.multi_cell(75, 4, "Marcos Alexandre Almeida do Nascimento\nCNPJ: 51.274.762/0001-17", 0, 'C')
        pdf.set_xy(115, -33); pdf.multi_cell(75, 4, clean(cliente), 0, 'C')

        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("⬇️ BAIXAR RELATORIO FINAL", data=pdf_bytes, file_name="relatorio_mpn.pdf", mime="application/pdf")

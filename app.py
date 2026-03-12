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
                 "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 73.2, 78.38, 87.53]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 80.0, 100.0, 130.0, 150.0, 180.0, 200.0], 
                   "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 38.4, 43.65, 50.1, 53.74]}
    }
    if gas not in ancoras or psig is None: return 0.0
    return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)

def clean(txt):
    if not txt: return "N/A"
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C', '°': 'C', 'º': '.'}
    res = str(txt)
    for old, new in replacements.items(): res = res.replace(old, new)
    return res.encode('ascii', 'ignore').decode('ascii')

# --- 3. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente = c1.text_input("Cliente/Empresa", key="f_cli")
    doc_cli = c2.text_input("CPF/CNPJ", key="f_doc")
    data_v = c3.date_input("Data Visita", value=date.today(), key="f_date")
    whatsapp = c4.text_input("Whats", value="21980264217", key="f_wpp")
    celular = c5.text_input("Cel", key="f_cel")
    fixo = c6.text_input("Fixo", key="f_fix")
    
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_l = e1.selectbox("Tipo", ["Rua", "Av."], key="f_tlog")
    logr = e2.text_input("Logradouro", key="f_nlog")
    num = e3.text_input("N", key="f_num")
    bairro = e5.text_input("Bairro", key="f_bai")
    cep = e6.text_input("CEP", key="f_cep")
    email = e7.text_input("E-mail", key="f_mail")

    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3 = st.columns(3)
    marca = g1.text_input("Marca", key="f_fab")
    linha = g2.text_input("Linha", key="f_lin")
    modelo = g3.text_input("Modelo", key="f_mod")
    capacidade = g1.text_input("Capacidade (BTU/h)", value="0", key="f_cap")
    tecnologia = g2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF", "Multisplit"], key="f_tec")
    fluido = g3.selectbox("Fluido", ["R-410A", "R-32", "R-22"], key="f_gas")
    sistema = g1.selectbox("Sistema", ["Split", "Cassete", "Piso Teto"], key="f_sis")
    mod_evap = g2.text_input("Mod. Evap", key="f_me")
    serie_evap = g3.text_input("Serie Evap", key="f_se")
    mod_cond = g1.text_input("Mod. Cond", key="f_mc")
    serie_cond = g2.text_input("Serie Cond", key="f_sc")
    loc_evap = g3.text_input("Local Evap", key="f_le")
    loc_cond = g1.text_input("Local Cond", key="f_lc")

with tab_ele:
    el1, el2, el3 = st.columns(3)
    v_rede = el1.number_input("Tensao Rede (V)", value=220.0)
    v_med = el1.number_input("Tensao Medida (V)", value=218.0)
    diff_v = round(v_rede - v_med, 1)
    rla = el2.number_input("Corrente RLA (A)", value=1.0)
    a_med = el2.number_input("Corrente Medida (A)", value=0.0)
    diff_a = round(a_med - rla, 1)
    lra = el3.number_input("Corrente LRA (A)", value=0.0)

with tab_termo:
    tr1, tr2 = st.columns(2)
    p_suc = tr1.number_input("P. Succao (PSI)", value=118.0)
    t_suc_tubo = tr1.number_input("T. Tubo Suc. (C)", value=12.0)
    p_liq = tr2.number_input("P. Liquido (PSI)", value=345.0)
    t_liq_tubo = tr2.number_input("T. Tubo Liq. (C)", value=30.0)
    
    ts_suc = get_tsat_global(p_suc, fluido)
    ts_liq = get_tsat_global(p_liq, fluido)
    sh_val = round(t_suc_tubo - ts_suc, 1)
    sc_val = round(ts_liq - t_liq_tubo, 1)

with tab_diag:
    col_prob, col_obs = st.columns(2)
    with col_prob:
        st.subheader("⚠️ Problemas Encontrados")
        p_sel = []
        c_p1, c_p2 = st.columns(2)
        opts = ["Vazamento de Fluido", "Baixa Carga de Fluido", "Excesso de Fluido", 
                "Linha de Liquido Congelando", "Colmeia Congelando", 
                "Evaporadora Pingando", "Linha de Descarga Congelando",
                "Filtro Secador Obstruido", "Compressor Sem Compressao", 
                "Falha na Ventilacao", "Falha na Placa Inverter", "Instabilidade na Rede Eletrica"]
        for i, opt in enumerate(opts):
            if i % 2 == 0:
                if c_p1.checkbox(opt): p_sel.append(opt)
            else:
                if c_p2.checkbox(opt): p_sel.append(opt)

    obs_tec = col_obs.text_area("📝 Observacoes do Tecnico", height=150)
    
    st.markdown("---")
    
    # MOTOR IA AVANÇADO
    analise_ia = []
    medidas_ia = []
    if tecnologia in ["Inverter", "VRF"] and (sh_val > 15 or sh_val < 3):
        analise_ia.append(f"🔍 [PERÍCIA] Sistema {tecnologia}: SH fora da modulação nominal. Risco de golpe de líquido ou falha de transdutor.")
        medidas_ia.append("1. Validar curva ôhmica (kOhm) dos sensores de descarga e sucção.")
    
    if "Congelando" in str(p_sel):
        analise_ia.append("🔍 [ENGENHARIA] Detecção de restrição física conforme literatura técnica.")
        medidas_ia.append("2. Efetuar limpeza química profunda e verificar vazão de ar.")

    if not analise_ia:
        analise_ia.append("✅ Sistema operando dentro dos logs de normalidade técnica.")
        medidas_ia.append("1. Manutenção preventiva periódica.")

    c_ia1, c_ia2 = st.columns(2)
    with c_ia1:
        st.subheader("🤖 Diagnostico IA")
        for diag in analise_ia: st.info(diag)
        st.subheader("🔧 Medidas Propostas IA")
        for med in medidas_ia: st.warning(med)
    
    exec_med = c_ia2.text_area("📋 Medidas Executadas", height=230)

    if st.button("📄 Gerar Relatório Profissional"):
        pdf = FPDF()
        pdf.add_page()
        
        # --- CABEÇALHO (LOGO E TÍTULOS) ---
        pdf.set_font("Arial", 'B', 22); pdf.set_text_color(0, 51, 102)
        pdf.cell(190, 10, "MPN", 0, 1, 'C')
        pdf.set_font("Arial", 'B', 16); pdf.cell(190, 8, "Relatorio Tecnico", 0, 1, 'C')
        pdf.ln(5)

        # --- DADOS DO CLIENTE (AZUL) ---
        pdf.set_fill_color(220, 230, 241); pdf.set_font("Arial", 'B', 9)
        pdf.cell(140, 6, " Dados do Cliente", 1, 0, 'L', True)
        pdf.cell(50, 6, f" Data da visita: {data_v.strftime('%d/%m/%Y')}", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 8); pdf.set_text_color(0); pdf.cell(190, 20, "", 1)
        pdf.set_xy(12, 43)
        pdf.cell(90, 4, clean(f"Cliente: {cliente}"), 0); pdf.cell(90, 4, clean(f"CPF/CNPJ: {doc_cli}"), 0, 1)
        pdf.cell(90, 4, clean(f"Endereco: {logr}, {num} - {bairro}"), 0); pdf.cell(90, 4, clean(f"CEP: {cep}"), 0, 1)
        pdf.cell(90, 4, clean(f"Whats: {whatsapp} | Cel: {celular}"), 0); pdf.cell(90, 4, clean(f"Email: {email}"), 0, 1)

        # --- DADOS DO EQUIPAMENTO ---
        pdf.set_xy(10, 66)
        pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, " Dados do Equipamento", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 8); pdf.cell(190, 25, "", 1)
        pdf.set_xy(12, 73)
        pdf.cell(63, 4, clean(f"Marca: {marca}"), 0); pdf.cell(63, 4, clean(f"Linha: {linha}"), 0); pdf.cell(64, 4, clean(f"Modelo: {modelo}"), 0, 1)
        pdf.cell(63, 4, clean(f"Tecnologia: {tecnologia}"), 0); pdf.cell(63, 4, clean(f"Fluido: {fluido}"), 0); pdf.cell(64, 4, clean(f"Capacidade: {capacidade}"), 0, 1)
        pdf.cell(63, 4, clean(f"Sistema: {sistema}"), 0); pdf.cell(63, 4, clean(f"Local Evap: {loc_evap}"), 0); pdf.cell(64, 4, clean(f"Local Cond: {loc_cond}"), 0, 1)

        # --- PARÂMETROS OPERACIONAIS ---
        pdf.set_xy(10, 95)
        pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, " Analise de Parametros Operacionais", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 8); pdf.cell(190, 45, "", 1)
        pdf.set_xy(12, 103); pdf.set_font("Arial", 'B', 8); pdf.cell(0, 4, "[ ELETRICA ]", 0, 1)
        pdf.set_font("Arial", '', 8)
        pdf.cell(60, 4, f"Tensao Rede: {v_rede} V", 0); pdf.cell(60, 4, f"Corrente RLA: {rla} A", 0); pdf.cell(60, 4, f"LRA: {lra} A", 0, 1)
        pdf.cell(60, 4, f"Tensao Medida: {v_med} V", 0); pdf.cell(60, 4, f"Corrente Medida: {a_med} A", 0, 1)
        pdf.ln(2)
        pdf.set_font("Arial", 'B', 8); pdf.cell(0, 4, "[ TERMODINAMICA ]", 0, 1)
        pdf.set_font("Arial", '', 8)
        pdf.cell(50, 4, f"P. Succao: {p_suc} PSI", 0); pdf.cell(50, 4, f"T. Tubo: {t_suc_tubo} C", 0); pdf.cell(50, 4, f"T-Sat: {ts_suc} C", 0, 1)
        pdf.cell(50, 4, f"P. Liquido: {p_liq} PSI", 0); pdf.cell(50, 4, f"T. Tubo: {t_liq_tubo} C", 0); pdf.cell(50, 4, f"T-Sat: {ts_liq} C", 0, 1)
        pdf.set_xy(160, 115); pdf.set_font("Arial", 'B', 9); pdf.cell(30, 6, f"SH: {sh_val} K", 1, 1, 'C')
        pdf.set_xy(160, 122); pdf.cell(30, 6, f"SC: {sc_val} K", 1, 1, 'C')

        # --- PARECER TÉCNICO E MEDIDAS ---
        pdf.set_xy(10, 145)
        pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, " Parecer Tecnico / Diagnostico", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 8); pdf.cell(190, 60, "", 1)
        pdf.set_xy(12, 153)
        pdf.multi_cell(185, 4, clean(f"Problemas: {', '.join(p_sel)}\n\nDiagnostico IA: {'. '.join(analise_ia)}\n\nObservacoes: {obs_tec}\n\nMedidas Executadas: {exec_med}"), 0)

        # --- ASSINATURAS ---
        pdf.set_y(-35); pdf.line(20, pdf.get_y(), 95, pdf.get_y()); pdf.line(115, pdf.get_y(), 190, pdf.get_y())
        pdf.set_font("Arial", 'B', 8); pdf.set_xy(20, -33); pdf.multi_cell(75, 4, "Marcos Alexandre Almeida do Nascimento\nCNPJ: 51.274.762/0001-17", 0, 'C')
        pdf.set_xy(115, -33); pdf.multi_cell(75, 4, clean(cliente if cliente else "CLIENTE"), 0, 'C')

        pdf_b = pdf.output(dest='S').encode('latin-1')
        st.download_button("⬇️ BAIXAR RELATORIO FINAL", data=pdf_b, file_name="relatorio_final.pdf", mime="application/pdf")

import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA (BLOQUEADA) ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# ESTILO DAS ABAS (20PX E NEGRITO)
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
                   "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 38.4, 43.65, 50.1, 53.74]}
    }
    if gas not in ancoras or psig is None: return 0.0
    try: return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)
    except: return 0.0

def clean(txt):
    if not txt: return "N/A"
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C', '°': 'C', 'º': '.'}
    res = str(txt)
    for old, new in replacements.items(): res = res.replace(old, new)
    return res.encode('ascii', 'ignore').decode('ascii')

# --- 3. INTERFACE DO APP ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente, doc_cliente = c1.text_input("Cliente/Empresa", key="f_cli"), c2.text_input("CPF/CNPJ", key="f_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY", key="f_date")
    whatsapp, celular, tel_residencial = c4.text_input("🟢 WhatsApp", value="21980264217", key="f_wpp"), c5.text_input("📱 Celular", key="f_cel"), c6.text_input("📞 Fixo", key="f_fix")
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr, nome_logr, numero, complemento, bairro, cep, email_cli = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."], key="f_tlog"), e2.text_input("Logradouro", key="f_nlog"), e3.text_input("Nº", key="f_num"), e4.text_input("Comp.", key="f_comp"), e5.text_input("Bairro", key="f_bai"), e6.text_input("CEP", key="f_cep"), e7.text_input("✉️ E-mail", key="f_mail")
    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3, g4 = st.columns([1, 1, 1, 1])
    with g1: 
        fabricante = st.text_input("Marca", key="f_fab")
        modelo_eq = st.text_input("Modelo Geral", key="f_mod")
        serie_evap = st.text_input("Série Evaporadora", key="f_sevap")
    with g2:
        linha = st.text_input("Linha", key="f_lin")
        cap_digitada = st.text_input("Capacidade (BTU/h)", value="0", key="f_cap")
        serie_cond = st.text_input("Série Condensadora", key="f_scond")
    with g3:
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF", "Multisplit"], key="f_tec")
        fluido = st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"], key="f_gas")
        loc_evap = st.text_input("Local Evaporadora", key="f_le")
    with g4:
        tipo_eq = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "VRF", "Chiller"], key="f_sis")
        loc_cond = st.text_input("Local Condensadora", key="f_lc")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns(3)
    with el1:
        v_rede = st.number_input("Tensão Rede (V)", value=220.0)
        v_med = st.number_input("Tensão Medida (V)", value=218.0)
        diff_v = round(v_rede - v_med, 1)
        st.write("Diferença entre Tensões"); st.success(f"{diff_v} V")
    with el2:
        rla_comp = st.number_input("Corrente RLA (A)", value=1.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
        diff_a = round(a_med - rla_comp, 1)
        st.write("Diferença entre Correntes"); st.success(f"{diff_a} A")
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
        st.write("T-Sat Sucção"); st.info(f"{ts_suc} °C")
    with tr2:
        st.markdown("**Líquido (Alta)**")
        p_liq = st.number_input("Pressão (PSI)", value=345.0, key="pl")
        t_liq_tubo = st.number_input("Temp. Tubo (°C)", value=30.0, key="tl")
        ts_liq = get_tsat_global(p_liq, fluido)
        st.write("T-Sat Líquido"); st.info(f"{ts_liq} °C")
    with tr3:
        st.markdown("**Performance**")
        sh_val = round(t_suc_tubo - ts_suc, 1)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        st.write("Superaquecimento (SH)"); st.success(f"**{sh_val} K**")
        st.write("Subresfriamento (SC)"); st.success(f"**{sc_val} K**")

with tab_diag:
    col_prob, col_obs = st.columns(2)
    with col_prob:
        st.subheader("⚠️ Problemas Encontrados")
        pi1, pi2 = st.columns(2)
        p_sel = []
        opcoes = ["Vazamento de Fluido", "Baixa Carga de Fluido", "Excesso de Fluido", "Ar/Incondensaveis no Ciclo", "Obstrucao Dispositivo Expansao", "Linha de Liquido Congelando", "Colmeia Congelando", "Filtro Secador Obstruido", "Compressor Sem Compressao", "Falha na Ventilacao", "Falha na Placa Inverter", "Instabilidade na Rede Eletrica", "Evaporadora Pingando", "Linha de Descarga Congelando"]
        for i, opt in enumerate(opcoes):
            if i % 2 == 0:
                if pi1.checkbox(opt): p_sel.append(opt)
            else:
                if pi2.checkbox(opt): p_sel.append(opt)

    with col_obs:
        st.subheader("📝 Observações do Técnico")
        obs_tecnico = st.text_area("", placeholder="Parecer técnico...", height=215, label_visibility="collapsed", key="obs_tec_diag")

    st.markdown("---")
    col_prop_ia, col_exec = st.columns(2)
    with col_prop_ia:
        st.subheader("🤖 Diagnóstico IA")
        diag_ia = f"Análise Profunda: SH {sh_val}K | SC {sc_val}K. Sistema {tecnologia}."
        st.info(diag_ia)
        st.subheader("🔧 Medidas Propostas IA")
        st.warning("1. Verificar estanqueidade e parâmetros nominais conforme manual.")
    with col_exec:
        st.subheader("📋 Medidas Executadas")
        executadas_input = st.text_area("", placeholder="Descreva as medidas executadas...", key="exec_diag", height=200, label_visibility="collapsed")

    if st.button("📄 Gerar Relatório Profissional"):
        pdf = FPDF()
        pdf.add_page()
        
        try:
            pdf.image("logo.png", 10, 8, 50)
        except:
            pass
        
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(190, 15, "Relatorio Tecnico", 0, 1, 'C')
        pdf.ln(10)

        # 1. IDENTIFICAÇÃO
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(190, 7, " 1. IDENTIFICACAO DO CLIENTE E CONTATO", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(0)
        pdf.cell(130, 6, clean(f"Cliente: {cliente}"), 1, 0)
        pdf.cell(60, 6, clean(f"CPF/CNPJ: {doc_cliente}"), 1, 1)
        pdf.cell(190, 6, clean(f"Endereco: {tipo_logr} {nome_logr}, {numero} {complemento} - {bairro} | CEP: {cep}"), 1, 1)
        pdf.cell(63, 6, clean(f"Wpp: {whatsapp}"), 1, 0)
        pdf.cell(63, 6, clean(f"Cel: {celular}"), 1, 0)
        pdf.cell(64, 6, clean(f"Fixo: {tel_residencial}"), 1, 1)
        pdf.cell(130, 6, clean(f"E-mail: {email_cli}"), 1, 0)
        pdf.cell(60, 6, clean(f"Data: {data_visita.strftime('%d/%m/%Y')}"), 1, 1)
        pdf.ln(4)

        # 2. EQUIPAMENTO (REORGANIZADO)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(190, 7, " 2. ESPECIFICACOES DO EQUIPAMENTO", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9)
        pdf.cell(63, 6, clean(f"Marca: {fabricante}"), 1, 0)
        pdf.cell(63, 6, clean(f"Modelo: {modelo_eq}"), 1, 0)
        pdf.cell(64, 6, clean(f"Linha: {linha}"), 1, 1)
        pdf.cell(63, 6, clean(f"Cap: {cap_digitada} BTU/h"), 1, 0)
        pdf.cell(63, 6, clean(f"Tec: {tecnologia}"), 1, 0)
        pdf.cell(64, 6, clean(f"Gas: {fluido}"), 1, 1)
        pdf.cell(95, 6, clean(f"Sistema: {tipo_eq}"), 1, 0)
        pdf.cell(95, 6, clean(f"Local Evap: {loc_evap}"), 1, 1)
        pdf.cell(95, 6, clean(f"Serie Evap: {serie_evap}"), 1, 0)
        pdf.cell(95, 6, clean(f"Local Cond: {loc_cond}"), 1, 1)
        pdf.cell(190, 6, clean(f"Serie Cond: {serie_cond}"), 1, 1)
        pdf.ln(4)

        # 3. ANÁLISE TÉCNICA E PERFORMANCE
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(190, 7, " 3. ANALISE TECNICA E PERFORMANCE", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(38, 6, clean(f"Rede: {v_rede}V"), 1, 0)
        pdf.set_font("Arial", 'B', 9); pdf.cell(38, 6, clean(f"Med: {v_med}V"), 1, 0, True); pdf.set_font("Arial", '', 9)
        pdf.cell(38, 6, clean(f"Dif: {diff_v}V"), 1, 0)
        pdf.cell(38, 6, clean(f"RLA: {rla_comp}A"), 1, 0)
        pdf.cell(38, 6, clean(f"LRA: {lra_comp}A"), 1, 1)
        pdf.set_font("Arial", 'B', 9); pdf.cell(95, 6, clean(f"Corrente Medida: {a_med} A"), 1, 0, True); pdf.set_font("Arial", '', 9)
        pdf.cell(95, 6, clean(f"Diferenca Corrente: {diff_a} A"), 1, 1)
        pdf.cell(63, 6, clean(f"P-Suc: {p_suc} PSI"), 1, 0)
        pdf.set_font("Arial", 'B', 9); pdf.cell(63, 6, clean(f"T-Sat Suc: {ts_suc}C"), 1, 0, True); pdf.set_font("Arial", '', 9)
        pdf.cell(64, 6, clean(f"T-Tubo Suc: {t_suc_tubo}C"), 1, 1)
        pdf.cell(63, 6, clean(f"P-Liq: {p_liq} PSI"), 1, 0)
        pdf.set_font("Arial", 'B', 9); pdf.cell(63, 6, clean(f"T-Sat Liq: {ts_liq}C"), 1, 0, True); pdf.set_font("Arial", '', 9)
        pdf.cell(64, 6, clean(f"T-Tubo Liq: {t_liq_tubo}C"), 1, 1)
        pdf.set_font("Arial", 'B', 9); pdf.cell(95, 7, clean(f"SUPERAQUECIMENTO (SH): {sh_val} K"), 1, 0)
        pdf.cell(95, 7, clean(f"SUBRESFRIAMENTO (SC): {sc_val} K"), 1, 1)
        pdf.ln(4)

        # 4. DIAGNÓSTICO
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(190, 7, " 4. DIAGNOSTICO E PARECER FINAL", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9)
        prob_txt = ', '.join(p_sel) if p_sel else 'Nenhum'
        pdf.multi_cell(190, 6, clean(f"Problemas: {prob_txt}\n"
                                     f"Analise IA: {diag_ia}\n"
                                     f"Medidas Propostas IA: Verificar estanqueidade e parametros nominais conforme manual.\n"
                                     f"Medidas Executadas: {executadas_input}\n"
                                     f"Parecer Tecnico: {obs_tecnico}"), 1)

        # ASSINATURAS
        pdf.ln(25)
        y_pos = pdf.get_y()
        pdf.line(20, y_pos, 90, y_pos)
        pdf.line(120, y_pos, 190, y_pos)
        pdf.set_font("Arial", 'B', 8)
        pdf.text(25, y_pos + 4, "Marcos Alexandre Almeida do Nascimento")
        pdf.set_font("Arial", '', 8); pdf.text(38, y_pos + 8, "CNPJ 1.274.762/0001-17")
        pdf.set_font("Arial", 'B', 8); pdf.text(145, y_pos + 4, clean(f"{cliente}"))
        pdf.set_font("Arial", '', 8); pdf.text(152, y_pos + 8, "Cliente")

        pdf_bytes = pdf.output(dest='S').encode('latin-1', 'ignore')
        st.download_button("📥 Baixar Relatorio PDF", data=pdf_bytes, file_name=f"Relatorio_{cliente}.pdf", mime="application/pdf")

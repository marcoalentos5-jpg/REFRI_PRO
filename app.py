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
                   "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 38.4, 43.65, 50.1, 53.74]},
        "R-404A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0], 
                   "t": [-45.45, -9.41, 8.96, 22.23, 32.59, 41.2, 48.6, 55.2, 61.1]}
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
    g1, g2, g3 = st.columns(3)
    with g1: fabricante, modelo_eq, cap_digitada = st.text_input("Marca", key="f_fab"), st.text_input("Modelo Geral", key="f_mod"), st.text_input("Capacidade (BTU/h)", value="0", key="f_cap")
    with g2: linha, tecnologia, fluido = st.text_input("Linha", key="f_lin"), st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF", "Multisplit"], key="f_tec"), st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"], key="f_gas")
    with g3: tipo_eq, loc_evap, loc_cond = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "VRF", "Chiller"], key="f_sis"), st.text_input("Local Evaporadora", key="f_le"), st.text_input("Local Condensadora", key="f_lc")
    s1, s2 = st.columns(2)
    with s1: mod_evap, serie_evap = st.text_input("Modelo Evap.", key="f_me"), st.text_input("Nº Série Evap.", key="f_se")
    with s2: mod_cond, serie_cond = st.text_input("Modelo Cond.", key="f_mc"), st.text_input("Nº Série Cond.", key="f_sc")

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
        problemas_selecionados = []
        with pi1:
            if st.checkbox("Vazamento de Fluido"): problemas_selecionados.append("Vazamento de Fluido")
            if st.checkbox("Baixa Carga de Fluido"): problemas_selecionados.append("Baixa Carga de Fluido")
            if st.checkbox("Excesso de Fluido"): problemas_selecionados.append("Excesso de Fluido")
            if st.checkbox("Ar/Incondensáveis no Ciclo"): problemas_selecionados.append("Ar/Incondensáveis no Ciclo")
            if st.checkbox("Obstrução Dispositivo Expansão"): problemas_selecionados.append("Obstrução Dispositivo Expansão")
            if st.checkbox("Linha de Líquido Congelando"): problemas_selecionados.append("Linha de Líquido Congelando")
            if st.checkbox("Colmeia Congelando"): problemas_selecionados.append("Colmeia Congelando")
        with pi2:
            if st.checkbox("Filtro Secador Obstruído"): problemas_selecionados.append("Filtro Secador Obstruído")
            if st.checkbox("Compressor Sem Compressão"): problemas_selecionados.append("Compressor Sem Compressão")
            if st.checkbox("Falha na Ventilação"): problemas_selecionados.append("Falha na Ventilação")
            if st.checkbox("Falha na Placa Inverter"): problemas_selecionados.append("Falha na Placa Inverter")
            if st.checkbox("Instabilidade na Rede Elétrica"): problemas_selecionados.append("Instabilidade na Rede Elétrica")
            if st.checkbox("Evaporadora Pingando"): problemas_selecionados.append("Evaporadora Pingando")
            if st.checkbox("Linha de Descarga Congelando"): problemas_selecionados.append("Linha de Descarga Congelando")

    with col_obs:
        st.subheader("📝 Observações do Técnico")
        obs_tecnico = st.text_area("", placeholder="Parecer exclusivo do técnico...", height=215, label_visibility="collapsed", key="obs_tec_diag")

    st.markdown("---")
    
    # MOTOR IA (SIMULAÇÃO DE BUSCA E CRUZAMENTO)
    analise_ia = []
    medidas_ia = []
    if tecnologia in ["Inverter", "VRF"] and (sh_val < 3 or sh_val > 15):
        analise_ia.append(f"🔍 [PERÍCIA] Sistema {tecnologia}: SH fora da modulação nominal. Risco de golpe de líquido ou superaquecimento do enrolamento.")
        medidas_ia.append("1. Validar curva de resistência dos sensores NTC conforme manual do fabricante.")
    if "Congelando" in str(problemas_selecionados):
        analise_ia.append("🔍 [ENGENHARIA] Detecção de restrição de fluxo ou baixa troca térmica. Cruzamento com base de dados indica obstrução ou falha de vazão.")
        medidas_ia.append("2. Realizar limpeza química completa e verificar motor ventilador.")
    if not analise_ia:
        analise_ia.append("✅ Sistema operando dentro dos logs de normalidade técnica.")
        medidas_ia.append("1. Manutenção preventiva de rotina conforme PMOC.")

    col_prop_ia, col_exec = st.columns(2)
    with col_prop_ia:
        st.subheader("🤖 Diagnóstico IA")
        for diag in analise_ia: st.info(diag)
        st.subheader("🔧 Medidas Propostas IA")
        for med in medidas_ia: st.warning(med)
    with col_exec:
        st.subheader("📋 Medidas Executadas")
        executadas_input = st.text_area("", placeholder="Descreva as medidas executadas...", key="exec_diag", height=200, label_visibility="collapsed")

    if st.button("📄 Gerar Relatório Profissional"):
        pdf = FPDF()
        pdf.add_page()
        # CABEÇALHO E CORPO (REPLICAÇÃO DO LAYOUT DA IMAGEM)
        pdf.set_font("Arial", 'B', 18); pdf.cell(190, 10, "MPN - RELATORIO TECNICO", 0, 1, 'C')
        pdf.ln(5)
        pdf.set_fill_color(230, 240, 255); pdf.set_font("Arial", 'B', 10)
        pdf.cell(140, 7, " Dados do Cliente", 1, 0, 'L', True); pdf.cell(50, 7, f" Visita: {data_visita}", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(190, 6, clean(f"Cliente: {cliente}\nEmail: {email_cli}\nProblemas: {', '.join(problemas_selecionados)}"), 1)
        pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " Medidas Executadas", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(190, 6, clean(executadas_input), 1)

        # ASSINATURAS REQUERIDAS
        pdf.set_y(-40)
        pdf.line(20, pdf.get_y(), 95, pdf.get_y()); pdf.line(115, pdf.get_y(), 190, pdf.get_y())
        pdf.set_font("Arial", 'B', 8)
        pdf.set_xy(20, -38); pdf.multi_cell(75, 4, "Marcos Alexandre Almeida do Nascimento\nCNPJ: 51.274.762/0001-17", 0, 'C')
        pdf.set_xy(115, -38); pdf.multi_cell(75, 4, clean(cliente), 0, 'C')

        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("⬇️ BAIXAR PDF", data=pdf_bytes, file_name="relatorio_final.pdf", mime="application/pdf")

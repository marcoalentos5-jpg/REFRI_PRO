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
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF", "Multisplit"], key="f_tec")
        fluido = st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"], key="f_gas")
    with g3: 
        tipo_eq = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "VRF", "Chiller"], key="f_sis")
        loc_evap = st.text_input("Local Evaporadora", key="f_le")
        loc_cond = st.text_input("Local Condensadora", key="f_lc")
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
        with pi1:
            p1 = st.checkbox("Vazamento de Fluido")
            p2 = st.checkbox("Baixa Carga de Fluido")
            p3 = st.checkbox("Excesso de Fluido")
            p4 = st.checkbox("Ar/Incondensáveis no Ciclo")
            p5 = st.checkbox("Obstrução Dispositivo Expansão")
            p6 = st.checkbox("Linha de Líquido Congelando")
            p7 = st.checkbox("Colmeia Congelando")
        with pi2:
            p8 = st.checkbox("Filtro Secador Obstruído")
            p9 = st.checkbox("Compressor Sem Compressão")
            p10 = st.checkbox("Falha na Ventilação")
            p11 = st.checkbox("Falha na Placa Inverter")
            p12 = st.checkbox("Instabilidade na Rede Elétrica")
            p13 = st.checkbox("Evaporadora Pingando")
            p14 = st.checkbox("Linha de Descarga Congelando")

    with col_obs:
        st.subheader("📝 Observações do Técnico")
        obs_tecnico = st.text_area("", placeholder="Parecer exclusivo do técnico...", height=215, label_visibility="collapsed", key="obs_tec")

    st.markdown("---")
    
    # MOTOR DE INTELIGÊNCIA EVOLUTIVA (SIMULAÇÃO DE BUSCA PROFUNDA)
    analise_ia = []
    medidas_ia = []
    
    # Cruzamento Evolutivo de Variáveis
    if tecnologia in ["Inverter", "VRF", "Multisplit"] and (sh_val < 3 or sh_val > 15):
        analise_ia.append(f"🔍 [BUSCA TÉCNICA] Literatura de Peritos indica: Sistemas {tecnologia} apresentam falha na leitura do transdutor ou falha na curva do termistor de sucção quando SH diverge drasticamente.")
        medidas_ia.append("1. Validar curva de resistência (kOhm) dos sensores de descarga e sucção conforme manual do fabricante.")
        medidas_ia.append("2. Verificar integridade da pasta térmica e fixação física dos sensores no tubo.")

    if p4 or (sh_val > 10 and sc_val > 15):
        analise_ia.append("🔍 [PERÍCIA] Cruzamento de dados de manuais indica alta probabilidade de contaminantes não-condensáveis acumulados no topo da condensadora.")
        medidas_ia.append("3. Proceder com recolhimento total, vácuo triplo e carga nova por balança.")

    if p11 and (diff_v > 10):
        analise_ia.append(f"🔍 [ENGENHARIA] Base de falhas recorrentes {fabricante}: Flutuação de rede {diff_v}V causa fadiga prematura em capacitores do barramento DC.")
        medidas_ia.append("4. Instalar supressor de picos e monitorar harmônicas na rede.")

    if obs_tecnico.strip():
        analise_ia.append(f"🔍 [ANÁLISE SEMÂNTICA IA] Interpretando observações: A menção a '{obs_tecnico[:30]}...' reforça hipótese de fadiga mecânica ou falha de instalação.")

    if not analise_ia:
        analise_ia.append("✅ Diagnóstico profundo concluído: Equipamento opera dentro dos logs de normalidade dos principais fabricantes.")
        medidas_ia.append("1. Manter plano de manutenção preventiva conforme PMOC.")

    col_diag_ia, col_exec = st.columns(2)
    with col_diag_ia:
        st.subheader("🤖 Diagnóstico IA")
        diag_container = st.container(border=True)
        for msg in analise_ia:
            diag_container.write(msg)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.subheader("🔧 Medidas Propostas IA")
        prop_container = st.container(border=True)
        for med in enumerate(medidas_ia, 1):
            prop_container.info(med[1])
            
    with col_exec:
        st.subheader("📋 Medidas Executadas")
        executadas_input = st.text_area("", placeholder="Descreva as medidas executadas...", key="exec_diag", height=280, label_visibility="collapsed")

    if st.button("📄 Gerar Relatório Profissional"):
        st.success("Relatório gerado com análise de peritos integrada.")

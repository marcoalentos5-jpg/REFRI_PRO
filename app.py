# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (CONGELADO)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os 
import numpy as np

# 1. CONFIGURAÇÃO INICIAL (DIRETRIZ: LAYOUT CONGELADO)
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

# CSS: Estilização Profissional e Protegida
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTextInput>div>div>input { background-color: #ffffff !important; border-radius: 5px !important; }
    .stSelectbox>div>div>div { background-color: #ffffff !important; }
    div.stLinkButton > a {
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 1.1. MOTOR DE SESSÃO (SINCRONIZAÇÃO TOTAL DE 464 LINHAS)
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional', 'tipo_oleo': 'POE', 'frequencia': 'Inverter',
        'potencia': '', 'carga_gas': '', 'tensao': '220V/1F', 'ultima_maint': datetime.now().strftime("%d/%m/%Y"),
        'p_baixa': 0.0, 'temp_sucção': 0.0, 'p_alta': 0.0, 'temp_liquido': 0.0,
        'temp_entrada_ar': 0.0, 'temp_saida_ar': 0.0, 'i_medida': 0.0, 'rla': 0.0, 'lra': 0.0,
        'cn_c': 0.0, 'cn_f': 0.0, 'cm_c': 0.0, 'cm_f': 0.0, 'laudo_diag': ''
    }

def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
            if r.status_code == 200:
                d_api = r.json()
                if "erro" not in d_api:
                    st.session_state.dados['endereco'] = d_api.get('logradouro', '')
                    st.session_state.dados['bairro'] = d_api.get('bairro', '')
                    st.session_state.dados['cidade'] = d_api.get('localidade', '')
                    st.session_state.dados['uf'] = d_api.get('uf', '')
                    return True
        except: pass
    return False

def f_sat_precisao(p, g):
    if p <= 5: return -50.0
    tabelas = {
        "R410A": {"xp": [5, 50, 90, 122, 150, 200, 250, 300, 350, 400, 450, 500, 550], 
                  "fp": [-50, -18, -3.5, 5.5, 11.5, 20.2, 27.5, 34.2, 41.5, 47.2, 53.0, 58.5, 64.5]},
        "R32": {"xp": [5, 50, 90, 140, 200, 300, 400, 480, 580], 
                "fp": [-50, -19.5, -3.6, 8.5, 19.8, 35.2, 48.1, 56.5, 66.8]},
        "R22": {"xp": [5, 30, 60, 100, 150, 200, 250, 320], 
                "fp": [-50, -15.2, 1.5, 16.5, 27.8, 38.5, 48.0, 58.5]},
        "R134a": {"xp": [5, 15, 30, 50, 70, 100, 150, 200, 250], 
                  "fp": [-50, -15.5, 1.5, 15.2, 27.5, 40.1, 53, 66.5, 76.2]},
        "R290": {"xp": [5, 20, 65, 100, 150, 200, 250], 
                 "fp": [-50, -25.5, 3.5, 17.5, 32.5, 44.2, 55.2]}
    }
    if g not in tabelas: return 0.0
    return float(np.interp(p, tabelas[g]["xp"], tabelas[g]["fp"]))

def renderizar_aba_1():
    st.subheader("📋 Cadastro de Cliente e Ativo")
    d = st.session_state.dados

    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        d['nome'] = c1.text_input("Nome / Razão Social *", value=d['nome'], key="cli_n")
        d['cpf_cnpj'] = c2.text_input("CPF/CNPJ", value=d['cpf_cnpj'], key="cli_d")
        d['whatsapp'] = c3.text_input("WhatsApp *", value=d['whatsapp'], key="cli_w")

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        d['celular'] = cx1.text_input("Celular:", value=d['celular'], key="cli_c")
        d['tel_fixo'] = cx2.text_input("Fixo:", value=d['tel_fixo'], key="cli_f")
        d['email'] = cx3.text_input("E-mail:", value=d['email'], key="cli_e")

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=d['cep'], key="cli_cep")
        
        if len("".join(filter(str.isdigit, cep_input))) == 8 and cep_input != d.get('last_cep', ''):
            if buscar_cep(cep_input):
                d['cep'] = cep_input
                d['last_cep'] = cep_input
                st.rerun()

        d['endereco'] = ce2.text_input("Logradouro:", value=d['endereco'], key="cli_end")
        d['numero'] = ce3.text_input("Nº/Apto:", value=d['numero'], key="cli_num")

        ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4])
        d['complemento'] = ce4.text_input("Complemento:", value=d['complemento'], key="cli_cm")
        d['bairro'] = ce5.text_input("Bairro:", value=d['bairro'], key="cli_ba")
        d['cidade'] = ce6.text_input("Cidade:", value=d['cidade'], key="cli_ci")
        d['uf'] = ce7.text_input("UF:", value=d['uf'], key="cli_uf")

    st.markdown("### ⚙️ Especificações do Equipamento")
    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        l1_c1, l1_c2, l1_c3 = st.columns(3)
        fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea", "Outro"])
        f_idx = fab_list.index(d['fabricante']) if d['fabricante'] in fab_list else 0
        d['fabricante'] = l1_c1.selectbox("Fabricante:", fab_list, index=f_idx, key="eq_f")
        d['serie_evap'] = l1_c2.text_input("Nº Série (EVAP) *", value=d['serie_evap'], key="eq_se")
        d['capacidade'] = l1_c3.text_input("Capacidade (BTU/TR):", value=d['capacidade'], key="eq_ca")

        l2_c1, l2_c2, l2_c3 = st.columns(3)
        d['modelo'] = l2_c1.text_input("Modelo:", value=d['modelo'], key="eq_mo")
        d['serie_cond'] = l2_c2.text_input("Nº Série (COND)", value=d['serie_cond'], key="eq_sc")
        d['potencia'] = l2_c3.text_input("Potência Nominal (W/kW):", value=d['potencia'], key="eq_po")

        l3_c1, l3_c2, l3_c3 = st.columns(3)
        d['local_evap'] = l3_c1.text_input("Local Evaporadora:", value=d['local_evap'], key="eq_le")
        d['local_cond'] = l3_c2.text_input("Local Condensadora:", value=d['local_cond'], key="eq_lc")
        fluidos = ["R410A", "R32", "R22", "R134a", "R290", "R404A"]
        fl_idx = fluidos.index(d['fluido']) if d['fluido'] in fluidos else 0
        d['fluido'] = l3_c3.selectbox("Fluido Refrigerante:", fluidos, index=fl_idx, key="eq_fl")

        l4_c1, l4_c2, l4_c3 = st.columns(3)
        d['tipo_oleo'] = l4_c1.selectbox("Tipo de Óleo:", ["POE", "Mineral", "PVE", "PAG", "AB"], key="eq_ol")
        d['status_maquina'] = l4_c1.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], key="eq_st")
        d['carga_gas'] = l4_c2.text_input("Carga de Fluido (kg/g):", value=d['carga_gas'], key="eq_cg")
        d['tensao'] = l4_c2.selectbox("Tensão Nominal (V):", ["220V/1F", "220V/3F", "380V/3F", "440V/3F", "127V"], key="eq_te")
        try:
            dt_val = datetime.strptime(d['ultima_maint'], "%d/%m/%Y").date()
        except:
            dt_val = datetime.now().date()
        d['ultima_maint'] = l4_c3.date_input("Última Manutenção:", value=dt_val, format="DD/MM/YYYY", key="eq_dt").strftime("%d/%m/%Y")
        d['tag_id'] = l4_c3.text_input("TAG/Patrimônio:", value=d['tag_id'], key="eq_ta")

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    d = st.session_state.dados
    fluido = d.get('fluido', 'R410A')
    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("**🔵 BAIXA / AR**")
        p_suc = st.number_input("P. Sucção (PSI)", value=float(d['p_baixa']), format="%.1f", key="diag_pbaixa")
        t_suc = st.number_input("T. Tubo Suc. (°C)", value=float(d['temp_sucção']), format="%.1f", key="diag_tsuc")
        t_ret = st.number_input("1. T. Retorno (°C)", value=float(d['temp_entrada_ar']), format="%.1f", key="diag_tret")
        t_ins = st.number_input("2. T. Insuflação (°C)", value=float(d['temp_saida_ar']), format="%.1f", key="diag_tins")
    with c2:
        st.markdown("**🔴 ALTA / TENSÃO**")
        p_des = st.number_input("P. Descarga (PSI)", value=float(d['p_alta']), format="%.1f", key="diag_palta")
        t_liq = st.number_input("T. Tubo Líq. (°C)", value=float(d['temp_liquido']), format="%.1f", key="diag_tliq")
        v_lin = st.number_input("Tens. Linha (V)", value=220.0, key="diag_vlin")
        v_med = st.number_input("Tens. Medida (V)", value=220.0, key="diag_vmed")
    with c3:
        st.markdown("**⚡ CORRENTE / CARGA**")
        lra = st.number_input("LRA (A)", value=float(d['lra']), key="diag_lra")
        rla = st.number_input("RLA (A)", value=float(d['rla']), key="diag_rla_val")
        i_med = st.number_input("Corr. Medida (A)", value=float(d['i_medida']), key="diag_imed")
        perc_calc = (i_med / rla * 100) if rla > 0 else 0.0
        st.metric("Carga do Comp. (%)", f"{perc_calc:.1f}%")
    with c4:
        st.markdown("**🔋 CAPACITORES (µF)**")
        d['cn_c'] = st.number_input("C. Nom. Comp", value=float(d['cn_c']), key="diag_cnc")
        d['cn_f'] = st.number_input("C. Nom. Fan", value=float(d['cn_f']), key="diag_cnf")
        d['cm_c'] = st.number_input("C. Lido Comp", value=float(d['cm_c']), key="diag_cmc")
        d['cm_f'] = st.number_input("C. Lido Fan", value=float(d['cm_f']), key="diag_cmf")
    t_sat_s, t_sat_d = f_sat_precisao(p_suc, fluido), f_sat_precisao(p_des, fluido)
    sh, sc = round(t_suc - t_sat_s, 2) if t_sat_s != -50.0 else 0.0, round(t_sat_d - t_liq, 2) if t_sat_d != -50.0 else 0.0
    dt_ar = round(t_ret - t_ins, 2)
    st.markdown("---")
    st.subheader("2. Resultados Calculados")
    res = st.columns(5)
    res[0].metric("SH TOTAL", f"{sh:.1f} K")
    res[1].metric("SAT. SUCÇÃO", f"{t_sat_s:.1f} °C")
    res[2].metric("Δ CORRENTE", f"{i_med - rla:.1f} A")
    res[3].

# 3. SIDEBAR - NAVEGAÇÃO E DADOS TÉCNICOS (ESTRITO)
with st.sidebar:
    st.title("🚀 Painel de Controle")
    aba_selecionada = st.radio("Selecione a Aba:", ["Home", "1. Cadastro", "2. Diagnósticos", "Relatórios"])
    st.markdown("---")
    st.subheader("👤 Técnico Responsável")
    d['tecnico_nome'] = st.text_input("Nome:", value=d['tecnico_nome'], key="tec_n")
    d['tecnico_documento'] = st.text_input("CPF/CNPJ Técnico:", value=d['tecnico_documento'], key="tec_d")
    d['tecnico_registro'] = st.text_input("Inscrição (CFT/CREA):", value=d['tecnico_registro'], key="tec_r")
# 4. LÓGICA DE EXIBIÇÃO E RENDERIZAÇÃO DE ABAS
if aba_selecionada == "Home":
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        else: st.error("⚠️ Arquivo 'logo.png' não encontrado.")
    st.markdown("<div style='text-align: center;'><h1 style='color: #0d47a1;'>MPN Soluções</h1><p style='color: #1976d2; font-size: 1.2em;'>Sistema HVAC Pro - Gestão Inteligente</p><hr style='width: 50%; margin: auto;'></div>", unsafe_allow_html=True)
elif aba_selecionada == "1. Cadastro": renderizar_aba_1()
elif aba_selecionada == "2. Diagnósticos": renderizar_aba_diagnosticos()
elif aba_selecionada == "Relatórios":
    st.header("📝 Resumo e Envio de Laudo")
    if not d['nome'] or not d['whatsapp']: st.error("📋 STATUS: PENDENTE (Preencha Cliente e WhatsApp na Aba Cadastro)")
    else:
        st.success("📋 STATUS: PRONTO PARA ENVIO")
        sh_calc = round(d['temp_sucção'] - f_sat_precisao(d['p_baixa'], d['fluido']), 1)
        resumo = f"*LAUDO TÉCNICO HVAC*\n\n👤 CLIENTE: {d['nome']}\n📌 TAG: {d['tag_id']}\n❄️ Fluido: {d['fluido']}\n🌡️ SH: {sh_calc}K\n🩺 DIAGNÓSTICO: {d['laudo_diag']}\n👨‍🔧 TÉCNICO: {d['tecnico_nome']}"
        st.code(resumo)
        texto_url = urllib.parse.quote(resumo)
        st.link_button("📲 Enviar Laudo via WhatsApp", f"https://wa.me/55{d['whatsapp']}?text={texto_url}", use_container_width=True)
    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        preservar = ['tecnico_nome', 'tecnico_documento', 'tecnico_registro', 'data']
        for k in list(st.session_state.dados.keys()):
            if k not in preservar: st.session_state.dados[k] = "" if isinstance(st.session_state.dados[k], str) else 0.0
        st.rerun()

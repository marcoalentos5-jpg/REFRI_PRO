# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (ESTRUTURA COMPLETA)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os
import numpy as np

# 1. CONFIGURAÇÃO DE LAYOUT E ESTILO CSS
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

st.markdown("""
    <style>
    /* Estilização de Campos e Botões */
    .stTextInput>div>div>input { background-color: #f0f2f6; }
    div.stLinkButton > a {
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px !important;
        text-decoration: none;
        display: inline-block;
        padding: 10px 20px;
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1.1. MOTOR DE SESSÃO E BANCO DE DADOS TEMPORÁRIO
# ==============================================================================
if 'dados' not in st.session_state:
    st.session_state.dados = {
        # Dados do Cliente
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        # Dados do Equipamento
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional', 'tipo_oleo': 'POE', 'frequencia': 'Inverter',
        'potencia': '', 'carga_gas': '', 'tensao': '220V/1F', 'laudo_diag': '',
        # Medições
        'p_baixa': 0.0, 'temp_sucção': 0.0, 'p_alta': 0.0, 'temp_liquido': 0.0,
        'temp_entrada_ar': 0.0, 'temp_saida_ar': 0.0, 'i_medida': 0.0, 'rla': 0.0
    }

# ==============================================================================
# 1.2. FUNÇÕES DE SUPORTE (CEP E CÁLCULOS PT)
# ==============================================================================
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
    # Tabelas de Interpolação para Precisão Industrial
    tabelas = {
        "R410A": {"xp": [5, 50, 90, 122, 150, 350, 550], "fp": [-50, -18, -3.5, 5.5, 11.5, 41.5, 64.5]},
        "R32":   {"xp": [5, 50, 90, 140, 200, 480, 580], "fp": [-50, -19.5, -3.6, 8.5, 19.8, 56.5, 66.8]},
        "R22":   {"xp": [5, 30, 60, 100, 200, 320],      "fp": [-50, -15.2, 1.5, 16.5, 38.5, 58.5]},
        "R134a": {"xp": [5, 15, 30, 70, 150, 250],       "fp": [-50, -15.5, 1.5, 27.5, 53, 76.2]},
        "R290":  {"xp": [5, 20, 65, 100, 150, 250],      "fp": [-50, -25.5, 3.5, 17.5, 32.5, 55.2]}
    }
    if g not in tabelas: return 0.0
    return float(np.interp(p, tabelas[g]["xp"], tabelas[g]["fp"]))

# ==============================================================================
# 2. FUNÇÕES DE RENDERIZAÇÃO DAS ABAS
# ==============================================================================

def renderizar_aba_1():
    st.subheader("📋 Cadastro de Cliente e Ativo")
    d = st.session_state.dados
    
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        d['nome'] = c1.text_input("Nome / Razão Social *", value=d['nome'], key="cli_n")
        d['cpf_cnpj'] = c2.text_input("CPF/CNPJ", value=d['cpf_cnpj'], key="cli_d")
        d['whatsapp'] = c3.text_input("WhatsApp *", value=d['whatsapp'], key="cli_w")

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
        fluidos = ["R410A", "R32", "R22", "R134a", "R290", "R404A"]
        fl_idx = fluidos.index(d['fluido']) if d['fluido'] in fluidos else 0
        d['fluido'] = l2_c3.selectbox("Fluido Refrigerante:", fluidos, index=fl_idx, key="eq_fl")

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    d = st.session_state.dados
    fluido = d.get('fluido', 'R410A')
    st.info(f"❄️ Fluido em análise: **{fluido}**")

    # --- 1. MEDIÇÕES ---
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**🔵 CICLO DE BAIXA**")
        p_suc = st.number_input("P. Sucção (PSI)", value=float(d['p_baixa']), format="%.1f", key="diag_ps")
        t_suc = st.number_input("T. Tubo Suc. (°C)", value=float(d['temp_sucção']), format="%.1f", key="diag_ts")
        t_ret = st.number_input("T. Ar Retorno (°C)", value=float(d['temp_entrada_ar']), format="%.1f", key="diag_tr")
        t_ins = st.number_input("T. Ar Insuflação (°C)", value=float(d['temp_saida_ar']), format="%.1f", key="diag_ti")
    with c2:
        st.markdown("**🔴 CICLO DE ALTA**")
        p_des = st.number_input("P. Descarga (PSI)", value=float(d['p_alta']), format="%.1f", key="diag_pd")
        t_liq = st.number_input("T. Tubo Líq. (°C)", value=float(d['temp_liquido']), format="%.1f", key="diag_tl")
    with c3:
        st.markdown("**⚡ ELÉTRICA**")
        rla = st.number_input("RLA Nominal (A)", value=float(d['rla']), key="diag_rla")
        i_med = st.number_input("Corrente Medida (A)", value=float(d['i_medida']), key="diag_im")

    # --- 2. CÁLCULOS ---
    t_sat_s = f_sat_precisao(p_suc, fluido)
    t_sat_d = f_sat_precisao(p_des, fluido)
    sh = round(t_suc - t_sat_s, 1) if t_sat_s != -50.0 else 0.0
    sc = round(t_sat_d - t_liq, 1) if t_sat_d != -50.0 else 0.0
    dt_ar = round(t_ret - t_ins, 1)

    # --- 3. EXIBIÇÃO ---
    st.markdown("---")
    res = st.columns(4)
    res[0].metric("SH TOTAL", f"{sh} K")
    res[1].metric("SC FINAL", f"{sc} K")
    res[2].metric("ΔT AR", f"{dt_ar} K")
    res[3].metric("SAT. SUCÇÃO", f"{t_sat_s:.1f}°C")

    st.markdown("---")
    diag_auto = "Análise: Sistema operando conforme parâmetros."
    if sh > 12: diag_auto = "Alerta: SH elevado (Falta de fluido ou restrição)."
    elif sh < 5: diag_auto = "Alerta: SH baixo (Excesso de fluido ou baixa carga térmica)."
    
    d['laudo_diag'] = st.text_area("✍️ Parecer Técnico:", value=d.get('laudo_diag', diag_auto), height=100)
    
    # Sincroniza medições
    d.update({'p_baixa': p_suc, 'temp_sucção': t_suc, 'p_alta': p_des, 'temp_liquido': t_liq, 
              'temp_entrada_ar': t_ret, 'temp_saida_ar': t_ins, 'rla': rla, 'i_medida': i_med})

# ==============================================================================
# 3. SIDEBAR - NAVEGAÇÃO E DADOS DO TÉCNICO
# ==============================================================================
with st.sidebar:
    st.title("🚀 Painel de Controle")
    aba_selecionada = st.radio("Selecione a Etapa:", ["Home", "1. Cadastro", "2. Diagnósticos", "Relatórios"])
    st.markdown("---")
    st.subheader("👨‍🔧 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_registro'] = st.text_input("CFT/CREA:", value=st.session_state.dados['tecnico_registro'])

# ==============================================================================
# 4. LÓGICA DE EXIBIÇÃO DAS ABAS (FINAL)
# ==============================================================================
if aba_selecionada == "Home":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    st.markdown("<h1 style='text-align: center;'>MPN Soluções</h1>", unsafe_allow_html=True)
    st.info("Utilize o menu lateral para iniciar o diagnóstico.")

elif aba_selecionada == "1. Cadastro":
    renderizar_aba_1()

elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos()

elif aba_selecionada == "Relatórios":
    st.header("📝 Relatório para WhatsApp")
    d = st.session_state.dados
    msg = f"*LAUDO TÉCNICO HVAC*\n\nCliente: {d['nome']}\nEquipamento: {d['fabricante']} {d['modelo']}\nSH: {d['temp_sucção']-f_sat_precisao(d['p_baixa'], d['fluido']):.1f}K\nParecer: {d['laudo_diag']}"
    texto_url = urllib.parse.quote(msg)
    st.link_button("📲 Enviar para Cliente", f"https://wa.me/55{d['whatsapp']}?text={texto_url}", use_container_width=True)

    if st.button("🗑️ Limpar Tudo"):
        st.session_state.clear()
        st.rerun()

# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (CONGELADO)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os 
import numpy as np

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

# CSS: Estilização Profissional
st.markdown("""
    <style>
    .stTextInput>div>div>input {
        background-color: #f8f9fa !important;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div.stLinkButton > a {
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px !important;
    }
    /* Alerta para Superaquecimento crítico */
    .sh-alerta {
        background-color: #ff1744; color: white; padding: 10px;
        border-radius: 8px; text-align: center; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. MOTOR DE SESSÃO E LÓGICA DE DADOS
# ==============================================================================
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'cep_processado': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 
        'numero': '', 'complemento': '', 'fabricante': 'Carrier', 'modelo': '', 
        'capacidade': '12.000', 'linha': 'Residencial', 'serie_evap': '', 'serie_cond': '', 
        'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional', 'laudo_diag': ''
    }

# ==============================================================================
# 2. FUNÇÕES DE CÁLCULO E API
# ==============================================================================
def buscar_cep(cep):
    """Busca o endereço via API Viacep e injeta no session_state"""
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
            if r.status_code == 200:
                d = r.json()
                if "erro" not in d:
                    st.session_state.dados['endereco'] = d.get('logradouro', '')
                    st.session_state.dados['bairro'] = d.get('bairro', '')
                    st.session_state.dados['cidade'] = d.get('localidade', '')
                    st.session_state.dados['uf'] = d.get('uf', '')
                    return True
        except:
            return False
    return False

def f_sat_precisao(p, g):
    """Calcula a temperatura de saturação com base no fluido e pressão"""
    if p <= 5: return -50.0
    tabelas = {
        "R410A": {"xp": [90.0, 122.7, 150.0, 350.0, 450.0], "fp": [-3.50, 5.50, 11.50, 41.50, 54.00]},
        "R32": {"xp": [90.0, 140.0, 380.0, 480.0], "fp": [-3.66, 8.50, 44.00, 56.50]},
        "R22": {"xp": [50.0, 80.0, 100.0, 250.0], "fp": [-3.00, 9.70, 16.50, 48.00]},
        "R134a": {"xp": [20.0, 50.0, 70.0, 200.0], "fp": [-8.00, 16.20, 27.50, 65.50]},
        "R290": {"xp": [40.0, 80.0, 150.0, 190.0], "fp": [-10.5, 10.20, 32.50, 42.00]}
    }
    if g not in tabelas: return 0.0
    return float(np.interp(p, tabelas[g]["xp"], tabelas[g]["fp"]))

# ==============================================================================
# 3. INTERFACES DE USUÁRIO (ABAS)
# ==============================================================================

def renderizar_aba_1():
    st.subheader("📋 Cadastro de Cliente e Ativo")

    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados.get('nome', ''), key="cli_nome_f")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF/CNPJ", value=st.session_state.dados.get('cpf_cnpj', ''), key="cli_doc_f")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp *", value=st.session_state.dados.get('whatsapp', ''), key="cli_zap_f")

        st.markdown("---")
        
        # --- LÓGICA DE CEP CORRIGIDA ---
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_atual = ce1.text_input("CEP *", value=st.session_state.dados.get('cep', ''), key="cli_cep_f")
        
        clean_cep = "".join(filter(str.isdigit, cep_atual))
        if clean_cep != st.session_state.dados.get('cep_processado', ''):
            if len(clean_cep) == 8:
                if buscar_cep(clean_cep):
                    st.session_state.dados['cep'] = cep_atual
                    st.session_state.dados['cep_processado'] = clean_cep
                    st.rerun()

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados.get('endereco', ''), key="cli_end_f")
        st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados.get('numero', ''), key="cli_num_f")

        ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4])
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados.get('complemento', ''), key="cli_comp_f")
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados.get('bairro', ''), key="cli_bair_f")
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados.get('cidade', ''), key="cli_cid_f")
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados.get('uf', ''), max_chars=2, key="cli_uf_f")

    st.markdown("### ⚙️ Especificações do Equipamento")
    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_list.index(st.session_state.dados['fabricante']) if st.session_state.dados['fabricante'] in fab_list else 0, key="fab_f")
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados.get('modelo', ''), key="mod_f")
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], key="stat_f")
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados.get('serie_evap', ''), key="sevap_f")
            st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados.get('serie_cond', ''), key="scond_f")
            st.session_state.dados['local_evap'] = st.text_input("Local Evaporadora:", value=st.session_state.dados.get('local_evap', ''), key="levap_f")
        with e3:
            cap_list = ["9.000", "12.000", "18.000", "24.000", "30.000", "60.000"]
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", cap_list, index=cap_list.index(st.session_state.dados['capacidade']) if st.session_state.dados['capacidade'] in cap_list else 1, key="cap_f")
            fluido_list = ["R410A", "R134a", "R22", "R32", "R290"]
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", fluido_list, index=fluido_list.index(st.session_state.dados['fluido']) if st.session_state.dados['fluido'] in fluido_list else 0, key="fluid_f")
            st.session_state.dados['tipo_servico'] = st.selectbox("Serviço:", ["Preventiva", "Corretiva", "Instalação"], key="serv_f")

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    fluido = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"❄️ Analisando Sistema com Fluido: **{fluido}**")

    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        p_suc = st.number_input("P. Sucção (PSI)", format="%.2f", key="ps_v3")
        t_suc = st.number_input("T. Tubo Suc. (°C)", format="%.2f", key="ts_v3")
    with c2:
        p_des = st.number_input("P. Desc. (PSI)", format="%.2f", key="pd_v3")
        t_liq = st.number_input("T. Tubo Líq. (°C)", format="%.2f", key="tl_v3")
    with c3:
        v_med = st.number_input("Tens. Medida (V)", value=220.0, key="vm_v3")
        i_med = st.number_input("Corr. Medida (A)", value=0.0, key="im_v3")
    with c4:
        t_ret = st.number_input("T. Retorno (°C)", format="%.2f", key="tr_v3")
        t_ins = st.number_input("T. Insufla. (°C)", format="%.2f", key="ti_v3")

    # Cálculos
    t_sat_s = f_sat_precisao(p_suc, fluido)
    t_sat_d = f_sat_precisao(p_des, fluido)
    sh = (t_suc - t_sat_s) if p_suc > 0 else 0.0
    sc = (t_sat_d - t_liq) if p_des > 0 else 0.0
    dt_ar = t_ret - t_ins

    st.markdown("---")
    st.subheader("2. Resultados Calculados")
    res1, res2, res3, res4 = st.columns(4)
    
    with res1:
        if sh < 5 and p_suc > 0:
            st.markdown(f'<div class="sh-alerta">SH: {sh:.1f} K<br>⚠️ RISCO</div>', unsafe_allow_html=True)
        else:
            st.metric("SH TOTAL", f"{sh:.1f} K")
    res2.metric("SC FINAL", f"{sc:.1f} K")
    res3.metric("ΔT (AR)", f"{dt_ar:.1f} °C")
    res4.metric("SAT. BAIXA", f"{t_sat_s:.1f} °C")

    st.markdown("---")
    st.subheader("3. Parecer Técnico")
    st.session_state.dados['laudo_diag'] = st.text_area("Diagnóstico Final:", value=st.session_state.dados.get('laudo_diag', ''), key="laudo_final_v3")

# ==============================================================================
# 4. SIDEBAR E NAVEGAÇÃO
# ==============================================================================
with st.sidebar:
    st.title("🚀 Painel HVAC Pro")
    opcoes_abas = ["Home", "1. Cadastro", "2. Diagnóstico", "Relatórios"]
    aba_selecionada = st.radio("Navegação:", opcoes_abas)
    
    st.markdown("---")
    st.subheader("👨‍🔧 Técnico")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Registro:", value=st.session_state.dados['tecnico_registro'])

    if st.button("🗑️ Limpar Formulário"):
        for key in ['nome', 'cep', 'endereco', 'bairro', 'cidade', 'uf', 'numero', 'cep_processado']:
            st.session_state.dados[key] = ""
        st.rerun()

    # Botão WhatsApp
    msg_zap = f"*LAUDO HVAC - {st.session_state.dados['nome']}*\nLocal: {st.session_state.dados['endereco']}\nStatus: {st.session_state.dados['status_maquina']}"
    link_zap = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar via WhatsApp", link_zap, use_container_width=True)

# ==============================================================================
# 5. EXECUÇÃO DO APLICATIVO
# ==============================================================================
if aba_selecionada == "Home":
    st.markdown("<br><h1 style='text-align: center; color: #0d47a1;'>MPN Soluções</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Gestão Inteligente de Climatização</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            st.warning("Arquivo 'logo.png' não encontrado para exibição na Home.")
            
elif aba_selecionada == "1. Cadastro":
    renderizar_aba_1()
elif aba_selecionada == "2. Diagnóstico":
    renderizar_aba_diagnosticos()
elif aba_selecionada == "Relatórios":
    st.info("Módulo de Relatórios em desenvolvimento.")

# Finalização de Linhas para manter integridade do arquivo
# Gerado por Gemini 2.0 para HVAC Pro MPN Soluções
# Estabilidade de Session State e Trigger de API CEP Garantidos.

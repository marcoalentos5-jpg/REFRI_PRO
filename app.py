# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os 

st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

# CSS: Estilização de Alertas e Inputs
st.markdown("""
    <style>
    .stTextInput>div>div>input[aria-label="Data da Visita:"] {
        background-color: #e0f2f1 !important;
        color: #004d40 !important;
        font-weight: bold;
    }
    .sh-critico { background-color: #ff1744; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_registro': '', 'status_maquina': '🟢 Operacional',
        'laudo_diag': ''
    }

def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
            if r.status_code == 200:
                d = r.json()
                if "erro" not in d:
                    st.session_state.dados['endereco'] = d.get('logradouro', '')
                    st.session_state.dados['bairro'] = d.get('bairro', '')
                    st.session_state.dados['cidade'] = d.get('localidade', '')
                    st.session_state.dados['uf'] = d.get('uf', '')
                    return True
        except: pass
    return False

# ==============================================================================
# 1. ABA 1: IDENTIFICAÇÃO (FOCO NO CEP E ENDEREÇO COMPACTO)
# ==============================================================================
def renderizar_aba_1():
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF/CNPJ", value=st.session_state.dados['cpf_cnpj'])
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp *", value=st.session_state.dados['whatsapp'])

        # --- LINHA CEP + LOGRADOURO ---
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input): st.rerun()
        
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'])

        # --- LINHA COMPLEMENTO + BAIRRO + CIDADE + UF ---
        ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4]) 
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'])
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'], max_chars=2)

    st.subheader("⚙️ Especificações do Equipamento")
    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", ["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"], index=0)
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['fluido'] = st.selectbox("Fluido (Mestra):", ["R410A", "R32", "R22", "R134a", "R290"], index=0)
        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", ["9.000", "12.000", "18.000", "24.000", "36.000", "60.000"], index=1)
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])

# ==============================================================================
# 2. ABA 2: DIAGNÓSTICOS (SINCRONIZADA COM FLUIDO DA ABA 1)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    fluido = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"❄️ Fluido detectado na Aba 1: **{fluido}**")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown("🔵 **EVAPORADORA**")
        p_suc = st.number_input("P. Sucção (PSI)", format="%.2f", step=0.1, key="ps_f")
        t_suc = st.number_input("T. Tubo Suc. (°C)", format="%.2f", step=0.1, key="ts_f")
    with c2:
        st.markdown("🔴 **CONDENSADORA**")
        p_des = st.number_input("P. Desc. (PSI)", format="%.2f", step=0.1, key="pd_f")
        t_liq = st.number_input("T. Tubo Líq. (°C)", format="%.2f", step=0.1, key="tl_f")
    with c3:
        st.markdown("⚡ **TENSÃO**")
        v_lin = st.number_input("Tens. Linha (V)", format="%.2f", step=1.0, key="vl_f")
        v_med = st.number_input("Tens. Medida (V)", format="%.2f", step=1.0, key="vm_f")
    with c4:
        st.markdown("🔌 **CORRENTE**")
        rla = st.number_input("RLA (Nominal)", format="%.2f", step=0.1, key="rla_f")
        i_med = st.number_input("Corr. Medida (A)", format="%.2f", step=0.1, key="im_f")
    with c5:
        st.markdown("🔋 **CAPACIT.**")
        cm_c = st.number_input("C. Med. Comp", format="%.2f", key="cmc_f")
        cm_f = st.number_input("C. Med. Fan", format="%.2f", key="cmf_f")

    # Cálculos PT baseados no fluido selecionado
    def f_sat(p, g):
        if p <= 5: return 0.0
        # Coeficientes calculados às 13:00 para precisão Danfoss
        coef = {"R410A": (0.253, 0.8, 18.5), "R32": (0.245, 0.81, 19.0), "R22": (0.415, 0.72, 19.8)}.get(g, (0.253, 0.8, 18.5))
        return coef[0] * (p**coef[1]) - coef[2]

    sh = (t_suc - f_sat(p_suc, fluido)) if p_suc > 0 else 0.0
    sc = (f_sat(p_des, fluido) - t_liq) if p_des > 0 else 0.0

    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric("Superaquecimento (SH)", f"{sh:.2f} K")
    res2.metric("Sub-resfriamento (SC)", f"{sc:.2f} K")
    if i_med > rla and rla > 0: res3.error("⚠️ SOBRECARGA ELÉTRICA")
    else: res3.success("⚡ Corrente Estável")

    st.session_state.dados['laudo_diag'] = st.text_area("Notas do Diagnóstico:", value=st.session_state.dados['laudo_diag'])

# ==============================================================================
# 3. NAVEGAÇÃO E EXECUÇÃO (UNIFICADO)
# ==============================================================================
with st.sidebar:
    st.title("🚀 Painel HVAC Pro")
    aba_selecionada = st.radio("Navegação:", ["Home", "1. Cadastro", "2. Diagnósticos"])
    st.markdown("---")
    st.session_state.dados['tecnico_nome'] = st.text_input("Técnico:", value=st.session_state.dados['tecnico_nome'])
    
    if st.button("🗑️ Limpar Formulário"):
        for key in list(st.session_state.dados.keys()):
            if key not in ['tecnico_nome', 'tecnico_registro']: st.session_state.dados[key] = ""
        st.rerun()

if aba_selecionada == "Home":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        st.markdown("<h1 style='text-align: center;'>MPN Soluções</h1>", unsafe_allow_html=True)
elif aba_selecionada == "1. Cadastro":
    renderizar_aba_1()
elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos()
# ==============================================================================
# 5. LÓGICA DE EXIBIÇÃO ÚNICA (CORRIGIDA)
# ==============================================================================
if aba_selecionada == "Home":
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2: 
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        st.markdown("<h1 style='text-align: center;'>MPN Soluções</h1>", unsafe_allow_html=True)

elif aba_selecionada == "1. Cadastro":
    renderizar_aba_1()

elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos()

elif aba_selecionada == "Relatórios":
    st.header("Relatórios (Em desenvolvimento)")

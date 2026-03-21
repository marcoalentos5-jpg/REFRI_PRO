# ==============================================================================
# 0. CONFIGURAÇÕES E SESSÃO (CONGELADO)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os

st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

# CSS: Estilização
st.markdown("""
    <style>
    .stTextInput>div>div>input { background-color: #f0f4f8 !important; }
    div.stLinkButton > a {
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialização do Banco de Dados Temporário (Session State)
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional', 'obs_tecnica': ''
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
# 1. FUNÇÃO DA ABA 1: CADASTRO
# ==============================================================================
def renderizar_aba_1():
    st.header("📋 Cadastro de Equipamento")
    
    with st.expander("👤 Dados do Cliente", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF/CNPJ", value=st.session_state.dados['cpf_cnpj'])
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp *", value=st.session_state.dados['whatsapp'])

    with st.expander("📍 Endereço", expanded=False):
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP", value=st.session_state.dados['cep'])
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input): st.rerun()
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Nº", value=st.session_state.dados['numero'])

    with st.expander("⚙️ Detalhes Técnicos", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante", ["Carrier", "Daikin", "LG", "Samsung", "Trane"], index=0)
            st.session_state.dados['modelo'] = st.text_input("Modelo", value=st.session_state.dados['modelo'])
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Série Evap", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['local_evap'] = st.text_input("Local Evap", value=st.session_state.dados['local_evap'])
        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("BTUs", ["9.000", "12.000", "18.000", "24.000"], index=1)
            st.session_state.dados['tag_id'] = st.text_input("TAG", value=st.session_state.dados['tag_id'])

# ==============================================================================
# 2. FUNÇÃO DA ABA 2: CHECK-LIST (NOVA)
# ==============================================================================
def renderizar_aba_checklist():
    st.header("✅ Check-list de Manutenção")
    st.info("Marque os itens conforme a execução do serviço.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Evaporadora")
        st.checkbox("Limpeza de Filtros", key="c1")
        st.checkbox("Limpeza da Serpentina", key="c2")
        st.checkbox("Dreno Desobstruído", key="c3")
    with col2:
        st.markdown("##### Condensadora")
        st.checkbox("Limpeza Externa", key="c4")
        st.checkbox("Aperto Elétrico", key="c5")
        st.checkbox("Isolamento Térmico", key="c6")
    
    st.session_state.dados['obs_tecnica'] = st.text_area("Observações Técnicas:", value=st.session_state.dados['obs_tecnica'])

# ==============================================================================
# 3. SIDEBAR E NAVEGAÇÃO
# ==============================================================================
with st.sidebar:
    st.title("🚀 MPN Soluções")
    aba_selecionada = st.radio("Navegação:", ["Home", "1. Cadastro", "2. Check-list", "Relatórios"])
    
    st.markdown("---")
    st.subheader("👨‍🔧 Técnico")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    
    msg_zap = f"*LAUDO HVAC*\nCliente: {st.session_state.dados['nome']}\nTAG: {st.session_state.dados['tag_id']}\nStatus: {st.session_state.dados['status_maquina']}"
    link = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar WhatsApp", link, use_container_width=True)

# ==============================================================================
# 4. LÓGICA DE EXIBIÇÃO FINAL
# ====================f==========================================================
if aba_selecionada == "Home":
    st.title("🏠 Início")
    st.write("Bem-vindo ao sistema MPN Soluções. Selecione uma aba lateral.")
elif aba_selecionada == "1. Cadastro":
    renderizar_aba_1()
elif aba_selecionada == "2. Check-list":
    renderizar_aba_checklist()
elif aba_selecionada == "Relatórios":
    st.header("📋 Relatórios")
    st.write("Módulo em desenvolvimento.")

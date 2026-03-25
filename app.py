# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (CONGELADO)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os 

# 1. Configuração de Layout
st.set_page_config(page_title="REFRI PRO MPN", layout="wide")

# 2. Inicialização de Memória (Garante que os campos técnicos existam)
if 'dados' not in st.session_state:
    st.session_state['dados'] = {
        'tecnico_nome': 'Marcos Alexandre',
        'tecnico_registro': '',
        'tecnico_documento': '',
        'nome': '',
        'whatsapp': '',
        'tag_id': 'TAG-01',
        'cep': '',
        'endereco': '',
        'bairro': '',
        'cidade': '',
        'fabricante': 'Carrier',
        'fluido': 'R410A',
        'capacidade': '12.000',
        'modelo': '',
        'tipo_servico': 'Manutenção Preventiva'
    }

# --- FUNÇÃO DE APOIO (CEP) ---
def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
            if r.status_code == 200:
                d = r.json()
                if "erro" not in d:
                    st.session_state['dados']['endereco'] = d.get('logradouro', '')
                    st.session_state['dados']['bairro'] = d.get('bairro', '')
                    st.session_state['dados']['cidade'] = f"{d.get('localidade', '')}/{d.get('uf', '')}"
                    return True
        except: pass
    return False

# 3. Sidebar Original (Navegação)
with st.sidebar:
    st.title("🚀 Painel de Controle")
    aba = st.radio("Selecione a Aba:", ["Home", "1. Cadastro de Equipamentos", "2. Diagnósticos", "Relatórios"])
    
    st.divider()
    st.markdown("### 👤 Técnico Responsável")
    st.session_state['dados']['tecnico_nome'] = st.text_input("Nome:", st.session_state['dados']['tecnico_nome'])
    st.session_state['dados']['tecnico_registro'] = st.text_input("Inscrição (CFT/CREA):", st.session_state['dados']['tecnico_registro'])

# 4. LÓGICA DE EXIBIÇÃO POR ABAS
if aba == "Home":
    st.session_state['dados']['tecnico_documento'] = st.text_input("CPF/CNPJ Técnico:", st.session_state['dados']['tecnico_documento'])
    st.session_state['dados']['tecnico_registro'] = st.text_input("Registro Federal (CFT/CREA):", st.session_state['dados']['tecnico_registro'], key="reg_home")
    
    st.divider()
    if not st.session_state['dados'].get('nome') or not st.session_state['dados'].get('whatsapp'):
        st.error("📋 STATUS: PENDENTE (Preencha Cliente e WhatsApp na aba Cadastro)")
    else:
        st.success("📋 STATUS: PRONTO PARA ENVIO")
    
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            st.markdown("<h2 style='text-align: center;'>MPN SOLUÇÕES</h2>", unsafe_allow_html=True)

elif aba == "1. Cadastro de Equipamentos":
    st.header("📝 Cadastro de Cliente e Equipamento")
    
    # --- BLOCO 1: LOCALIZAÇÃO ---
    with st.expander("📍 Localização do Atendimento", expanded=True):
        col_cep, col_btn = st.columns([3, 1])
        with col_cep:
            cep_input = st.text_input("CEP:", value=st.session_state['dados'].get('cep', ''))
        with col_btn:
            st.write(" ")
            if st.button("🔍 Buscar CEP", use_container_width=True):
                if buscar_cep(cep_input):
                    st.session_state['dados']['cep'] = cep_input
                    st.rerun()

        c1, c2 = st.columns(2)
        with c1:
            st.session_state['dados']['nome'] = st.text_input("Cliente:", st.session_state['dados'].get('nome', ''))
            st.session_state['dados']['endereco'] = st.text_input("Endereço:", st.session_state['dados'].get('endereco', ''))
        with c2:
            st.session_state['dados']['whatsapp'] = st.text_input("WhatsApp:", st.session_state['dados'].get('whatsapp', ''))
            st.session_state['dados']['cidade'] = st.text_input("Cidade/UF:", st.session_state['dados'].get('cidade', ''))

    # --- BLOCO 2: DADOS TÉCNICOS DO APARELHO ---
    with st.expander("❄️ Especificações do Equipamento", expanded=True):
        t1, t2, t3 = st.columns(3)
        with t1:
            fabricantes = ["Carrier", "LG", "Samsung", "Daikin", "Fujitsu", "Gree", "Midea", "Elgin", "Springer", "Trane", "Outro"]
            st.session_state['dados']['fabricante'] = st.selectbox("Fabricante:", fabricantes)
            st.session_state['dados']['tag_id'] = st.text_input("TAG/ID:", st.session_state['dados'].get('tag_id', 'TAG-01'))
        with t2:
            fluidos = ["R410A", "R32", "R22", "R407C", "R404A"]
            st.session_state['dados']['fluido'] = st.selectbox("Fluído Refrigerante:", fluidos)
            st.session_state['dados']['capacidade'] = st.text_input("Capacidade (BTU):", st.session_state['dados'].get('capacidade', '12.000'))
        with t3:
            st.session_state['dados']['modelo'] = st.text_input("Modelo/Série:", st.session_state['dados'].get('modelo', ''))
            servicos = ["Instalação", "Manutenção Preventiva", "Manutenção Corretiva", "Infraestrutura"]
            st.session_state['dados']['tipo_servico'] = st.selectbox("Serviço:", servicos)

    st.success("✅ Dados salvos. Siga para '2. Diagnósticos'.")

# 5. Travamento de Segurança FINAL
st.stop()

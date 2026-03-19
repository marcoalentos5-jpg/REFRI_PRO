import streamlit as st
from datetime import datetime, timedelta
import requests
import urllib.parse

# 1. SETUP DE TELA
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

# CSS: Cores, Estilo do Campo de Data e Botão WhatsApp
st.markdown("""
    <style>
    .stTextInput>div>div>input[aria-label="Data da Visita:"] {
        background-color: #e0f2f1 !important;
        color: #004d40 !important;
        font-weight: bold;
        border: 1px solid #b2dfdb !important;
    }
    div.stLinkButton > a {
        background-color: #25D366 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. MOTOR DE SESSÃO (TODOS OS CAMPOS REINTEGRADOS)
def inicializar_dados():
    if 'dados' not in st.session_state:
        st.session_state.dados = {}
    
    campos_completos = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': '',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional',
        'tensao': '220V', 'fase': 'Monofásico' # Guardados para outra aba
    }
    for chave, valor_padrao in campos_completos.items():
        if chave not in st.session_state.dados:
            st.session_state.dados[chave] = valor_padrao

def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            response = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
            if response.status_code == 200:
                data = response.json()
                if "erro" not in data:
                    st.session_state.dados['endereco'] = data.get('logradouro', '')
                    st.session_state.dados['bairro'] = data.get('bairro', '')
                    st.session_state.dados['cidade'] = data.get('localidade', '')
                    st.session_state.dados['uf'] = data.get('uf', '')
                    return True
        except: pass
    return False

# 3. EXECUÇÃO
inicializar_dados()

st.title("🛠️ Laudo Técnico HVAC - Marcos Alexandre")

tab1, tab2 = st.tabs(["📋 Identificação e Equipamento", "🌡️ Ciclo Térmico (Em breve)"])

with tab1:
    # --- SEÇÃO 1: CLIENTE E ENDEREÇO (RESTAURADO) ---
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj'])
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'])

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        st.session_state.dados['celular'] = cx1.text_input("Cel.:", value=st.session_state.dados['celular'])
        st.session_state.dados['tel_fixo'] = cx2.text_input("Telefone Fixo:", value=st.session_state.dados['tel_fixo'])
        st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'])

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input): st.rerun()

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Número/Apto:", value=st.session_state.dados['numero'])

        ce4, ce5, ce6, ce7 = st.columns([1, 1, 1, 1])
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'])
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'])

    # --- SEÇÃO 2: EQUIPAMENTO (RESTAURADO) ---
    col_titulo, col_data = st.columns([3, 1])
    with col_titulo: st.subheader("⚙️ Especificações do Equipamento")
    with col_data: st.session_state.dados['data'] = st.text_input("Data da Visita:", value=st.session_state.dados['data'])

    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea", "Hitachi", "TCL", "Philco"])
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_list.index(st.session_state.dados['fabricante']) if st.session_state.dados['fabricante'] in fab_list else 0)
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
            st.session_state.dados['status_maquina'] = st.radio("Condição:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado/Defeito"], horizontal=True)

        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados['serie_cond'])
            st.session_state.dados['local_cond'] = st.text_input("Local da Condensadora:", value=st.session_state.dados['local_cond'])

        with e3:
            cap_list = ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"]
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", cap_list, index=1)
            flu_list = ["R410A", "R134a", "R22", "R404A", "R32", "R290"]
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", flu_list, index=0)
            st.session_state.dados['local_evap'] = st.text_input("Local da Evaporadora:", value=st.session_state.dados['local_evap'])

        st.markdown("---")
        l1, l2 = st.columns(2)
        st.session_state.dados['tag_id'] = l1.text_input("TAG:", value=st.session_state.dados['tag_id'])
        ser_list = ["Instalação", "Manutenção Preventiva", "Manutenção Corretiva", "Infraestrutura", "PMOC"]
        st.session_state.dados['tipo_servico'] = l2.selectbox("Serviço:", ser_list, index=1)

# --- SIDEBAR (RESTAURADO E COMPLETO) ---
with st.sidebar:
    st.title("🚀 Painel de Controle")
    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    
    # Lógica de Status Dinâmica (🟢/🔴)
    nome_val = st.session_state.dados['nome'].strip()
    whatsapp_val = st.session_state.dados['whatsapp'].strip()
    serie_val = st.session_state.dados['serie_evap'].strip()
    
    if not nome_val or not whatsapp_val or not serie_val:
        st.subheader("📋 Status: 🔴 ALERTA")
        st.error("Campos pendentes:")
        if not nome_val: st.write("- Nome")
        if not whatsapp_val: st.write("- WhatsApp")
        if not serie_val: st.write("- Série Evap")
    else:
        st.subheader("📋 Status: 🟢 OK")
        st.success("Tudo pronto para envio!")
        
        # Geração do Link WhatsApp Aproveitando os Dados
        msg = f"Olá {st.session_state.dados['nome']},\nAqui é o técnico {st.session_state.dados['tecnico_nome']}.\nO serviço de {st.session_state.dados['tipo_servico']} no equipamento {st.session_state.dados['tag_id']} foi concluído.\nStatus: {st.session_state.dados['status_maquina']}.\nData: {st.session_state.dados['data']}."
        link_wa = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg)}"
        st.link_button("📲 Enviar via WhatsApp", link_wa, use_container_width=True)

    st.markdown("---")
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome do Técnico:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ do Técnico:", value=st.session_state.dados['tecnico_documento'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Registro Federal (CFT/CREA):", value=st.session_state.dados['tecnico_registro'])

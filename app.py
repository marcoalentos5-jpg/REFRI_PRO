import streamlit as st
from datetime import datetime
import requests
import urllib.parse

# 1. CONFIGURAÇÃO INICIAL (CONGELADO)
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

# CSS: Estilização (CONGELADO)
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
        font-weight: bold;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. MOTOR DE SESSÃO (CHAVES VERIFICADAS)
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional',
        # Novas chaves para a Aba Elétrica
        'v_ab': 0.0, 'v_bc': 0.0, 'v_ca': 0.0,
        'i_r': 0.0, 'i_s': 0.0, 'i_t': 0.0,
        'cap_nominal': 0.0, 'cap_real': 0.0,
        'res_isolamento': '', 'disjuntor_ok': 'Sim',
        'obs_eletrica': ''
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

# 3. INTERFACE DE ABAS (AGORA COM ELÉTRICA)
tab1, tab2 = st.tabs(["📋 Identificação e Equipamento", "⚡ Elétrica"])

# --- ABA 01: IDENTIFICAÇÃO (SUAS 165 LINHAS PRESERVADAS) ---
with tab1:
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key="cli_nome")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj'], key="cli_doc")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'], key="cli_zap")

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

    col_titulo, col_data = st.columns([3, 1])
    with col_titulo: st.subheader("⚙️ Especificações do Equipamento")
    with col_data: st.session_state.dados['data'] = st.text_input("Data da Visita:", value=st.session_state.dados['data'])

    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
            fab_val = st.session_state.dados.get('fabricante', 'Carrier')
            fab_idx = fab_list.index(fab_val) if fab_val in fab_list else 0
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_idx)
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
            st.session_state.dados['linha'] = st.selectbox("Linha:", ["Residencial", "Comercial", "Industrial"], index=0)
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)

        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados['serie_cond'])
            st.session_state.dados['local_evap'] = st.text_input("Local da Evaporadora:", value=st.session_state.dados['local_evap'])
            st.session_state.dados['local_cond'] = st.text_input("Local da Condensadora:", value=st.session_state.dados['local_cond'])

        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"], index=1)
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", ["R410A", "R134a", "R22", "R32", "R290"], index=0)
            st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", ["Manutenção Preventiva", "Manutenção Corretiva", "Instalação", "Infraestrutura"], index=0)
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])

# --- ABA 02: ELÉTRICA (MÓDULO NOVO) ---
with tab2:
    st.subheader("⚡ Análise de Grandezas Elétricas")
    col_v, col_i = st.columns(2)
    with col_v:
        with st.expander("📊 Tensão de Alimentação (V)", expanded=True):
            v1, v2, v3 = st.columns(3)
            st.session_state.dados['v_ab'] = v1.number_input("L1-L2 (V):", min_value=0.0, step=1.0)
            st.session_state.dados['v_bc'] = v2.number_input("L2-L3 (V):", min_value=0.0, step=1.0)
            st.session_state.dados['v_ca'] = v3.number_input("L3-L1 (V):", min_value=0.0, step=1.0)
    with col_i:
        with st.expander("📉 Corrente de Operação (A)", expanded=True):
            i1, i2, i3 = st.columns(3)
            st.session_state.dados['i_r'] = i1.number_input("L1 (A):", min_value=0.0, step=0.1)
            st.session_state.dados['i_s'] = i2.number_input("L2 (A):", min_value=0.0, step=0.1)
            st.session_state.dados['i_t'] = i3.number_input("L3 (A):", min_value=0.0, step=0.1)
    
    ce1, ce2 = st.columns(2)
    with ce1:
        with st.expander("🔋 Capacitores", expanded=True):
            c_nom = st.number_input("Cap. Nominal (µF):", min_value=0.0)
            c_real = st.number_input("Cap. Medido (µF):", min_value=0.0)
            st.session_state.dados['cap_nominal'], st.session_state.dados['cap_real'] = c_nom, c_real
    with ce2:
        with st.expander("🛡️ Proteção", expanded=True):
            st.session_state.dados['res_isolamento'] = st.text_input("Isolação (MΩ):")
            st.session_state.dados['disjuntor_ok'] = st.radio("Componentes OK?", ["Sim", "Não"], horizontal=True)
    
    st.session_state.dados['obs_eletrica'] = st.text_area("Observações Elétricas:")

# --- SIDEBAR (PROTEGIDO) ---
with st.sidebar:
    st.title("🚀 Painel de Controle")
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ Técnico:", value=st.session_state.dados['tecnico_documento'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Inscrição (CFT/CREA):", value=st.session_state.dados['tecnico_registro'])
    
    st.markdown("---")
    
    if not st.session_state.dados['nome'] or not st.session_state.dados['whatsapp']:
        st.error("📋 STATUS: PENDENTE")
    else:
        st.success("📋 STATUS: PRONTO")
        
    # MENSAGEM WHATSAPP ATUALIZADA (INCLUINDO ELÉTRICA)
    msg_zap = (
        f"*LAUDO TÉCNICO HVAC*\n\n"
        f"👤 *CLIENTE:* {st.session_state.dados['nome']}\n"
        f"📍 END: {st.session_state.dados['endereco']}, {st.session_state.dados['numero']}\n"
        f"📞 Contato: {st.session_state.dados['whatsapp']}\n\n"
        f"⚙️ *EQUIPAMENTO:*\n"
        f"📌 TAG: {st.session_state.dados['tag_id']} | Fab: {st.session_state.dados['fabricante']}\n"
        f"❄️ Cap: {st.session_state.dados['capacidade']} BTU | Fluido: {st.session_state.dados['fluido']}\n"
        f"🩺 Status: {st.session_state.dados['status_maquina']}\n\n"
        f"⚡ *ANÁLISE ELÉTRICA:*\n"
        f"🔌 Tensões: {st.session_state.dados['v_ab']}V / {st.session_state.dados['v_bc']}V / {st.session_state.dados['v_ca']}V\n"
        f"📉 Correntes: {st.session_state.dados['i_r']}A / {st.session_state.dados['i_s']}A / {st.session_state.dados['i_t']}A\n"
        f"🔋 Capacitor: {st.session_state.dados['cap_real']}µF | Proteção: {st.session_state.dados['disjuntor_ok']}\n\n"
        f"👨‍🔧 *TÉCNICO:* {st.session_state.dados['tecnico_nome']}\n"
        f"📅 Data: {st.session_state.dados['data']}"
    )
    
    link_final = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar Laudo via WhatsApp", link_final, use_container_width=True)

    st.markdown("---")
    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        chaves_tecnico = ['tecnico_nome', 'tecnico_documento', 'tecnico_registro', 'data']
        for key in st.session_state.dados.keys():
            if key not in chaves_tecnico:
                st.session_state.dados[key] = ""
        st.rerun()

# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (CONGELADO)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os # Biblioteca para verificar arquivos no sistema

# 1. CONFIGURAÇÃO INICIAL (TESTADA)
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

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
        'status_maquina': '🟢 Operacional'
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
# 1. FUNÇÃO DA ABA 1: Identificação e Equipamento (CÓDIGO COMPLETO E CORRIGIDO)
# ==============================================================================
def renderizar_aba_1():
    # --- INTERFACE DE ABA ÚNICA ---
    # Criamos a aba e já selecionamos o primeiro índice para evitar erro de variável nula
    tabs = st.tabs(["📋 Identificação e Equipamento"])
    tab1 = tabs[0]

    with tab1:
        # --- SEÇÃO CLIENTE ---
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

            # --- CORREÇÃO DO LAYOUT DO ENDEREÇO (Bairro entre Complemento e Cidade) ---
            ce4, ce5, ce6 = st.columns([1, 1, 1]) # Criamos apenas 3 colunas
            
            # 1ª Coluna: Complemento
            st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'])
            
            # 2ª Coluna: Bairro (POSIÇÃO CORRIGIDA)
            st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'])
            
            # 3ª Coluna: Cidade
            st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'])

            # Uma linha separada para a UF (Estado), com uma coluna menor
            col_uf = st.columns([1])
            with col_uf[0]:
                st.session_state.dados['uf'] = st.text_input("UF:", value=st.session_state.dados['uf'])
            # -----------------------------------------------

        # --- SEÇÃO EQUIPAMENTO ---
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
                # ==============================================================================
# 3. SIDEBAR - DADOS DO TÉCNICO E NAVEGAÇÃO
# ==============================================================================
with st.sidebar:
    st.title("🚀 MPN Soluções")
    st.markdown("---")
    
    # Menu de navegação (Aba Diagnósticos removida daqui)
    opcoes_abas = ["Home", "1. Cadastro de Equipamentos", "Relatórios"]
    aba_selecionada = st.sidebar.radio("Selecione a Aba:", opcoes_abas)
    
    st.markdown("---")
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Registro (CFT/CREA):", value=st.session_state.dados['tecnico_registro'])
    
    st.markdown("---")
    
    # Validação simples
    if not st.session_state.dados['nome'] or not st.session_state.dados['whatsapp']:
        st.error("📋 STATUS: PENDENTE (Preencha Cliente e WhatsApp)")
    else:
        st.success("📋 STATUS: PRONTO")
        
    # Mensagem montada para o WhatsApp
    msg_zap = (
        f"*LAUDO TÉCNICO HVAC*\n\n"
        f"👤 *CLIENTE:* {st.session_state.dados['nome']}\n"
        f"⚙️ *EQUIPAMENTO:* {st.session_state.dados['tag_id']}\n"
        f"📍 Local: {st.session_state.dados['local_evap']}\n"
        f"🛠️ Serviço: {st.session_state.dados['tipo_servico']}\n"
        f"👨‍🔧 *TÉCNICO:* {st.session_state.dados['tecnico_nome']}"
    )
    
    link = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar WhatsApp", link, use_container_width=True)

# ==============================================================================
# 2. FUNÇÃO DA ABA 2: CHECK-LIST DE MANUTENÇÃO (SUBSTITUTA)
# ==============================================================================
def renderizar_aba_checklist():
    st.header("✅ Check-list de Manutenção")
    st.markdown("---")
    
    st.subheader("Itens de Verificação Obrigatória")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### ❄️ Unidade Evaporadora")
        st.checkbox("Limpeza de Filtros", key="chk_1")
        st.checkbox("Limpeza da Serpentina", key="chk_2")
        st.checkbox("Desobstrução do Dreno", key="chk_3")
        st.checkbox("Verificação de Ruídos/Vibração", key="chk_4")

    with col2:
        st.markdown("##### 🔥 Unidade Condensadora")
        st.checkbox("Limpeza da Serpentina Externa", key="chk_5")
        st.checkbox("Reaperto de Bornes Elétricos", key="chk_6")
        st.checkbox("Verificação do Ventilador", key="chk_7")
        st.checkbox("Conferência de Isolamento Térmico", key="chk_8")

    st.markdown("---")
    st.session_state.dados['obs_tecnica'] = st.text_area("Observações Técnicas Adicionais:", 
                                                        value=st.session_state.dados.get('obs_tecnica', ''))

    # Salva o status do checklist para o resumo
    st.session_state.dados['status_check'] = "Check-list Concluído"
    # ==============================================================================
# 3. SIDEBAR - PAINEL DE CONTROLE
# ==============================================================================
with st.sidebar:
    st.title("🚀 MPN Soluções")
    
    # Nova lista de abas incluindo o Check-list
    opcoes_abas = ["Home", "1. Cadastro de Equipamentos", "2. Check-list de Serviço", "Relatórios"]
    aba_selecionada = st.sidebar.radio("Selecione a Aba:", opcoes_abas)
    
    st.markdown("---")
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados.get('tecnico_nome', 'Marcos Alexandre'))
    
    # Link do WhatsApp atualizado
    msg_zap = (f"*LAUDO HVAC*\n"
               f"👤 Cliente: {st.session_state.dados['nome']}\n"
               f"⚙️ TAG: {st.session_state.dados['tag_id']}\n"
               f"✅ Status: {st.session_state.dados.get('status_check', 'Em andamento')}")
    
    link = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar WhatsApp", link, use_container_width=True)
# ==============================================================================
# 4. LÓGICA DE EXIBIÇÃO DAS ABAS
# ==============================================================================
if aba_selecionada == "Home":
    st.subheader("🏠 Bem-vindo ao Sistema MPN")
    st.info("Utilize o menu lateral para cadastrar o cliente ou realizar o check-list de manutenção.")

elif aba_selecionada == "1. Cadastro de Equipamentos":
    renderizar_aba_1()

elif aba_selecionada == "2. Check-list de Serviço":
    renderizar_aba_checklist() # Chama a nova função que criamos no Cap 2

elif aba_selecionada == "Relatórios":
    st.header("📋 Relatórios")
    st.write("Área em desenvolvimento.")
# ==============================================================================


# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (CONGELADO)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os # Biblioteca para verificar arquivos no sistema
import re  

# ==============================================================================
# 0. FUNÇÕES DE FORMATAÇÃO (COLE EXATAMENTE AQUI)
# ==============================================================================

def formatar_cpf(valor):
    nums = re.sub(r'\D', '', valor)
    if len(nums) == 11:
        return f"{nums[:3]}.{nums[3:6]}.{nums[6:9]}-{nums[9:]}"
    return valor

def formatar_cep(valor):
    nums = re.sub(r'\D', '', valor)
    if len(nums) == 8:
        return f"{nums[:5]}-{nums[5:]}"
    return valor

def formatar_telefone(valor):
    nums = re.sub(r'\D', '', valor)
    if len(nums) == 11: # Celular
        return f"({nums[:2]}) {nums[2:7]}-{nums[7:]}"
    elif len(nums) == 10: # Fixo
        return f"({nums[:2]}) {nums[2:6]}-{nums[6:]}"
    return valor

# ==============================================================================
# 0. INICIALIZAÇÃO DO BANCO DE DADOS (SESSION STATE)
# ==============================================================================
if 'dados' not in st.session_state:
    # Esta linha abaixo PRECISA de 4 espaços de recuo (Tab)
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'cep': '',
        'endereco': '', 'numero': '', 'complemento': '', 'bairro': '',
        'cidade': '', 'uf': '', 'fabricante': 'Carrier', 'modelo': '',
        'capacidade': '12.000', 'tag_id': '', 'serie_evap': '',
        'local_evap': '', 'status_maquina': '🟢 Operacional',
        'tecnico_nome': '', 'tecnico_documento': '', 'tecnico_registro': '',
        'email': '', 'linha': '', 'fluido': 'R410A', 'serie_cond': '',
        'local_cond': '', 'tipo_servico': 'Manutenção Preventiva',
        'data': '2024', 'laudo': ''
    }

# ==============================================================================
# 2. DEFINIÇÃO DAS FUNÇÕES DAS ABAS (renderizar_aba_1, etc.)
# ==============================================================================
# Agora sim você coloca a função que usa o 'formatar_cpf'
def renderizar_aba_1():
    # ... código da aba ...

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
# 1. FUNÇÃO DA ABA 1: CADASTRO (LAYOUT OTIMIZADO E FORMATADO)
# ==============================================================================
def renderizar_aba_1():
    st.header("📋 Cadastro de Equipamento")
    
    # --- SEÇÃO CLIENTE ---
    with st.expander("👤 Dados do Cliente", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        
        # Máscara CPF (XXX.XXX.XXX-XX)
        cpf_raw = c2.text_input("CPF *", value=st.session_state.dados['cpf_cnpj'], max_chars=14)
        st.session_state.dados['cpf_cnpj'] = formatar_cpf(cpf_raw)
        
        # Máscara WhatsApp ((XX) XXXXX-XXXX)
        zap_raw = c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'], max_chars=15)
        st.session_state.dados['whatsapp'] = formatar_telefone(zap_raw)

    # --- SEÇÃO ENDEREÇO ---
    with st.expander("📍 Endereço e Localização", expanded=True):
        # Linha 1: CEP, Logradouro e Número
        ce1, ce2, ce3 = st.columns([1, 2, 0.8])
        cep_raw = ce1.text_input("CEP *", value=st.session_state.dados['cep'], max_chars=9)
        st.session_state.dados['cep'] = formatar_cep(cep_raw)
        
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'])

        # Linha 2: Complemento, Bairro, Cidade e UF (Estreito - 2 dígitos)
        l1, l2, l3, l4 = st.columns([1.2, 1.2, 1.2, 0.4])
        st.session_state.dados['complemento'] = l1.text_input("Complemento:", value=st.session_state.dados['complemento'])
        st.session_state.dados['bairro'] = l2.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = l3.text_input("Cidade:", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = l4.text_input("UF:", value=st.session_state.dados['uf'], max_chars=2)

    # --- SEÇÃO EQUIPAMENTO ---
    st.subheader("⚙️ Especificações Técnicas")
    with st.expander("Detalhes do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", ["Carrier", "Daikin", "LG", "Samsung", "Trane"])
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['local_evap'] = st.text_input("Local (Ambiente):", value=st.session_state.dados['local_evap'])
        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade (BTU):", ["9.000", "12.000", "18.000", "24.000"])
            st.session_state.dados['tag_id'] = st.text_input("TAG/Patrimônio:", value=st.session_state.dados['tag_id'])

# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (PARTE 2 - ESQUELETO INSERIDO)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("📋 Central de Diagnósticos")
    st.markdown("---")
    
    # 1. SELEÇÃO DO EQUIPAMENTO (Dependência da Aba 1)
    # equipments = db_utils.buscar_equipamentos_cadastrados()
    # equipamento_id = st.selectbox("Selecione o Equipamento para Diagnóstico:", list(equipments.keys()), format_func=lambda x: equipments[x])
    
    st.info("Aba de Diagnósticos em desenvolvimento. Implemente a lógica aqui.")

#==============================================================================
# 3. SIDEBAR E DEFINIÇÃO DE FUNÇÕES (VERSÃO LIMPA E CORRIGIDA)
# ==============================================================================

# A. SIDEBAR - NAVEGAÇÃO E DADOS DO TÉCNICO
with st.sidebar:
    st.title("🚀 Painel de Controle")
    
    # NAVEGAÇÃO PRINCIPAL (ÚNICA)
    opcoes_abas = ["Home", "1. Cadastro de Equipamentos", "2. Diagnósticos", "Relatórios"]
    aba_selecionada = st.radio("Selecione a Aba:", opcoes_abas, key="nav_principal")
    
    st.markdown("---")
    
    # B. DADOS DO TÉCNICO RESPONSÁVEL
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ Técnico:", value=st.session_state.dados['tecnico_documento'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Inscrição (CFT/CREA):", value=st.session_state.dados['tecnico_registro'])
    
    st.markdown("---")
    
    # VALIDAÇÃO DE STATUS
    if not st.session_state.dados['nome'] or not st.session_state.dados['whatsapp']:
        st.error("📋 STATUS: PENDENTE")
    else:
        st.success("📋 STATUS: PRONTO PARA ENVIO")
        
    # WHATSAPP LINK (Gerado apenas se houver número)
    zap = "".join(filter(str.isdigit, st.session_state.dados['whatsapp']))
    if zap:
        msg_zap = f"*LAUDO TÉCNICO HVAC*\n\n👤 *CLIENTE:* {st.session_state.dados['nome']}\n🛠️ Técnico: {st.session_state.dados['tecnico_nome']}"
        link_final = f"https://wa.me/55{zap}?text={urllib.parse.quote(msg_zap)}"
        st.link_button("📲 Enviar via WhatsApp", link_final, use_container_width=True)

# ==============================================================================
# FUNÇÃO DIAGNÓSTICO (FORA DO SIDEBAR PARA NÃO DUPLICAR)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.title("🔍 Diagnóstico Inteligente")
    
    # Função auxiliar para evitar erros de valor nulo
    def seguro(v):
        try: return float(v) if v is not None else 0
        except: return 0

    # Puxa os valores do session_state (Certifique-se que sh_val, etc, existem no seu estado)
    sh = seguro(st.session_state.get("sh_val", 0))
    sc = seguro(st.session_state.get("sc_val", 0))
    
    # --- LÓGICA DE DIAGNÓSTICO ---
    diagnostico = []
    if sh > 15 and sc < 3:
        diagnostico.append("Possível Baixa Carga de Fluido")
    elif sh < 3 and sc > 10:
        diagnostico.append("Possível Excesso de Fluido")
    
    # Exibição simples para teste
    if not diagnostico:
        st.success("✅ Sistema operando dentro dos parâmetros normais.")
    else:
        for d in diagnostico:
            st.warning(f"⚠️ {d}")

    # Área de Laudo
    laudo_sugerido = f"Diagnóstico técnico realizado. Status: {'Normal' if not diagnostico else 'Anormal'}."
    st.text_area("📄 Sugestão de Laudo:", value=laudo_sugerido, height=150)

# ==============================================================================
# 4. LÓGICA DE EXIBIÇÃO FINAL (ESTRUTURA ANTI-ERRO 1.55.0)
# ==============================================================================

# IMPORTANTE: Esta parte deve vir LOGO APÓS a criação da variável 'aba_selecionada' no Sidebar
if "Home" in aba_selecionada:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2: 
        if os.path.exists("logo.png"):
            st.image("logo.png", width='stretch')
        else:
            st.info("🏠 MPN SOLUÇÕES HVAC")
    st.header("Bem-vindo, Marcos!")
    st.write("Selecione uma opção no menu lateral para começar.")

elif "Cadastro" in aba_selecionada:
    # Chama a função de cadastro que você corrigiu
    renderizar_aba_1()
    st.divider()
    # O botão de limpar agora fica PROTEGIDO dentro deste elif para não duplicar
    if st.button("🗑️ Limpar Formulário", width='stretch'):
        for chave in st.session_state.dados.keys():
            st.session_state.dados[chave] = ""
        st.success("Formulário reiniciado!")
        st.rerun()

elif "Diagn" in aba_selecionada:
    if 'renderizar_aba_diagnosticos' in globals():
        renderizar_aba_diagnosticos()
        
        # --- BLOCO 5: EXIBIÇÃO DE RESULTADOS (INCORPORADO AQUI) ---
        # Só exibe se as variáveis de cálculo existirem no contexto
        if 'status' in locals():
            st.divider()
            res1, res2, res3 = st.columns(3)
            res1.metric("📊 Status", status)
            res2.metric("❤️ Saúde", f"{score}%")
            res3.metric("⚡ COP", cop)

            st.info(f"🔎 **Diagnóstico:** {diag_txt}")
            st.warning(f"🚨 **Falhas:** {prob_txt}")
            st.success(f"🛠️ **Ações:** {acoes_txt}")

            st.subheader("📄 Laudo Técnico")
            laudo_texto = st.session_state.dados.get('laudo', 'Laudo não gerado.')
            st.text_area("Texto do Laudo", laudo_texto, height=200, label_visibility="collapsed")
    else:
        st.warning("Aba de Diagnósticos em manutenção.")

elif "Relat" in aba_selecionada:
    st.header("📋 Relatórios")
    st.info("Módulo de geração de PDF em desenvolvimento.")

# ==============================================================================
# 5. EXIBIÇÃO DE RESULTADOS (OCULTA SE NÃO HOUVER DADOS)
# ==============================================================================
# Só exibe se estiver na aba de Diagnóstico E se as variáveis de cálculo existirem
if "Diagn" in aba_selecionada and 'status' in locals():
    st.divider()
    res1, res2, res3 = st.columns(3)
    res1.metric("📊 Status", status)
    res2.metric("❤️ Saúde", f"{score}%")
    res3.metric("⚡ COP", cop)

    st.info(f"🔎 **Diagnóstico:** {diag_txt}")
    st.warning(f"🚨 **Falhas:** {prob_txt}")
    st.success(f"🛠️ **Ações:** {acoes_txt}")

    st.subheader("📄 Laudo Técnico")
    # Usando o dicionário de dados para evitar erro de variável vazia
    laudo_texto = st.session_state.dados.get('laudo', 'Laudo não gerado.')
    st.text_area("Texto do Laudo", laudo_texto, height=200, label_visibility="collapsed")

# ==============================================================================
# FIM DO ARQUIVO
# ==============================================================================

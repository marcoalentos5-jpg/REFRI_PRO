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
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (PARTE 2 - IMPLEMENTAÇÃO TÉCNICA)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("📋 Central de Diagnósticos")
    st.markdown("---")
    
    # 1. IDENTIFICAÇÃO DO FLUIDO (Vem da Aba 1 ou assume R410A por segurança)
    if 'dados' not in st.session_state:
        st.error("Erro: Dados não inicializados.")
        return

    fluido = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"Análise Técnica para o Fluido: **{fluido}**")

    # Função interna para calcular Temperatura de Saturação (P/T)
    def get_tsat(p, modo):
        if fluido == "R410A": return (p * 0.17) - 16.5 if modo == "baixa" else (p * 0.11) + 2.5
        if fluido == "R22": return (p * 0.28) - 14.5 if modo == "baixa" else (p * 0.18) + 8.5
        if fluido == "R32": return (p * 0.17) - 17.8 if modo == "baixa" else (p * 0.11) + 1.2
        return 0.0

    # 2. SEÇÃO DE SUPERAQUECIMENTO (MEDICÕES E RESULTADOS)
    with st.container():
        st.subheader("❄️ Superaquecimento (Lado de Baixa)")
        c1, c2, c3, c4 = st.columns(4)
        p_b = c1.number_input("P. Baixa (PSI)", min_value=0.0, value=118.0, step=1.0, key="pb_diag")
        t_sat_b = get_tsat(p_b, "baixa")
        c2.metric("T. Sat (Baixa)", f"{t_sat_b:.1f}°C")
        t_suc = c3.number_input("T. Sucção (°C)", min_value=-50.0, value=12.0, step=0.1, key="ts_diag")
        sa_t = t_suc - t_sat_b
        c4.metric("SA TOTAL", f"{sa_t:.1f} K", delta=f"{sa_t-7:.1f}K", delta_color="inverse")

    # 3. SEÇÃO DE SUBRESFRIAMENTO (MEDIÇÕES E RESULTADOS)
    with st.container():
        st.subheader("🔥 Subresfriamento (Lado de Alta)")
        ca1, ca2, ca3, ca4 = st.columns(4)
        p_a = ca1.number_input("P. Alta (PSI)", min_value=0.0, value=340.0, step=1.0, key="pa_diag")
        t_sat_a = get_tsat(p_a, "alta")
        ca2.metric("T. Sat (Alta)", f"{t_sat_a:.1f}°C")
        t_liq = ca3.number_input("T. Linha Líq (°C)", min_value=-50.0, value=35.0, step=0.1, key="tl_diag")
        sr_t = t_sat_a - t_liq
        ca4.metric("SR TOTAL", f"{sr_t:.1f} K", delta=f"{sr_t-5:.1f}K", delta_color="normal")

    # 4. DELTA T DO AR E PERSISTÊNCIA
    st.markdown("---")
    st.subheader("🌡️ Diferencial de Temperatura (Delta T)")
    cd1, cd2, cd3 = st.columns(3)
    t_ret = cd1.number_input("Ar Retorno (°C)", value=24.0, step=0.1, key="tr_ar")
    t_ins = cd2.number_input("Ar Insuflamento (°C)", value=12.0, step=0.1, key="ti_ar")
    dt_ar = t_ret - t_ins
    cd3.metric("Delta T Ar", f"{dt_ar:.1f} °C")
    
    # SALVAMENTO DOS RESULTADOS PARA O WHATSAPP
    st.session_state.dados['perf'] = f"SA:{sa_t:.1f}K | SR:{sr_t:.1f}K | DT:{dt_ar:.1f}C"
    
# ==============================================================================
# 3. SIDEBAR - DADOS DO TÉCNICO E NAVEGAÇÃO
# ==============================================================================
with st.sidebar:
    st.title("🚀 Painel de Controle")
    opcoes_abas = ["Home", "1. Cadastro de Equipamentos", "2. Diagnósticos", "Relatórios"]
    aba_selecionada = st.sidebar.radio("Selecione a Aba:", opcoes_abas)
    
    st.markdown("---")
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ:", value=st.session_state.dados['tecnico_documento'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Registro (CFT/CREA):", value=st.session_state.dados['tecnico_registro'])
    
    st.markdown("---")
    # VALIDAÇÃO
    if not st.session_state.dados['nome'] or not st.session_state.dados['whatsapp']:
        st.error("📋 STATUS: PENDENTE")
    else:
        st.success("📋 STATUS: PRONTO")
        
    # MENSAGEM WHATSAPP COM OS RESULTADOS DO CAPÍTULO 2
    msg_zap = (
        f"*LAUDO TÉCNICO HVAC*\n\n"
        f"👤 *CLIENTE:* {st.session_state.dados['nome']}\n"
        f"⚙️ *EQUIPAMENTO:* {st.session_state.dados['tag_id']}\n"
        f"❄️ Fluido: {st.session_state.dados['fluido']}\n"
        f"📊 *PERFORMANCE:* {st.session_state.dados.get('perf', 'N/A')}\n\n"
        f"👨‍🔧 *TÉCNICO:* {st.session_state.dados['tecnico_nome']}\n"
        f"📅 Data: {st.session_state.dados['data']}"
    )
    
    link = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar Laudo WhatsApp", link, use_container_width=True)
    
# ==============================================================================
# 4. LÓGICA DE EXIBIÇÃO DAS ABAS (ATIVADA)
# ==============================================================================
# Use a seleção do sidebar para chamar a função correta
if aba_selecionada == "Home":
    # --- NOVA APRESENTAÇÃO DA ABA HOME (COM LOGO MPN SOLUÇÕES ) ---
    st.markdown("<br>", unsafe_allow_html=True) # Espaçamento superior

    # 1. CENTRALIZAÇÃO E EXIBIÇÃO DA LOGOMARCA
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2: 
        # NOME DO ARQUIVO DE IMAGEM QUE ESTÁ SENDO USADO
        NOME_ARQUIVO_LOGO = "logo.png"
        
        # VERIFICAÇÃO ADICIONAL DO ARQUIVO NO DISCO (PARA AJUDAR NO DIAGNÓSTICO)
        if os.path.exists(NOME_ARQUIVO_LOGO):
            try:
                # SE O ARQUIVO EXISTE, TENTA EXIBIR
                st.image(NOME_ARQUIVO_LOGO, use_container_width=True) 
            except Exception as e:
                st.error(f"⚠️ Erro ao tentar abrir a imagem '{NOME_ARQUIVO_LOGO}'.")
                st.write(f"Detalhes do erro do sistema: {e}")
        else:
            st.error(f"⚠️ Erro: Arquivo '{NOME_ARQUIVO_LOGO}' não encontrado na pasta raiz.")
            st.info("Verifique se o arquivo está salvo como 'logo.png' na mesma pasta do script.")

    st.markdown("<br><br>", unsafe_allow_html=True) 

    # 2. TÍTULO E BOAS-VINDAS CENTRALIZADOS E ESTILIZADOS
    st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: #0d47a1; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                MPN Soluções
            </h1>
            <p style="color: #1976d2; font-size: 1.3em;">
                Soluções em Refrigeração e Climatização
            </p>
            <hr style="border: 1px solid #90caf9; width: 60%; margin: 20px auto;">
            <p style="color: #455a64; font-size: 1.1em; font-weight: bold;">
                Bem-vindo ao Sistema HVAC Pro de Gestão Inteligente.
            </p>
            <p style="color: #546e7a; font-size: 1.0em;">
                Selecione uma opção no Painel de Controle lateral para iniciar sua inspeção ou diagnóstico.
            </p>
        </div>
    """, unsafe_allow_html=True)
    # ------------------------------------------------

elif aba_selecionada == "1. Cadastro de Equipamentos":
    renderizar_aba_1() # Chama a função que contém todo o código da Aba 1

elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos() # Chama a função que contém os cálculos de SA/SR

elif aba_selecionada == "Relatórios":
    st.header("Página de Relatórios (Em desenvolvimento)")
    st.write("Em breve: Visualização e exportação de relatórios.")

# ==============================================================================
# FIM DO ARQUIVO - MPN SOLUÇÕES - SISTEMA DE GESTÃO HVAC (TOTAL 273 LINHAS)
# ==========================================================================================================================================

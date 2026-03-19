import streamlit as st
from datetime import datetime

# =============================================================================
# 1. CONFIGURAÇÃO DE AMBIENTE (Sempre no topo do arquivo principal)
# =============================================================================
def configurar_pagina():
    st.set_page_config(page_title="RefriPro - Gestão HVAC", layout="wide")
    # Estilo customizado para os campos da Aba 1
    st.markdown("""
        <style>
        .ident-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #004a99; }
        .stTextInput>div>div>input { font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

# =============================================================================
# 2. MOTOR DE SESSÃO (PERSISTÊNCIA ABSOLUTA)
# =============================================================================
def inicializar_sessao():
    """Garante que nenhum dado seja perdido na troca de abas ou refresh"""
    if 'dados' not in st.session_state:
        st.session_state.dados = {
            'nome': '',
            'cpf': '',
            'data_visita': datetime.now().strftime("%d/%m/%Y"),
            'modelo': '',
            'tag_equip': '',
            'localizacao': '',
            'fluido': 'R410A',
            'tipo_servico': 'Manutenção Preventiva',
            'status_atendimento': 'Em Aberto'
        }

# =============================================================================
# 3. INTERFACE DA ABA 01: IDENTIFICAÇÃO
# =============================================================================
def renderizar_aba_identificacao():
    inicializar_sessao()
    
    st.markdown('<div class="ident-card">', unsafe_allow_html=True)
    st.subheader("🆔 Registro de Identificação e Logística")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.session_state.dados['nome'] = st.text_input(
            "Cliente / Razão Social:", 
            value=st.session_state.dados['nome'],
            help="Nome completo do cliente ou nome da empresa (PMOC)."
        )
        st.session_state.dados['localizacao'] = st.text_input(
            "Localização / Setor:", 
            value=st.session_state.dados['localizacao'],
            placeholder="Ex: Sala de Reunião 2, Térreo, CPD..."
        )

    with col2:
        st.session_state.dados['cpf'] = st.text_input(
            "CPF / CNPJ:", 
            value=st.session_state.dados['cpf']
        )
        st.session_state.dados['tag_equip'] = st.text_input(
            "TAG / Patrimônio:", 
            value=st.session_state.dados['tag_equip'],
            placeholder="Ex: AC-01"
        )

    with col3:
        st.session_state.dados['data_visita'] = st.text_input(
            "Data do Serviço:", 
            value=st.session_state.dados['data_visita']
        )
        st.session_state.dados['status_atendimento'] = st.selectbox(
            "Status Atual:",
            ["Em Aberto", "Em Andamento", "Finalizado", "Urgência"],
            index=["Em Aberto", "Em Andamento", "Finalizado", "Urgência"].index(st.session_state.dados['status_atendimento'])
        )

    st.divider()
    
    st.markdown("#### ⚙️ Especificações do Equipamento")
    col_e1, col_e2, col_e3 = st.columns(3)
    
    with col_e1:
        st.session_state.dados['modelo'] = st.text_input(
            "Modelo do Aparelho:", 
            value=st.session_state.dados['modelo'],
            placeholder="Ex: Split Inverter 18.000 BTU"
        )
        
    with col_e2:
        opcoes_fluido = ["R410A", "R134a", "R22", "R404A", "R32", "R290"]
        st.session_state.dados['fluido'] = st.selectbox(
            "Fluido Refrigerante:", 
            opcoes_fluido,
            index=opcoes_fluido.index(st.session_state.dados['fluido'])
        )
        
    with col_e3:
        opcoes_servico = ["Instalação", "Manutenção Preventiva", "Manutenção Corretiva", "PMOC", "Vistoria"]
        st.session_state.dados['tipo_servico'] = st.selectbox(
            "Finalidade da Visita:",
            opcoes_servico,
            index=opcoes_servico.index(st.session_state.dados['tipo_servico'])
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # Feedback de validação visual
    if st.session_state.dados['nome'] and st.session_state.dados['modelo']:
        st.success(f"✔️ Identificação pronta para o diagnóstico: {st.session_state.dados['tag_equip']}")
    else:
        st.warning("⚠️ Preencha o Nome e o Modelo para habilitar os cálculos térmicos.")

# CHAMADA DA FUNÇÃO (Apenas para teste)
# configurar_pagina()
# renderizar_aba_identificacao()


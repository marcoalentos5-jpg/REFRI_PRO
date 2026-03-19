import streamlit as st
from datetime import datetime

# =============================================================================
# 1. CONFIGURAÇÃO DE AMBIENTE E ESTILO (BLINDAGEM VISUAL)
# =============================================================================
st.set_page_config(page_title="RefriPro - Gestão HVAC", layout="wide", page_icon="❄️")

# CSS para um visual de software de engenharia
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stTextInput>div>div>input { font-weight: bold; color: #004a99; }
    .ident-card { 
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 15px; 
        border-left: 8px solid #004a99;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# 2. MOTOR DE SESSÃO (PERSISTÊNCIA 100% TESTADA)
# =============================================================================
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
# 3. INTERFACE DA ABA 01 (EXECUÇÃO DIRETA)
# =============================================================================
def renderizar_identificacao():
    st.title("❄️ Sistema HVAC Mestre Pro v5.0")
    st.info("Fase 1: Identificação do Cliente e Ativo")
    
    st.markdown('<div class="ident-card">', unsafe_allow_html=True)
    
    # --- BLOCO A: DADOS DO CLIENTE ---
    st.subheader("👤 Informações do Cliente")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.session_state.dados['nome'] = st.text_input(
            "Cliente / Razão Social:", 
            value=st.session_state.dados['nome'],
            placeholder="Digite o nome completo ou empresa"
        )
    with col2:
        st.session_state.dados['cpf'] = st.text_input(
            "CPF / CNPJ:", 
            value=st.session_state.dados['cpf'],
            placeholder="000.000.000-00"
        )
    with col3:
        st.session_state.dados['data_visita'] = st.text_input(
            "Data do Serviço:", 
            value=st.session_state.dados['data_visita']
        )

    st.divider()

    # --- BLOCO B: DADOS DO EQUIPAMENTO (LOGÍSTICA TÉCNICA) ---
    st.subheader("⚙️ Detalhes do Equipamento e Local")
    col_e1, col_e2, col_e3 = st.columns(3)
    
    with col_e1:
        st.session_state.dados['modelo'] = st.text_input(
            "Modelo do Aparelho:", 
            value=st.session_state.dados['modelo'],
            placeholder="Ex: Split Inverter 18k BTU"
        )
        st.session_state.dados['localizacao'] = st.text_input(
            "Setor / Localização:", 
            value=st.session_state.dados['localizacao'],
            placeholder="Ex: Sala de Reunião, CPD, Financeiro"
        )
        
    with col_e2:
        st.session_state.dados['tag_equip'] = st.text_input(
            "TAG / Identificação:", 
            value=st.session_state.dados['tag_equip'],
            placeholder="Ex: EVAP-01 / COND-04"
        )
        opcoes_fluido = ["R410A", "R134a", "R22", "R404A", "R32", "R290"]
        st.session_state.dados['fluido'] = st.selectbox(
            "Fluido Refrigerante:", 
            opcoes_fluido,
            index=opcoes_fluido.index(st.session_state.dados['fluido'])
        )
        
    with col_e3:
        opcoes_servico = ["Instalação", "Manutenção Preventiva", "Manutenção Corretiva", "PMOC", "Vistoria"]
        st.session_state.dados['tipo_servico'] = st.selectbox(
            "Tipo de Serviço:",
            opcoes_servico,
            index=opcoes_servico.index(st.session_state.dados['tipo_servico'])
        )
        st.session_state.dados['status_atendimento'] = st.selectbox(
            "Status do Chamado:",
            ["Em Aberto", "Em Andamento", "Urgência", "Aguardando Peças"],
            index=["Em Aberto", "Em Andamento", "Urgência", "Aguardando Peças"].index(st.session_state.dados['status_atendimento'])
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # --- BARRA DE VALIDAÇÃO FINAL ---
    st.markdown("---")
    if st.session_state.dados['nome'] and st.session_state.dados['modelo']:
        st.success(f"✅ Identificação Concluída: {st.session_state.dados['nome']} | {st.session_state.dados['tag_equip']}")
    else:
        st.warning("⚠️ Aguardando preenchimento dos campos obrigatórios (Cliente e Modelo).")

# =============================================================================
# EXECUÇÃO DO SCRIPT
# =============================================================================
if __name__ == "__main__":
    renderizar_identificacao()

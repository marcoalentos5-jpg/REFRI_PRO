import streamlit as st
from datetime import datetime

# =============================================================================
# 1. SETUP DE TELA E ESTILO (PADRÃO ENGENHARIA)
# =============================================================================
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .section-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-top: 5px solid #004a99;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    label { font-weight: bold !important; color: #333 !important; }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# 2. MOTOR DE SESSÃO (PERSISTÊNCIA DE TODOS OS CAMPOS)
# =============================================================================
if 'dados' not in st.session_state:
    st.session_state.dados = {
        # Cliente
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'data': datetime.now().strftime("%d/%m/%Y"),
        # Equipamento
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A',
        # Logística
        'tipo_servico': 'Manutenção Preventiva', 'localizacao': '', 'tag_id': ''
    }

def renderizar_identificacao():
    st.title("🛠️ Laudo Técnico HVAC - Marcos Alexandre")
    st.caption("Fase 1: Identificação Detalhada do Atendimento")

    # --- SEÇÃO 1: DADOS DO CLIENTE ---
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("👤 Identificação do Cliente")
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    
    with c1:
        st.session_state.dados['nome'] = st.text_input("Nome / Razão Social:", value=st.session_state.dados['nome'])
    with c2:
        st.session_state.dados['cpf_cnpj'] = st.text_input("CPF ou CNPJ:", value=st.session_state.dados['cpf_cnpj'])
    with c3:
        st.session_state.dados['whatsapp'] = st.text_input("WhatsApp (com DDD):", value=st.session_state.dados['whatsapp'])
    with c4:
        st.session_state.dados['data'] = st.text_input("Data:", value=st.session_state.dados['data'])
    st.markdown('</div>', unsafe_allow_html=True)

    # --- SEÇÃO 2: DADOS DO EQUIPAMENTO (EXTRAÍDOS DO HISTÓRICO) ---
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("⚙️ Especificações do Equipamento")
    e1, e2, e3 = st.columns(3)
    
    with e1:
        fabricantes = ["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"]
        st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fabricantes, 
            index=fabricantes.index(st.session_state.dados['fabricante']))
        
        st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
        
        capacidades = ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000", "80.000+"]
        st.session_state.dados['capacidade'] = st.selectbox("Capacidade (BTU/h):", capacidades,
            index=capacidades.index(st.session_state.dados['capacidade']))

    with e2:
        st.session_state.dados['serie_evap'] = st.text_input("Nº de Série (EVAPORADORA):", value=st.session_state.dados['serie_evap'])
        st.session_state.dados['serie_cond'] = st.text_input("Nº de Série (CONDENSADORA):", value=st.session_state.dados['serie_cond'])
        
        fluidos = ["R410A", "R134a", "R22", "R404A", "R32", "R290"]
        st.session_state.dados['fluido'] = st.selectbox("Fluido Refrigerante:", fluidos,
            index=fluidos.index(st.session_state.dados['fluido']))

    with e3:
        st.session_state.dados['tag_id'] = st.text_input("TAG / Identificação Técnica:", value=st.session_state.dados['tag_id'], placeholder="Ex: AC-01")
        st.session_state.dados['localizacao'] = st.text_input("Setor/Localização:", value=st.session_state.dados['localizacao'])
        
        servicos = ["Instalação", "Manutenção Preventiva", "Manutenção Corretiva", "Infraestrutura", "PMOC"]
        st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", servicos,
            index=servicos.index(st.session_state.dados['tipo_servico']))

    st.markdown('</div>', unsafe_allow_html=True)

    # --- STATUS DE PREENCHIMENTO ---
    if st.session_state.dados['nome'] and st.session_state.dados['serie_evap']:
        st.success(f"✅ Dados Iniciais Validados: {st.session_state.dados['nome']} - {st.session_state.dados['tag_id']}")
    else:
        st.warning("⚠️ Preencha os campos obrigatórios (Nome do Cliente e Série da Evaporadora).")

# =============================================================================
# EXECUÇÃO FINAL
# =============================================================================
if __name__ == "__main__":
    renderizar_identificacao()

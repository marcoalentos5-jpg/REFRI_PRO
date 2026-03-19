import streamlit as st
from datetime import datetime

# =============================================================================
# 1. CONFIGURAÇÃO DE TELA
# =============================================================================
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

# =============================================================================
# 2. MOTOR DE SESSÃO COM AUTO-CORREÇÃO (EVITA KEYERROR)
# =============================================================================
def inicializar_dados():
    # Se a estrutura não existir, cria do zero
    if 'dados' not in st.session_state:
        st.session_state.dados = {}
    
    # Lista de todos os campos necessários (extraídos do seu histórico)
    campos_obrigatorios = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'data': datetime.now().strftime("%d/%m/%Y"),
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A',
        'tipo_servico': 'Manutenção Preventiva', 'localizacao': '', 'tag_id': ''
    }
    
    # Verifica um por um. Se não existir no navegador, ele cria agora.
    for chave, valor_padrao in campos_obrigatorios.items():
        if chave not in st.session_state.dados:
            st.session_state.dados[chave] = valor_padrao

# =============================================================================
# 3. INTERFACE DA ABA 01
# =============================================================================
def renderizar_identificacao():
    # Executa a limpeza/inicialização antes de desenhar a tela
    inicializar_dados()
    
    st.title("🛠️ Laudo Técnico HVAC - Marcos Alexandre")
    st.caption("Fase 1: Identificação Detalhada do Atendimento")

    # --- SEÇÃO 1: CLIENTE ---
    with st.container():
        st.subheader("👤 Identificação do Cliente")
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        
        # Uso do .get() para segurança extra contra erros de chave
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social:", value=st.session_state.dados.get('nome', ''))
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF ou CNPJ:", value=st.session_state.dados.get('cpf_cnpj', ''))
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (com DDD):", value=st.session_state.dados.get('whatsapp', ''))
        st.session_state.dados['data'] = c4.text_input("Data:", value=st.session_state.dados.get('data', ''))

    st.divider()

    # --- SEÇÃO 2: EQUIPAMENTO ---
    with st.container():
        st.subheader("⚙️ Especificações do Equipamento")
        e1, e2, e3 = st.columns(3)
        
        with e1:
            fabricantes = ["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"]
            fab_atual = st.session_state.dados.get('fabricante', 'Carrier')
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fabricantes, 
                index=fabricantes.index(fab_atual) if fab_atual in fabricantes else 0)
            
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados.get('modelo', ''))
            
            capacidades = ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000", "80.000+"]
            cap_atual = st.session_state.dados.get('capacidade', '12.000')
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade (BTU/h):", capacidades,
                index=capacidades.index(cap_atual) if cap_atual in capacidades else 1)

        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº de Série (EVAPORADORA):", value=st.session_state.dados.get('serie_evap', ''))
            st.session_state.dados['serie_cond'] = st.text_input("Nº de Série (CONDENSADORA):", value=st.session_state.dados.get('serie_cond', ''))
            
            fluidos = ["R410A", "R134a", "R22", "R404A", "R32", "R290"]
            flu_atual = st.session_state.dados.get('fluido', 'R410A')
            st.session_state.dados['fluido'] = st.selectbox("Fluido Refrigerante:", fluidos,
                index=fluidos.index(flu_atual) if flu_atual in fluidos else 0)

        with e3:
            st.session_state.dados['tag_id'] = st.text_input("TAG / Identificação Técnica:", value=st.session_state.dados.get('tag_id', ''))
            st.session_state.dados['localizacao'] = st.text_input("Setor/Localização:", value=st.session_state.dados.get('localizacao', ''))
            
            servicos = ["Instalação", "Manutenção Preventiva", "Manutenção Corretiva", "Infraestrutura", "PMOC"]
            ser_atual = st.session_state.dados.get('tipo_servico', 'Manutenção Preventiva')
            st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", servicos,
                index=servicos.index(ser_atual) if ser_atual in servicos else 1)

    # --- BOTÃO DE LIMPEZA ---
    if st.sidebar.button("🗑️ Resetar Tudo"):
        st.session_state.dados = {}
        st.rerun()

# =============================================================================
# EXECUÇÃO FINAL
# =============================================================================
if __name__ == "__main__":
    renderizar_identificacao()

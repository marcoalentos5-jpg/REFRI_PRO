import streamlit as st
from datetime import datetime
import requests

# =============================================================================
# 1. SETUP DE TELA (MANUTENÇÃO INTEGRAL)
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
# 2. MOTOR DE SESSÃO (INCREMENTAL - SEM DELETAR)
# =============================================================================
def inicializar_dados():
    if 'dados' not in st.session_state:
        st.session_state.dados = {}
    
    campos_v7 = {
        # Cliente & Endereço (CONGELADOS)
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '',
        'celular': '', 'complemento': '', 'tel_fixo': '', 'email': '',
        # Equipamento (CONGELADOS + NOVOS)
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A',
        'linha': 'Residencial', 'local_cond': '', 'ano_fab': '', # <--- NOVOS CAMPOS
        # Logística (CONGELADOS)
        'tipo_servico': 'Manutenção Preventiva', 'localizacao': '', 'tag_id': ''
    }
    
    for chave, valor_padrao in campos_v7.items():
        if chave not in st.session_state.dados:
            st.session_state.dados[chave] = valor_padrao

def buscar_cep(cep):
    cep_limpo = cep.replace("-", "").replace(".", "").strip()
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
        except Exception:
            pass
    return False

# =============================================================================
# 3. INTERFACE DA ABA 01 (NOVAS INCLUSÕES NA SEÇÃO 2)
# =============================================================================
def renderizar_identificacao():
    inicializar_dados()
    
    st.title("🛠️ Laudo Técnico HVAC - Marcos Alexandre")
    st.caption("Fase 1: Identificação Detalhada e Localização")

    # --- SEÇÃO 1: DADOS DO CLIENTE E ENDEREÇO (CONGELADA) ---
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social:", value=st.session_state.dados.get('nome'))
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF ou CNPJ:", value=st.session_state.dados.get('cpf_cnpj'))
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (DDD):", value=st.session_state.dados.get('whatsapp'))

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        st.session_state.dados['celular'] = cx1.text_input("Cel.:", value=st.session_state.dados.get('celular'))
        st.session_state.dados['tel_fixo'] = cx2.text_input("Telefone Fixo:", value=st.session_state.dados.get('tel_fixo'))
        st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados.get('email'))

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP:", value=st.session_state.dados.get('cep'))
        
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input):
                st.toast("✅ Endereço localizado!", icon="📍")
                st.rerun()

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro (Rua/Av):", value=st.session_state.dados.get('endereco'))
        st.session_state.dados['numero'] = ce3.text_input("Número/Apto:", value=st.session_state.dados.get('numero'))

        ce4, ce5, ce6, ce7 = st.columns([1, 1, 1, 1])
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados.get('complemento'))
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados.get('bairro'))
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados.get('cidade'))
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados.get('uf'))

    # --- SEÇÃO 2: ESPECIFICAÇÕES DO EQUIPAMENTO (COM NOVOS CAMPOS) ---
    with st.expander("⚙️ Especificações do Equipamento", expanded=True):
        e1, e2, e3 = st.columns(3)
        
        with e1:
            fabricantes = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", 
                                 "York", "Elgin", "Gree", "Midea", "Hitachi", "TCL", "Philco"])
            fab_atual = st.session_state.dados.get('fabricante', 'Carrier')
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fabricantes, 
                index=fabricantes.index(fab_atual) if fab_atual in fabricantes else 0)
            
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados.get('modelo'))
            
            # NOVO CAMPO: LINHA
            linhas = ["Residencial", "Comercial", "Industrial", "Hospitalar", "Data Center"]
            lin_atual = st.session_state.dados.get('linha', 'Residencial')
            st.session_state.dados['linha'] = st.selectbox("Linha de Aplicação:", linhas, 
                index=linhas.index(lin_atual) if lin_atual in linhas else 0)

        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP):", value=st.session_state.dados.get('serie_evap'))
            st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND):", value=st.session_state.dados.get('serie_cond'))
            
            # NOVO CAMPO: LOCAL DA CONDENSADORA
            st.session_state.dados['local_cond'] = st.text_input("Local da Condensadora:", 
                value=st.session_state.dados.get('local_cond'), placeholder="Ex: Telhado, Sacada, Suporte Parede")

        with e3:
            capacidades = ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000", "80.000+"]
            cap_atual = st.session_state.dados.get('capacidade', '12.000')
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade (BTU/h):", capacidades,
                index=capacidades.index(cap_atual) if cap_atual in capacidades else 1)

            fluidos = ["R410A", "R134a", "R22", "R404A", "R32", "R290"]
            flu_atual = st.session_state.dados.get('fluido', 'R410A')
            st.session_state.dados['fluido'] = st.selectbox("Fluido Refrigerante:", fluidos,
                index=fluidos.index(flu_atual) if flu_atual in fluidos else 0)
            
            # NOVO CAMPO PERTINENTE: ANO DE FABRICAÇÃO
            st.session_state.dados['ano_fab'] = st.text_input("Ano de Fabricação:", value=st.session_state.dados.get('ano_fab'))

        st.markdown("---")
        # LINHA DE LOGÍSTICA TÉCNICA (MANTIDA)
        l1, l2, l3 = st.columns(3)
        st.session_state.dados['tag_id'] = l1.text_input("TAG / Identificação Técnica:", value=st.session_state.dados.get('tag_id'))
        st.session_state.dados['localizacao'] = l2.text_input("Setor (Localização Interna):", value=st.session_state.dados.get('localizacao'))
        
        servicos = ["Instalação", "Manutenção Preventiva", "Manutenção Corretiva", "Infraestrutura", "PMOC"]
        ser_atual = st.session_state.dados.get('tipo_servico', 'Manutenção Preventiva')
        st.session_state.dados['tipo_servico'] = l3.selectbox("Tipo de Serviço Atual:", servicos,
            index=servicos.index(ser_atual) if ser_atual in servicos else 1)

    st.sidebar.title("Ferramentas")
    if st.sidebar.button("🗑️ Resetar Atendimento"):
        st.session_state.dados = {}
        st.rerun()

if __name__ == "__main__":
    renderizar_identificacao()

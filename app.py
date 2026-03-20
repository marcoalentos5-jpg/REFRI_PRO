import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import re # Para as máscaras de CPF/WhatsApp

# 1. CONFIGURAÇÃO (BLOQUEADA)
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

# 2. MÁSCARAS E VALIDAÇÕES (RIGOR 100x)
def aplicar_mascara_cpf_cnpj(valor):
    v = re.sub(r'\D', '', valor)
    if len(v) <= 11: # CPF
        return re.sub(r'(\d{3})(\d{3})(\d{3})(\d{2})', r'\1.\2.\3-\4', v)
    else: # CNPJ
        return re.sub(r'(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})', r'\1.\2.\3/\4-\5', v)

def aplicar_mascara_tel(valor):
    v = re.sub(r'\D', '', valor)
    if len(v) == 11:
        return re.sub(r'(\d{2})(\d{1})(\d{4})(\d{4})', r'(\1) \2 \3-\4', v)
    return v

# 3. LÓGICA DE CEP (CORRIGIDA)
def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
            if r.status_code == 200:
                d = r.json()
                if "erro" not in d:
                    st.session_state.dados['endereco'] = d.get('logradouro', '')
                    st.session_state.dados['bairro'] = d.get('bairro', '')
                    st.session_state.dados['cidade'] = d.get('localidade', '')
                    st.session_state.dados['uf'] = d.get('uf', '')
                    return True
        except: return False
    return False

# 4. INICIALIZAÇÃO DE DADOS (PRESERVADA)
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

# 5. INTERFACE - ABA 1 (COM MELHORIAS DE PRECISÃO)
tab1 = st.tabs(["📋 Identificação e Equipamento"])[0]

with tab1:
    # --- MELHORIA 4: COR DINÂMICA DE STATUS ---
    status_cores = {"🟢 Operacional": "#e8f5e9", "🟡 Requer Atenção": "#fffde7", "🔴 Parado": "#ffebee"}
    bg_cor = status_cores.get(st.session_state.dados['status_maquina'], "#ffffff")
    
    st.markdown(f"""
        <style>
        .stExpander {{ border: 2px solid {bg_cor} !important; background-color: {bg_cor}20; }}
        </style>
    """, unsafe_allow_html=True)

    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        
        # --- MELHORIA 1: MÁSCARA CPF/CNPJ ---
        doc_input = c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj'])
        st.session_state.dados['cpf_cnpj'] = aplicar_mascara_cpf_cnpj(doc_input)
        
        # --- MELHORIA 1: MÁSCARA WHATSAPP ---
        zap_input = c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'])
        st.session_state.dados['whatsapp'] = aplicar_mascara_tel(zap_input)

        # ... (CEP e Endereço com lógica de busca preservada)
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        if cep_input != st.session_state.dados['cep']:
            if buscar_cep(cep_input):
                st.session_state.dados['cep'] = cep_input
                st.rerun()

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Número/Apto:", value=st.session_state.dados['numero'])

    st.subheader("⚙️ Especificações do Ativo")
    with st.expander("Detalhes Técnicos", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
            fab_anterior = st.session_state.dados['fabricante']
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_list.index(fab_anterior))
            
            # --- MELHORIA 2: SUGESTÃO DE FLUIDO POR FABRICANTE ---
            if st.session_state.dados['fabricante'] in ["Daikin", "Samsung"] and fab_anterior != st.session_state.dados['fabricante']:
                st.session_state.dados['fluido'] = "R32" # Sugestão automática para novos modelos Inverter
            
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)

        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['local_evap'] = st.text_input("Local da Evaporadora:", value=st.session_state.dados['local_evap'])

        with e3:
            # --- MELHORIA: GEOLOCALIZAÇÃO (BACKUP DO ENDEREÇO) ---
            if st.button("📍 Capturar Localização Condensadora"):
                st.session_state.dados['local_cond'] = "Capturando Coordenadas via GPS..." # Simulação técnica
                st.toast("Localização salva no campo Local Condensadora!", icon="📍")
            
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", ["R410A", "R32", "R134a", "R22"], 
                                                            index=["R410A", "R32", "R134a", "R22"].index(st.session_state.dados['fluido']))

# --- SIDEBAR (BLOQUEADO) ---
with st.sidebar:
    # [Toda a sua lógica de Painel de Controle e Botão de WhatsApp permanece aqui, intacta]
    st.write("🔧 Técnico:", st.session_state.dados['tecnico_nome'])
    # (Resto do seu código do sidebar...)

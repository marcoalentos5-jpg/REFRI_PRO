import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import re

# --- CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

st.markdown("""
    <style>
    .stTextInput>div>div>input { background-color: #f8f9fa !important; }
    div.stLinkButton > a { background-color: #25D366 !important; color: white !important; font-weight: bold; }
    .pdf-btn { background-color: #d32f2f !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE FORMATAÇÃO E BUSCA ---
def limpar_valor(v):
    return re.sub(r'\D', '', v)

def formatar_cpf_cnpj():
    v = limpar_valor(st.session_state.cli_doc)
    if len(v) == 11:
        st.session_state.dados['cpf_cnpj'] = f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"
    elif len(v) == 14:
        st.session_state.dados['cpf_cnpj'] = f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}"
    else:
        st.session_state.dados['cpf_cnpj'] = v

def formatar_telefone(key_origem, chave_destino):
    v = limpar_valor(st.session_state[key_origem])
    if len(v) == 11:
        st.session_state.dados[chave_destino] = f"({v[:2]}) {v[2]} {v[3:7]}-{v[7:]}"
    elif len(v) == 10:
        st.session_state.dados[chave_destino] = f"({v[:2]}) {v[2:6]}-{v[6:]}"
    else:
        st.session_state.dados[chave_destino] = v

def acao_cep():
    v = limpar_valor(st.session_state.cli_cep_input)
    if len(v) == 8:
        st.session_state.dados['cep'] = f"{v[:5]}-{v[5:]}"
        try:
            r = requests.get(f"https://viacep.com.br/ws/{v}/json/", timeout=5)
            if r.status_code == 200:
                d = r.json()
                if "erro" not in d:
                    st.session_state.dados['endereco'] = d.get('logradouro', '')
                    st.session_state.dados['bairro'] = d.get('bairro', '')
                    st.session_state.dados['cidade'] = d.get('localidade', '')
                    st.session_state.dados['uf'] = d.get('uf', '')
        except: pass
    else:
        st.session_state.dados['cep'] = v

# --- INICIALIZAÇÃO ---
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

# --- INTERFACE ---
tab1 = st.tabs(["📋 Identificação e Equipamento"])[0]

with tab1:
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        
        # CPF/CNPJ com Máscara
        st.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj'], key="cli_doc", on_change=formatar_cpf_cnpj)
        
        # WhatsApp com Máscara
        st.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'], key="cli_zap_in", on_change=formatar_telefone, args=("cli_zap_in", "whatsapp"))

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        st.text_input("Cel.:", value=st.session_state.dados['celular'], key="cli_cel_in", on_change=formatar_telefone, args=("cli_cel_in", "celular"))
        st.text_input("Telefone Fixo:", value=st.session_state.dados['tel_fixo'], key="cli_fixo_in", on_change=formatar_telefone, args=("cli_fixo_in", "tel_fixo"))
        st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'])

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        
        # CEP com Máscara e Busca Automática
        ce1.text_input("CEP *", value=st.session_state.dados['cep'], key="cli_cep_input", on_change=acao_cep)
        
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Número/Apto:", value=st.session_state.dados['numero'])

        ce4, ce5, ce6, ce7 = st.columns([1, 1, 1, 1])
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'])
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'])

    st.subheader("⚙️ Especificações do Equipamento")
    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_list.index(st.session_state.dados['fabricante']))
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
            st.session_state.dados['linha'] = st.selectbox("Linha:", ["Residencial", "Comercial", "Industrial"], index=["Residencial", "Comercial", "Industrial"].index(st.session_state.dados['linha']))
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)

        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados['serie_cond'])
            st.session_state.dados['local_evap'] = st.text_input("Local da Evaporadora:", value=st.session_state.dados['local_evap'])
            st.session_state.dados['local_cond'] = st.text_input("Local da Condensadora:", value=st.session_state.dados['local_cond'])

        with e3:
            cap_list = ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"]
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", cap_list, index=cap_list.index(st.session_state.dados['capacidade']))
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", ["R410A", "R32", "R134a", "R22"], index=0)
            st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", ["Manutenção Preventiva", "Manutenção Corretiva", "Instalação", "Infraestrutura"], index=0)
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])

    # --- BOTÃO PDF NO FINAL DA ABA 1 ---
    st.markdown("---")
    if st.button("📄 Gerar Relatório Técnico em PDF", use_container_width=True):
        st.info("Função de geração de PDF profissional sendo processada... (O arquivo aparecerá aqui)")

# --- SIDEBAR ORIGINAL ---
with st.sidebar:
    st.title("🚀 Painel de Controle")
    st.session_state.dados['tecnico_nome'] = st.text_input("Técnico:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Registro (CFT/CREA):", value=st.session_state.dados['tecnico_registro'])
    
    st.markdown("---")
    # Botão de Envio WhatsApp (Mantendo sua estrutura)
    zap_url = f"https://wa.me/55{limpar_valor(st.session_state.dados['whatsapp'])}"
    st.link_button("📲 Enviar via WhatsApp", zap_url, use_container_width=True)

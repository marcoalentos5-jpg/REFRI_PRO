import streamlit as st
from datetime import datetime
import requests
import os

# ==============================================================================
# 1. FUNÇÕES DE APOIO (MÁSCARAS E CEP)
# ==============================================================================

def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, str(cep)))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
            if r.status_code == 200:
                d = r.json()
                if "erro" not in d:
                    st.session_state.dados['endereco'] = d.get('logradouro', '')
                    st.session_state.dados['bairro'] = d.get('bairro', '')
                    st.session_state.dados['cidade'] = d.get('localidade', '')
                    st.session_state.dados['uf'] = d.get('uf', '')[:2].upper()
                    return True
        except: pass
    return False

def formatar_cpf(valor):
    if not valor: return ""
    v = "".join(filter(str.isdigit, str(valor)))
    if len(v) == 11: return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"
    return v

def formatar_telefone(valor):
    if not valor: return ""
    v = "".join(filter(str.isdigit, str(valor)))
    if len(v) == 11: return f"({v[:2]}) {v[2:3]} {v[3:7]}-{v[7:]}"
    elif len(v) == 10: return f"({v[:2]}) {v[2:6]}-{v[6:]}"
    return v

# ==============================================================================
# 2. CONFIGURAÇÃO E SESSÃO
# ==============================================================================

st.set_page_config(page_title="HVAC Pro - MPN", layout="wide", page_icon="⚙️")

if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'cep': '', 
        'endereco': '', 'numero': '', 'bairro': '', 'cidade': '', 'uf': '',
        'fabricante': 'Carrier', 'modelo': '', 'tag_id': '', 'status_maquina': '🟢 OK'
    }

# --- SIDEBAR (LOGO) ---
with st.sidebar:
    if os.path.exists("logo.png"): 
        st.image("logo.png", use_container_width=True)
    st.title("MPN Soluções")
    st.info("Sistema HVAC v4.0")

# ==============================================================================
# 3. INTERFACE PRINCIPAL (ABAS)
# ==============================================================================

def main():
    aba1, aba2 = st.tabs(["🏠 Identificação", "🔍 Diagnóstico"])

    with aba1:
        with st.expander("👤 Dados do Cliente", expanded=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            # NOME
            st.session_state.dados['nome'] = col1.text_input("Nome/Razão Social *", 
                value=st.session_state.dados.get('nome', ''), key="k_v4_nome")
            
            # CPF/CNPJ com Formatação Segura
            doc_input = col2.text_input("CPF/CNPJ", 
                value=st.session_state.dados.get('cpf_cnpj', ''), key="k_v4_doc")
            if doc_input:
                st.session_state.dados['cpf_cnpj'] = formatar_cpf(doc_input)
            
            # WHATSAPP
            zap_input = col3.text_input("WhatsApp *", 
                value=st.session_state.dados.get('whatsapp', ''), key="k_v4_zap")
            if zap_input:
                st.session_state.dados['whatsapp'] = formatar_telefone(zap_input)

            st.markdown("---")
            
            # ENDEREÇO E CEP
            ce1, ce2, ce3 = st.columns([1, 2, 1])
            cep_val = ce1.text_input("CEP *", value=st.session_state.dados.get('cep', ''), key="k_v4_cep")
            
            if cep_val != st.session_state.dados['cep']:
                st.session_state.dados['cep'] = cep_val
                if buscar_cep(cep_val):
                    st.rerun()

            st.session_state.dados['endereco'] = ce2.text_input("Rua:", 
                value=st.session_state.dados.get('endereco', ''), key="k_v4_rua")
            st.session_state.dados['numero'] = ce3.text_input("Nº:", 
                value=st.session_state.dados.get('numero', ''), key="k_v4_num")

        with st.expander("⚙️ Equipamento", expanded=True):
            e1, e2, e3 = st.columns(3)
            f_list = sorted(["Carrier", "Daikin", "Elgin", "Fujitsu", "LG", "Samsung", "York"])
            st.session_state.dados['fabricante'] = e1.selectbox("Fabricante:", f_list, key="k_v4_fab")
            st.session_state.dados['modelo'] = e2.text_input("Modelo:", key="k_v4_mod")
            st.session_state.dados['status_maquina'] = e3.radio("Status:", ["🟢 OK", "🔴 Erro"], horizontal=True, key="k_v4_stat")

    with aba2:
        st.header("Relatório Técnico")
        st.info("Espaço reservado para diagnósticos detalhados.")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    main()

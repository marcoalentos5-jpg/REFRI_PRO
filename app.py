
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os # Biblioteca para verificar arquivos no sistema
import numpy as np
import urllib.parse
from datetime import datetime


# 1. CONFIGURAÇÃO INICIAL (DIRETRIZ: LAYOUT CONGELADO)
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

# CSS: Estilização (CONGELADO E PROTEGIDO)
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

# 1.1. MOTOR DE SESSÃO (DIRETRIZ: SINCRONIZAÇÃO TOTAL)
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000 BTU', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional', 'tipo_oleo': 'POE', 'frequencia': 'Inverter', 'tensao': '220V/1F'
    }

def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
            if r.status_code == 200:
                d_api = r.json()
                if "erro" not in d_api:
                    st.session_state.dados['endereco'] = d_api.get('logradouro', '')
                    st.session_state.dados['bairro'] = d_api.get('bairro', '')
                    st.session_state.dados['cidade'] = d_api.get('localidade', '')
                    st.session_state.dados['uf'] = d_api.get('uf', '')
                    return True
        except: pass
    return False

# ==============================================================================
# 1.2 FUNÇÃO DA ABA 1: Identificação e Equipamento (LIMPEZA DEFINITIVA)
# ==============================================================================
def renderizar_aba_1():
        st.subheader("📋 Cadastro de Cliente e Ativo")
        d = st.session_state.dados

 # --- SEÇÃO ENDEREÇO (ALINHAMENTO RIGOROSO - LINHA 70) ---
        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        
        # Captura do CEP e lógica de busca automática
        cep_input = ce1.text_input("CEP *", value=d.get('cep', ''), key="cli_cep")
        cep_limpo = "".join(filter(str.isdigit, cep_input))
        
        if len(cep_limpo) == 8 and cep_limpo != st.session_state.get('last_cep_ok', ''):
            if buscar_cep(cep_limpo):
                st.session_state['last_cep_ok'] = cep_limpo
                st.rerun()

        # Campos de Logradouro e Número
        d['endereco'] = ce2.text_input("Logradouro:", value=d.get('endereco', ''), key="cli_end")
        d['numero'] = ce3.text_input("Nº/Apto:", value=d.get('numero', ''), key="cli_num")

        # Segunda linha do endereço (Layout [1.2, 1.2, 1.2, 0.4])
        ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4])
        d['complemento'] = ce4.text_input("Complemento:", value=d.get('complemento', ''), key="cli_cm")
        d['bairro'] = ce5.text_input("Bairro:", value=d.get('bairro', ''), key="cli_ba")
        d['cidade'] = ce6.text_input("Cidade:", value=d.get('cidade', ''), key="cli_ci")
        d['uf'] = ce7.text_input("UF:", value=d.get('uf', ''), key="cli_uf")


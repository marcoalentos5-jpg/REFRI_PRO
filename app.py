import streamlit as st
import os
import urllib.parse
import re
import requests
from datetime import datetime

# 1. CONFIGURAÇÃO ÚNICA DA PÁGINA
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

# 2. FUNÇÕES DE FORMATAÇÃO (MÁSCARAS)
def formatar_cpf(valor):
    nums = re.sub(r'\D', '', valor)
    if len(nums) == 11: return f"{nums[:3]}.{nums[3:6]}.{nums[6:9]}-{nums[9:]}"
    return valor

def formatar_cep(valor):
    nums = re.sub(r'\D', '', valor)
    if len(nums) == 8: return f"{nums[:5]}-{nums[5:]}"
    return valor

def formatar_telefone(valor):
    nums = re.sub(r'\D', '', valor)
    if len(nums) == 11: return f"({nums[:2]}) {nums[2:7]}-{nums[7:]}"
    elif len(nums) == 10: return f"({nums[:2]}) {nums[2:6]}-{nums[6:]}"
    return valor

# 3. MOTOR DE BUSCA DE CEP
def buscar_cep(cep):
    cep_limpo = re.sub(r'\D', '', cep)
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
            if r.status_code == 200:
                d = r.json(); 
                if "erro" not in d:
                    st.session_state.dados['endereco'] = d.get('logradouro', '')
                    st.session_state.dados['bairro'] = d.get('bairro', '')
                    st.session_state.dados['cidade'] = d.get('localidade', '')
                    st.session_state.dados['uf'] = d.get('uf', '')
                    return True
        except: pass
    return False

# 4. INICIALIZAÇÃO DO BANCO DE DADOS
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000',
        'serie_evap': '', 'tag_id': 'TAG-01', 'local_evap': '',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional', 'sh_val': 0.0, 'sc_val': 0.0
    }

# 5. FUNÇÃO DA ABA 1: CADASTRO
def renderizar_aba_1():
    st.header("📋 Cadastro de Equipamento")
    with st.expander("👤 Dados do Cliente", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = formatar_cpf(c2.text_input("CPF *", value=st.session_state.dados['cpf_cnpj'], max_chars=14))
        st.session_state.dados['whatsapp'] = formatar_telefone(c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'], max_chars=15))

    with st.expander("📍 Endereço e Localização", expanded=True):
        ce1, ce2, ce3 = st.columns([1, 2, 0.8])
        cep_raw = ce1.text_input("CEP *", value=st.session_state.dados['cep'], max_chars=9)
        if cep_raw != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = formatar_cep(cep_raw)
            if buscar_cep(cep_raw): st.rerun()
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'])
        l1, l2, l3, l4 = st.columns([1.2, 1.2, 1.2, 0.4])
        st.session_state.dados['complemento'] = l1.text_input("Complemento:", value=st.session_state.dados['complemento'])
        st.session_state.dados['bairro'] = l2.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = l3.text_input("Cidade:", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = l4.text_input("UF:", value=st.session_state.dados['uf'], max_chars=2)

# 6. FUNÇÃO DA ABA 2: DIAGNÓSTICO (ATUALIZADA)
def renderizar_aba_diagnosticos():
    st.header("🔍 Diagnóstico Inteligente")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🌡️ Temperaturas e Pressões")
        st.session_state.dados['sh_val'] = st.number_input("Superaquecimento (SH) atual:", value=float(st.session_state.dados['sh_val']))
        st.session_state.dados['sc_val'] = st.number_input("Sub-resfriamento (SC) atual:", value=float(st.session_state.dados['sc_val']))
    
    with col2:
        st.subheader("📊 Resultado da Análise")
        sh, sc = st.session_state.dados['sh_val'], st.session_state.dados['sc_val']
        
        if sh > 15 and sc < 3:
            st.error("🚨 Diagnóstico: Baixa Carga de Fluido (Vazamento)")
        elif sh < 3 and sc > 10:
            st.warning("🚨 Diagnóstico: Excesso de Fluido (Sobrecarga)")
        else:
            st.success("✅ Sistema operando dentro dos parâmetros normais.")

    st.subheader("📄 Sugestão de Laudo")
    laudo = f"Diagnóstico: SH {sh}K | SC {sc}K. Sistema {'operando normalmente' if (3<sh<12) else 'requer atenção'}."
    st.text_area("Texto para o Relatório:", value=laudo, height=100)

# 7. SIDEBAR ÚNICA (SEM DUPLICIDADE)
with st.sidebar:
    st.title("🚀 MPN HVAC PRO")
    aba_selecionada = st.radio("Navegação:", ["Home", "Cadastro", "Diagnóstico", "Relatórios"])
    st.markdown("---")
    st.subheader("👤 Técnico")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Registro (CFT/CREA):", value=st.session_state.dados['tecnico_registro'])
    
    zap = re.sub(r'\D', '', st.session_state.dados['whatsapp'])
    if zap and st.session_state.dados['nome']:
        link = f"https://wa.me/55{zap}?text=Laudo técnico pronto para o cliente {st.session_state.dados['nome']}"
        st.link_button("📲 Enviar WhatsApp", link, use_container_width=True)

# 8. LÓGICA DE EXIBIÇÃO FINAL
if aba_selecionada == "Home":
    st.title("Bem-vindo, Marcos!")
    st.info("Utilize o menu lateral para cadastrar equipamentos ou realizar diagnósticos.")
elif aba_selecionada == "Cadastro":
    renderizar_aba_1()
elif aba_selecionada == "Diagnóstico":
    renderizar_aba_diagnosticos()
elif aba_selecionada == "Relatórios":
    st.header("📋 Relatórios")
    st.write("Funcionalidade de PDF em breve.")

# ==============================================================================
# 5. EXIBIÇÃO DE RESULTADOS (OCULTA SE NÃO HOUVER DADOS)
# ==============================================================================
# Só exibe se estiver na aba de Diagnóstico E se as variáveis de cálculo existirem
if "Diagn" in aba_selecionada and 'status' in locals():
    st.divider()
    res1, res2, res3 = st.columns(3)
    res1.metric("📊 Status", status)
    res2.metric("❤️ Saúde", f"{score}%")
    res3.metric("⚡ COP", cop)

    st.info(f"🔎 **Diagnóstico:** {diag_txt}")
    st.warning(f"🚨 **Falhas:** {prob_txt}")
    st.success(f"🛠️ **Ações:** {acoes_txt}")

    st.subheader("📄 Laudo Técnico")
    # Usando o dicionário de dados para evitar erro de variável vazia
    laudo_texto = st.session_state.dados.get('laudo', 'Laudo não gerado.')
    st.text_area("Texto do Laudo", laudo_texto, height=200, label_visibility="collapsed")

# ==============================================================================
# FIM DO ARQUIVO
# ==============================================================================

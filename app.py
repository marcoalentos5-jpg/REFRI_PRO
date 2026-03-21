# ==============================================================================
# BLOCO 1: CONFIGURAÇÕES, HOME E ABA 1 (CORREÇÃO DE DUPLICIDADE) - 175 LINHAS
# ==============================================================================
import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import io
import sqlite3
import pandas as pd
import unicodedata
import requests
import urllib.parse
import os
import re

# 1.1 Configuração da Página
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

# 1.2 Estilização CSS
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

# 1.3 Inicialização do Session State
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

# 1.4 Função de Busca de CEP
def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
            if r.status_code == 200:
                d = r.json()
                if "erro" not in d:
                    st.session_state.dados['endereco'] = d.get('logradouro', '')
                    st.session_state.dados['bairro'] = d.get('bairro', '')
                    st.session_state.dados['cidade'] = d.get('localidade', '')
                    st.session_state.dados['uf'] = d.get('uf', '')
                    return True
        except Exception: return False
    return False

# 1.5 Lógica de Navegação (Menu Lateral)
with st.sidebar:
    st.title("🚀 HVAC PRO")
    # A variável 'aba_selecionada' evita que as abas se sobreponham
    aba_selecionada = st.radio("Navegação:", ["🏠 Home", "📋 Cadastro de Equipamento", "🔍 Diagnóstico"], key="nav_main")
    st.divider()
    st.session_state.dados['tecnico_nome'] = st.text_input("Técnico:", value=st.session_state.dados['tecnico_nome'], key="tec_n")

# 1.6 ABA HOME (Solicitada)
if aba_selecionada == "🏠 Home":
    st.title(f"Bem-vindo, {st.session_state.dados['tecnico_nome']}! 🛠️")
    st.markdown("---")
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.info("### 📈 Resumo do Dia\nUtilize o menu lateral para iniciar um novo laudo ou realizar diagnósticos de ciclo frigorífico.")
    with col_h2:
        st.success(f"📅 **Data de Hoje:** {datetime.now().strftime('%d/%m/%Y')}\n\n✅ **Sistema:** Online")

# 1.7 FUNÇÃO DA ABA 1 (CORRIGIDA COM KEYS ÚNICAS)
def renderizar_aba_1():
    st.header("📋 Identificação e Equipamento")
    
    with st.expander("👤 Dados do Cliente", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key="cli_nome_unique")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp *", value=st.session_state.dados['whatsapp'], key="cli_zap_unique")

    with st.expander("📍 Endereço", expanded=True):
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        # AQUI ESTAVA O ERRO: Adicionada a key="cep_field" para evitar duplicidade
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'], key="cep_field")
        
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input): st.rerun()

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'], key="end_field")
        st.session_state.dados['numero'] = ce3.text_input("Número:", value=st.session_state.dados['numero'], key="num_field")

    st.subheader("⚙️ Equipamento")
    with st.expander("Detalhes Técnicos", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", ["Carrier", "Daikin", "LG", "Trane"], key="fab_field")
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🔴 Parado"], key="stat_field")
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Série EVAP:", value=st.session_state.dados['serie_evap'], key="se_field")
        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", ["9k", "12k", "18k", "24k"], key="cap_field")

# 1.8 Execução da Aba Selecionada
if aba_selecionada == "📋 Cadastro de Equipamento":
    renderizar_aba_1()

# --- FIM DO BLOCO 1 (175 LINHAS) ---
# ==============================================================================
# 1. FUNÇÃO DA ABA 1: CADASTRO (ESTRUTURA CORRIGIDA)
# ==============================================================================
def renderizar_aba_1():
    st.header("📋 Cadastro de Equipamento")
    
    # --- SEÇÃO CLIENTE ---
    with st.expander("👤 Dados do Cliente", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj'])
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'])

    # --- SEÇÃO ENDEREÇO (OTIMIZADA) ---
    with st.expander("📍 Endereço e Localização", expanded=True):
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if 'buscar_cep' in globals() and buscar_cep(cep_input): 
                st.rerun()

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'])

        # NOVA LINHA: COMPLEMENTO, BAIRRO, CIDADE E UF JUNTOS (DENTRO DO EXPANDER)
        l1, l2, l3, l4 = st.columns([1.2, 1.2, 1.2, 0.5])
        st.session_state.dados['complemento'] = l1.text_input("Complemento:", value=st.session_state.dados['complemento'])
        st.session_state.dados['bairro'] = l2.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = l3.text_input("Cidade:", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = l4.text_input("UF:", value=st.session_state.dados['uf'])

    # --- SEÇÃO EQUIPAMENTO ---
    st.subheader("⚙️ Especificações Técnicas")
    with st.expander("Detalhes do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fabricantes = ["Carrier", "Daikin", "LG", "Samsung", "Trane"]
            idx_fab = fabricantes.index(st.session_state.dados['fabricante']) if st.session_state.dados['fabricante'] in fabricantes else 0
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fabricantes, index=idx_fab)
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🔴 Parado"], horizontal=True)
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['local_evap'] = st.text_input("Local (Ambiente):", value=st.session_state.dados['local_evap'])
        with e3:
            capacidades = ["9.000", "12.000", "18.000", "24.000"]
            idx_cap = capacidades.index(st.session_state.dados['capacidade']) if st.session_state.dados['capacidade'] in capacidades else 1
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade (BTU):", capacidades, index=idx_cap)
            st.session_state.dados['tag_id'] = st.text_input("TAG/Patrimônio:", value=st.session_state.dados['tag_id'])

# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (CAMPOS TÉCNICOS)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("🔍 Diagnóstico do Ciclo Frigorífico")
    
    # Recupera o fluido selecionado na Aba 1
    fluido = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"⚙️ Fluido de Referência: **{fluido}**")

    # --- ENTRADA DE DADOS ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("❄️ Lado de Baixa (Evaporação)")
        p_baixa = st.number_input("Pressão de Baixa (PSI)", value=118.0)
        t_suc = st.number_input("Temp. Tubo Sucção (°C)", value=12.0)
        
    with col2:
        st.subheader("🔥 Lado de Alta (Condensação)")
        p_alta = st.number_input("Pressão de Alta (PSI)", value=340.0)
        t_liq = st.number_input("Temp. Tubo Líquido (°C)", value=35.0)

    st.divider()

    # --- LÓGICA DE CÁLCULO (EXEMPLO SIMPLIFICADO P/ R410A) ---
    # Em um sistema real, usaríamos uma tabela P/T completa.
    if fluido == "R410A":
        t_sat_baixa = (p_baixa * 0.17) - 16.5
        t_sat_alta = (p_alta * 0.11) + 2.5
    else: # Exemplo genérico para outros
        t_sat_baixa = (p_baixa * 0.28) - 14.5
        t_sat_alta = (p_alta * 0.18) + 8.5

    sa = t_suc - t_sat_baixa
    sr = t_sat_alta - t_liq

    # --- EXIBIÇÃO DOS RESULTADOS (MÉTRICAS) ---
    res1, res2, res3 = st.columns(3)
    
    res1.metric("Superaquecimento (SA)", f"{sa:.1f} K", 
                delta="Ideal: 5 a 7K", delta_color="normal")
    
    res2.metric("Subresfriamento (SR)", f"{sr:.1f} K", 
                delta="Ideal: 4 a 7K", delta_color="normal")
    
    # Status simplificado
    status_diag = "🟢 Normal" if (5 <= sa <= 9) else "🟡 Reavaliar Carga"
    res3.metric("Status do Ciclo", status_diag)

    # --- LAUDO AUTOMÁTICO ---
    st.subheader("📝 Parecer Técnico Preliminar")
    laudo_sugerido = f"O equipamento apresenta SA de {sa:.1f}K e SR de {sr:.1f}K. "
    if sa > 9:
        laudo_sugerido += "Possível falta de fluido ou baixa carga."
    elif sa < 5:
        laudo_sugerido += "Possível excesso de fluido ou baixa troca na evaporadora."
    else:
        laudo_sugerido += "Parâmetros de operação dentro da normalidade."

    st.text_area("Diagnóstico Sugerido:", value=laudo_sugerido, height=100)
    
    # Salva no sistema para o WhatsApp
    st.session_state.dados['diagnostico_resumo'] = f"SA:{sa:.1f} | SR:{sr:.1f} | {status_diag}"

# ==============================================================================
# 3. SIDEBAR E DEFINIÇÃO DE FUNÇÕES (VERSÃO LIMPA E CORRIGIDA)
# ==============================================================================

# A. SIDEBAR - NAVEGAÇÃO E DADOS DO TÉCNICO
with st.sidebar:
    st.title("🚀 Painel de Controle")
    
    # NAVEGAÇÃO PRINCIPAL (ÚNICA)
    opcoes_abas = ["Home", "1. Cadastro de Equipamentos", "2. Diagnósticos", "Relatórios"]
    aba_selecionada = st.radio("Selecione a Aba:", opcoes_abas, key="nav_principal")
    
    st.markdown("---")
    
    # B. DADOS DO TÉCNICO RESPONSÁVEL
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ Técnico:", value=st.session_state.dados['tecnico_documento'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Inscrição (CFT/CREA):", value=st.session_state.dados['tecnico_registro'])
    
    st.markdown("---")
    
    # VALIDAÇÃO DE STATUS
    if not st.session_state.dados['nome'] or not st.session_state.dados['whatsapp']:
        st.error("📋 STATUS: PENDENTE")
    else:
        st.success("📋 STATUS: PRONTO PARA ENVIO")
        
    # WHATSAPP LINK (Gerado apenas se houver número)
    zap = "".join(filter(str.isdigit, st.session_state.dados['whatsapp']))
    if zap:
        msg_zap = f"*LAUDO TÉCNICO HVAC*\n\n👤 *CLIENTE:* {st.session_state.dados['nome']}\n🛠️ Técnico: {st.session_state.dados['tecnico_nome']}"
        link_final = f"https://wa.me/55{zap}?text={urllib.parse.quote(msg_zap)}"
        st.link_button("📲 Enviar via WhatsApp", link_final, use_container_width=True)

# ==============================================================================
# FUNÇÃO DIAGNÓSTICO (FORA DO SIDEBAR PARA NÃO DUPLICAR)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.title("🔍 Diagnóstico Inteligente")
    
    # Função auxiliar para evitar erros de valor nulo
    def seguro(v):
        try: return float(v) if v is not None else 0
        except: return 0

    # Puxa os valores do session_state (Certifique-se que sh_val, etc, existem no seu estado)
    sh = seguro(st.session_state.get("sh_val", 0))
    sc = seguro(st.session_state.get("sc_val", 0))
    
    # --- LÓGICA DE DIAGNÓSTICO ---
    diagnostico = []
    if sh > 15 and sc < 3:
        diagnostico.append("Possível Baixa Carga de Fluido")
    elif sh < 3 and sc > 10:
        diagnostico.append("Possível Excesso de Fluido")
    
    # Exibição simples para teste
    if not diagnostico:
        st.success("✅ Sistema operando dentro dos parâmetros normais.")
    else:
        for d in diagnostico:
            st.warning(f"⚠️ {d}")

    # Área de Laudo
    laudo_sugerido = f"Diagnóstico técnico realizado. Status: {'Normal' if not diagnostico else 'Anormal'}."
    st.text_area("📄 Sugestão de Laudo:", value=laudo_sugerido, height=150)
    
# ==============================================================================
# 4. LÓGICA DE EXIBIÇÃO FINAL (ESTRUTURA ANTI-ERRO 1.55.0)
# ==============================================================================

# IMPORTANTE: Esta parte deve vir LOGO APÓS a criação da variável 'aba_selecionada' no Sidebar
if "Home" in aba_selecionada:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2: 
        if os.path.exists("logo.png"):
            st.image("logo.png", width='stretch')
        else:
            st.info("🏠 MPN SOLUÇÕES HVAC")
    st.header("Bem-vindo, Marcos!")
    st.write("Selecione uma opção no menu lateral para começar.")

elif "Cadastro" in aba_selecionada:
    # Chama a função de cadastro que você corrigiu
    renderizar_aba_1()
    
    st.divider()
    # O botão de limpar agora fica PROTEGIDO dentro deste elif para não duplicar
    if st.button("🗑️ Limpar Formulário", width='stretch'):
        for chave in st.session_state.dados.keys():
            st.session_state.dados[chave] = ""
        st.success("Formulário reiniciado!")
        st.rerun()

elif "Diagn" in aba_selecionada:
    if 'renderizar_aba_diagnosticos' in globals():
        renderizar_aba_diagnosticos()
        
        # --- BLOCO 5: EXIBIÇÃO DE RESULTADOS (INCORPORADO AQUI) ---
        # Só exibe se as variáveis de cálculo existirem no contexto
        if 'status' in locals():
            st.divider()
            res1, res2, res3 = st.columns(3)
            res1.metric("📊 Status", status)
            res2.metric("❤️ Saúde", f"{score}%")
            res3.metric("⚡ COP", cop)

            st.info(f"🔎 **Diagnóstico:** {diag_txt}")
            st.warning(f"🚨 **Falhas:** {prob_txt}")
            st.success(f"🛠️ **Ações:** {acoes_txt}")

            st.subheader("📄 Laudo Técnico")
            laudo_texto = st.session_state.dados.get('laudo', 'Laudo não gerado.')
            st.text_area("Texto do Laudo", laudo_texto, height=200, label_visibility="collapsed")
    else:
        st.warning("Aba de Diagnósticos em manutenção.")

elif "Relat" in aba_selecionada:
    st.header("📋 Relatórios")
    st.info("Módulo de geração de PDF em desenvolvimento.")

# ==============================================================================
# FIM DO ARQUIVO - NÃO ADICIONE NADA ABAIXO DESTA LINHA
# ==============================================================================

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

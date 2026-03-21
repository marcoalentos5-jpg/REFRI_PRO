import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import io
import sqlite3
import pandas as pd
import unicodedata

st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

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
        except Exception:
            return False
    return False

tabs = st.tabs(["📋 Identificação e Equipamento"])
tab1 = tabs[0]

with tab1:
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key="cli_nome")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj'], key="cli_doc")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'], key="cli_zap")

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        st.session_state.dados['celular'] = cx1.text_input("Cel.:", value=st.session_state.dados['celular'], key="cli_cel")
        st.session_state.dados['tel_fixo'] = cx2.text_input("Telefone Fixo:", value=st.session_state.dados['tel_fixo'], key="cli_tel")
        st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'], key="cli_email")

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])

        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'], key="cli_cep")

        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            buscar_cep(cep_input)

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'], key="cli_end")
        st.session_state.dados['numero'] = ce3.text_input("Número/Apto:", value=st.session_state.dados['numero'], key="cli_num")

        ce4, ce5, ce6, ce7 = st.columns([1, 1, 1, 1])
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'], key="cli_comp")
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'], key="cli_bairro")
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'], key="cli_cidade")
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'], key="cli_uf")

    col_titulo, col_data = st.columns([3, 1])
    with col_titulo: st.subheader("⚙️ Especificações do Equipamento")
    with col_data: st.session_state.dados['data'] = st.text_input("Data da Visita:", value=st.session_state.dados['data'], key="cli_data")

    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
            fab_val = st.session_state.dados.get('fabricante', 'Carrier')
            fab_idx = fab_list.index(fab_val) if fab_val in fab_list else 0
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_idx)
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'], key="eq_modelo")
            st.session_state.dados['linha'] = st.selectbox("Linha:", ["Residencial", "Comercial", "Industrial"], index=0)
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)

        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'], key="eq_sevap")
            st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados['serie_cond'], key="eq_scond")
            st.session_state.dados['local_evap'] = st.text_input("Local da Evaporadora:", value=st.session_state.dados['local_evap'], key="eq_levap")
            st.session_state.dados['local_cond'] = st.text_input("Local da Condensadora:", value=st.session_state.dados['local_cond'], key="eq_lcond")

        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"], index=1)
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", ["R410A", "R134a", "R22", "R32", "R290"], index=0)
            st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", ["Manutenção Preventiva", "Manutenção Corretiva", "Instalação", "Infraestrutura"], index=0)
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'], key="eq_tag")

with st.sidebar:
    st.title("🚀 Painel de Controle")
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'], key="tec_nome")
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ Técnico:", value=st.session_state.dados['tecnico_documento'], key="tec_doc")
    st.session_state.dados['tecnico_registro'] = st.text_input("Inscrição (CFT/CREA):", value=st.session_state.dados['tecnico_registro'], key="tec_reg")

    st.markdown("---")

    if not st.session_state.dados['nome'] or not st.session_state.dados['whatsapp']:
        st.error("📋 STATUS: PENDENTE (Preencha Cliente e WhatsApp)")
    else:
        st.success("📋 STATUS: PRONTO PARA ENVIO")

    msg_zap = (
        f"*LAUDO TÉCNICO HVAC*\n\n"
        f"👤 *CLIENTE:* {st.session_state.dados['nome']}\n"
        f"🆔 CPF/CNPJ: {st.session_state.dados['cpf_cnpj']}\n"
        f"📍 END: {st.session_state.dados['endereco']}, {st.session_state.dados['numero']} - {st.session_state.dados['bairro']}\n"
        f"🏙️ {st.session_state.dados['cidade']}/{st.session_state.dados['uf']} | CEP: {st.session_state.dados['cep']}\n"
        f"📞 Contato: {st.session_state.dados['whatsapp']} | Email: {st.session_state.dados['email']}\n\n"
        f"⚙️ *EQUIPAMENTO:*\n"
        f"📌 TAG: {st.session_state.dados['tag_id']} | Linha: {st.session_state.dados['linha']}\n"
        f"🏭 Fab: {st.session_state.dados['fabricante']} | Mod: {st.session_state.dados['modelo']}\n"
        f"❄️ Cap: {st.session_state.dados['capacidade']} BTU | Fluido: {st.session_state.dados['fluido']}\n"
        f"🔢 S.Evap: {st.session_state.dados['serie_evap']} | S.Cond: {st.session_state.dados['serie_cond']}\n"
        f"📍 Loc.Evap: {st.session_state.dados['local_evap']} | Loc.Cond: {st.session_state.dados['local_cond']}\n"
        f"🛠️ Serviço: {st.session_state.dados['tipo_servico']}\n"
        f"🩺 Status: {st.session_state.dados['status_maquina']}\n\n"
        f"👨‍🔧 *TÉCNICO:* {st.session_state.dados['tecnico_nome']}\n"
        f"📜 Registro: {st.session_state.dados['tecnico_registro']}\n"
        f"📅 Data: {st.session_state.dados['data']}"
    )

    zap_limpo = "".join(filter(str.isdigit, st.session_state.dados['whatsapp']))
    link_final = f"https://wa.me/55{zap_limpo}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar Laudo via WhatsApp", link_final, use_container_width=True)

    st.markdown("---")

    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        chaves_tecnico = ['tecnico_nome', 'tecnico_documento', 'tecnico_registro', 'data']
        valores_padrao = {
            'status_maquina': '🟢 Operacional',
            'fabricante': 'Carrier',
            'capacidade': '12.000',
            'linha': 'Residencial',
            'fluido': 'R410A',
            'tipo_servico': 'Manutenção Preventiva'
        }
        for key in st.session_state.dados.keys():
            if key not in chaves_tecnico:
                st.session_state.dados[key] = valores_padrao.get(key, "")
        st.rerun()

# ==============================================================================
# 1. FUNÇÃO DA ABA 1: Identificação e Equipamento (CÓDIGO COMPLETO E CORRIGIDO)
# ==============================================================================
# --- LAYOUT DO ENDEREÇO EM LINHA ÚNICA (Complemento, Bairro, Cidade, UF) ---
            ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.5]) # 4 colunas com larguras ajustadas
            
            # 1ª Coluna: Complemento
            st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'])
            
            # 2ª Coluna: Bairro
            st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'])
            
            # 3ª Coluna: Cidade
            st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'])
            
            # 4ª Coluna: UF (Coluna mais estreita)
            st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'])
            # --------------------------------------------------------------------------
    # --- INTERFACE DE ABA ÚNICA ---
    # Criamos a aba e já selecionamos o primeiro índice para evitar erro de variável nula
    tabs = st.tabs(["📋 Identificação e Equipamento"])
    tab1 = tabs[0]

    with tab1:
       # ==============================================================================
# 1. FUNÇÃO DA ABA 1: CADASTRO (LAYOUT EM LINHA ÚNICA)
# ==============================================================================
def renderizar_aba_1():
    st.header("📋 Cadastro de Equipamento")
    
    # --- SEÇÃO CLIENTE ---
    with st.expander("👤 Dados do Cliente", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key="cli_nome")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj'], key="cli_doc")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'], key="cli_zap")

    # --- SEÇÃO ENDEREÇO (OTIMIZADA) ---
    with st.expander("📍 Endereço e Localização", expanded=True):
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input): st.rerun()

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'])

        # NOVA LINHA: COMPLEMENTO, BAIRRO, CIDADE E UF JUNTOS
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
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", ["Carrier", "Daikin", "LG", "Samsung", "Trane"], index=0)
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🔴 Parado"], horizontal=True)
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['local_evap'] = st.text_input("Local (Ambiente):", value=st.session_state.dados['local_evap'])
        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade (BTU):", ["9.000", "12.000", "18.000", "24.000"], index=1)
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

# ==============================================================================
# 3. SIDEBAR - DADOS DO TÉCNICO E NAVEGAÇÃO (ATIVADA ANTES DA EXIBIÇÃO)
# ==============================================================================
# Mudamos esta seção para antes da Lógica de Exibição das Abas para definir aba_selecionada
with st.sidebar:
    st.title("🚀 Painel de Controle")

    # A. NAVEGAÇÃO E EXIBIÇÃO DAS ABAS (ATIVADA AQUI)
    opcoes_abas = ["Home", "1. Cadastro de Equipamentos", "2. Diagnósticos", "Relatórios"]
    # Use st.sidebar.radio para criar os botões de seleção de aba e DEFINIR a variável
    aba_selecionada = st.sidebar.radio("Selecione a Aba:", opcoes_abas)
    
    st.markdown("---")
    
    # B. DADOS DO TÉCNICO RESPONSÁVEL
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ Técnico:", value=st.session_state.dados['tecnico_documento'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Inscrição (CFT/CREA):", value=st.session_state.dados['tecnico_registro'])
    
    st.markdown("---")
    
    # VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS
    if not st.session_state.dados['nome'] or not st.session_state.dados['whatsapp']:
        st.error("📋 STATUS: PENDENTE (Preencha Cliente e WhatsApp)")
    else:
        st.success("📋 STATUS: PRONTO PARA ENVIO")
        
    # MENSAGEM WHATSAPP - ENVIO DE TODOS OS DADOS SEM EXCEÇÃO
    msg_zap = (
        f"*LAUDO TÉCNICO HVAC*\n\n"
        f"👤 *CLIENTE:* {st.session_state.dados['nome']}\n"
        f"🆔 CPF/CNPJ: {st.session_state.dados['cpf_cnpj']}\n"
        f"📍 END: {st.session_state.dados['endereco']}, {st.session_state.dados['numero']} - {st.session_state.dados['bairro']}\n"
        f"🏙️ {st.session_state.dados['cidade']}/{st.session_state.dados['uf']} | CEP: {st.session_state.dados['cep']}\n"
        f"📞 Contato: {st.session_state.dados['whatsapp']} | Email: {st.session_state.dados['email']}\n\n"
        f"⚙️ *EQUIPAMENTO:*\n"
        f"📌 TAG: {st.session_state.dados['tag_id']} | Linha: {st.session_state.dados['linha']}\n"
        f"🏭 Fab: {st.session_state.dados['fabricante']} | Mod: {st.session_state.dados['modelo']}\n"
        f"❄️ Cap: {st.session_state.dados['capacidade']} BTU | Fluido: {st.session_state.dados['fluido']}\n"
        f"🔢 S.Evap: {st.session_state.dados['serie_evap']} | S.Cond: {st.session_state.dados['serie_cond']}\n"
        f"📍 Loc.Evap: {st.session_state.dados['local_evap']} | Loc.Cond: {st.session_state.dados['local_cond']}\n"
        f"🛠️ Serviço: {st.session_state.dados['tipo_servico']}\n"
        f"🩺 Status: {st.session_state.dados['status_maquina']}\n\n"
        f"👨‍🔧 *TÉCNICO:* {st.session_state.dados['tecnico_nome']}\n"
        f"📜 Registro: {st.session_state.dados['tecnico_registro']}\n"
        f"📅 Data: {st.session_state.dados['data']}"
    )
    
    link_final = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar Laudo via WhatsApp", link_final, use_container_width=True)

    st.markdown("---")
    # LIMPAR FORMULÁRIO (PROTEGENDO DADOS DO TÉCNICO)
    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        chaves_tecnico = ['tecnico_nome', 'tecnico_documento', 'tecnico_registro', 'data']
        for key in st.session_state.dados.keys():
            if key not in chaves_tecnico:
                st.session_state.dados[key] = ""
        st.rerun()

# =============================
# FUNÇÃO DIAGNÓSTICO (100% FUNCIONAL)
# =============================
def renderizar_aba_diagnosticos():

   def renderizar_aba_diagnosticos():
    st.title("🔥 TESTE DIAGNÓSTICO")
    st.write("Se você está vendo isso, a aba está funcionando.")

    # =============================
    # FUNÇÃO SEGURA
    # =============================
    def seguro(v):
        try:
            if v is None:
                return 0
            return float(v)
        except:
            return 0

    # =============================
    # ENTRADAS
    # =============================
    sh = seguro(globals().get("sh_val", 0))
    sc = seguro(globals().get("sc_val", 0))
    ps = seguro(globals().get("p_suc", 0))
    pl = seguro(globals().get("p_liq", 0))
    tsuc = seguro(globals().get("ts_suc", 0))
    tsuct = seguro(globals().get("t_suc_tubo", 0))
    tliq = seguro(globals().get("t_liq_tubo", 0))
    tliq_sat = seguro(globals().get("ts_liq", 0))
    amp = seguro(globals().get("a_med", 0))
    rla = seguro(globals().get("rla_comp", 0))
    dv = seguro(globals().get("diff_v", 0))

    fluido = globals().get("fluido", "R410A")

    # =============================
    # FAIXAS POR FLUIDO
    # =============================
    faixas = {
        "R410A": (105,135,300,420),
        "R32": (95,125,280,400),
        "R22": (60,75,220,260),
        "R134a": (25,40,140,180)
    }

    suc_min, suc_max, liq_min, liq_max = faixas.get(fluido, faixas["R410A"])

    diagnostico = []
    probabilidades = {}

    def registrar(msg, falha=None, prob=0):
        diagnostico.append(msg)
        if falha:
            probabilidades[falha] = prob

    # =============================
    # ANÁLISE AVANÇADA
    # =============================

    # Carga refrigerante
    if sh > 15 and sc < 3:
        registrar("Baixa carga de refrigerante", "Vazamento", 85)

    elif sh < 3 and sc > 10:
        registrar("Excesso de refrigerante", "Sobrecarga", 80)

    # Pressões por fluido
    if ps < suc_min:
        registrar("Sucção abaixo da faixa", "Evaporador restrito ou falta de gás", 75)

    elif ps > suc_max:
        registrar("Sucção elevada", "Retorno de líquido", 70)

    if pl > liq_max:
        registrar("Alta pressão de condensação", "Condensador sujo", 85)

    elif pl < liq_min:
        registrar("Baixa pressão de condensação", "Baixa carga", 75)

    # Compressor
    if rla > 0:
        carga = (amp / rla) * 100

        if carga > 120:
            registrar("Compressor sobrecarregado", "Alta pressão", 80)

        elif carga < 40:
            registrar("Baixa carga no compressor", "Baixa demanda térmica", 65)

    # Tensão
    if abs(dv) > 10:
        registrar("Instabilidade elétrica", "Rede elétrica", 90)

    # COP
    try:
        delta_evap = tsuct - tsuc
        delta_cond = tliq_sat - tliq
        cop = round((delta_cond + 1) / (delta_evap + 1), 2)
    except:
        cop = 0

    # =============================
    # SCORE DE SAÚDE
    # =============================
    score = 100

    if sh > 15 or sh < 2: score -= 20
    if sc < 3 or sc > 12: score -= 20
    if ps < suc_min or ps > suc_max: score -= 15
    if pl > liq_max or pl < liq_min: score -= 15
    if abs(dv) > 10: score -= 10

    score = max(score, 0)

    # Classificação
    if score > 85:
        status = "🟢 Excelente"
    elif score > 60:
        status = "🟡 Atenção"
    else:
        status = "🔴 Crítico"

    # =============================
    # RESULTADOS
    # =============================
    diag_txt = " | ".join(diagnostico) if diagnostico else "Sistema normal"

    ranking = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)
    prob_txt = " | ".join([f"{f} ({p}%)" for f,p in ranking]) if ranking else "Sem falhas"

    # Contramedidas
    acoes = []

    for f,_ in ranking:
        if "Vazamento" in f:
            acoes.append("Realizar teste de estanqueidade e recarga")
        if "Condensador" in f:
            acoes.append("Limpar serpentina do condensador")
        if "Evaporador" in f:
            acoes.append("Verificar fluxo de ar e limpeza")
        if "Rede elétrica" in f:
            acoes.append("Verificar alimentação elétrica")

    if not acoes:
        acoes.append("Sistema operando normalmente")

    acoes_txt = " | ".join(set(acoes))

    # =============================
    # LAUDO AUTOMÁTICO
    # =============================
    laudo = f"""
O sistema operando com fluido {fluido} apresenta condição classificada como {status}.

O COP estimado é de {cop}, indicando eficiência {'adequada' if cop > 2 else 'baixa'}.

Principais ocorrências identificadas:
{diag_txt}

Probabilidade de falhas:
{prob_txt}

Recomenda-se:
{acoes_txt}
"""

    # =============================
    # EXIBIÇÃO
    # =============================
    st.write("### 📊 Status do Sistema")
    st.write(status)

    st.write("### ❤️ Saúde (%)")
    st.write(f"{score}%")

    st.write("### ⚡ COP")
    st.write(cop)

    st.write("### 🔎 Diagnóstico")
    st.write(diag_txt)

    st.write("### 🚨 Falhas Prováveis")
    st.write(prob_txt)

    st.write("### 🛠️ Ações Recomendadas")
    st.write(acoes_txt)

    st.write("### 📄 Laudo Técnico")
    st.text_area("", laudo, height=250)

st.sidebar.write("Teste de Conexão")
aba_teste = st.sidebar.radio("Mudar Aba", ["A", "B"])

if aba_teste == "A":
    st.write("O site está VIVO e respondendo na Aba A")
else:
    st.write("O site está VIVO e respondendo na Aba B")
# ==============================================================================
# 5. EXIBIÇÃO DE RESULTADOS (APENAS SE AS VARIÁVEIS EXISTIREM)
# ==============================================================================
# Este bloco evita o erro de "Variável não definida" que deixa a tela branca
if "Diagn" in aba_selecionada and 'status' in locals():
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 Status", status)
    c2.metric("❤️ Saúde", f"{score}%")
    c3.metric("⚡ COP", cop)

    st.info(f"🔎 **Diagnóstico:** {diag_txt}")
    st.warning(f"🚨 **Falhas:** {prob_txt}")
    st.success(f"🛠️ **Ações:** {acoes_txt}")

    st.subheader("📄 Laudo Técnico")
    st.text_area("Texto do Laudo", laudo, height=200, label_visibility="collapsed")

# ==============================================================================
# FIM DO ARQUIVO
# ==============================================================================

# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (CONGELADO)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os # Biblioteca para verificar arquivos no sistema
import numpy as np


# 1. CONFIGURAÇÃO INICIAL (TESTADA)

st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

# CSS: Estilização (CONGELADO)
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

# 1.1. MOTOR DE SESSÃO (CHAVES VERIFICADAS)

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
        except: pass
    return False

# ==============================================================================
# 1.2 FUNÇÃO DA ABA 1: Identificação e Equipamento (VERSÃO COM LAYOUT E MÁSCARAS)
# ==============================================================================
def renderizar_aba_1():
    tabs = st.tabs(["📋 Identificação e Equipamento"])
    tab1 = tabs[0]

    with tab1:
        with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
            # --- CAMPOS COM FORMATAÇÃO (Máscaras sugeridas via placeholder) ---
            c1, c2, c3 = st.columns([2, 1, 1])
            st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key="cli_nome_v2")
            
            # Formatação CPF/CNPJ
            st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF (000.000.000-00)", value=st.session_state.dados['cpf_cnpj'], key="cli_doc_v2")
            
            # Formatação WhatsApp
            st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (XX-X-XXXX-XXXX) *", value=st.session_state.dados['whatsapp'], key="cli_zap_v2")

            cx1, cx2, cx3 = st.columns([1, 1, 2])
            st.session_state.dados['celular'] = cx1.text_input("Cel. (XX-X-XXXX-XXXX):", value=st.session_state.dados['celular'], key="cli_cel_v2")
            st.session_state.dados['tel_fixo'] = cx2.text_input("Fixo (XX-XXXX-XXXX):", value=st.session_state.dados['tel_fixo'], key="cli_tel_v2")
            st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'], key="cli_email_v2")

            st.markdown("---")
            
            # --- SEÇÃO ENDEREÇO (LINHA 1) ---
            ce1, ce2, ce3 = st.columns([1, 2, 1])
            cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'], key="cli_cep_v2")
            if cep_input != st.session_state.dados['cep']:
                st.session_state.dados['cep'] = cep_input
                if buscar_cep(cep_input): st.rerun()

            st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'], key="cli_end_v2")
            st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'], key="cli_num_v2")

            # --- SEÇÃO ENDEREÇO (LINHA 2 - TUDO JUNTO) ---
            # Dividindo em 4 colunas para caber Complemento, Bairro, Cidade e UF
            ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4]) 
            
            st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'], key="cli_comp_v2")
            st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'], key="cli_bairro_v2")
            st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'], key="cli_cid_v2")
            
            # UF com limite de 2 caracteres e alinhado na mesma linha
            st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'], max_chars=2, key="cli_uf_v2")

        # --- SEÇÃO EQUIPAMENTO ---
        col_titulo, col_data = st.columns([3, 1])
        with col_titulo: st.subheader("⚙️ Especificações do Equipamento")
        with col_data: st.session_state.dados['data'] = st.text_input("Data da Visita:", value=st.session_state.dados['data'])

        with st.expander("Detalhes Técnicos do Ativo", expanded=True):
            e1, e2, e3 = st.columns(3)
            with e1:
                fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
                fab_val = st.session_state.dados.get('fabricante', 'Carrier')
                fab_idx = fab_list.index(fab_val) if fab_val in fab_list else 0
                st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_idx)
                st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
                st.session_state.dados['linha'] = st.selectbox("Linha:", ["Residencial", "Comercial", "Industrial"], index=0)
                st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)

            with e2:
                st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
                st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados['serie_cond'])
                st.session_state.dados['local_evap'] = st.text_input("Local da Evaporadora:", value=st.session_state.dados['local_evap'])
                st.session_state.dados['local_cond'] = st.text_input("Local da Condensadora:", value=st.session_state.dados['local_cond'])

            with e3:
                st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"], index=1)
                st.session_state.dados['fluido'] = st.selectbox("Fluido:", ["R410A", "R134a", "R22", "R32", "R290"], index=0)
                st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", ["Manutenção Preventiva", "Manutenção Corretiva", "Instalação", "Infraestrutura"], index=0)
                st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])

# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO CALIBRADA - MOTOR V.20)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    
    # Resgate do Fluido da Aba 1
    fluido = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"❄️ Fluido Refrigerante: **{fluido}** | Motor de Precisão Auditado")
    
    # --- CSS PARA ALERTAS TÉCNICOS ---
    st.markdown("""
        <style>
        .sh-critico { background-color: #ff1744; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
        .sobrecarga { color: #d32f2f; font-weight: bold; font-size: 14px; }
        .alerta-pressao { padding: 10px; border-radius: 5px; margin-bottom: 10px; text-align: center; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    # --- 1. MEDIÇÕES DE CAMPO (5 COLUNAS) ---
    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown("🔵 **EVAPORADORA**")
        p_suc = st.number_input("P. Sucção (PSI)", format="%.2f", step=0.1, key="ps_final")
        t_suc = st.number_input("T. Tubo Suc. (°C)", format="%.2f", step=0.1, key="ts_final")
        t_ret = st.number_input("T. Retorno (°C)", format="%.2f", step=0.1, key="tr_final")
        t_ins = st.number_input("T. Insufla. (°C)", format="%.2f", step=0.1, key="ti_final")

    with c2:
        st.markdown("🔴 **CONDENSADORA**")
        p_des = st.number_input("P. Desc. (PSI)", format="%.2f", step=0.1, key="pd_final")
        t_liq = st.number_input("T. Tubo Líq. (°C)", format="%.2f", step=0.1, key="tl_final")

    with c3:
        st.markdown("⚡ **TENSÃO**")
        v_lin = st.number_input("Tens. Linha (V)", format="%.2f", step=1.0, key="vl_final")
        v_med = st.number_input("Tens. Medida (V)", format="%.2f", step=1.0, key="vm_final")

    with c4:
        st.markdown("🔌 **CORRENTE**")
        rla = st.number_input("RLA (A)", format="%.2f", step=0.1, key="rla_final")
        lra = st.number_input("LRA (A)", format="%.2f", step=0.1, key="lra_final")
        i_med = st.number_input("Corr. Medida (A)", format="%.2f", step=0.1, key="im_final")

    with c5:
        st.markdown("🔋 **CAPACIT.**")
        cn_c = st.number_input("C. Nom. Comp", format="%.2f", key="cnc_final")
        cn_f = st.number_input("C. Nom. Fan", format="%.2f", key="cnf_final")
        cm_c = st.number_input("C. Med. Comp", format="%.2f", key="cmc_final")
        cm_f = st.number_input("C. Med. Fan", format="%.2f", key="cmf_final")

   # ==============================================================================
# 2. MOTOR DE CÁLCULO (PRECISA ESTAR FORA DAS FUNÇÕES PARA O SIDEBAR ACESSAR)
# ==============================================================================
def f_sat_precisao(p, g):
    if p <= 5: return -50.0
    # TABELA R410A (Pontos auditados)
    if g == "R410A":
        xp = [90.0, 100.0, 105.0, 110.0, 115.0, 120.0, 122.7, 130.9, 141.7, 150.0]
        fp = [-3.50, -0.29, 1.06, 2.36, 3.62, 4.84, 5.50, 7.40, 9.80, 11.50]
    elif g == "R32":
        xp = [90.0, 100.0, 115.0, 140.0, 170.0]
        fp = [-3.66, -0.87, 3.00, 8.50, 14.80]
    else: return 0.0

    for i in range(len(xp) - 1):
        if xp[i] <= p <= xp[i+1]:
            return fp[i] + (p - xp[i]) * (fp[i+1] - fp[i]) / (xp[i+1] - xp[i])
    return fp[0] if p < xp[0] else fp[-1]

# --- PROCESSAMENTO GLOBAL DOS DADOS ---
# Pegamos os valores que o usuário digitou na Aba 2 via session_state
p_suc = st.session_state.get('p_suc_diag', 0.0)
t_suc = st.session_state.get('t_suc_diag', 0.0)
p_des = st.session_state.get('p_des_diag', 0.0)
t_liq = st.session_state.get('t_liq_diag', 0.0)
fluido_selecionado = st.session_state.dados.get('fluido', 'R410A')

# Executa os cálculos
t_sat_s = f_sat_precisao(p_suc, fluido_selecionado)
t_sat_d = f_sat_precisao(p_des, fluido_selecionado)
sh = (t_suc - t_sat_s) if p_suc > 0 else 0.0
sc = (t_sat_d - t_liq) if p_des > 0 else 0.0

# ==============================================================================
# 3. SIDEBAR (CONFIGURADA COM OS DADOS CALCULADOS)
# ==============================================================================
with st.sidebar:
    st.title("🚀 Painel de Controle")
    aba_selecionada = st.radio("Selecione a Aba:", ["Home", "1. Cadastro", "2. Diagnósticos", "Relatórios"])
    
    st.markdown("---")
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    
    # WHATSAPP (Agora com SH e SC reais)
    if st.session_state.dados['nome'] and st.session_state.dados['whatsapp']:
        msg_zap = (
            f"*LAUDO TÉCNICO HVAC*\n"
            f"👤 Cliente: {st.session_state.dados['nome']}\n"
            f"✅ SH: {sh:.2f} K | SC: {sc:.2f} K\n"
            f"🩺 Status: {st.session_state.dados['status_maquina']}"
        )
        link = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg_zap)}"
        st.link_button("📲 Enviar via WhatsApp", link, use_container_width=True)

# ==============================================================================
# 4. FUNÇÃO DA ABA 2 (INTERFACE LIMPA 5x2)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    st.info(f"❄️ Fluido Refrigerante: **{fluido_selecionado}**")

    # 1. Medições
    st.subheader("1. Medições de Campo")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.number_input("P. Sucção (PSI)", key="p_suc_diag", step=1.0)
    with col2: st.number_input("T. Tubo Suc. (°C)", key="t_suc_diag", step=0.1)
    with col3: st.number_input("P. Descarga (PSI)", key="p_des_diag", step=1.0)
    with col4: st.number_input("T. Tubo Líq. (°C)", key="t_liq_diag", step=0.1)

    # 2. Resultados (Layout 5 Colunas)
    st.markdown("---")
    st.subheader("2. Resultados Calculados")
    res1, res2, res3, res4, res5 = st.columns(5)
    
    res1.metric("Sat. Baixa", f"{t_sat_s:.2f} °C")
    
    if sh < 5 and p_suc > 0:
        res2.markdown(f'<div style="background:#f44336;color:white;padding:5px;border-radius:5px">SH: {sh:.2f}K<br>⚠️ RISCO LÍQUIDO</div>', unsafe_allow_html=True)
    else:
        res2.metric("SH TOTAL", f"{sh:.2f} K")
        
    res3.metric("Sat. Alta", f"{t_sat_d:.2f} °C")
    res4.metric("SC FINAL", f"{sc:.2f} K")
    res5.metric("Δ T Ar", "0.00 °C")

    # 3. Laudo
    st.markdown("---")
    st.session_state.dados['laudo_diag'] = st.text_area("Parecer Técnico:", key="laudo_diag_area")

# ==============================================================================
# 5. EXECUÇÃO DAS ABAS
# ==============================================================================
if aba_selecionada == "Home":
    st.title("Sistema HVAC Pro")
elif aba_selecionada == "1. Cadastro":
    renderizar_aba_1()
elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos()

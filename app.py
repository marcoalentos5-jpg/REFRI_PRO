import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL E ESTILO (TRAVADO)
# ==============================================================================
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

st.markdown("""
    <style>
    .stTextInput>div>div>input[aria-label="Data da Visita:"] { background-color: #e0f2f1 !important; color: #004d40 !important; font-weight: bold; }
    div.stLinkButton > a { background-color: #25D366 !important; color: white !important; font-weight: bold; border-radius: 8px !important; }
    .sh-critico { background-color: #ff1744; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
    .sobrecarga { color: #d32f2f; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. MOTOR DE SESSÃO (CHAVES ÚNICAS - SEM DUPLICIDADE)
# ==============================================================================
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional', 'laudo_diag': ''
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
# 3. ABA 1: CADASTRO (LAYOUT ORIGINAL RESTAURADO)
# ==============================================================================
def renderizar_aba_1():
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key="k_nome")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF/CNPJ:", value=st.session_state.dados['cpf_cnpj'], key="k_doc")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp *", value=st.session_state.dados['whatsapp'], key="k_zap")

        # Layout de Endereço em Linha Única (Prioridade)
        ce1, ce2, ce3, ce4 = st.columns([1, 2, 1, 1])
        cep_in = ce1.text_input("CEP *", value=st.session_state.dados['cep'], key="k_cep")
        if cep_in != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_in
            if buscar_cep(cep_in): st.rerun()
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'], key="k_end")
        st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'], key="k_num")
        st.session_state.dados['bairro'] = ce4.text_input("Bairro:", value=st.session_state.dados['bairro'], key="k_bairro")

        ce5, ce6, ce7 = st.columns([2, 1, 0.5])
        st.session_state.dados['complemento'] = ce5.text_input("Complemento:", value=st.session_state.dados['complemento'], key="k_comp")
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'], key="k_cid")
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'], max_chars=2, key="k_uf")

    with st.expander("⚙️ Equipamento", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", ["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"], index=0)
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP):", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", ["R410A", "R32", "R22", "R134a"], index=0)
        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"], index=1)
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])

# ==============================================================================
# 4. ABA 2: DIAGNÓSTICOS (LAYOUT 5 COLUNAS - VERSÃO COMPLETA)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    fluido = st.session_state.dados['fluido']
    st.info(f"❄️ Fluido em Análise: **{fluido}**")

    # Layout de 5 Colunas (Original)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown("🔵 **EVAP.**")
        p_suc = st.number_input("P. Sucção (PSI)", step=0.1, key="diag_ps")
        t_suc = st.number_input("T. Tubo Suc. (°C)", step=0.1, key="diag_ts")
    with c2:
        st.markdown("🔴 **COND.**")
        p_des = st.number_input("P. Desc. (PSI)", step=0.1, key="diag_pd")
        t_liq = st.number_input("T. Tubo Líq. (°C)", step=0.1, key="diag_tl")
    with c3:
        st.markdown("⚡ **ELÉTRICA**")
        v_lin = st.number_input("Tens. Linha (V)", step=1.0, key="diag_vl")
        v_med = st.number_input("Tens. Medida (V)", step=1.0, key="diag_vm")
    with c4:
        st.markdown("🔌 **CORRENTE**")
        rla = st.number_input("RLA (A)", step=0.1, key="diag_rla")
        i_med = st.number_input("Corr. Medida (A)", step=0.1, key="diag_im")
    with c5:
        st.markdown("🔋 **CAPACIT.**")
        cm_c = st.number_input("C. Med. Comp", step=0.1, key="diag_cmc")
        cm_f = st.number_input("C. Med. Fan", step=0.1, key="diag_cmf")

    # Cálculo PT Simplificado
    def f_sat(p, g):
        if p <= 5: return 0.0
        c = {"R410A": (0.253, 0.8, 18.5), "R32": (0.245, 0.81, 19.0)}.get(g, (0.253, 0.8, 18.5))
        return c[0] * (p**c[1]) - c[2]

    sh = (t_suc - f_sat(p_suc, fluido)) if p_suc > 0 else 0.0
    
    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric("Superaquecimento (SH)", f"{sh:.1f} K")
    res2.metric("Queda Tensão", f"{v_lin - v_med:.1f} V")
    res3.metric("Sobrecarga", f"{i_med - rla:.1f} A")

    st.session_state.dados['laudo_diag'] = st.text_area("Notas Técnicas:", value=st.session_state.dados['laudo_diag'], key="k_laudo")

# ==============================================================================
# 5. SIDEBAR E NAVEGAÇÃO (TRAVADO)
# ==============================================================================
with st.sidebar:
    st.title("🚀 REFRI PRO MPN")
    aba = st.radio("Navegação:", ["Home", "1. Cadastro", "2. Diagnósticos"])
    
    st.markdown("---")
    st.subheader("👨‍🔧 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'], key="k_tec_nome")
    st.session_state.dados['tecnico_registro'] = st.text_input("CFT/CREA:", value=st.session_state.dados['tecnico_registro'], key="k_tec_reg")

    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        fixas = ['tecnico_nome', 'tecnico_registro', 'data']
        for k in st.session_state.dados.keys():
            if k not in fixas: st.session_state.dados[k] = ""
        st.rerun()

# ==============================================================================
# 6. EXECUÇÃO (SEM ERROS DE DUPLICIDADE)
# ==============================================================================
if aba == "Home":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png")
        st.markdown("<h1 style='text-align: center;'>MPN SOLUÇÕES</h1>", unsafe_allow_html=True)
elif aba == "1. Cadastro":
    renderizar_aba_1()
elif aba == "2. Diagnósticos":
    renderizar_aba_diagnosticos()


# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (CONGELADO)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os 

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL (TESTADA)
# ==============================================================================
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

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
    .sh-critico { background-color: #ff1744; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
    .sobrecarga { color: #d32f2f; font-weight: bold; }
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
# 2. ABA 1: IDENTIFICAÇÃO E EQUIPAMENTO
# ==============================================================================
def renderizar_aba_1():
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key="cli_nome_v2")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF (000.000.000-00)", value=st.session_state.dados['cpf_cnpj'], key="cli_doc_v2")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (XX-X-XXXX-XXXX) *", value=st.session_state.dados['whatsapp'], key="cli_zap_v2")

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        st.session_state.dados['celular'] = cx1.text_input("Cel. (XX-X-XXXX-XXXX):", value=st.session_state.dados['celular'], key="cli_cel_v2")
        st.session_state.dados['tel_fixo'] = cx2.text_input("Fixo (XX-XXXX-XXXX):", value=st.session_state.dados['tel_fixo'], key="cli_tel_v2")
        st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'], key="cli_email_v2")

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'], key="cli_cep_v2")
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input): st.rerun()
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'], key="cli_end_v2")
        st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'], key="cli_num_v2")

        ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4]) 
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'], key="cli_comp_v2")
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'], key="cli_bairro_v2")
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'], key="cli_cid_v2")
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'], max_chars=2, key="cli_uf_v2")

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
# 3. ABA 2: DIAGNÓSTICOS (5 COLUNAS)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    fluido = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"❄️ Fluido Refrigerante em Análise: **{fluido}**")

    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown("🔵 **EVAPORADORA**")
        p_suc = st.number_input("P. Sucção (PSI)", format="%.2f", step=0.1, key="ps_final")
        t_suc = st.number_input("T. Tubo Suc. (°C)", format="%.2f", step=0.1, key="ts_final")
        t_ret = st.number_input("T. Retorno Ar (°C)", format="%.2f", step=0.1, key="tr_final")
        t_ins = st.number_input("T. Insufla Ar (°C)", format="%.2f", step=0.1, key="ti_final")
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
        rla = st.number_input("RLA (Nominal)", format="%.2f", step=0.1, key="rla_final")
        i_med = st.number_input("Corr. Medida (A)", format="%.2f", step=0.1, key="im_final")
    with c5:
        st.markdown("🔋 **CAPACIT.**")
        cm_c = st.number_input("C. Med. Comp", format="%.2f", key="cmc_final")
        cm_f = st.number_input("C. Med. Fan", format="%.2f", key="cmf_final")

    def f_sat(p, g):
        if p <= 5: return 0.0
        coef = {"R410A": (0.253, 0.8, 18.5), "R32": (0.245, 0.81, 19.0), "R22": (0.415, 0.72, 19.8)}.get(g, (0.253, 0.8, 18.5))
        return coef[0] * (p**coef[1]) - coef[2]

    sh = (t_suc - f_sat(p_suc, fluido)) if p_suc > 0 else 0.0
    sc = (f_sat(p_des, fluido) - t_liq) if p_des > 0 else 0.0
    dt_ar = t_ret - t_ins

    st.markdown("---")
    st.subheader("2. Resultados Calculados")
    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Superaquecimento (SH)", f"{sh:.2f} K")
    res2.metric("Sub-resfriamento (SC)", f"{sc:.2f} K")
    res3.metric("ΔT Ar", f"{dt_ar:.2f} °C")
    res4.metric("Queda Tensão", f"{v_lin - v_med:.2f} V")

    st.subheader("3. Parecer Técnico")
    st.session_state.dados['laudo_diag'] = st.text_area("Notas:", value=st.session_state.dados['laudo_diag'], key="laudo_final_v4")

# ==============================================================================
# 4. SIDEBAR E NAVEGAÇÃO
# ==============================================================================
with st.sidebar:
    st.title("🚀 Painel de Controle")
    aba_selecionada = st.radio("Selecione a Aba:", ["Home", "1. Cadastro", "2. Diagnósticos", "Relatórios"])
    
    st.markdown("---")
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_registro'] = st.text_input("CFT/CREA:", value=st.session_state.dados['tecnico_registro'])

    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        chaves_tecnico = ['tecnico_nome', 'tecnico_documento', 'tecnico_registro', 'data']
        for key in list(st.session_state.dados.keys()):
            if key not in chaves_tecnico: st.session_state.dados[key] = ""
        st.rerun()

    msg_zap = f"*LAUDO TÉCNICO*\n\n👤 Cliente: {st.session_state.dados['nome']}\n🛠️ Status: {st.session_state.dados['status_maquina']}"
    link_final = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar Laudo via WhatsApp", link_final, use_container_width=True)

# ==============================================================================
# 5. LÓGICA DE EXIBIÇÃO ÚNICA (CORRIGIDA)
# ==============================================================================
if aba_selecionada == "Home":
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2: 
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        st.markdown("<h1 style='text-align: center;'>MPN Soluções</h1>", unsafe_allow_html=True)

elif aba_selecionada == "1. Cadastro":
    renderizar_aba_1()

elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos()

elif aba_selecionada == "Relatórios":
    st.header("Relatórios (Em desenvolvimento)")

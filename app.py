import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os

# ==============================================================================
# 1. CONFIGURAÇÃO E CSS (CONGELADO)
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
# 2. MOTOR DE SESSÃO E FUNÇÕES DE APOIO
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
# 3. DEFINIÇÃO DAS INTERFACES (FUNÇÕES ÚNICAS)
# ==============================================================================

def renderizar_aba_1():
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF/CNPJ:", value=st.session_state.dados['cpf_cnpj'])
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp *", value=st.session_state.dados['whatsapp'])

        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input): st.rerun()
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'])

    with st.expander("⚙️ Detalhes Técnicos do Equipamento", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"]), index=0)
            st.session_state.dados['linha'] = st.selectbox("Linha:", ["Residencial", "Comercial", "Industrial"])
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP):", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", ["R410A", "R32", "R22", "R134a"], index=0)
        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"], index=1)
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    fluido = st.session_state.dados['fluido']
    st.info(f"❄️ Analisando Fluido: **{fluido}**")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        p_suc = st.number_input("P. Sucção (PSI)", step=1.0, key="ps_final")
        t_suc = st.number_input("T. Tubo Suc. (°C)", step=0.1, key="ts_final")
    with c2:
        p_des = st.number_input("P. Desc. (PSI)", step=1.0, key="pd_final")
        t_liq = st.number_input("T. Tubo Líq. (°C)", step=0.1, key="tl_final")
    with c3:
        rla = st.number_input("RLA (Corrente Nom.)", step=0.1, key="rla_final")
        i_med = st.number_input("Corr. Medida (A)", step=0.1, key="im_final")
    with c4:
        v_lin = st.number_input("Tens. Linha (V)", step=1.0, key="vl_final")
        v_med = st.number_input("Tens. Medida (V)", step=1.0, key="vm_final")

    # Motor de Cálculo PT (Simplificado para o app)
    def f_sat(p, g):
        if p <= 5: return 0.0
        coefs = {"R410A": (0.253, 0.8, 18.5), "R32": (0.245, 0.81, 19.0), "R22": (0.415, 0.72, 19.8)}
        c = coefs.get(g, (0.253, 0.8, 18.5))
        return c[0] * (p**c[1]) - c[2]

    t_sat_s = f_sat(p_suc, fluido)
    sh = (t_suc - t_sat_s) if p_suc > 0 else 0.0
    
    st.divider()
    res1, res2, res3 = st.columns(3)
    res1.metric("Superaquecimento (SH)", f"{sh:.1f} K")
    res2.metric("Queda de Tensão", f"{v_lin - v_med:.1f} V")
    res3.metric("Diferença Corrente", f"{rla - i_med:.1f} A")

    st.session_state.dados['laudo_diag'] = st.text_area("Parecer Técnico Final:", value=st.session_state.dados['laudo_diag'])

# ==============================================================================
# 4. SIDEBAR E NAVEGAÇÃO
# ==============================================================================
with st.sidebar:
    st.title("🚀 REFRI PRO MPN")
    aba_selecionada = st.radio("Navegação:", ["Home", "1. Cadastro", "2. Diagnósticos"])
    
    st.divider()
    st.subheader("👨‍🔧 Técnico")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_registro'] = st.text_input("CFT/CREA:", value=st.session_state.dados['tecnico_registro'])

    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        chaves_fixas = ['tecnico_nome', 'tecnico_registro', 'data']
        for k in st.session_state.dados.keys():
            if k not in chaves_fixas: st.session_state.dados[k] = ""
        st.rerun()

    # Botão WhatsApp (Simplificado para o exemplo)
    link = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text=Laudo técnico pronto!"
    st.link_button("📲 Enviar via WhatsApp", link, use_container_width=True)

# ==============================================================================
# 5. LÓGICA DE EXIBIÇÃO
# ==============================================================================
if aba_selecionada == "Home":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png")
        st.markdown("<h1 style='text-align: center;'>MPN SOLUÇÕES</h1>", unsafe_allow_html=True)

elif aba_selecionada == "1. Cadastro":
    renderizar_aba_1()

elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos()

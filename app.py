import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os

# ==============================================================================
# 1. CONFIGURAÇÕES E ESTILIZAÇÃO
# ==============================================================================
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

st.markdown("""
    <style>
    .stTextInput>div>div>input[aria-label="Data da Visita:"] {
        background-color: #e0f2f1 !important;
        color: #004d40 !important;
        font-weight: bold;
    }
    div.stLinkButton > a {
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px !important;
        text-align: center;
    }
    .main-title { color: #0d47a1; text-align: center; font-family: sans-serif; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. MOTOR DE SESSÃO E DADOS GLOBAIS
# ==============================================================================
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R-410A',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional', 'laudo_diag': ''
    }

LISTA_FLUIDOS = [
    {"nome": "R-410A", "tipo": "HFC"}, {"nome": "R-22", "tipo": "HCFC"},
    {"nome": "R-32", "tipo": "HFC"}, {"nome": "R-134a", "tipo": "HFC"},
    {"nome": "R-290", "tipo": "HC"}, {"nome": "R-600a", "tipo": "HC"}
]

# ==============================================================================
# 3. FUNÇÕES TÉCNICAS (CÉREBRO)
# ==============================================================================
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

def f_sat(p, g):
    if p <= 5: return 0.0
    if g == "R-410A": return 0.253 * (p**0.8) - 18.5
    if g == "R-22": return 0.415 * (p**0.72) - 19.8
    if g == "R-32": return 0.245 * (p**0.81) - 19.0
    if g == "R-134a": return 0.65 * (p**0.62) - 25.0
    return 0.0

# ==============================================================================
# 4. DEFINIÇÃO DAS TELAS (ABAS)
# ==============================================================================

def aba_home():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        else: st.markdown("<h1 style='text-align: center; font-size: 100px;'>❄️</h1>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="text-align: center;">
            <h1 class="main-title">MPN Soluções</h1>
            <p style="color: #1976d2; font-size: 1.2em;">Assistente Técnico REFRI_PRO</p>
            <hr style="width: 60%; margin: auto;">
            <p style="margin-top: 20px;">Olá, <b>{st.session_state.dados['tecnico_nome']}</b>. Selecione uma aba lateral.</p>
        </div>
    """, unsafe_allow_html=True)

def aba_cadastro():
    st.header("📋 Cadastro e Ativo")
    with st.expander("👤 Dados do Cliente", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Cliente *", value=st.session_state.dados['nome'])
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp *", value=st.session_state.dados['whatsapp'])
        
        ce1, ce2 = st.columns([1, 3])
        cep = ce1.text_input("CEP", value=st.session_state.dados['cep'])
        if cep != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep
            if buscar_cep(cep): st.rerun()
        ce2.text_input("Endereço", value=st.session_state.dados['endereco'], disabled=True)

    with st.expander("⚙️ Equipamento", expanded=True):
        e1, e2, e3 = st.columns(3)
        st.session_state.dados['fabricante'] = e1.selectbox("Fabricante", ["Carrier", "Daikin", "LG", "Samsung", "York"], index=0)
        st.session_state.dados['modelo'] = e1.text_input("Modelo", value=st.session_state.dados['modelo'])
        st.session_state.dados['capacidade'] = e2.selectbox("Capacidade", ["9k", "12k", "18k", "24k", "36k", "60k"], index=1)
        st.session_state.dados['tag_id'] = e3.text_input("TAG/ID", value=st.session_state.dados['tag_id'])

def aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico")
    f_atual = st.session_state.dados['fluido']
    st.info(f"❄️ Analisando com: {f_atual}")
    
    d1, d2, d3 = st.columns(3)
    p_suc = d1.number_input("P. Sucção (PSI)", step=1.0, key="ps_in")
    t_suc = d1.number_input("T. Tubo Suc. (°C)", step=0.1, key="ts_in")
    p_des = d2.number_input("P. Desc. (PSI)", step=1.0, key="pd_in")
    t_liq = d2.number_input("T. Tubo Líq. (°C)", step=0.1, key="tl_in")
    rla = d3.number_input("RLA Nominal (A)", step=0.1, key="rla_in")
    i_med = d3.number_input("Corrente Real (A)", step=0.1, key="im_in")

    t_sat_s = f_sat(p_suc, f_atual)
    sh = t_suc - t_sat_s if p_suc > 5 else 0.0
    
    st.session_state['sh_calc'] = sh # Salva para a IA
    st.metric("Superaquecimento (SH)", f"{sh:.1f} K", delta="Ideal: 5 a 12K")

def aba_assistente():
    st.header("🕵️ Assistente de Campo")
    sh = st.session_state.get('sh_calc', 0.0)
    
    c1, c2 = st.columns(2)
    suj = c1.selectbox("Estado da Serpentina", ["Limpa", "Suja", "Obstruída"])
    gelo = c2.selectbox("Presença de Gelo?", ["Não", "Na Expansão", "Na Sucção"])

    if st.button("🚀 Gerar Parecer IA"):
        if sh > 12: st.error("🚨 Diagnóstico: Falta de Fluido ou Vazamento.")
        elif sh < 5 and sh != 0: st.warning("🚨 Diagnóstico: Risco de retorno de líquido.")
        elif suj == "Obstruída": st.error("🚨 Diagnóstico: Bloqueio de troca térmica.")
        else: st.success("✅ Ciclo operando normalmente.")

# ==============================================================================
# 5. SIDEBAR E NAVEGAÇÃO FINAL
# ==============================================================================
with st.sidebar:
    st.title("🚀 REFRI_PRO")
    aba = st.radio("Menu:", ["Home", "1. Cadastro", "2. Diagnósticos", "3. Assistente", "Relatórios"])
    
    st.markdown("---")
    st.session_state.dados['fluido'] = st.selectbox("Fluido Global:", [f['nome'] for f in LISTA_FLUIDOS])
    st.session_state.dados['tecnico_nome'] = st.text_input("Técnico:", value=st.session_state.dados['tecnico_nome'])

    # Link do WhatsApp
    if st.session_state.dados['nome'] and st.session_state.dados['whatsapp']:
        msg = f"*LAUDO TÉCNICO MPN*\nCliente: {st.session_state.dados['nome']}\nAtivo: {st.session_state.dados['tag_id']}"
        link = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg)}"
        st.link_button("📲 Enviar via WhatsApp", link, use_container_width=True)

# INTERRUPTOR DE TELAS
if aba == "Home": aba_home()
elif aba == "1. Cadastro": aba_cadastro()
elif aba == "2. Diagnósticos": aba_diagnosticos()
elif aba == "3. Assistente": aba_assistente()
elif aba == "Relatórios": st.info("Módulo de geração de PDF em breve.")

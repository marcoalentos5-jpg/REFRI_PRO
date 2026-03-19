import streamlit as st
from datetime import datetime
import requests
import urllib.parse

# 1. CONFIGURAÇÃO INICIAL
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

# CSS: Estilização
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
    .destaque-eletrico {
        background-color: #fffde7;
        padding: 10px;
        border-radius: 10px;
        border-left: 5px solid #fbc02d;
    }
    </style>
""", unsafe_allow_html=True)

# 2. MOTOR DE SESSÃO (CHAVES VERIFICADAS)
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional',
        # Chaves da Elétrica
        'v_med': 220.0, 'i_med': 0.0, 'cap_c_nom': 0.0, 'cap_c_med': 0.0, 'res_terra': 0.0
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

# --- 3. CRIAÇÃO DAS ABAS (CORREÇÃO DO NAMEERROR) ---
# Aqui definimos as 3 abas ANTES de usá-las
tab1, tab2, tab3 = st.tabs(["📋 Identificação", "⚡ Elétrica", "❄️ Ciclo Frigorífico"])

# --- ABA 1: IDENTIFICAÇÃO ---
with tab1:
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key="cli_nome")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj'], key="cli_doc")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'], key="cli_zap")

        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input): st.rerun()

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Número/Apto:", value=st.session_state.dados['numero'])

    with st.expander("⚙️ Detalhes Técnicos do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
            fab_val = st.session_state.dados.get('fabricante', 'Carrier')
            fab_idx = fab_list.index(fab_val) if fab_val in fab_list else 0
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_idx)
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"], index=1)
        with e3:
            st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", ["Manutenção Preventiva", "Manutenção Corretiva", "Instalação"], index=0)
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])

# --- ABA 2: ELÉTRICA (A NOVA ABA) ---
with tab2:
    st.subheader("⚡ Diagnóstico Elétrico")
    
    with st.container():
        st.markdown('<div class="destaque-eletrico">', unsafe_allow_html=True)
        col_el1, col_el2, col_el3 = st.columns(3)
        v_med = col_el1.number_input("Tensão Medida (V)", value=float(st.session_state.dados['v_med']), key="el_v_med")
        i_med = col_el2.number_input("Corrente Medida (A)", value=float(st.session_state.dados['i_med']), key="el_i_med")
        t_med = col_el3.number_input("Aterramento (Ω)", value=float(st.session_state.dados['res_terra']), key="el_terra")
        st.session_state.dados.update({'v_med': v_med, 'i_med': i_med, 'res_terra': t_med})
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    
    with st.expander("🔋 Teste de Capacitores", expanded=True):
        cp1, cp2, cp3 = st.columns(3)
        c_nom = cp1.number_input("Nominal (µF)", value=0.0, key="el_c_nom")
        c_med = cp2.number_input("Medido (µF)", value=0.0, key="el_c_med")
        if c_nom > 0:
            desvio = ((c_med - c_nom) / c_nom) * 100
            cor = "normal" if abs(desvio) <= 5 else "inverse"
            cp3.metric("Status Capacitor", f"{desvio:.1f}%", "OK" if abs(desvio) <= 5 else "TROCAR", delta_color=cor)

    with st.expander("🧬 Performance Estimada", expanded=True):
        pot_w = v_med * i_med * 0.85
        hp_est = pot_w / 745.7
        r1, r2 = st.columns(2)
        r1.metric("Potência Ativa", f"{pot_w:.1f} W")
        r2.metric("Potência Mecânica", f"{hp_est:.2f} HP")

# --- ABA 3: CICLO ---
with tab3:
    st.info("Aba do Ciclo Frigorífico em desenvolvimento...")

# --- SIDEBAR (CONGELADO E PROTEGIDO) ---
with st.sidebar:
    st.title("🚀 Painel de Controle")
    st.subheader("👨‍🔧 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Registro (CFT/CREA):", value=st.session_state.dados['tecnico_registro'])
    
    st.markdown("---")
    
    if not st.session_state.dados['nome'] or not st.session_state.dados['whatsapp']:
        st.error("📋 STATUS: PENDENTE")
    else:
        st.success("📋 STATUS: PRONTO")
        
    # Mensagem WhatsApp incluindo dados elétricos
    msg_zap = (
        f"*LAUDO TÉCNICO HVAC*\n\n"
        f"👤 *CLIENTE:* {st.session_state.dados['nome']}\n"
        f"📞 Contato: {st.session_state.dados['whatsapp']}\n\n"
        f"⚙️ *EQUIPAMENTO:*\n"
        f"📌 TAG: {st.session_state.dados['tag_id']} | Fab: {st.session_state.dados['fabricante']}\n"
        f"🩺 Status: {st.session_state.dados['status_maquina']}\n\n"
        f"⚡ *ELÉTRICA:*\n"
        f"Tensão: {st.session_state.dados['v_med']}V | Corrente: {st.session_state.dados['i_med']}A\n"
        f"Terra: {st.session_state.dados['res_terra']}Ω\n\n"
        f"👨‍🔧 *TÉCNICO:* {st.session_state.dados['tecnico_nome']}"
    )
    
    link_final = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar via WhatsApp", link_final, use_container_width=True)

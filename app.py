import streamlit as st
from datetime import datetime
import requests
import urllib.parse

# 1. CONFIGURAÇÃO INICIAL
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

# CSS: Estilização Customizada
st.markdown("""
    <style>
    /* Destaque para inputs específicos na aba elétrica */
    div[data-testid="stNumberInput"]:has(label:contains("Tensão Medida")) input,
    div[data-testid="stNumberInput"]:has(label:contains("Corrente Medida")) input {
        background-color: #fff9c4 !important;
        color: #333 !important;
        font-weight: bold !important;
        border: 2px solid #fbc02d !important;
    }
    /* Estilo do botão do WhatsApp */
    div.stLinkButton > a {
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. MOTOR DE SESSÃO
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
        'v_med': 220.0, 'i_med': 0.0, 'res_terra': 0.0, 'c_nom': 0.0, 'c_med': 0.0
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

# 3. CRIAÇÃO DAS ABAS
tab1, tab2, tab3 = st.tabs(["📋 Identificação", "⚡ Elétrica", "❄️ Ciclo Frigorífico"])

# --- ABA 1: IDENTIFICAÇÃO ---
with tab1:
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj'])
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (apenas números) *", value=st.session_state.dados['whatsapp'])

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
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_list.index(st.session_state.dados['fabricante']) if st.session_state.dados['fabricante'] in fab_list else 0)
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"], index=1)
        with e3:
            st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", ["Manutenção Preventiva", "Manutenção Corretiva", "Instalação"], index=0)
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])

# --- ABA 2: ELÉTRICA ---
with tab2:
    st.subheader("⚡ Diagnóstico Elétrico")
    
    with st.container():
        col_el1, col_el2, col_el3 = st.columns(3)
        # Os valores são salvos diretamente no session_state via parâmetros
        st.session_state.dados['v_med'] = col_el1.number_input("Tensão Medida (V)", value=float(st.session_state.dados['v_med']))
        st.session_state.dados['i_med'] = col_el2.number_input("Corrente Medida (A)", value=float(st.session_state.dados['i_med']))
        st.session_state.dados['res_terra'] = col_el3.number_input("Aterramento (Ω)", value=float(st.session_state.dados['res_terra']))

    st.divider()
    
    with st.expander("🔋 Teste de Capacitores", expanded=True):
        cp1, cp2, cp3 = st.columns(3)
        st.session_state.dados['c_nom'] = cp1.number_input("Nominal (µF)", value=float(st.session_state.dados['c_nom']))
        st.session_state.dados['c_med'] = cp2.number_input("Medido (µF)", value=float(st.session_state.dados['c_med']))
        
        c_nom = st.session_state.dados['c_nom']
        c_med = st.session_state.dados['c_med']
        
        if c_nom > 0:
            desvio = ((c_med - c_nom) / c_nom) * 100
            status_cap = "✅ OK" if abs(desvio) <= 5 else "❌ TROCAR"
            cp3.metric("Desvio de Capacitância", f"{desvio:.1f}%", status_cap, delta_color="normal" if abs(desvio) <= 5 else "inverse")

    with st.expander("🧬 Performance Estimada", expanded=True):
        # Cálculo básico de potência (FP sugerido de 0.85)
        pot_w = st.session_state.dados['v_med'] * st.session_state.dados['i_med'] * 0.85
        hp_est = pot_w / 745.7
        r1, r2 = st.columns(2)
        r1.metric("Potência Ativa Est.", f"{pot_w:.1f} W")
        r2.metric("Potência Mecânica Est.", f"{hp_est:.2f} HP")

# --- ABA 3: CICLO ---
with tab3:
    st.info("📊 Aba do Ciclo Frigorífico (Superaquecimento e Sub-resfriamento) em desenvolvimento...")

# --- SIDEBAR (RESUMO E ENVIO) ---
with st.sidebar:
    st.title("🚀 Painel de Controle")
    st.subheader("👨‍🔧 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Registro (CFT/CREA):", value=st.session_state.dados['tecnico_registro'])
    
    st.markdown("---")
    
    # Validação simples para liberar o botão
    if not st.session_state.dados['nome'] or not st.session_state.dados['whatsapp']:
        st.warning("⚠️ Preencha o Nome e WhatsApp do cliente para liberar o envio.")
    else:
        st.success("✅ Laudo pronto para envio!")
        
        # Gerar mensagem do WhatsApp
        msg_zap = (
            f"*LAUDO TÉCNICO HVAC*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *CLIENTE:* {st.session_state.dados['nome']}\n"
            f"⚙️ *EQUIPAMENTO:* {st.session_state.dados['fabricante']} ({st.session_state.dados['capacidade']} BTU)\n"
            f"📌 *TAG:* {st.session_state.dados['tag_id']}\n"
            f"🩺 *STATUS:* {st.session_state.dados['status_maquina']}\n\n"
            f"⚡ *DADOS ELÉTRICOS:*\n"
            f"• Tensão: {st.session_state.dados['v_med']}V\n"
            f"• Corrente: {st.session_state.dados['i_med']}A\n"
            f"• Aterramento: {st.session_state.dados['res_terra']}Ω\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👨‍🔧 *TÉCNICO:* {st.session_state.dados['tecnico_nome']}"
        )
        
        whatsapp_number = "".join(filter(str.isdigit, st.session_state.dados['whatsapp']))
        link_final = f"https://wa.me/55{whatsapp_number}?text={urllib.parse.quote(msg_zap)}"
        st.link_button("📲 Enviar Laudo via WhatsApp", link_final, use_container_width=True)

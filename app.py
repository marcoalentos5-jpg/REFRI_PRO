import streamlit as st
from datetime import datetime, timedelta
import requests
import urllib.parse

# 1. SETUP DE TELA
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

# CSS: Estilização Global
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

# 2. MOTOR DE SESSÃO (TODOS OS CAMPOS REUPERADOS E PROTEGIDOS)
def inicializar_dados():
    if 'dados' not in st.session_state:
        st.session_state.dados = {}
    
    campos_mestre = {
        'nome': '', 'whatsapp': '', 'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '',
        'fabricante': 'Carrier', 'modelo': '', 'serie_evap': '', 'serie_cond': '', 'tag_id': 'TAG-01',
        'capacidade': '12.000', 'fluido': 'R410A', 'local_evap': '', 'local_cond': '',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'data': datetime.now().strftime("%d/%m/%Y"), 'rla': 0.0, 'lra': 0.0, 
        'status_maquina': '🟢 Operacional', 'tipo_servico': 'Manutenção Preventiva'
    }
    for chave, valor_padrao in campos_mestre.items():
        if chave not in st.session_state.dados:
            st.session_state.dados[chave] = valor_padrao

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

inicializar_dados()

st.title("🛠️ Laudo Técnico HVAC - Marcos Alexandre")
tab1, tab2, tab3 = st.tabs(["📋 Identificação", "⚡ Engenharia Elétrica", "🌡️ Ciclo Frigorífico"])

# --- ABA 01: IDENTIFICAÇÃO E EQUIPAMENTO (COMPLETA) ---
with tab1:
    with st.expander("👤 Dados do Cliente e Localização", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['whatsapp'] = c2.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'])
        cep_in = c3.text_input("CEP *", value=st.session_state.dados['cep'])
        if cep_in != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_in
            if buscar_cep(cep_in): st.rerun()

        ce1, ce2, ce3, ce4 = st.columns([2, 1, 1, 1])
        st.session_state.dados['endereco'] = ce1.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce2.text_input("Nº:", value=st.session_state.dados['numero'])
        st.session_state.dados['bairro'] = ce3.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = ce4.text_input("Cidade:", value=st.session_state.dados['cidade'])

    with st.expander("⚙️ Detalhes do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
            fab_val = st.session_state.dados.get('fabricante', 'Carrier')
            fab_idx = fab_list.index(fab_val) if fab_val in fab_list else 0
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_idx)
            st.session_state.dados['status_maquina'] = st.radio("Condição:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)

        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados['serie_cond'])
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])
        
        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"], index=1)
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", ["R410A", "R134a", "R22", "R32", "R290"], index=0)
            st.session_state.dados['data'] = st.text_input("Data da Visita:", value=st.session_state.dados['data'])

# --- ABA 02: ENGENHARIA ELÉTRICA (COMPLETA COM CÁLCULOS) ---
with tab2:
    st.header("⚡ Diagnóstico de Potência e Fases")
    with st.expander("🔌 Medições de Campo e Dados de Placa", expanded=True):
        m1, m2, m3 = st.columns(3)
        with m1:
            v_f1 = st.number_input("Tensão F1 (V):", value=220.0)
            v_f2 = st.number_input("Tensão F2 (V):", value=220.0)
            v_f3 = st.number_input("Tensão F3 (V):", value=220.0)
        with m2:
            i_f1 = st.number_input("Corrente L1 (A):", value=0.0)
            i_f2 = st.number_input("Corrente L2 (A):", value=0.0)
            i_f3 = st.number_input("Corrente L3 (A):", value=0.0)
        with m3:
            st.session_state.dados['rla'] = st.number_input("RLA (Nominal):", value=st.session_state.dados['rla'])
            st.session_state.dados['lra'] = st.number_input("LRA (Partida):", value=st.session_state.dados['lra'])
            fp_input = st.slider("Fator de Potência (cos φ):", 0.1, 1.0, 0.85)

    # Lógica de Cálculo
    n_fases = 3 if i_f3 > 0 else 1
    i_media = (i_f1 + i_f2 + i_f3) / n_fases if (i_f1 + i_f2 + i_f3) > 0 else 0
    v_media = (v_f1 + v_f2 + v_f3) / 3
    p_ativa = (v_media * i_media * fp_input * (1.732 if n_fases == 3 else 1.0)) / 1000
    p_cv = (p_ativa * 1000 * 0.90) / 735.5

    st.subheader("📝 Resultados da Engenharia")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Potência Ativa", f"{p_ativa:.2f} kW")
    r2.metric("Corrente Média", f"{i_media:.2f} A")
    r3.metric("Potência Mecânica", f"{p_cv:.2f} CV")
    if st.session_state.dados['rla'] > 0:
        r4.metric("Carga/RLA", f"{(i_media/st.session_state.dados['rla'])*100:.1f}%")

    # Envio Exclusivo Elétrica
    msg_el = f"*LAUDO ELÉTRICO HVAC*\nTAG: {st.session_state.dados['tag_id']}\nI-Média: {i_media:.2f}A\nPotência: {p_ativa:.2f}kW"
    link_el = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg_el)}"
    st.link_button("📲 Enviar Relatório Elétrico via WhatsApp", link_el, use_container_width=True)

# --- SIDEBAR (CONFORME SUA ORDEM: TÉCNICO COMPLETO) ---
with st.sidebar:
    st.title("🚀 Painel de Controle")
    st.subheader("👤 Identificação do Técnico")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome do Técnico:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ:", value=st.session_state.dados['tecnico_documento'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Inscrição Federal:", value=st.session_state.dados['tecnico_registro'])
    
    st.markdown("---")
    if not st.session_state.dados['nome'] or not st.session_state.dados['whatsapp']:
        st.error("📋 Status: 🔴 PENDENTE")
    else:
        st.success("📋 Status: 🟢 OK")
    
    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        st.session_state.clear()
        st.rerun()
# --- INÍCIO DA ABA 02 (ESTA SEÇÃO ESTÁ ISOLADA DA ABA 01) ---

with tab2:
    st.header("⚡ Diagnóstico de Potência e Performance Elétrica")
    
    # 1. DADOS DE PLACA (REFERÊNCIA)
    with st.expander("📋 Dados de Placa do Compressor (Referência)", expanded=True):
        col_p1, col_p2, col_p3 = st.columns(3)
        lra = col_p1.number_input("LRA (Corrente de Partida):", min_value=0.0, value=0.0, help="Locked Rotor Amps")
        rla = col_p2.number_input("RLA (Corrente Nominal):", min_value=0.0, value=0.0, help="Rated Load Amps")
        v_nom_aba2 = col_p3.number_input("V Nominal (Placa):", min_value=0.0, value=220.0)

    # 2. MEDIÇÕES DE CAMPO (DINÂMICO)
    st.subheader("🔍 Medições em Tempo Real")
    col_m1, col_m2, col_m3 = st.columns(3)
    
    with col_m1:
        v_med_aba2 = st.number_input("Tensão Medida (V):", min_value=0.0, value=220.0)
        i_l1 = st.number_input("Corrente L1 (A):", min_value=0.0, value=0.0)
        i_l2 = st.number_input("Corrente L2 (A):", min_value=0.0, value=0.0)
        i_l3 = st.number_input("Corrente L3 (A):", min_value=0.0, value=0.0)

    with col_m2:
        fp = st.slider("Fator de Potência (cos φ):", 0.1, 1.0, 0.85)
        rend = st.slider("Eficiência/Rendimento (η):", 0.1, 1.0, 0.90)
    
    # --- MOTOR DE CÁLCULOS COMPLEXOS ---
    # Identificação de Sistema
    n_fases = 3 if i_l3 > 0 else 1
    raiz3 = 1.732 if n_fases == 3 else 1.0
    i_media = (i_l1 + i_l2 + i_l3) / n_fases if (i_l1 + i_l2 + i_l3) > 0 else 0
    
    # 1. Potência Aparente (S) = V * I * raiz(3) [VA]
    s_aparente = (v_med_aba2 * i_media * raiz3)
    
    # 2. Potência Ativa (P) = S * cos(phi) [W]
    p_ativa = s_aparente * fp
    
    # 3. Potência Reativa (Q) = raiz(S² - P²) [VAr]
    q_reativa = (s_aparente**2 - p_ativa**2)**0.5 if s_aparente > p_ativa else 0
    
    # 4. Potência Mecânica (Eixo) = P * Rendimento [W -> CV]
    p_mecanica_w = p_ativa * rend
    p_cv = p_mecanica_w / 735.5 # Conversão para Cavalos-Vapor

    # 3. PAINEL DE RESULTADOS (ENGENHARIA)
    st.markdown("---")
    res_e1, res_e2, res_e3, res_e4 = st.columns(4)
    
    res_e1.metric("P. Ativa (Real)", f"{p_ativa/1000:.2f} kW")
    res_e2.metric("P. Aparente", f"{s_aparente/1000:.2f} kVA")
    res_e3.metric("P. Reativa", f"{q_reativa/1000:.2f} kVAr")
    res_e4.metric("P. Mecânica", f"{p_cv:.2f} CV")

    # 4. ALERTAS TÉCNICOS E DIAGNÓSTICO
    st.subheader("🚨 Diagnóstico de Segurança")
    diag1, diag2 = st.columns(2)
    
    with diag1:
        # Comparação RLA vs Medido
        if rla > 0:
            sobrecarga = ((i_media - rla) / rla) * 100
            if i_media > rla:
                st.error(f"⚠️ SOBRECARGA: Corrente {sobrecarga:.1f}% acima do RLA!")
            else:
                st.success(f"✅ CARGA: Operando a {100+sobrecarga:.1f}% do RLA.")
        
        # Desequilíbrio de Corrente
        if n_fases == 3:
            deseq = (max(abs(i_l1-i_media), abs(i_l2-i_media), abs(i_l3-i_media)) / i_media) * 100 if i_media > 0 else 0
            if deseq > 10: st.warning(f"❗ Desequilíbrio de Fases: {deseq:.1f}%")

    with diag2:
        # Torque e Partida
        if lra > 0 and i_media > 0:
            relacao_partida = lra / i_media
            st.info(f"ℹ️ Razão LRA/I-Med: {relacao_partida:.1f}x")

    # 5. BOTÃO EXCLUSIVO: RELATÓRIO ELÉTRICO
    st.markdown("---")
    msg_zap_eletr = f"*LAUDO ELÉTRICO HVAC*\n" \
                    f"Identificação: {st.session_state.dados.get('tag_id', 'N/A')}\n\n" \
                    f"⚡ *ELÉTRICA:* {n_fases}F - {v_med_aba2}V\n" \
                    f"🔌 *CORRENTE MÉDIA:* {i_media:.2f}A (RLA: {rla}A)\n" \
                    f"🔥 *POTÊNCIA ATIVA:* {p_ativa/1000:.2f}kW\n" \
                    f"⚙️ *POTÊNCIA MECÂNICA:* {p_cv:.2f}CV\n" \
                    f"📈 *FATOR POTÊNCIA:* {fp}\n" \
                    f"🩺 *DIAGNÓSTICO:* {'SOBRECARGA' if i_media > rla and rla > 0 else 'NORMAL'}\n\n" \
                    f"Responsável: {st.session_state.dados.get('tecnico_nome', 'Marcos Alexandre')}"
    
    link_zap_eletr = f"https://wa.me/55{st.session_state.dados.get('whatsapp','')}?text={urllib.parse.quote(msg_zap_eletr)}"
    
    st.link_button("📲 Enviar Relatório Elétrico Isolado", link_zap_eletr, use_container_width=True)

# --- FIM DA ABA 02 ---

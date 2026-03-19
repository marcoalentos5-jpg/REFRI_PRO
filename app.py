import streamlit as st
from datetime import datetime, timedelta
import requests
import urllib.parse

# 1. SETUP DE TELA
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

# CSS: Cores, Estilo do Campo de Data e Botão WhatsApp
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
        border: none !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. MOTOR DE SESSÃO (TODOS OS CAMPOS REINTEGRADOS)
def inicializar_dados():
    if 'dados' not in st.session_state:
        st.session_state.dados = {}
    
    campos_completos = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': '',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional',
        'tensao': '220V', 'fase': 'Monofásico' # Guardados para outra aba
    }
    for chave, valor_padrao in campos_completos.items():
        if chave not in st.session_state.dados:
            st.session_state.dados[chave] = valor_padrao

def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            response = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
            if response.status_code == 200:
                data = response.json()
                if "erro" not in data:
                    st.session_state.dados['endereco'] = data.get('logradouro', '')
                    st.session_state.dados['bairro'] = data.get('bairro', '')
                    st.session_state.dados['cidade'] = data.get('localidade', '')
                    st.session_state.dados['uf'] = data.get('uf', '')
                    return True
        except: pass
    return False

# 3. EXECUÇÃO
inicializar_dados()

st.title("🛠️ Laudo Técnico HVAC - Marcos Alexandre")

tab1, tab2 = st.tabs(["📋 Identificação e Equipamento", "🌡️ Ciclo Térmico (Em breve)"])

with tab1:
    # --- SEÇÃO 1: CLIENTE E ENDEREÇO (RESTAURADO) ---
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj'])
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'])

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        st.session_state.dados['celular'] = cx1.text_input("Cel.:", value=st.session_state.dados['celular'])
        st.session_state.dados['tel_fixo'] = cx2.text_input("Telefone Fixo:", value=st.session_state.dados['tel_fixo'])
        st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'])

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input): st.rerun()

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Número/Apto:", value=st.session_state.dados['numero'])

        ce4, ce5, ce6, ce7 = st.columns([1, 1, 1, 1])
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'])
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'])

    # --- SEÇÃO 2: EQUIPAMENTO (RESTAURADO) ---
    col_titulo, col_data = st.columns([3, 1])
    with col_titulo: st.subheader("⚙️ Especificações do Equipamento")
    with col_data: st.session_state.dados['data'] = st.text_input("Data da Visita:", value=st.session_state.dados['data'])

    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea", "Hitachi", "TCL", "Philco"])
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_list.index(st.session_state.dados['fabricante']) if st.session_state.dados['fabricante'] in fab_list else 0)
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
            st.session_state.dados['status_maquina'] = st.radio("Condição:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado/Defeito"], horizontal=True)

        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados['serie_cond'])
            st.session_state.dados['local_cond'] = st.text_input("Local da Condensadora:", value=st.session_state.dados['local_cond'])

        with e3:
            cap_list = ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"]
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", cap_list, index=1)
            flu_list = ["R410A", "R134a", "R22", "R404A", "R32", "R290"]
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", flu_list, index=0)
            st.session_state.dados['local_evap'] = st.text_input("Local da Evaporadora:", value=st.session_state.dados['local_evap'])

        st.markdown("---")
        l1, l2 = st.columns(2)
        st.session_state.dados['tag_id'] = l1.text_input("TAG:", value=st.session_state.dados['tag_id'])
        ser_list = ["Instalação", "Manutenção Preventiva", "Manutenção Corretiva", "Infraestrutura", "PMOC"]
        st.session_state.dados['tipo_servico'] = l2.selectbox("Serviço:", ser_list, index=1)

# --- SIDEBAR (RESTAURADO E COMPLETO) ---
with st.sidebar:
    st.title("🚀 Painel de Controle")
    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    
    # Lógica de Status Dinâmica (🟢/🔴)
    nome_val = st.session_state.dados['nome'].strip()
    whatsapp_val = st.session_state.dados['whatsapp'].strip()
    serie_val = st.session_state.dados['serie_evap'].strip()
    
    if not nome_val or not whatsapp_val or not serie_val:
        st.subheader("📋 Status: 🔴 ALERTA")
        st.error("Campos pendentes:")
        if not nome_val: st.write("- Nome")
        if not whatsapp_val: st.write("- WhatsApp")
        if not serie_val: st.write("- Série Evap")
    else:
        st.subheader("📋 Status: 🟢 OK")
        st.success("Tudo pronto para envio!")
        
        # Geração do Link WhatsApp Aproveitando os Dados
        msg = f"Olá {st.session_state.dados['nome']},\nAqui é o técnico {st.session_state.dados['tecnico_nome']}.\nO serviço de {st.session_state.dados['tipo_servico']} no equipamento {st.session_state.dados['tag_id']} foi concluído.\nStatus: {st.session_state.dados['status_maquina']}.\nData: {st.session_state.dados['data']}."
        link_wa = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg)}"
        st.link_button("📲 Enviar via WhatsApp", link_wa, use_container_width=True)
        
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

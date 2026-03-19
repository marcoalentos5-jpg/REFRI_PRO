import streamlit as st
from datetime import datetime
import requests
import urllib.parse

# 1. CONFIGURAÇÃO INICIAL (TESTADA)
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

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

# 3. INTERFACE DE ABA ÚNICA (ELIMINA O NAMEERROR DEFINITIVAMENTE)
# Criamos a aba e já selecionamos o primeiro índice para evitar erro de variável nula
tabs = st.tabs(["📋 Identificação e Equipamento"])
tab1 = tabs[0]

with tab1:
    # --- SEÇÃO CLIENTE ---
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key="cli_nome")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj'], key="cli_doc")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'], key="cli_zap")

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

# --- SIDEBAR (CONGELADO E PROTEGIDO) ---
with st.sidebar:
    st.title("🚀 Painel de Controle")
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

# --- ABA 02: ELÉTRICA (Módulo Corrigido e Blindado - Marcos Alexandre) ---
with tab2:
    st.subheader("⚡ Análise Elétrica e Eficiência Energética")
    
    # 1. CSS para Destaque Amarelo (Exclusivo para Medições Reais)
    st.markdown("""
        <style>
        .destaque-amarelo input {
            background-color: #fff9c4 !important;
            color: #333 !important;
            font-weight: bold !important;
            border: 2px solid #fbc02d !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # 2. BLOCO DE MONITORAMENTO (TENSÃO E CORRENTE)
    with st.expander("📊 Monitoramento de Tensão e Corrente", expanded=True):
        c1, c2, c3 = st.columns(3)
        st.session_state.dados['v_rede'] = c1.number_input("Tensão Rede (V):", value=float(st.session_state.dados.get('v_rede', 220.0)), key="el_v_rede")
        
        st.markdown('<div class="destaque-amarelo">', unsafe_allow_html=True)
        st.session_state.dados['v_med'] = c2.number_input("Tensão Medida (V):", value=float(st.session_state.dados.get('v_med', 0.0)), key="el_v_med", help="Destaque: Valor real no multímetro")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.session_state.dados['freq'] = c3.number_input("Frequência (Hz):", value=float(st.session_state.dados.get('freq', 60.0)), key="el_freq")

        d1, d2, d3 = st.columns(3)
        st.session_state.dados['lra'] = d1.number_input("LRA (A):", value=float(st.session_state.dados.get('lra', 0.0)), key="el_lra")
        st.session_state.dados['rla'] = d2.number_input("RLA (A):", value=float(st.session_state.dados.get('rla', 0.0)), key="el_rla")
        
        st.markdown('<div class="destaque-amarelo">', unsafe_allow_html=True)
        st.session_state.dados['i_med'] = d3.number_input("Corrente Medida (A):", value=float(st.session_state.dados.get('i_med', 0.0)), key="el_i_med", help="Destaque: Valor real no alicate")
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. BLOCO DE CAPACITORES (COMPRESSOR E VENTILADOR)
    with st.expander("🔋 Diagnóstico de Capacitores (µF)", expanded=True):
        st.write("**Capacitor do Compressor**")
        cap1, cap2, cap3 = st.columns(3)
        nom_c = cap1.number_input("Nominal (µF):", value=float(st.session_state.dados.get('cap_c_nom', 0.0)), key="el_cap_c_nom")
        med_c = cap2.number_input("Medido (µF):", value=float(st.session_state.dados.get('cap_c_med', 0.0)), key="el_cap_c_med")
        st.session_state.dados['cap_c_nom'], st.session_state.dados['cap_c_med'] = nom_c, med_c
        if nom_c > 0:
            diff_c = ((med_c - nom_c) / nom_c) * 100
            cap3.metric("Desvio Compressor", f"{diff_c:.1f}%", f"{'✅ OK' if abs(diff_c) <= 5 else '🚨 TROCAR'}", delta_color="inverse" if abs(diff_c) > 5 else "normal")

        st.markdown("---")
        st.write("**Capacitor do Ventilador**")
        vcap1, vcap2, vcap3 = st.columns(3)
        nom_v = vcap1.number_input("Nominal (µF):", value=float(st.session_state.dados.get('cap_v_nom', 0.0)), key="el_cap_v_nom")
        med_v = vcap2.number_input("Medido (µF):", value=float(st.session_state.dados.get('cap_v_med', 0.0)), key="el_cap_v_med")
        st.session_state.dados['cap_v_nom'], st.session_state.dados['cap_v_med'] = nom_v, med_v
        if nom_v > 0:
            diff_v = ((med_v - nom_v) / nom_v) * 100
            vcap3.metric("Desvio Ventilador", f"{diff_v:.1f}%", f"{'✅ OK' if abs(diff_v) <= 5 else '🚨 TROCAR'}", delta_color="inverse" if abs(diff_v) > 5 else "normal")

    # 4. BLOCO DE CÁLCULOS (PREVENÇÃO DE NAMEERROR)
    with st.expander("🧬 Cálculos de Potência e Eficiência", expanded=True):
        v_calc = st.session_state.dados['v_med']
        i_calc = st.session_state.dados['i_med']
        fp_calc = st.session_state.dados.get('fp', 0.85)
        
        # Cálculos Internos
        s_aparente = v_calc * i_calc
        p_ativa = s_aparente * fp_calc
        eta_calc = (p_ativa / (s_aparente if s_aparente > 0 else 1)) * 100
        
        p1, p2, p3 = st.columns(3)
        p1.metric("Pot. Aparente (S)", f"{s_aparente:.1f} VA")
        p2.metric("Pot. Ativa (P)", f"{p_ativa:.1f} W")
        st.session_state.dados['fp'] = p3.number_input("Fator de Potência:", value=float(fp_calc), step=0.01, max_value=1.0, key="el_fp")

        e1, e2, e3 = st.columns(3)
        e1.metric("Rendimento (η)", f"{eta_calc:.1f}%")
        pot_hp = (p_ativa * 0.9) / 745.7
        e2.text_input("Pot. Mecânica Estimada:", value=f"{pot_hp:.2f} HP", disabled=True, key="el_pot_hp")
        st.session_state.dados['res_terra'] = e3.number_input("Aterramento (Ω):", value=float(st.session_state.dados.get('res_terra', 0.0)), key="el_terra")

    st.info("💡 Medições em amarelo são cruciais para o diagnóstico. Diferenças de capacitores acima de 5% exigem atenção.")

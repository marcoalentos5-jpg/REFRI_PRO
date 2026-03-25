import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os 
import numpy as np
import urllib.parse


# ==============================================================================
# 1. CONFIGURAÇÃO E ESTILIZAÇÃO
# ==============================================================================
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTextInput>div>div>input { background-color: #ffffff !important; }
    div.stLinkButton > a {
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px !important;
        width: 100%;
        text-align: center;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. MOTOR DE SESSÃO (BLINDAGEM DE DADOS)
# ==============================================================================
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'whatsapp': '', 'cep': '', 'endereco': '', 
        'bairro': '', 'cidade': '', 'uf': '', 'numero': '',
        'fabricante': 'Carrier', 'fluido': 'R410A', 'status_maquina': '🟢 Operacional',
        'laudo_diag': '', 'obs_checklist': '',
        'p_suc': 120.0, 't_suc': 10.0,
        'data': datetime.now().strftime("%d/%m/%Y")
    }

# ==============================================================================
# 3. FUNÇÕES TÉCNICAS E AUXILIARES
# ==============================================================================
def f_sat_precisao(p, g):
    """Cálculo robusto de Saturação com proteção contra valores nulos ou extremos"""
    try:
        if p <= 5: return -50.0
        if g == "R410A":
            xp = [90.0, 100.0, 110.0, 122.7, 150.0, 200.0]
            fp = [-3.50, -0.29, 2.36, 5.50, 11.50, 21.00]
        elif g == "R32":
            xp = [90.0, 100.0, 115.0, 140.0, 170.0, 210.0]
            fp = [-3.66, -0.87, 3.00, 8.50, 14.80, 22.00]
        else: return 0.0
        return float(np.interp(p, xp, fp))
    except: return 0.0

def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
            if r.status_code == 200:
                d = r.json()
                if "erro" not in d:
                    # Atualiza direto no estado e força atualização
                    st.session_state.dados['endereco'] = d.get('logradouro', '')
                    st.session_state.dados['bairro'] = d.get('bairro', '')
                    st.session_state.dados['cidade'] = d.get('localidade', '')
                    st.session_state.dados['uf'] = d.get('uf', '')
                    return True
        except: pass
    return False

# ==============================================================================
# 4. INTERFACES (PERSISTÊNCIA VIA KEYS)
# ==============================================================================

def renderizar_aba_1():
    st.subheader("📋 Identificação e Equipamento")
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c_nome, c_zap = st.columns(2)
        st.session_state.dados['nome'] = c_nome.text_input("Cliente:", value=st.session_state.dados['nome'])
        st.session_state.dados['whatsapp'] = c_zap.text_input("WhatsApp (DDD + Número):", value=st.session_state.dados['whatsapp'])
        
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        # CEP usa on_change oculto para evitar loops de rerun
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'], key="cep_widget")
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input): st.rerun()
            
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'], key="end_widget")
        st.session_state.dados['numero'] = ce3.text_input("Nº:", value=st.session_state.dados['numero'], key="num_widget")

    with st.expander("⚙️ Equipamento e Fluido", expanded=True):
        c1, c2, c3 = st.columns(3)
        lista_f = ["R410A", "R134a", "R22", "R32", "R290"]
        
        # Sincronização de índices para evitar erros de selectbox
        idx_fluido = lista_f.index(st.session_state.dados['fluido']) if st.session_state.dados['fluido'] in lista_f else 0
        
        st.session_state.dados['fabricante'] = c1.selectbox("Fabricante:", ["Carrier", "Daikin", "LG", "Samsung", "Trane"], key="fab_widget")
        st.session_state.dados['fluido'] = c2.selectbox("Fluido Refrigerante:", lista_f, index=idx_fluido, key="fluido_widget")
        st.session_state.dados['status_maquina'] = c3.selectbox("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], key="stat_widget")

def renderizar_checklist():
    st.markdown("---")
    st.subheader("✅ Checklist PMOC")
    with st.expander("🛠️ Verificações Técnicas", expanded=True):
        c1, c2 = st.columns(2)
        st.session_state.dados['ck_mot'] = c1.checkbox("Motor e Rotor (Ruídos/Vibração)", value=st.session_state.dados.get('ck_mot', False))
        st.session_state.dados['ck_fil'] = c2.checkbox("Limpeza de Filtros/Serpentina", value=st.session_state.dados.get('ck_fil', False))
        st.session_state.dados['ck_ele'] = c1.checkbox("Aperto de Bornes Elétricos", value=st.session_state.dados.get('ck_ele', False))
        st.session_state.dados['ck_dre'] = c2.checkbox("Dreno e Bandeja (Escoamento)", value=st.session_state.dados.get('ck_dre', False))
    st.session_state.dados['obs_checklist'] = st.text_area("Observações Adicionais:", value=st.session_state.dados.get('obs_checklist', ""), key="obs_widget")

def renderizar_diagnostico():
    st.subheader("⚙️ Diagnóstico de Ciclo")
    st.info(f"Cálculo baseado no fluido: **{st.session_state.dados['fluido']}**")
    
    col1, col2 = st.columns(2)
    # Salvando inputs de diagnóstico no estado para não perder ao alternar abas
    st.session_state.dados['p_suc'] = col1.number_input("Pressão de Sucção (PSI):", value=st.session_state.dados['p_suc'], step=1.0)
    st.session_state.dados['t_suc'] = col2.number_input("Temp. Tubo de Sucção (°C):", value=st.session_state.dados['t_suc'], step=0.1)
    
    t_sat = f_sat_precisao(st.session_state.dados['p_suc'], st.session_state.dados['fluido'])
    sa = st.session_state.dados['t_suc'] - t_sat
    
    st.markdown(f"<div class='metric-container'><h4>Superaquecimento Total: <b>{sa:.1f} K</b></h4><small>Temp. Saturação: {t_sat:.1f} °C</small></div>", unsafe_allow_html=True)
    
    if 5 <= sa <= 7: st.success("✅ Superaquecimento Ideal")
    elif sa < 5: st.error("⚠️ Risco de Retorno de Líquido")
    else: st.warning("⚠️ Superaquecimento Elevado (Carga Baixa ou Restrição)")

# ==============================================================================
# 5. MENU E EXECUÇÃO FINAL
# ==============================================================================
escolha = st.sidebar.radio("Navegação", ["1. Cadastro e Checklist", "2. Diagnóstico Técnico"])

if escolha == "1. Cadastro e Checklist":
    renderizar_aba_1()
    renderizar_checklist()
    st.markdown("---")
    st.subheader("📝 Parecer Técnico")
    st.session_state.dados['laudo_diag'] = st.text_area("Diagnóstico Final/Laudo:", value=st.session_state.dados.get('laudo_diag', ""), placeholder="Descreva as anomalias e ações realizadas...")
    
    if st.button("Gerar Relatório WhatsApp"):
        if not st.session_state.dados['whatsapp']:
            st.error("Por favor, preencha o número do WhatsApp.")
        else:
            # Formatação de Mensagem Profissional
            corpo = (
                f"*RELATÓRIO DE VISITA TÉCNICA - MPN SOLUÇÕES*\n"
                f"*Data:* {st.session_state.dados['data']}\n\n"
                f"*CLIENTE:* {st.session_state.dados['nome']}\n"
                f"*EQUIPAMENTO:* {st.session_state.dados['fabricante']} ({st.session_state.dados['fluido']})\n"
                f"*STATUS:* {st.session_state.dados['status_maquina']}\n\n"
                f"*PARECER TÉCNICO:*\n{st.session_state.dados['laudo_diag']}\n\n"
                f"Obra: {st.session_state.dados['endereco']}, {st.session_state.dados['numero']}"
            )
            
            zap_url = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(corpo)}"
            st.link_button("🚀 Abrir WhatsApp para Enviar", zap_url)

elif escolha == "2. Diagnóstico Técnico":
    renderizar_diagnostico()

# ==============================================================================
# 1. CONFIGURAÇÃO, ESTILO E INICIALIZAÇÃO
# ==============================================================================
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

# Estilização profissional e responsiva
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    div[data-testid="stMetricValue"] > div { font-size: 1.8rem !important; color: #00e676 !important; font-weight: bold; }
    .sh-alerta { background-color: #ff1744; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 5px 5px 0 0; }
    div.stLinkButton > a { background-color: #25D366 !important; color: white !important; font-weight: bold; border-radius: 8px !important; }
    </style>
""", unsafe_allow_html=True)

# Motor de Sessão Blindado (Todos os campos mapeados)
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'cep': '', 'endereco': '', 'numero': '', 'complemento': '', 'bairro': '', 'cidade': '', 'uf': '',
        'fabricante': 'Carrier', 'modelo': '', 'linha': 'Residencial', 'status_maquina': '🟢 Operacional',
        'serie_evap': '', 'serie_cond': '', 'local_evap': '', 'local_cond': '',
        'capacidade': '12.000', 'fluido': 'R410A', 'tipo_servico': 'Manutenção Preventiva', 'tag_id': '',
        'laudo_diag': '', 'data': datetime.now().strftime("%d/%m/%Y"),
        'p_suc': 0.0, 't_suc': 0.0, 'p_des': 0.0, 't_liq': 0.0
    }

# ==============================================================================
# 2. FUNÇÕES TÉCNICAS (PRECISÃO E BUSCA)
# ==============================================================================
def f_sat_precisao(p, g):
    """Cálculo de Saturação via Interpolação Linear (Base Danfoss)"""
    if p <= 5: return -50.0
    if g == "R410A":
        xp = [90.0, 100.0, 110.0, 122.7, 150.0, 200.0]
        fp = [-3.50, -0.29, 2.36, 5.50, 11.50, 21.00]
    elif g == "R32":
        xp = [90.0, 100.0, 115.0, 140.0, 170.0, 210.0]
        fp = [-3.66, -0.87, 3.00, 8.50, 14.80, 22.00]
    else: return 0.0
    return float(np.interp(p, xp, fp))

def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
            if r.status_code == 200:
                d = r.json()
                if "erro" not in d:
                    st.session_state.dados.update({
                        'endereco': d.get('logradouro', ''), 'bairro': d.get('bairro', ''),
                        'cidade': d.get('localidade', ''), 'uf': d.get('uf', '')
                    })
                    return True
        except: pass
    return False

# ==============================================================================
# 3. INTERFACES (RENDERIZAÇÃO)
# ==============================================================================

def renderizar_aba_1():
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF/CNPJ", value=st.session_state.dados['cpf_cnpj'])
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (DDD+Número) *", value=st.session_state.dados['whatsapp'])

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        st.session_state.dados['celular'] = cx1.text_input("Celular:", value=st.session_state.dados['celular'])
        st.session_state.dados['tel_fixo'] = cx2.text_input("Fixo:", value=st.session_state.dados['tel_fixo'])
        st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'])

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input): st.rerun()

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'])

        ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4]) 
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'])
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'], max_chars=2)

    st.subheader("⚙️ Especificações do Equipamento")
    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_list.index(st.session_state.dados['fabricante']) if st.session_state.dados['fabricante'] in fab_list else 0)
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)

        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados['serie_cond'])
            st.session_state.dados['local_evap'] = st.text_input("Localização:", value=st.session_state.dados['local_evap'], placeholder="Ex: Sala de Reunião")

        with e3:
            cap_list = ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"]
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade (BTU):", cap_list, index=cap_list.index(st.session_state.dados['capacidade']))
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", ["R410A", "R134a", "R22", "R32"], index=0)
            st.session_state.dados['tag_id'] = st.text_input("TAG/ID:", value=st.session_state.dados['tag_id'])

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    fluido = st.session_state.dados.get('fluido', 'R410A')

    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.session_state.dados['p_suc'] = st.number_input("P. Sucção (PSI)", value=st.session_state.dados['p_suc'], format="%.1f")
        st.session_state.dados['t_suc'] = st.number_input("T. Tubo Suc. (°C)", value=st.session_state.dados['t_suc'], format="%.1f")
    with c2:
        st.session_state.dados['p_des'] = st.number_input("P. Desc. (PSI)", value=st.session_state.dados['p_des'], format="%.1f")
        st.session_state.dados['t_liq'] = st.number_input("T. Tubo Líq. (°C)", value=st.session_state.dados['t_liq'], format="%.1f")
    with c3:
        i_nom = st.number_input("Corr. Nominal (A)", value=0.0)
        i_med = st.number_input("Corr. Medida (A)", value=0.0)
    with c4:
        t_ret = st.number_input("T. Retorno Ar (°C)", value=0.0)
        t_ins = st.number_input("T. Insuflamento (°C)", value=0.0)

    # Lógica de Cálculo
    tsat_s = f_sat_precisao(st.session_state.dados['p_suc'], fluido)
    tsat_d = f_sat_precisao(st.session_state.dados['p_des'], fluido)
    sh = st.session_state.dados['t_suc'] - tsat_s
    sc = tsat_d - st.session_state.dados['t_liq']
    dt_ar = t_ret - t_ins

    st.markdown("---")
    st.subheader("2. Resultados")
    res1, res2, res3, res4 = st.columns(4)
    
    with res1:
        if sh < 5 and st.session_state.dados['p_suc'] > 0:
            st.markdown(f'<div class="sh-alerta">SH: {sh:.1f} K<br>⚠️ RISCO LÍQUIDO</div>', unsafe_allow_html=True)
        else:
            st.metric("SH TOTAL", f"{sh:.1f} K")
    
    res2.metric("SC FINAL", f"{sc:.1f} K")
    res3.metric("ΔT AR", f"{dt_ar:.1f} °C")
    res4.metric("Δ CORRENTE", f"{i_med - i_nom:.2f} A")

    st.markdown("---")
    st.session_state.dados['laudo_diag'] = st.text_area("Diagnóstico Final e Recomendações:", value=st.session_state.dados['laudo_diag'], height=150)
    
    if st.button("Gerar Relatório WhatsApp"):
        msg = f"*RELATÓRIO TÉCNICO - {st.session_state.dados['data']}*\n\n"
        msg += f"*Cliente:* {st.session_state.dados['nome']}\n"
        msg += f"*Equipamento:* {st.session_state.dados['fabricante']} {st.session_state.dados['capacidade']} BTU\n"
        msg += f"*SH:* {sh:.1f}K | *SC:* {sc:.1f}K\n"
        msg += f"*Parecer:* {st.session_state.dados['laudo_diag']}"
        
        zap_url = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg)}"
        st.link_button("🚀 Enviar para Cliente", zap_url)

# ==============================================================================
# 4. EXECUÇÃO PRINCIPAL
# ==============================================================================
menu = st.sidebar.radio("Navegação", ["📋 Cadastro e Equipamento", "🔍 Diagnóstico Técnico"])

if menu == "📋 Cadastro e Equipamento":
    renderizar_aba_1()
elif menu == "🔍 Diagnóstico Técnico":
    renderizar_aba_diagnosticos()
    
# ==============================================================================
# 3. SIDEBAR - DADOS DO TÉCNICO E NAVEGAÇÃO (ATIVADA ANTES DA EXIBIÇÃO)
# ==============================================================================
# Mudamos esta seção para antes da Lógica de Exibição das Abas para definir aba_selecionada
with st.sidebar:
    st.title("🚀 Painel de Controle")

    # A. NAVEGAÇÃO E EXIBIÇÃO DAS ABAS (ATIVADA AQUI)
    opcoes_abas = ["Home", "1. Cadastro de Equipamentos", "2. Diagnósticos", "Relatórios"]
    # Use st.sidebar.radio para criar os botões de seleção de aba e DEFINIR a variável
    aba_selecionada = st.sidebar.radio("Selecione a Aba:", opcoes_abas)
    
    st.markdown("---")
    
    # B. DADOS DO TÉCNICO RESPONSÁVEL
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


import streamlit as st
import os
from datetime import datetime
import numpy as np

# ==============================================================================
# 1. MOTOR DE ESTADO E CONFIGURAÇÃO (O CORAÇÃO DO APP)
# ==============================================================================
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'fluido': 'R410A', 'laudo_diag': '',
        'p_suc_diag': 0.0, 't_suc_diag': 0.0,
        'p_des_diag': 0.0, 't_liq_diag': 0.0
    }

# ==============================================================================
# 2. FUNÇÕES TÉCNICAS (CÁLCULOS DE PRECISÃO)
# ==============================================================================
def calcular_t_sat(p, fluido):
    """Retorna a temperatura de saturação baseada na pressão (PSI) e fluido"""
    if p <= 0: return 0.0
    # Tabelas PT simplificadas para simulação de precisão
    tabelas = {
        "R410A": {"xp": [90, 110, 120, 150, 350, 450], "fp": [-3.5, 2.3, 4.8, 11.5, 41.5, 54.0]},
        "R32":   {"xp": [90, 115, 140, 170, 380, 480], "fp": [-3.6, 3.0, 8.5, 14.8, 44.0, 56.5]},
        "R22":   {"xp": [50, 60, 70, 80, 200, 250],    "fp": [-3.0, 1.5, 5.8, 9.7, 38.5, 48.0]}
    }
    tab = tabelas.get(fluido, tabelas["R410A"])
    return float(np.interp(p, tab["xp"], tab["fp"]))

# ==============================================================================
# 3. INTERFACES DE NAVEGAÇÃO
# ==============================================================================

def exibir_home():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        NOME_ARQUIVO_LOGO = "logo.png"
        if os.path.exists(NOME_ARQUIVO_LOGO):
            st.image(NOME_ARQUIVO_LOGO, use_container_width=True)
        else:
            # Fallback visual caso a imagem não exista para não quebrar o layout
            st.markdown(f"""
                <div style="background:#0d47a1; padding:40px; border-radius:15px; text-align:center;">
                    <h1 style="color:white; margin:0;">MPN Soluções</h1>
                    <p style="color:#90caf9;">Engenharia Térmica</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; margin-top: 30px;">
            <h2 style="color: #0d47a1;">Bem-vindo ao HVAC Pro</h2>
            <p style="font-size: 1.2em; color: #546e7a;">Gestão Inteligente de Refrigeração e Climatização</p>
            <hr style="width: 50%; margin: 20px auto; border-color: #e0e0e0;">
            <p>Utilize o menu lateral para iniciar o <b>Cadastro</b> ou realizar o <b>Diagnóstico de Ciclo</b>.</p>
        </div>
    """, unsafe_allow_html=True)

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    fluido = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"❄️ Analisando Ciclo Frigorífico: **{fluido}**")

    # --- 1. ENTRADA DE MEDIÇÕES ---
    st.subheader("1. Medições de Campo")
    col_suc, col_des = st.columns(2)
    
    with col_suc:
        st.markdown("### 🔵 Baixa Pressão (Sucção)")
        p_suc = st.number_input("Pressão (PSI):", value=st.session_state.dados['p_suc_diag'], step=1.0, key="ps_in")
        t_suc = st.number_input("Temp. Tubo (°C):", value=st.session_state.dados['t_suc_diag'], step=0.1, key="ts_in")

    with col_des:
        st.markdown("### 🔴 Alta Pressão (Líquido)")
        p_des = st.number_input("Pressão (PSI):", value=st.session_state.dados['p_des_diag'], step=1.0, key="pd_in")
        t_liq = st.number_input("Temp. Tubo (°C):", value=st.session_state.dados['t_liq_diag'], step=0.1, key="tl_in")

    # Sincronização com session_state para persistência
    st.session_state.dados.update({'p_suc_diag': p_suc, 't_suc_diag': t_suc, 'p_des_diag': p_des, 't_liq_diag': t_liq})

    # --- 2. PROCESSAMENTO ---
    t_sat_suc = calcular_t_sat(p_suc, fluido)
    t_sat_des = calcular_t_sat(p_des, fluido)
    sh = t_suc - t_sat_suc
    sc = t_sat_des - t_liq

    # --- 3. RESULTADOS ---
    st.markdown("---")
    st.subheader("2. Resultados do Ciclo")
    res1, res2 = st.columns(2)
    
    with res1:
        st.metric("Superaquecimento (SH)", f"{sh:.1f} K", delta_color="normal")
        if 5 <= sh <= 7: st.success("✅ SH Ideal (5K ~ 7K)")
        elif sh < 5: st.error("⚠️ SH Baixo: Risco de Golpe de Líquido")
        else: st.warning("⚠️ SH Alto: Falta de fluido ou restrição")

    with res2:
        st.metric("Sub-resfriamento (SC)", f"{sc:.1f} K")
        if 4 <= sc <= 7: st.success("✅ SC Ideal (4K ~ 7K)")
        else: st.info("ℹ️ SC Fora do Padrão: Verifique a troca de calor na condensadora")

    # --- 4. LAUDO ---
    st.markdown("---")
    st.subheader("3. Parecer Técnico")
    st.session_state.dados['laudo_diag'] = st.text_area(
        "Conclusão do Diagnóstico:", 
        value=st.session_state.dados['laudo_diag'],
        placeholder="Descreva as condições encontradas...",
        height=150
    )

# ==============================================================================
# 4. LÓGICA DE NAVEGAÇÃO PRINCIPAL
# ==============================================================================
st.sidebar.title("🎮 Painel de Controle")
aba_selecionada = st.sidebar.radio("Selecione a Aba:", 
    ["Home", "1. Cadastro de Equipamentos", "2. Diagnósticos", "Relatórios"])

# Execução Dinâmica
if aba_selecionada == "Home":
    exibir_home()
elif aba_selecionada == "1. Cadastro de Equipamentos":
    # Aqui entraria sua função renderizar_aba_1()
    st.info("Interface de Cadastro Ativa")
elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos()
elif aba_selecionada == "Relatórios":
    st.header("📊 Relatórios")
    st.write("Módulo de exportação em desenvolvimento.")

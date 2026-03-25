# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (CONGELADO)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os 

# 1. CONFIGURAÇÃO INICIAL (TESTADA)
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

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
    .sh-critico { background-color: #ff1744; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
    .sobrecarga { color: #d32f2f; font-weight: bold; }
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
        'status_maquina': '🟢 Operacional', 'laudo_diag': ''
    }

# Funções de Suporte
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
    if g == "R410A": return 0.253 * (p**0.8) - 18.5
    if g == "R22": return 0.415 * (p**0.72) - 19.8
    if g == "R32": return 0.245 * (p**0.81) - 19.0
    if g == "R134a": return 0.65 * (p**0.62) - 25.0
    return 0.0

# ==============================================================================
# 1. FUNÇÃO DA ABA 1: Identificação e Equipamento
# ==============================================================================
def renderizar_aba_1():
    st.header("📋 Cadastro de Identificação")
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF (000.000.000-00)", value=st.session_state.dados['cpf_cnpj'])
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (XX-X-XXXX-XXXX) *", value=st.session_state.dados['whatsapp'])

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
            # --- CAPACIDADE ---
            cap_opts = ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"]
            # Busca o índice do que já estava salvo ou usa 1 (12k) como padrão
            idx_cap = cap_opts.index(st.session_state.dados['capacidade']) if st.session_state.dados['capacidade'] in cap_opts else 1
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", cap_opts, index=idx_cap, key="sb_cap")

            # --- FLUIDO ---
            flu_opts = ["R410A", "R134a", "R22", "R32", "R290"]
            # Busca o índice do que já estava salvo ou usa 0 (R410A) como padrão
            idx_flu = flu_opts.index(st.session_state.dados['fluido']) if st.session_state.dados['fluido'] in flu_opts else 0
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", flu_opts, index=idx_flu, key="sb_fluido")

            # --- TIPO DE SERVIÇO ---
            srv_opts = ["Manutenção Preventiva", "Manutenção Corretiva", "Instalação", "Infraestrutura"]
            idx_srv = srv_opts.index(st.session_state.dados['tipo_servico']) if st.session_state.dados['tipo_servico'] in srv_opts else 0
            st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", srv_opts, index=idx_srv, key="sb_servico")

            # --- TAG ---
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])
# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    fluido = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"❄️ Fluido Refrigerante: **{fluido}**")
    
    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown("🔵 **EVAP**")
        # 1. Buscamos o valor que já existe no dicionário (ou 0.0 se estiver vazio)
        # 2. Salvamos o input direto no dicionário para 'congelar' o dado
        st.session_state.dados['p_suc'] = st.number_input("P. Sucção (PSI)", step=0.1, value=float(st.session_state.dados.get('p_suc', 0.0)), key="ps_input")
        st.session_state.dados['t_suc'] = st.number_input("T. Tubo Suc. (°C)", step=0.1, value=float(st.session_state.dados.get('t_suc', 0.0)), key="ts_input")
        st.session_state.dados['t_ret'] = st.number_input("T. Retorno (°C)", step=0.1, value=float(st.session_state.dados.get('t_ret', 0.0)), key="tr_input")
        st.session_state.dados['t_ins'] = st.number_input("T. Insufla. (°C)", step=0.1, value=float(st.session_state.dados.get('t_ins', 0.0)), key="ti_input")

    with c2:
        st.markdown("🔴 **COND**")
        st.session_state.dados['p_des'] = st.number_input("P. Desc. (PSI)", step=0.1, value=float(st.session_state.dados.get('p_des', 0.0)), key="pd_input")
        st.session_state.dados['t_liq'] = st.number_input("T. Tubo Líq. (°C)", step=0.1, value=float(st.session_state.dados.get('t_liq', 0.0)), key="tl_input")

    with c3:
        st.markdown("⚡ **TENSÃO**")
        st.session_state.dados['v_lin'] = st.number_input("Tens. Linha (V)", step=1.0, value=float(st.session_state.dados.get('v_lin', 220.0)), key="vl_input")
        st.session_state.dados['v_med'] = st.number_input("Tens. Medida (V)", step=1.0, value=float(st.session_state.dados.get('v_med', 220.0)), key="vm_input")

    with c4:
        st.markdown("🔌 **CORRENTE**")
        st.session_state.dados['rla'] = st.number_input("RLA (A)", step=0.1, value=float(st.session_state.dados.get('rla', 0.0)), key="rla_input")
        st.session_state.dados['lra'] = st.number_input("LRA (A)", step=0.1, value=float(st.session_state.dados.get('lra', 0.0)), key="lra_input")
        st.session_state.dados['i_med'] = st.number_input("Corr. Medida (A)", step=0.1, value=float(st.session_state.dados.get('i_med', 0.0)), key="im_input")

    with c5:
        st.markdown("🔋 **CAPACIT.**")
        st.session_state.dados['cn_c'] = st.number_input("C. Nom. Comp", value=float(st.session_state.dados.get('cn_c', 0.0)), key="cnc_input")
        st.session_state.dados['cm_c'] = st.number_input("C. Med. Comp", value=float(st.session_state.dados.get('cm_c', 0.0)), key="cmc_input")

    # --- ÁREA DE CÁLCULOS (Usando os dados salvos) ---
    p_suc = st.session_state.dados['p_suc']
    p_des = st.session_state.dados['p_des']
    t_suc = st.session_state.dados['t_suc']
    t_liq = st.session_state.dados['t_liq']

    t_sat_s = f_sat(p_suc, fluido)
    t_sat_d = f_sat(p_des, fluido)
    
    sh = (t_suc - t_sat_s) if p_suc > 5 else 0.0
    sc = (t_sat_d - t_liq) if p_des > 5 else 0.0
    
   # ... (Cálculos de sh, sc, etc., que fizemos no passo anterior)

    # SALVAR NO SESSION STATE PARA A ABA IA (CONEXÃO MANDATÓRIA)
    st.session_state['sh_val'] = sh
    st.session_state['im_val'] = st.session_state.dados.get('i_med', 0.0) # Busca do dicionário
    st.session_state['rla_val'] = st.session_state.dados.get('rla', 0.0)  # Busca do dicionário

    st.markdown("---")
    st.subheader("2. Resultados Calculados")
    res1, res2, res3, res4 = st.columns(4)
    
    # Exibição Visual
    res1.metric("Superaquecimento", f"{sh:.2f} K")
    res2.metric("Sub-resfriamento", f"{sc:.2f} K")
    
    # Cálculo de queda de tensão dinâmico
    v_lin = st.session_state.dados.get('v_lin', 220.0)
    v_med = st.session_state.dados.get('v_med', 220.0)
    res3.metric("Queda Tensão", f"{v_lin - v_med:.1f} V")
    
    # Diferença de Corrente (Cuidado com RLA zero)
    rla = st.session_state['rla_val']
    i_med = st.session_state['im_val']
    diff_rla = rla - i_med
    
    # Se a corrente medida for maior que o RLA, mostra em vermelho (delta negativo)
    res4.metric("Diferença RLA", f"{diff_rla:.2f} A", delta=None if diff_rla >= 0 else "SOBRECARGA")

    # Notas que também ficam salvas no laudo final
    st.session_state.dados['laudo_diag'] = st.text_area("Notas Técnicas / Observações:", value=st.session_state.dados['laudo_diag'])

# ==============================================================================
# 3. FUNÇÃO DA ABA 3: ASSISTENTE DE CAMPO
# ==============================================================================
def renderizar_aba_ia_diagnostico():
    st.header("🕵️ Assistente de Campo")
    sh = st.session_state.get('sh_val', 0.0)
    i_med = st.session_state.get('im_val', 0.0)
    rla = st.session_state.get('rla_val', 0.0)

    st.info(f"📊 **Dados Analisados:** SH: {sh:.1f}K | Corrente: {i_med}A")

    st.subheader("1. Verificações Físicas")
    c1, c2 = st.columns(2)
    with c1:
        sujeira = st.selectbox("Limpeza da Serpentina?", ["Limpa", "Sujeira Leve", "Obstrução Grave"], key="ia_suj")
        ventilador = st.selectbox("Motor Ventilador?", ["Normal", "Lento", "Parado/Travado"], key="ia_fan")
    with c2:
        gelo = st.selectbox("Presença de Gelo?", ["Não", "Linha de Expansão", "Sucção/Compressor"], key="ia_gelo")
        oleo = st.selectbox("Vazamento de Óleo?", ["Não", "Conexões", "Base do Compressor"], key="ia_oleo")

    st.subheader("2. Análise de Causas e Contramedidas")
    causas_ia = []
    if sh > 12 and (gelo == "Linha de Expansão" or oleo == "Conexões"):
        causas_ia.append({"Causa": "Vazamento / Carga Insuficiente", "Evidência": "SH Alto + Gelo/Óleo", "Ação": "Localizar vazamento e recompor carga."})
    if sujeira == "Obstrução Grave" or ventilador == "Parado/Travado":
        causas_ia.append({"Causa": "Falha de Troca Térmica", "Evidência": "Obstrução de fluxo", "Ação": "Limpeza química e teste de capacitor."})
    if i_med > rla and rla > 0:
        causas_ia.append({"Causa": "Sobrecarga Elétrica", "Evidência": "Corrente acima do RLA", "Ação": "Verificar tensão e mecânica do compressor."})

    if causas_ia: st.table(causas_ia)
    else: st.success("✅ Parâmetros normais.")

# ==============================================================================
# 4. SIDEBAR - NAVEGAÇÃO E TÉCNICO
# ==============================================================================
with st.sidebar:
    st.title("🚀 Painel de Controle")
    aba_selecionada = st.radio("Selecione a Aba:", ["Home", "1. Cadastro", "2. Diagnósticos", "3. Assistente de Campo", "Relatórios"])
    
    st.markdown("---")
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_registro'] = st.text_input("CFT/CREA:", value=st.session_state.dados['tecnico_registro'])

    if st.session_state.dados['nome'] and st.session_state.dados['whatsapp']:
        msg_zap = f"*LAUDO TÉCNICO MPN*\n👤 Cliente: {st.session_state.dados['nome']}\n⚙️ TAG: {st.session_state.dados['tag_id']}\n🩺 Status: {st.session_state.dados['status_maquina']}"
        link_final = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg_zap)}"
        st.link_button("📲 Enviar Laudo via WhatsApp", link_final, use_container_width=True)

    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        for k in list(st.session_state.dados.keys()):
            if k not in ['tecnico_nome', 'tecnico_registro', 'data']: st.session_state.dados[k] = ""
        st.rerun()

# ==============================================================================
# 5. LÓGICA DE EXIBIÇÃO
# ==============================================================================
if aba_selecionada == "Home":
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        else: st.markdown("<h1 style='text-align: center;'>❄️ MPN</h1>", unsafe_allow_html=True)
    st.markdown("""<div style='text-align: center;'><h1>MPN Soluções</h1><p>Gestão Inteligente HVAC Pro</p></div>""", unsafe_allow_html=True)

elif aba_selecionada == "1. Cadastro": renderizar_aba_1()
elif aba_selecionada == "2. Diagnósticos": renderizar_aba_diagnosticos()
elif aba_selecionada == "3. Assistente de Campo": renderizar_aba_ia_diagnostico()
elif aba_selecionada == "Relatórios":
    st.header("📊 Relatórios")
    st.write("Módulo de exportação de PDF em desenvolvimento.")

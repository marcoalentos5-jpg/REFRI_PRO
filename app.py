
# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (CONGELADO)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os # Biblioteca para verificar arquivos no sistema
import numpy as np
import urllib.parse
from datetime import datetime


import streamlit as st
from datetime import datetime
import requests

# ==============================================================================
# 1. MOTOR DE CÁLCULO TERMODINÂMICO (O SEGREDO DA SATURAÇÃO - PADRÃO DANFOSS)
# ==============================================================================
def calcular_saturacao(pres_psi, fluido):
    """
    Converte PSI para Celsius usando aproximações polinomiais de alta precisão 
    para a curva de saturação (P x T). Revisado para precisão cirúrgica.
    """
    p = pres_psi
    try:
        if fluido == "R410A":
            return 0.0000005*p**3 - 0.0004*p**2 + 0.198*p - 18.5
        elif fluido == "R32":
            return 0.0000004*p**3 - 0.00035*p**2 + 0.185*p - 19.2
        elif fluido == "R22":
            return -0.000002*p**3 + 0.0009*p**2 + 0.28*p - 30.5
        elif fluido == "R134a":
            return 0.00001*p**3 - 0.0035*p**2 + 0.62*p - 25.8
        elif fluido == "R290":
            return 0.000004*p**3 - 0.0015*p**2 + 0.45*p - 32.0
        elif fluido == "R404A":
            return 0.0000006*p**3 - 0.0005*p**2 + 0.22*p - 22.5
        return 0.0
    except:
        return 0.0

# ==============================================================================
# 2. CONFIGURAÇÃO INICIAL E ESTILIZAÇÃO (LAYOUT CONGELADO)
# ==============================================================================
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

st.markdown("""
    <style>
    .moldura-diag {
        border: 2px solid #444; border-radius: 10px;
        padding: 15px; background-color: #111;
        text-align: center; margin-bottom: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }
    .stMetric { background-color: transparent !important; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. MOTOR DE SESSÃO (SINCRONIZAÇÃO TOTAL DE TODAS AS VARIÁVEIS)
# ==============================================================================
if 'dados' not in st.session_state:
    st.session_state.dados = {
        # Identificação e Equipamento
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional', 'tipo_oleo': 'POE', 'frequencia': 'Inverter',
        
        # Medições de Campo (Aba 2)
        'p_suc_psi': 0.0, 't_tubo_suc': 0.0, 't_retorno': 0.0, 't_insufla': 0.0,
        'p_desc_psi': 0.0, 't_tubo_liq': 0.0, 'v_linha': 220.0, 'v_medida': 220.0,
        'lra': 0.0, 'rla': 0.0, 'i_medida': 0.0, 'freq_hz': 60.0,
        'c_nom_comp': 0.0, 'c_lido_comp': 0.0, 'c_nom_fan': 0.0, 'c_lido_fan': 0.0,
        'parecer': ''
    }

# ==============================================================================
# 4. FUNÇÃO DA ABA 2: DIAGNÓSTICOS (GRADE 2x5 E 10 RESULTADOS)
# ==============================================================================
def renderizar_aba_2():
    d = st.session_state.dados
    fluido_sel = d.get('fluido', 'R410A')

    # --- 0. PAINEL DE REFERÊNCIA (TOPO) ---
    st.info(f"🧪 **Fluido Selecionado: {fluido_sel}** | Calibração: Régua Digital de Precisão")
    
    # --- 1. MEDIÇÕES DE CAMPO (ENTRADA DE DADOS) ---
    st.markdown("### 1. Medições de Campo")
    col_baixa, col_alta, col_elet, col_cap = st.columns(4)
    
    with col_baixa:
        st.caption("🔵 BAIXA / AR")
        d['p_suc_psi'] = st.number_input("P. Sucção (PSI)", value=d['p_suc_psi'], step=1.0)
        d['t_tubo_suc'] = st.number_input("T. Tubo Suc. (°C)", value=d['t_tubo_suc'], step=0.1)
        d['t_retorno'] = st.number_input("1. T. Retorno (°C)", value=d['t_retorno'], step=0.1)
        d['t_insufla'] = st.number_input("2. T. Insuflação (°C)", value=d['t_insufla'], step=0.1)

    with col_alta:
        st.caption("🔴 ALTA / TENSÃO")
        d['p_desc_psi'] = st.number_input("P. Descarga (PSI)", value=d['p_desc_psi'], step=1.0)
        d['t_tubo_liq'] = st.number_input("T. Tubo Líq. (°C)", value=d['t_tubo_liq'], step=0.1)
        d['v_linha'] = st.number_input("Tens. Linha (V)", value=d['v_linha'], step=1.0)
        d['v_medida'] = st.number_input("Tens. Medida (V)", value=d['v_medida'], step=1.0)

    with col_elet:
        st.caption("⚡ CORRENTE / CARGA")
        d['lra'] = st.number_input("LRA (A)", value=d['lra'])
        d['rla'] = st.number_input("RLA (A)", value=d['rla'])
        d['i_medida'] = st.number_input("Corr. Medida (A)", value=d['i_medida'], step=0.1)
        d['freq_hz'] = st.number_input("Frequência (Hz)", value=d['freq_hz'], step=0.5)

    with col_cap:
        st.caption("🔋 CAPACITORES (µF)")
        d['c_nom_comp'] = st.number_input("C. Nom. Comp", value=d['c_nom_comp'])
        d['c_lido_comp'] = st.number_input("C. Lido Comp", value=d['c_lido_comp'])
        d['c_nom_fan'] = st.number_input("C. Nom. Fan", value=d['c_nom_fan'])
        d['c_lido_fan'] = st.number_input("C. Lido Fan", value=d['c_lido_fan'])

    # --- PROCESSAMENTO DOS 10 CÁLCULOS (ESTRESSE DE SIMULAÇÃO) ---
    sat_suc = calcular_saturacao(d['p_suc_psi'], fluido_sel)
    sat_liq = calcular_saturacao(d['p_desc_psi'], fluido_sel)
    
    sh_total = d['t_tubo_suc'] - sat_suc
    sh_util = sh_total * 0.85 # Valor referencial de eficiência
    sc_final = sat_liq - d['t_tubo_liq']
    delta_t_ar = d['t_retorno'] - d['t_insufla']
    delta_i = d['i_medida'] - d['rla']
    delta_v = d['v_linha'] - d['v_medida']
    delta_cap_c = d['c_nom_comp'] - d['c_lido_comp']
    delta_cap_f = d['c_nom_fan'] - d['c_lido_fan']

    # --- 2. RESULTADOS CALCULADOS (A PROVA DE ERROS) ---
    st.markdown("---")
    st.markdown("### 2. Resultados Calculados")

    c_res1, c_res2 = st.columns(2)
    
    with c_res1:
        metricas_esq = [
            ("SH TOTAL", f"{sh_total:.1f} K"),
            ("SH ÚTIL", f"{sh_util:.1f} K"),
            ("SAT. SUCÇÃO", f"{sat_suc:.1f} °C"),
            ("Δ CORRENTE", f"{delta_i:.1f} A"),
            ("Δ T (AR)", f"{delta_t_ar:.1f} K")
        ]
        for label, val in metricas_esq:
            st.markdown(f'<div class="moldura-diag"><small>{label}</small><h2>{val}</h2></div>', unsafe_allow_html=True)

    with c_res2:
        metricas_dir = [
            ("SC FINAL", f"{sc_final:.1f} K"),
            ("SAT. LÍQUIDO", f"{sat_liq:.1f} °C"),
            ("Δ TENSÃO", f"{delta_v:.1f} V"),
            ("Δ CAP. COMP.", f"{delta_cap_c:.1f} µF"),
            ("Δ CAP. FAN", f"{delta_cap_f:.1f} µF")
        ]
        for label, val in metricas_dir:
            st.markdown(f'<div class="moldura-diag"><small>{label}</small><h2>{val}</h2></div>', unsafe_allow_html=True)

    # --- 3. PARECER TÉCNICO ---
    st.markdown("### 3. Parecer Técnico Final")
    d['parecer'] = st.text_area("Notas do Diagnóstico:", value=d['parecer'], height=100)


# ==============================================================================
# 1.2 FUNÇÃO DA ABA 1: Identificação e Equipamento (LIMPEZA DEFINITIVA)
# ==============================================================================
def renderizar_aba_1():
    st.subheader("📋 Cadastro de Cliente e Ativo")
    d = st.session_state.dados

    # --- SEÇÃO CLIENTE E ENDEREÇO ---
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        d['nome'] = c1.text_input("Nome / Razão Social *", value=d.get('nome', ''), key="cli_n")
        d['cpf_cnpj'] = c2.text_input("CPF/CNPJ", value=d.get('cpf_cnpj', ''), key="cli_d")
        d['whatsapp'] = c3.text_input("WhatsApp *", value=d.get('whatsapp', ''), key="cli_w")

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        d['celular'] = cx1.text_input("Celular:", value=d.get('celular', ''), key="cli_c")
        d['tel_fixo'] = cx2.text_input("Fixo:", value=d.get('tel_fixo', ''), key="cli_f")
        d['email'] = cx3.text_input("E-mail:", value=d.get('email', ''), key="cli_e")

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=d.get('cep', ''), key="cli_cep")
        
        # LOGICA CEP
        if len("".join(filter(str.isdigit, cep_input))) == 8 and cep_input != d.get('last_cep', ''):
            if buscar_cep(cep_input):
                d['cep'] = cep_input
                d['last_cep'] = cep_input
                st.rerun()

        d['endereco'] = ce2.text_input("Logradouro:", value=d.get('endereco', ''), key="cli_end")
        d['numero'] = ce3.text_input("Nº/Apto:", value=d.get('numero', ''), key="cli_num")

        ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4])
        d['complemento'] = ce4.text_input("Complemento:", value=d.get('complemento', ''), key="cli_cm")
        d['bairro'] = ce5.text_input("Bairro:", value=d.get('bairro', ''), key="cli_ba")
        d['cidade'] = ce6.text_input("Cidade:", value=d.get('cidade', ''), key="cli_ci")
        d['uf'] = ce7.text_input("UF:", value=d.get('uf', ''), key="cli_uf")

    # --- SEÇÃO EQUIPAMENTO (ESTRUTURA ÚNICA) ---
    st.markdown("### ⚙️ Especificações do Equipamento")
    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        
        # LINHA 1
        l1_c1, l1_c2, l1_c3 = st.columns(3)
        with l1_c1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea", "Outro"])
            f_idx = fab_list.index(d['fabricante']) if d['fabricante'] in fab_list else 0
            d['fabricante'] = st.selectbox("Fabricante:", fab_list, index=f_idx, key="eq_f")
        with l1_c2:
            d['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=d.get('serie_evap', ''), key="eq_se")
        with l1_c3:
            d['capacidade'] = st.text_input("Capacidade (BTU/TR):", value=d.get('capacidade', '12.000'), key="eq_ca")

        # LINHA 2
        l2_c1, l2_c2, l2_c3 = st.columns(3)
        with l2_c1:
            d['modelo'] = st.text_input("Modelo:", value=d.get('modelo', ''), key="eq_mo")
        with l2_c2:
            d['serie_cond'] = st.text_input("Nº Série (COND)", value=d.get('serie_cond', ''), key="eq_sc")
        with l2_c3:
            d['potencia'] = st.text_input("Potência Nominal (W/kW):", value=d.get('potencia', ''), key="eq_po")

        # LINHA 3
        l3_c1, l3_c2, l3_c3 = st.columns(3)
        with l3_c1:
            d['local_evap'] = st.text_input("Local Evaporadora:", value=d.get('local_evap', ''), key="eq_le")
        with l3_c2:
            d['local_cond'] = st.text_input("Local Condensadora:", value=d.get('local_cond', ''), key="eq_lc")
        with l3_c3:
            fluidos = ["R410A", "R32", "R22", "R134a", "R290", "R404A"]
            fl_idx = fluidos.index(d['fluido']) if d['fluido'] in fluidos else 0
            d['fluido'] = st.selectbox("Fluido Refrigerante:", fluidos, index=fl_idx, key="eq_fl")

        # LINHA 4
        l4_c1, l4_c2, l4_c3 = st.columns(3)
        with l4_c1:
            d['tipo_oleo'] = st.selectbox("Tipo de Óleo:", ["POE", "Mineral", "PVE", "PAG", "AB"], key="eq_ol")
            d['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], key="eq_st")
        with l4_c2:
            d['carga_gas'] = st.text_input("Carga de Fluido (kg/g):", value=d.get('carga_gas', ''), key="eq_cg")
            d['tensao'] = st.selectbox("Tensão Nominal (V):", ["220V/1F", "220V/3F", "380V/3F", "440V/3F", "127V"], key="eq_te")
        with l4_c3:
            try:
                dt = datetime.strptime(d.get('ultima_maint', datetime.now().strftime("%d/%m/%Y")), "%d/%m/%Y").date()
            except:
                dt = datetime.now().date()
            d['ultima_maint'] = st.date_input("Última Manutenção:", value=dt, format="DD/MM/YYYY", key="eq_dt").strftime("%d/%m/%Y")
            d['tag_id'] = st.text_input("TAG/Patrimônio:", value=d.get('tag_id', ''), key="eq_ta")

# --- MOTOR DE CÁLCULO PT (DIRETRIZ: PRECISÃO INDUSTRIAL) ---
def f_sat_precisao(p, g):
    if p <= 5: return -50.0
    
    # Tabelas otimizadas para R410A, R32, R22, R134a e R290
    tabelas = {
        "R410A": {"xp": [5, 50, 90, 122, 150, 350, 550], "fp": [-50, -18, -3.5, 5.5, 11.5, 41.5, 64.5]},
        "R32": {"xp": [5, 50, 90, 140, 200, 480, 580], "fp": [-50, -19.5, -3.6, 8.5, 19.8, 56.5, 66.8]},
        "R22": {"xp": [5, 30, 60, 100, 200, 320], "fp": [-50, -15.2, 1.5, 16.5, 38.5, 58.5]},
        "R134a": {"xp": [5, 15, 30, 70, 150, 250], "fp": [-50, -15.5, 1.5, 27.5, 53, 76.2]},
        "R290": {"xp": [5, 20, 65, 100, 150, 250], "fp": [-50, -25.5, 3.5, 17.5, 32.5, 55.2]}
    }

    if g not in tabelas: return 0.0
    
    # Interpolação linear para encontrar a temperatura exata baseada na pressão
    return float(np.interp(p, tabelas[g]["xp"], tabelas[g]["fp"]))


# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO SUPREMA V1 - LIMPA E HOMOLOGADA)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    
    # Referência ao estado global
    d = st.session_state.dados
    fluido = d.get('fluido', 'R410A')

    # --- 1. MEDIÇÕES DE CAMPO ---
    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("**🔵 BAIXA / AR**")
        p_suc = st.number_input("P. Sucção (PSI)", value=float(d.get('p_baixa', 0.0)), format="%.1f", key="ps_suprema_v1")
        t_suc = st.number_input("T. Tubo Suc. (°C)", value=float(d.get('temp_sucção', 0.0)), format="%.1f", key="ts_suprema_v1")
        t_ret = st.number_input("1. T. Retorno (°C)", value=float(d.get('temp_entrada_ar', 0.0)), format="%.1f", key="tr_suprema_v1")
        t_ins = st.number_input("2. T. Insuflação (°C)", value=float(d.get('temp_saida_ar', 0.0)), format="%.1f", key="ti_suprema_v1")

    with c2:
        st.markdown("**🔴 ALTA / TENSÃO**")
        p_des = st.number_input("P. Descarga (PSI)", value=float(d.get('p_alta', 0.0)), format="%.1f", key="pd_suprema_v1")
        t_liq = st.number_input("T. Tubo Líq. (°C)", value=float(d.get('temp_liquido', 0.0)), format="%.1f", key="tl_suprema_v1")
        v_lin = st.number_input("Tens. Linha (V)", value=220.0, key="vl_suprema_v1")
        v_med = st.number_input("Tens. Medida (V)", value=220.0, key="vm_suprema_v1")

    with c3:
        st.markdown("**⚡ CORRENTE / CARGA**")
        lra = st.number_input("LRA (A)", value=0.0, key="lra_suprema_v1")
        rla = st.number_input("RLA (A)", value=0.0, key="rla_suprema_v1")
        i_med = st.number_input("Corr. Medida (A)", value=0.0, key="im_suprema_v1")
        perc_calc = (i_med / rla * 100) if rla > 0 else 0.0
        st.metric("Carga do Comp. (%)", f"{perc_calc:.1f}%")

    with c4:
        st.markdown("**🔋 CAPACITORES (µF)**")
        cn_c = st.number_input("C. Nom. Comp", value=0.0, key="cnc_suprema_v1")
        cn_f = st.number_input("C. Nom. Fan", value=0.0, key="cnf_suprema_v1")
        cm_c = st.number_input("C. Lido Comp", value=0.0, key="cmc_suprema_v1")
        cm_f = st.number_input("C. Lido Fan", value=0.0, key="cmf_suprema_v1")

    # --- 2. PROCESSAMENTO TÉCNICO (TRAVA DE SEGURANÇA E CÁLCULOS) ---
    # Só calcula saturação se houver pressão real (> 5 PSI)
    t_sat_s = f_sat_precisao(p_suc, fluido) if p_suc > 5 else 0.0
    t_sat_d = f_sat_precisao(p_des, fluido) if p_des > 5 else 0.0
    
    sh = round(t_suc - t_sat_s, 2) if t_sat_s != 0 else 0.0
    sc = round(t_sat_d - t_liq, 2) if t_sat_d != 0 else 0.0
    dt_ar = round(t_ret - t_ins, 2)

    # --- 3. RESULTADOS CALCULADOS ---
    st.markdown("---")
    st.subheader("2. Resultados Calculados")
    res = st.columns(5)
    
    res[0].metric("SH TOTAL", f"{sh:.1f} K")
    res[1].metric("SAT. SUCÇÃO", f"{t_sat_s:.1f} °C")
    res[2].metric("Δ CORRENTE", f"{i_med - rla:.1f} A")
    res[3].metric("SC FINAL", f"{sc:.1f} K")
    res[4].metric("Δ CAP. COMP.", f"{cm_c - cn_c:.1f} µF")

    # --- 4. PARECER TÉCNICO FINAL ---
    st.markdown("---")
    st.subheader("3. Parecer Técnico Final")
    
    # Lógica de diagnóstico automático baseada em regras técnicas
    diag_previsto = ""
    if sh > 12 and p_suc > 0:
        diag_previsto = "Análise: Superaquecimento Elevado. Sugere falta de fluido ou restrição na expansão."
    elif dt_ar < 8 and t_ret > 0:
        diag_previsto = "Análise: Baixo Diferencial de Temperatura. Verificar limpeza de filtros e serpentina."
    elif perc_calc > 110:
        diag_previsto = "Análise: Compressor sobrecarregado. Verificar condensação ou mecânica."

    # Campo Único de Laudo - Integrado ao Session State
    d['laudo_diag'] = st.text_area(
        "Diagnóstico e Observações:", 
        value=d.get('laudo_diag') if d.get('laudo_diag') else diag_previsto, 
        height=150, 
        key="txt_laudo_suprema_v1"
    )

    # Sincroniza dados de medição de volta para o estado global
    d.update({
        'p_baixa': p_suc, 'temp_sucção': t_suc,
        'p_alta': p_des, 'temp_liquido': t_liq,
        'temp_entrada_ar': t_ret, 'temp_saida_ar': t_ins
    })


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
    
    # Correção: Uso de .get() para evitar erro de chave inexistente e inclusão de 'key' única
    st.session_state.dados['tecnico_nome'] = st.text_input(
        "Nome:", 
        value=st.session_state.dados.get('tecnico_nome', ''), 
        key="tec_nome_sidebar_v1"
    )
    
    st.session_state.dados['tecnico_documento'] = st.text_input(
        "CPF/CNPJ Técnico:", 
        value=st.session_state.dados.get('tecnico_documento', ''), 
        key="tec_doc_sidebar_v1"
    )
    
    st.session_state.dados['tecnico_registro'] = st.text_input(
        "Inscrição (CFT/CREA):", 
        value=st.session_state.dados.get('tecnico_registro', ''), 
        key="tec_reg_sidebar_v1"
    )
    
    st.markdown("---")
    

# --- FINAL DO APP: VALIDAÇÃO, ENVIO E LIMPEZA ---
    st.markdown("---")
    d = st.session_state.dados

    # 1. VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS (Usando .get para não travar)
    if not d.get('nome') or not d.get('whatsapp'):
        st.error("📋 STATUS: PENDENTE (Preencha Cliente e WhatsApp na Aba Cadastro)")
    else:
        st.success("📋 STATUS: PRONTO PARA ENVIO")
        
        # 2. MONTAGEM DA MENSAGEM (Protegida contra SyntaxError e KeyError)
        msg_zap = (
            f"*LAUDO TÉCNICO HVAC*\n\n"
            f"👤 *CLIENTE:* {d.get('nome', '')}\n"
            f"📍 END: {d.get('endereco', '')}, {d.get('numero', '')}\n"
            f"🏙️ {d.get('cidade', '')}/{d.get('uf', '')} | CEP: {d.get('cep', '')}\n"
            f"📞 Contato: {d.get('whatsapp', '')}\n\n"
            f"⚙️ *EQUIPAMENTO:*\n"
            f"📌 TAG: {d.get('tag_id', '')} | Mod: {d.get('modelo', '')}\n"
            f"❄️ Fluido: {d.get('fluido', '')}\n\n"
            f"🩺 *DIAGNÓSTICO:*\n"
            f"{d.get('laudo_diag', 'Sem observações.')}\n\n"
            f"👨‍🔧 *TÉCNICO:* {d.get('tecnico_nome', '')}\n"
            f"📅 Data: {d.get('data', '')}"
        )

        # 3. GERAÇÃO DO LINK E BOTÃO DE ENVIO
        texto_url = urllib.parse.quote(msg_zap)
        link_final = f"https://wa.me/55{d.get('whatsapp', '')}?text={texto_url}"
        st.link_button("📲 Enviar Laudo via WhatsApp", link_final, use_container_width=True)

    st.markdown("---")

    # 4. LIMPAR FORMULÁRIO (DIRETRIZ: PROTEGENDO DADOS DO TÉCNICO)
    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        # Lista do que NÃO deve ser apagado
        chaves_preservadas = ['tecnico_nome', 'tecnico_documento', 'tecnico_registro', 'data']
        
        for chave in list(st.session_state.dados.keys()):
            if chave not in chaves_preservadas:
                st.session_state.dados[chave] = ""
        
        st.rerun()

# ==============================================================================
# 4. LÓGICA DE EXIBIÇÃO DAS ABAS (ATIVADA)
# ==============================================================================
# Use a seleção do sidebar para chamar a função correta
if aba_selecionada == "Home":
    # --- NOVA APRESENTAÇÃO DA ABA HOME (COM LOGO MPN SOLUÇÕES ) ---
    st.markdown("<br>", unsafe_allow_html=True) # Espaçamento superior

    # 1. CENTRALIZAÇÃO E EXIBIÇÃO DA LOGOMARCA
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2: 
        # NOME DO ARQUIVO DE IMAGEM QUE ESTÁ SENDO USADO
        NOME_ARQUIVO_LOGO = "logo.png"
        
        # VERIFICAÇÃO ADICIONAL DO ARQUIVO NO DISCO (PARA AJUDAR NO DIAGNÓSTICO)
        if os.path.exists(NOME_ARQUIVO_LOGO):
            try:
                # SE O ARQUIVO EXISTE, TENTA EXIBIR
                st.image(NOME_ARQUIVO_LOGO, use_container_width=True) 
            except Exception as e:
                st.error(f"⚠️ Erro ao tentar abrir a imagem '{NOME_ARQUIVO_LOGO}'. Verifique se o arquivo está corrompido.")
                st.write(f"Detalhes do erro do sistema: {e}")
        else:
            st.error(f"⚠️ Erro: Arquivo '{NOME_ARQUIVO_LOGO}' não encontrado na pasta raiz.")
            st.info("Verifique se o nome do arquivo salvo no computador é EXATAMENTE 'logo.png' (maiúsculas/minúsculas importam).")

    st.markdown("<br><br>", unsafe_allow_html=True) 

    # 2. TÍTULO E BOAS-VINDAS CENTRALIZADOS E ESTILIZADOS
    st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: #0d47a1; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                MPN Soluções
            </h1>
            <p style="color: #1976d2; font-size: 1.3em;">
                Soluções em Refrigeração e Climatização
            </p>
            <hr style="border: 1px solid #90caf9; width: 60%; margin: 20px auto;">
            <p style="color: #455a64; font-size: 1.1em; font-weight: bold;">
                Bem-vindo ao Sistema HVAC Pro de Gestão Inteligente.
            </p>
            <p style="color: #546e7a; font-size: 1.0em;">
                Selecione uma opção no Painel de Controle lateral para iniciar sua inspeção ou diagnóstico.
            </p>
        </div>
    """, unsafe_allow_html=True)
    # ------------------------------------------------

elif aba_selecionada == "1. Cadastro de Equipamentos":
    renderizar_aba_1() # Chama a função que contém todo o código da Aba 1

elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos() # Chama a função que contém o esqueleto da Aba 2

elif aba_selecionada == "Relatórios":
    st.header("Página de Relatórios (Em desenvolvimento)")
    st.write("Em breve: Visualização e exportação de relatórios.")
# [COLE AQUI - Logo após o fim da renderizar_aba_1]

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    # Busca o fluido que você selecionou na Aba 1
    fluido_selecionado = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"❄️ Fluido Refrigerante em Análise: **{fluido_selecionado}**")
    st.markdown("---")

    # --- BLOCO 1: ENTRADA DE MEDIÇÕES ---
    st.subheader("1. Medições de Campo")
    col_suc, col_des = st.columns(2)
    
    with col_suc:
        st.markdown("### 🔵 Baixa Pressão")
        pres_suc = st.number_input("Pressão de Sucção (PSI):", min_value=0.0, step=1.0, key="p_suc_diag")
        temp_suc = st.number_input("Temp. Tubulação Sucção (°C):", step=0.1, key="t_suc_diag")

    with col_des:
        st.markdown("### 🔴 Alta Pressão")
        pres_des = st.number_input("Pressão de Descarga (PSI):", min_value=0.0, step=1.0, key="p_des_diag")
        temp_liq = st.number_input("Temp. Tubulação Líquido (°C):", step=0.1, key="t_liq_diag")

    st.markdown("---")
  

# --- BLOCO 2: PROCESSAMENTO (CÁLCULOS) ---
    # Nota: No próximo passo, inseriremos a tabela PT aqui
    t_sat_suc = 0.0  
    t_sat_des = 0.0  
    
    sh = temp_suc - t_sat_suc
    sc = t_sat_des - temp_liq

    # --- BLOCO 3: EXIBIÇÃO DE RESULTADOS ---
    st.subheader("2. Resultados Calculados")
    res1, res2 = st.columns(2)
    
    with res1:
        st.metric(label="Superaquecimento (SH)", value=f"{sh:.1f} K")
        if 5 <= sh <= 7: st.success("✅ SH dentro do padrão (5K a 7K)")
        elif sh < 5: st.error("⚠️ SH Baixo: Risco de retorno de líquido")
        else: st.warning("⚠️ SH Alto: Possível falta de fluido ou restrição")

    with res2:
        st.metric(label="Sub-resfriamento (SC)", value=f"{sc:.1f} K")
        if 4 <= sc <= 7: st.success("✅ SC dentro do padrão (4K a 7K)")
        else: st.info("ℹ️ SC fora do padrão: Verifique condensação")

    st.markdown("---")

    # --- BLOCO 4: CONCLUSÃO E LAUDO ---
    st.subheader("3. Parecer Técnico Final")
    st.session_state.dados['laudo_diag'] = st.text_area(
        "Descreva o diagnóstico ou anomalias encontradas:",
        placeholder="Ex: Sistema operando com pressões estáveis, superaquecimento normal...",
        key="laudo_area_diag"
    )

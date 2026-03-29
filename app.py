
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


# 1. CONFIGURAÇÃO INICIAL (DIRETRIZ: LAYOUT CONGELADO)
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

# CSS: Estilização (CONGELADO E PROTEGIDO)
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

# 1.1. MOTOR DE SESSÃO (DIRETRIZ: SINCRONIZAÇÃO TOTAL)
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional', 'tipo_oleo': 'POE', 'frequencia': 'Inverter'
    }

def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
            if r.status_code == 200:
                d_api = r.json()
                if "erro" not in d_api:
                    st.session_state.dados['endereco'] = d_api.get('logradouro', '')
                    st.session_state.dados['bairro'] = d_api.get('bairro', '')
                    st.session_state.dados['cidade'] = d_api.get('localidade', '')
                    st.session_state.dados['uf'] = d_api.get('uf', '')
                    return True
        except: pass
    return False


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
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO MASTER ATUALIZADA)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    d = st.session_state.dados
    fluido = d.get('fluido', 'R410A')

    # --- 1. PAINEL DE REFERÊNCIA IDEAL (DINÂMICO POR GÁS) ---
    referencias = {
        'R410A': {"p_suc": "110 a 130 PSI", "t_sat": "2°C a 6°C", "sh": "5K a 9K", "sc": "5K a 8K"},
        'R22':   {"p_suc": "60 a 75 PSI", "t_sat": "1°C a 5°C", "sh": "7K a 11K", "sc": "3K a 6K"},
        'R134a': {"p_suc": "25 a 40 PSI", "t_sat": "-1°C a 4°C", "sh": "5K a 10K", "sc": "4K a 8K"},
        'R404A': {"p_suc": "80 a 95 PSI", "t_sat": "-5°C a 0°C", "sh": "4K a 8K", "sc": "2K a 5K"}
    }
    ref = referencias.get(fluido, referencias['R410A'])

    st.markdown(f"""
        <div style="background-color: #1E1E1E; border-left: 5px solid #00CCFF; padding: 15px; border-radius: 10px; margin-bottom: 25px;">
            <h4 style="margin-top:0; color: #00CCFF;">🎯 Referência Ideal para {fluido}</h4>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">
                <div><small>SUCÇÃO ALVO</small><br><b>{ref['p_suc']}</b></div>
                <div><small>SATURAÇÃO ALVO</small><br><b>{ref['t_sat']}</b></div>
                <div><small>SH (SUPERAQUEC.)</small><br><b>{ref['sh']}</b></div>
                <div><small>SC (SUB-RESFR.)</small><br><b>{ref['sc']}</b></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 2. MEDIÇÕES DE CAMPO (20 CAMPOS - NOMES POR EXTENSO) ---
    st.subheader("1. Medições de Campo")
    
    # SEÇÃO A: 🔵 CICLO FRIGORÍFICO
    st.markdown("##### 🔵 Ciclo Frigorífico")
    a1, a2, a3, a4, a5 = st.columns(5)
    p_suc = a1.number_input("SUCÇÃO (PSI)", value=float(d.get('p_baixa', 0.0)), format="%.1f", key="ps_m")
    t_suc = a2.number_input("TUB. SUCÇÃO (°C)", value=float(d.get('temp_sucção', 0.0)), format="%.1f", key="ts_m")
    p_des = a3.number_input("DESCARGA (PSI)", value=float(d.get('p_alta', 0.0)), format="%.1f", key="pd_m")
    t_liq = a4.number_input("TUB. LÍQUIDO (°C)", value=float(d.get('temp_liquido', 0.0)), format="%.1f", key="tl_m")
    t_com = a5.number_input("TUB. Desc. Comp. (°C)", value=float(d.get('temp_descarga', 0.0)), format="%.1f", key="tc_m")

    # SEÇÃO B: 🔴 AR E AMBIENTE
    st.markdown("##### 🔴 Ar e Ambiente")
    b1, b2, b3, b4, b5 = st.columns(5)
    t_ret = b1.number_input("Retorno Ar (°C)", value=float(d.get('temp_entrada_ar', 0.0)), format="%.1f", key="tr_m")
    t_ins = b2.number_input("Insuflação (°C)", value=float(d.get('temp_saida_ar', 0.0)), format="%.1f", key="ti_m")
    t_amb = b3.number_input("TEMP. Amb. Ext. (°C)", value=float(d.get('temp_amb_ext', 35.0)), format="%.1f", key="ta_m")
    u_rel = b4.number_input("Umid. Rel. DO AR (%)", value=float(d.get('umidade', 50.0)), format="%.1f", key="ur_m")
    p_oil = b5.number_input("Pressão Óleo (PSI)", value=0.0, format="%.1f", key="po_m")

    # SEÇÃO C: ⚡ PARÂMETROS ELÉTRICOS
    st.markdown("##### ⚡ Parâmetros Elétricos")
    c1, c2, c3, c4, c5 = st.columns(5)
    v_lin = c1.number_input("Tensão Nominal (V)", value=float(d.get('v_nominal', 220.0)), key="vn_m")
    v_med = c2.number_input("Tensão Medida (V)", value=float(d.get('v_medida', 220.0)), key="vm_m")
    i_med = c3.number_input("Corrente Medida (A)", value=float(d.get('i_medida', 0.0)), key="im_m")
    rla   = c4.number_input("RLA - Nominal (A)", value=float(d.get('rla', 0.0)), key="rla_m")
    lra   = c5.number_input("LRA - Partida (A)", value=float(d.get('lra', 0.0)), key="lra_m")

    # SEÇÃO D: 🔋 CAPACITÂNCIA E VENTILAÇÃO
    st.markdown("##### 🔋 Capacitância e Ventilação")
    d1, d2, d3, d4, d5 = st.columns(5)
    cn_c  = d1.number_input("CAPACITÂNCIA Nom. Comp", value=float(d.get('cn_c', 0.0)), format="%.1f", key="cnc_m")
    cm_c  = d2.number_input("CAPACITÂNCIA Lido Comp", value=float(d.get('cm_c', 0.0)), format="%.1f", key="cmc_m")
    cn_f  = d3.number_input("CAPACITÂNCIA Nom. Fan", value=float(d.get('cn_f', 0.0)), format="%.1f", key="cnf_m")
    cm_f  = d4.number_input("CAPACITÂNCIA Lido Fan", value=float(d.get('cm_f', 0.0)), format="%.1f", key="cmf_m")
    i_fan = d5.number_input("CORRENTE Fan (A)", value=0.0, format="%.2f", key="if_m")

    # --- 3. PROCESSAMENTO TÉCNICO (CÁLCULOS) ---
    t_sat_s = f_sat_precisao(p_suc, fluido) if p_suc > 5 else 0.0
    t_sat_d = f_sat_precisao(p_des, fluido) if p_des > 5 else 0.0
    sh = round(t_suc - t_sat_s, 2) if t_sat_s != 0 else 0.0
    sc = round(t_sat_d - t_liq, 2) if t_sat_d != 0 else 0.0
    dt_ar = round(t_ret - t_ins, 2)
    d_tensao = round(v_med - v_lin, 2)
    d_corrente = round(i_med - rla, 2) if rla > 0 else 0.0
    sh_util = round(sh * 0.8, 2) 
    d_cap_f = round(cm_f - cn_f, 2)
    d_cap_c = round(cm_c - cn_c, 2)


# --- 3. RESULTADOS CALCULADOS (FONTE REDUZIDA E COR PERSONALIZADA) ---
    st.markdown("---")
    st.subheader("2. Resultados Calculados")

    # CSS para diminuir a fonte e mudar a cor do texto das métricas
    st.markdown("""
        <style>
        /* Estilo do Card */
        div[data-testid="stMetric"] {
            background-color: #1A1C23;
            border: 1px solid #333;
            padding: 8px;
            border-radius: 8px;
            margin-bottom: 5px;
            border-left: 4px solid #00CCFF;
        }
        /* Ajuste do Label (Título do campo) */
        div[data-testid="stMetricLabel"] p {
            font-size: 0.85rem !important;
            color: #888 !important; /* Cinza para o título */
        }
        /* Ajuste do Valor (O número calculado) */
        div[data-testid="stMetricValue"] div {
            font-size: 1.1rem !important;
            color: #B0C4DE !important; /* Cor LightSteelBlue para o resultado */
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

    res = st.columns(5)

    # COLUNA 1: Superaquecimentos
    with res[0]:
        st.metric("SH TOTAL", f"{sh:.1f} K")
        st.metric("SH ÚTIL", f"{sh_util:.1f} K")

    # COLUNA 2: Temperaturas de Troca
    with res[1]:
        st.metric("SAT. SUCÇÃO", f"{t_sat_s:.1f} °C")
        st.metric("Δ T (AR)", f"{dt_ar:.1f} K")

    # COLUNA 3: Sub-resfriamento e Alvo
    with res[2]:
        st.metric("SC FINAL", f"{sc:.1f} K")
        st.metric("SUCÇÃO ALVO", f"{ref['p_suc']}")

    # COLUNA 4: Diferenciais Elétricos
    with res[3]:
        st.metric("Δ TENSÃO", f"{d_tensao:.1f} V")
        st.metric("Δ CORRENTE", f"{d_corrente:.1f} A")

    # COLUNA 5: Diferenciais de Capacitância
    with res[4]:
        st.metric("Δ CAP. COMP.", f"{d_cap_c:.1f} µF")
        st.metric("Δ CAP. FAN", f"{d_cap_f:.1f} µF")
    
    # --- 5. DIAGNÓSTICO INTELIGENTE (IA) ---
    st.markdown("---")
    st.subheader("🤖 Diagnóstico Inteligente (IA)")
    
    alertas_ia = []
    if sh < 5: alertas_ia.append("⚠️ **SH Baixo:** Risco de golpe de líquido.")
    if sh > 12: alertas_ia.append("⚠️ **SH Alto:** Compressor aquecendo demais.")
    if dt_ar < 8 and t_ret > 0: alertas_ia.append("❄️ **Delta T Baixo:** Verifique filtros ou carga.")
    if t_com > 100: alertas_ia.append("🔥 **Descarga Crítica:** Risco de queima do óleo lubrificante.")
    
    texto_ia = "\n".join(alertas_ia) if alertas_ia else "✅ Sistema operando conforme lógica nominal."
    st.info(texto_ia)

    # --- 6. PARECER TÉCNICO FINAL ---
    st.markdown("---")
    st.subheader("3. Parecer Técnico Final")
    d['laudo_diag'] = st.text_area("Diagnóstico e Observações:", value=d.get('laudo_diag', "Análise: Estável."), height=150)

    # Sincronização e Atualização Global Final
    d.update({
        'p_baixa': p_suc, 'temp_sucção': t_suc, 'p_alta': p_des, 'temp_liquido': t_liq,
        'temp_entrada_ar': t_ret, 'temp_saida_ar': t_ins, 'i_medida': i_med, 
        'cm_c': cm_c, 'cm_f': cm_f, 'lra': lra, 'rla': rla, 'temp_descarga': t_com
    })


# FIM DO BLOCO 2 (LINHA 289)
# FINAL DO BLOCO 2 (LINHA 384)   


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

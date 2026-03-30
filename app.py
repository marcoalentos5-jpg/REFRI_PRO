
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os # Biblioteca para verificar arquivos no sistema
import numpy as np
import urllib.parse
import pandas as pd
import matplotlib.pyplot as plt  # <--- ADICIONE ESTE

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
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000 BTU', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional', 'tipo_oleo': 'POE', 'frequencia': 'Inverter', 'tensao': '220V/1F'
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

    # --- SEÇÃO EQUIPAMENTO ---
    st.markdown("### ⚙️ Especificações do Equipamento")
    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        l1_c1, l1_c2, l1_c3 = st.columns(3)
        with l1_c1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea", "Hitachi"]) + ["Outro"]
            f_idx = fab_list.index(d['fabricante']) if d['fabricante'] in fab_list else 0
            d['fabricante'] = st.selectbox("Fabricante:", fab_list, index=f_idx, key="eq_f")
        with l1_c2:
            d['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=d.get('serie_evap', ''), key="eq_se")
        with l1_c3:
            btus_list = ["7.000 BTU", "9.000 BTU", "12.000 BTU", "18.000 BTU", "22.000 BTU", "24.000 BTU", "30.000 BTU", "36.000 BTU", "48.000 BTU", "60.000 BTU", "80.000 BTU", "Outra"]
            c_idx = btus_list.index(d['capacidade']) if d['capacidade'] in btus_list else 2
            d['capacidade'] = st.selectbox("Capacidade (BTU's):", btus_list, index=c_idx, key="eq_ca")

        l2_c1, l2_c2, l2_c3 = st.columns(3)
        with l2_c1:
            d['modelo'] = st.text_input("Modelo:", value=d.get('modelo', ''), key="eq_mo")
        with l2_c2:
            d['serie_cond'] = st.text_input("Nº Série (COND)", value=d.get('serie_cond', ''), key="eq_sc")
        with l2_c3:
            d['potencia'] = st.text_input("Potência Nominal (W/kW):", value=d.get('potencia', ''), key="eq_po")

        l3_c1, l3_c2, l3_c3 = st.columns(3)
        with l3_c1:
            d['local_evap'] = st.text_input("Local Evaporadora:", value=d.get('local_evap', ''), key="eq_le")
        with l3_c2:
            d['local_cond'] = st.text_input("Local Condensadora:", value=d.get('local_cond', ''), key="eq_lc")
        with l3_c3:
            fluidos = ["R410A", "R32", "R22", "R134a", "R290", "R404A"]
            fl_idx = fluidos.index(d['fluido']) if d['fluido'] in fluidos else 0
            d['fluido'] = st.selectbox("Fluido Refrigerante:", fluidos, index=fl_idx, key="eq_fl")

        l4_c1, l4_c2, l4_c3 = st.columns(3)
        with l4_c1:
            lista_oleo = ["POE", "Mineral", "PVE", "PAG", "AB"]
            o_idx = lista_oleo.index(d['tipo_oleo']) if d['tipo_oleo'] in lista_oleo else 0
            d['tipo_oleo'] = st.selectbox("Tipo de Óleo:", lista_oleo, index=o_idx, key="eq_ol")
            
            # FIX: CORREÇÃO DEFINITIVA DO STATUS (PERSISTÊNCIA)
            lista_status = ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"]
            s_idx = lista_status.index(d['status_maquina']) if d['status_maquina'] in lista_status else 0
            d['status_maquina'] = st.radio("Status:", lista_status, index=s_idx, key="eq_st")
            
        with l4_c2:
            d['carga_gas'] = st.text_input("Carga de Fluido (kg/g):", value=d.get('carga_gas', ''), key="eq_cg")
            lista_tensao = ["220V/1F", "220V/3F", "380V/3F", "440V/3F", "127V"]
            t_idx = lista_tensao.index(d['tensao']) if d['tensao'] in lista_tensao else 0
            d['tensao'] = st.selectbox("Tensão Nominal (V):", lista_tensao, index=t_idx, key="eq_te")
        with l4_c3:
            try:
                dt = datetime.strptime(d.get('ultima_maint', datetime.now().strftime("%d/%m/%Y")), "%d/%m/%Y").date()
            except:
                dt = datetime.now().date()
            d['ultima_maint'] = st.date_input("Última Manutenção:", value=dt, format="DD/MM/YYYY", key="eq_dt").strftime("%d/%m/%Y")
            d['tag_id'] = st.text_input("TAG/Patrimônio:", value=d.get('tag_id', ''), key="eq_ta")

# --- MOTOR DE CÁLCULO PT ---
def f_sat_precisao(p, g):
    if p <= 5: return -50.0
    tabelas = {
        "R410A": {"xp": [5, 50, 90, 122, 150, 350, 550], "fp": [-50, -18, -3.5, 5.5, 11.5, 41.5, 64.5]},
        "R32": {"xp": [5, 50, 90, 140, 200, 480, 580], "fp": [-50, -19.5, -3.6, 8.5, 19.8, 56.5, 66.8]},
        "R22": {"xp": [5, 30, 60, 100, 200, 320], "fp": [-50, -15.2, 1.5, 16.5, 38.5, 58.5]},
        "R134a": {"xp": [5, 15, 30, 70, 150, 250], "fp": [-50, -15.5, 1.5, 27.5, 53, 76.2]},
        "R290": {"xp": [5, 20, 65, 100, 150, 250], "fp": [-50, -25.5, 3.5, 17.5, 32.5, 55.2]}
    }
    if g not in tabelas: return 0.0
    return float(np.interp(p, tabelas[g]["xp"], tabelas[g]["fp"]))

# FINAL DO BLOCO 1 - INTEGRIDADE MANTIDA - LINHA 172
    


## ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO MASTER CONSOLIDADA - 160+ LINHAS)
# ==============================================================================
def renderizar_aba_2():
    """
    Renderiza a Central de Diagnóstico Técnico.
    Mantém o layout original de medições (5 colunas) e resultados (6 colunas).
    Integra lógica de balança virtual, alertas térmicos e Razão de Compressão.
    """
    st.header("🔍 Central de Diagnóstico Técnico")
    
    # Recuperação do estado de sessão para persistência de dados
    if 'dados' not in st.session_state:
        st.session_state.dados = {}
        
    d = st.session_state.dados
    fluido = d.get('fluido', 'R410A')

    # --- FUNÇÃO AUXILIAR DE ESTABILIDADE ---
    def safe_float(key, default=0.0):
        """Garante conversão segura de strings formatadas para float."""
        val = d.get(key)
        try:
            if isinstance(val, str):
                # Limpeza de unidades e formatação regional (vírgula por ponto)
                val = val.lower().replace('kg', '').replace('g', '').replace(',', '.')
            return float(val) if val not in [None, ""] else default
        except (ValueError, TypeError):
            return default

    # --- 1. CONFIGURAÇÃO DE REFERÊNCIAS TÉCNICAS (DINÂMICO POR FLUIDO) ---
    referencias = {
        'R410A': {"p_suc": "110 a 130 PSI", "t_sat": "2°C a 6°C", "sh": "5K a 9K", "sc": "5K a 8K"},
        'R32':   {"p_suc": "115 a 135 PSI", "t_sat": "1°C a 5°C", "sh": "5K a 9K", "sc": "5K a 9K"},
        'R22':   {"p_suc": "60 a 75 PSI", "t_sat": "1°C a 5°C", "sh": "7K a 11K", "sc": "3K a 6K"},
        'R134a': {"p_suc": "25 a 40 PSI", "t_sat": "-1°C a 4°C", "sh": "5K a 10K", "sc": "4K a 8K"},
        'R404A': {"p_suc": "80 a 95 PSI", "t_sat": "-5°C a 0°C", "sh": "4K a 8K", "sc": "2K a 5K"}
    }
    ref = referencias.get(fluido, referencias['R410A'])

    # --- LÓGICA DE PROCESSAMENTO SUPERIOR (BALANÇA E STATUS) ---
    p_atual = safe_float('p_baixa')
    limites_p = ref['p_suc'].replace(' PSI', '').split(' a ')
    p_alvo_centro = (float(limites_p[0]) + float(limites_p[1])) / 2
    carga_total_placa = safe_float('carga_gas') 
    
    cor_alerta, msg_status, sugestao_massa = "#00CCFF", "", 0.0
    
    # Cálculo da sugestão de carga via Balança Virtual Proporcional
    if p_atual > 0:
        if carga_total_placa > 0:
            diff_p = p_alvo_centro - p_atual
            # Lógica estimada: desvio de pressão reflete ~70% da massa proporcional
            sugestao_massa = (diff_p / p_alvo_centro) * carga_total_placa * 0.7

        if float(limites_p[0]) <= p_atual <= float(limites_p[1]):
            cor_alerta, msg_status = "#00FF7F", " - ✅ DENTRO DO ALVO"
        else:
            cor_alerta, msg_status = "#FF4B4B", " - ⚠️ FORA DO ALVO"

    txt_bal_card = "ESTÁVEL" if abs(sugestao_massa) < 15 or carga_total_placa == 0 else f"{'+' if sugestao_massa > 0 else '-'}{abs(sugestao_massa):.0f}g"

    # --- ESTILIZAÇÃO DO PAINEL DE REFERÊNCIA (CARD SUPERIOR) ---
    st.markdown(f"""
        <div style="background-color: #1E1E1E; border-left: 5px solid {cor_alerta}; padding: 15px; border-radius: 10px; margin-bottom: 25px; border: 1px solid #333;">
            <h4 style="margin-top:0; color: {cor_alerta};">🎯 Referência Ideal para {fluido}{msg_status}</h4>
            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px;">
                <div style="color: #FFFFFF;"><small style="color: #888;">SUCÇÃO ALVO</small><br><b>{ref['p_suc']}</b></div>
                <div style="color: #FFFFFF;"><small style="color: #888;">SATURAÇÃO ALVO</small><br><b>{ref['t_sat']}</b></div>
                <div style="color: #FFFFFF;"><small style="color: #888;">SH (SUPERAQUEC.)</small><br><b>{ref['sh']}</b></div>
                <div style="color: #FFFFFF;"><small style="color: #888;">SC (SUB-RESFR.)</small><br><b>{ref['sc']}</b></div>
                <div style="background-color: rgba(255,255,255,0.05); padding: 5px; border-radius: 5px; text-align: center; border: 1px dashed {cor_alerta};">
                    <small style="color: {cor_alerta}; font-weight: bold;">⚖️ BALANÇA</small><br><b style="color: #FFF; font-size: 1.1rem;">{txt_bal_card}</b>
                </div>
            </div>
            <div style="margin-top: 10px; color: {cor_alerta}; font-size: 14px; font-weight: bold;">PRESSÃO DE SUCÇÃO ATUAL: {p_atual:.1f} PSI</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 2. MEDIÇÕES DE CAMPO (INTEGRIDADE TOTAL DO LAYOUT) ---
    st.subheader("1. Medições de Campo")
    
    # Bloco 1: Ciclo Frigorífico (5 Colunas)
    st.markdown("##### 🔵 Ciclo Frigorífico")
    a1, a2, a3, a4, a5 = st.columns(5)
    p_suc_val = a1.number_input("SUCÇÃO (PSI)", value=p_atual, format="%.1f", key="ps_m_aba2")
    t_suc_val = a2.number_input("TUB. SUCÇÃO (°C)", value=safe_float('temp_sucção'), format="%.1f", key="ts_m_aba2")
    p_des_val = a3.number_input("DESCARGA (PSI)", value=safe_float('p_alta'), format="%.1f", key="pd_m_aba2")
    t_liq_val = a4.number_input("TUB. LÍQUIDO (°C)", value=safe_float('temp_liquido'), format="%.1f", key="tl_m_aba2")
    t_com_val = a5.number_input("TUB. Desc. Comp. (°C)", value=safe_float('temp_descarga'), format="%.1f", key="tc_m_aba2")

    # Bloco 2: Ar e Ambiente (5 Colunas)
    st.markdown("##### 🔴 Ar e Ambiente")
    b1, b2, b3, b4, b5 = st.columns(5)
    t_ret_val = b1.number_input("Retorno Ar (°C)", value=safe_float('temp_entrada_ar'), format="%.1f", key="tr_m_aba2")
    t_ins_val = b2.number_input("Insuflação (°C)", value=safe_float('temp_saida_ar'), format="%.1f", key="ti_m_aba2")
    t_amb_val = b3.number_input("TEMP. Amb. Ext. (°C)", value=safe_float('temp_amb_ext', 35.0), format="%.1f", key="ta_m_aba2")
    u_rel_val = b4.number_input("Umid. Rel. DO AR (%)", value=safe_float('umidade', 50.0), format="%.1f", key="ur_m_aba2")
    p_oil_val = b5.number_input("Pressão Óleo (PSI)", value=safe_float('p_oleo', 0.0), format="%.1f", key="po_m_aba2")

    # Bloco 3: Parâmetros Elétricos (5 Colunas)
    st.markdown("##### ⚡ Parâmetros Elétricos")
    c1, c2, c3, c4, c5 = st.columns(5)
    v_lin_val = c1.number_input("Tensão Nominal (V)", value=safe_float('v_nominal', 220.0), key="vn_m_aba2")
    v_med_val = c2.number_input("Tensão Medida (V)", value=safe_float('v_medida', 220.0), key="vm_m_aba2")
    i_med_val = c3.number_input("Corrente Medida (A)", value=safe_float('i_medida'), key="im_m_aba2")
    rla_val   = c4.number_input("RLA - Nominal (A)", value=safe_float('rla'), key="rla_m_aba2")
    lra_val   = c5.number_input("LRA - Partida (A)", value=safe_float('lra'), key="lra_m_aba2")

    # Bloco 4: Capacitância e Ventilação (5 Colunas)
    st.markdown("##### 🔋 Capacitância e Ventilação")
    d1, d2, d3, d4, d5 = st.columns(5)
    cn_c_val  = d1.number_input("CAPACITÂNCIA Nom. Comp", value=safe_float('cn_c'), format="%.1f", key="cnc_m_aba2")
    cm_c_val  = d2.number_input("CAPACITÂNCIA Lido Comp", value=safe_float('cm_c'), format="%.1f", key="cmc_m_aba2")
    cn_f_val  = d3.number_input("CAPACITÂNCIA Nom. Fan", value=safe_float('cn_f'), format="%.1f", key="cnf_m_aba2")
    cm_f_val  = d4.number_input("CAPACITÂNCIA Lido Fan", value=safe_float('cm_f'), format="%.1f", key="cmf_m_aba2")
    i_fan_val = d5.number_input("CORRENTE Fan (A)", value=safe_float('i_fan'), format="%.2f", key="if_m_aba2")

    # --- 3. PROCESSAMENTO TÉCNICO E CÁLCULOS TERMODINÂMICOS ---
    # Cálculo de Saturação utilizando a função externa f_sat_precisao
    t_sat_s = f_sat_precisao(p_suc_val, fluido) if p_suc_val > 5 else 0.0
    t_sat_d = f_sat_precisao(p_des_val, fluido) if p_des_val > 5 else 0.0
    
    # Superaquecimento (SH) e Sub-resfriamento (SC)
    sh_calc = round(t_suc_val - t_sat_s, 2) if t_sat_s != 0 else 0.0
    sc_calc = round(t_sat_d - t_liq_val, 2) if t_sat_d != 0 else 0.0
    
    # Diferenciais Térmicos e Elétricos
    dt_ar_calc = round(t_ret_val - t_ins_val, 2)
    d_tensao_calc = round(v_med_val - v_lin_val, 2)
    d_corrente_calc = round(i_med_val - rla_val, 2) if rla_val > 0 else 0.0
    
    # SH Útil e Desvios de Capacitância
    sh_util_calc = round(sh_calc * 0.8, 2)
    d_cap_f_calc = round(cm_f_val - cn_f_val, 2)
    d_cap_c_calc = round(cm_c_val - cn_c_val, 2)
    
    # Razão de Compressão (P. Absoluta Descarga / P. Absoluta Sucção)
    razao_compr = round((p_des_val + 14.7) / (p_suc_val + 14.7), 2) if p_suc_val > 0 else 0.0
    # COP Estimado baseado na entalpia do ar simplificada
    cop_estimado = round((abs(dt_ar_calc) * 1.2 * 1000) / (v_med_val * i_med_val + 0.1), 2) if i_med_val > 0 else 0.0

    # --- 4. EXIBIÇÃO DE RESULTADOS (GRID DE PERFORMANCE - 6 COLUNAS) ---
    st.markdown("---")
    st.subheader("2. Diagnóstico de Performance e Integridade")
    
    # CSS para os Cards de Métricas (Mantendo identidade visual)
    st.markdown("""
        <style> 
            div[data-testid="stMetric"] { 
                background-color: #1A1C23; 
                border: 1px solid #333; 
                padding: 12px; 
                border-radius: 8px; 
                border-left: 4px solid #00CCFF; 
            } 
        </style>
    """, unsafe_allow_html=True)
    
    # Renderização do Grid Master de 6 Colunas
    res_cols = st.columns(6)
    
    with res_cols[0]:
        st.metric("SH TOTAL", f"{sh_calc:.1f} K")
        st.metric("SH ÚTIL", f"{sh_util_calc:.1f} K")
        
    with res_cols[1]:
        st.metric("SAT. SUCÇÃO", f"{t_sat_s:.1f} °C")
        st.metric("SAT. DESCARGA", f"{t_sat_d:.1f} °C")
        
    with res_cols[2]:
        st.metric("Δ T (AR)", f"{dt_ar_calc:.1f} K")
        st.metric("SC FINAL", f"{sc_calc:.1f} K")
        
    with res_cols[3]:
        st.metric("Δ CORRENTE", f"{d_corrente_calc:.1f} A")
        st.metric("Δ TENSÃO", f"{d_tensao_calc:.1f} V")
        
    with res_cols[4]:
        # SUBSTITUIÇÃO REALIZADA: Linha 1 = Razão de Compressão | Linha 2 = COP
        st.metric("Razão Compr.", f"{razao_compr}", "⚠️ Crítico" if razao_compr > 4.5 else None)
        st.metric("COP ESTIMADO", f"{cop_estimado:.2f}")
        
    with res_cols[5]:
        st.metric("Δ CAP. COMP.", f"{d_cap_c_calc:.1f} µF")
        st.metric("Δ CAP. FAN.", f"{d_cap_f_calc:.1f} µF")
    
    # --- 5. DIAGNÓSTICO INTELIGENTE (MOTOR DE REGRAS IA) ---
    st.markdown("---")
    st.subheader("🤖 Diagnóstico Inteligente (Motor de Regras)")
    
    alertas_lista = []
    if sh_calc < 5 and p_suc_val > 0:
        alertas_lista.append("⚠️ **Superaquecimento Baixo:** Risco de retorno de líquido ao compressor.")
    if sh_calc > 12:
        alertas_lista.append("⚠️ **Superaquecimento Alto:** Possível falta de fluido ou restrição na expansão.")
    if t_com_val > 105:
        alertas_lista.append("🔥 **Descarga Crítica:** Temperatura acima do limite de segurança do óleo.")
    if sc_calc < 3 and p_des_val > 0:
        alertas_lista.append("📉 **Sub-resfriamento Baixo:** Ineficiência na condensação ou carga incompleta.")
    if abs(d_tensao_calc) > (v_lin_val * 0.1):
        alertas_lista.append("⚡ **Alerta Elétrico:** Tensão fora da margem de 10% de tolerância.")

    if alertas_lista:
        for alerta in alertas_lista:
            st.error(alerta)
    else:
        st.success("✅ Sistema operando dentro dos parâmetros de estabilidade termodinâmica.")

    # --- 6. PARECER TÉCNICO E PERSISTÊNCIA ---
    st.markdown("---")
    st.subheader("3. Parecer Técnico Final")
    d['laudo_diag'] = st.text_area("Diagnóstico e Observações Detalhadas:", value=d.get('laudo_diag', "Análise: Sistema estável."), height=150)

    # ATUALIZAÇÃO DO DICIONÁRIO DE DADOS (GARANTINDO PERSISTÊNCIA DE TODAS AS CHAVES)
    st.session_state.dados.update({
        'p_baixa': p_suc_val,
        'temp_sucção': t_suc_val,
        'p_alta': p_des_val,
        'temp_liquido': t_liq_val,
        'temp_entrada_ar': t_ret_val,
        'temp_saida_ar': t_ins_val,
        'temp_amb_ext': t_amb_val,
        'umidade': u_rel_val,
        'p_oleo': p_oil_val,
        'v_nominal': v_lin_val,
        'v_medida': v_med_val,
        'i_medida': i_med_val,
        'cn_c': cn_c_val,
        'cm_c': cm_c_val,
        'cn_f': cn_f_val,
        'cm_f': cm_f_val, 
        'i_fan': i_fan_val,
        'lra': lra_val,
        'rla': rla_val,
        'temp_descarga': t_com_val,
        'sh_calculado': sh_calc,
        'sc_calculado': sc_calc,
        'sh_util': sh_util_calc,
        'dt_ar': dt_ar_calc,
        'razao_compressao': razao_compr,
        'cop_estimado': cop_estimado,
        'balanca_sugestao': sugestao_massa
    })
# FINAL DO BLOCO 2 (LINHA 384)   


# ==============================================================================
# 3. SIDEBAR - MOTOR DE RELATÓRIO TÉCNICO MASTER (VERSÃO FINAL BLINDADA)
# ==============================================================================
with st.sidebar:
    # A. LOGO AMPLIADA NA SIDEBAR
    col_l1, col_l2, col_l3 = st.columns([0.5, 9, 0.5])
    with col_l2:
        try: 
            st.image("logo.png", use_container_width=True)
        except: 
            st.subheader("MPN SOLUÇÕES")
    
    st.markdown("---")
    
    # B. NAVEGAÇÃO OPERACIONAL
    opcoes_abas = ["Home", "1. Cadastro de Equipamentos", "2. Diagnósticos", "Relatórios"]
    aba_selecionada = st.radio("Navegar para:", opcoes_abas, key="nav_master_vfinal")
    
    st.markdown("---")
    
    # C. IDENTIFICAÇÃO DO TÉCNICO
    st.subheader("👨‍🔧 Identificação do Técnico")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome Completo:", value=st.session_state.dados.get('tecnico_nome', ''), key="f_tec_n")
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ do Técnico:", value=st.session_state.dados.get('tecnico_documento', ''), key="f_tec_d")
    st.session_state.dados['tecnico_registro'] = st.text_input("Registro (CREA/CFT):", value=st.session_state.dados.get('tecnico_registro', ''), key="f_tec_r")

    st.markdown("---")

    # D. MOTOR DE GERAÇÃO PDF (VARREDURA TOTAL E SINCRONIZADA)
    d = st.session_state.dados
    
    # Validação para habilitar o botão (Nome e Documento do Cliente)
    n_val = str(d.get('nome', '')).strip()
    d_val = str(d.get('cliente_documento', d.get('cpf_cnpj', ''))).strip()
    
    if len(n_val) > 3 and len(d_val) > 5:
        st.success("✅ Relatório Pronto")
        
        try:
            from fpdf import FPDF
            from datetime import datetime

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            C_PRI = (13, 71, 161) # Azul MPN Profissional
            
            # --- 1. CABEÇALHO ---
            try: pdf.image('logo.png', x=10, y=10, w=45)
            except: pass
            
            pdf.set_xy(10, 32)
            pdf.set_font("Arial", "B", 18)
            pdf.set_text_color(*C_PRI)
            pdf.cell(190, 10, "LAUDO TÉCNICO DE INSPEÇÃO HVAC-R", ln=True, align='C')
            pdf.ln(2)

            # --- 2. SEÇÃO 1: IDENTIFICAÇÃO (13+ CAMPOS - SINCRONIZADOS) ---
            pdf.set_fill_color(*C_PRI); pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 9)
            data_v = datetime.now().strftime('%d/%m/%Y')
            pdf.cell(130, 7, " 1. IDENTIFICAÇÃO DO CLIENTE E ENDEREÇO", fill=True)
            pdf.cell(60, 7, f"DATA DA VISITA: {data_v} ", fill=True, ln=True, align='R')
            
            pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", "B", 8)
            pdf.cell(30, 6, " CLIENTE:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(160, 6, f" {n_val.upper()}", border=1, ln=True)
            pdf.set_font("Arial", "B", 8); pdf.cell(30, 6, " CPF/CNPJ:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(65, 6, f" {d_val}", border=1)
            pdf.set_font("Arial", "B", 8); pdf.cell(30, 6, " E-MAIL:", border=1); pdf.set_font("Arial", "", 7); pdf.cell(65, 6, f" {d.get('cliente_email', '---').lower()}", border=1, ln=True)
            
            # Linha de Contatos (WhatsApp, Celular, Fixo)
            pdf.set_font("Arial", "B", 8); pdf.cell(30, 6, " WHATSAPP*:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(35, 6, f" {d.get('cliente_whatsapp', '---')}", border=1)
            pdf.cell(30, 6, " CELULAR:", border=1); pdf.cell(35, 6, f" {d.get('cliente_celular', '---')}", border=1)
            pdf.cell(30, 6, " FIXO:", border=1); pdf.cell(30, 6, f" {d.get('cliente_fixo', '---')}", border=1, ln=True)
            
            # Endereço Completo
            pdf.set_font("Arial", "B", 8); pdf.cell(30, 6, " ENDEREÇO:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(110, 6, f" {d.get('logradouro', '---')}", border=1)
            pdf.set_font("Arial", "B", 8); pdf.cell(20, 6, " Nº:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(30, 6, f" {d.get('numero', '---')}", border=1, ln=True)
            pdf.set_font("Arial", "B", 8); pdf.cell(30, 6, " COMPL.:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(65, 6, f" {d.get('complemento', '---')}", border=1)
            pdf.set_font("Arial", "B", 8); pdf.cell(30, 6, " BAIRRO:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(65, 6, f" {d.get('bairro', '---')}", border=1, ln=True)
            pdf.set_font("Arial", "B", 8); pdf.cell(30, 6, " CIDADE/UF:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(95, 6, f" {d.get('cidade', '---')}/{d.get('uf', '---')}", border=1)
            pdf.set_font("Arial", "B", 8); pdf.cell(25, 6, " CEP:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(40, 6, f" {d.get('cep', '---')}", border=1, ln=True)
            pdf.ln(2)

            # --- 3. SEÇÃO 2: DETALHES TÉCNICOS DO ATIVO (TAG POR ÚLTIMO) ---
            pdf.set_fill_color(*C_PRI); pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 9)
            pdf.cell(190, 7, " 2. DETALHES TÉCNICOS DO ATIVO", ln=True, fill=True)
            pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", "B", 8)
            
            pdf.cell(35, 6, " FABRICANTE:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(60, 6, f" {d.get('fabricante', '---')}", border=1)
            pdf.set_font("Arial", "B", 8); pdf.cell(35, 6, " MODELO:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(60, 6, f" {d.get('modelo', '---')}", border=1, ln=True)
            
            pdf.set_font("Arial", "B", 8); pdf.cell(35, 6, " N° SÉRIE (EVAP):", border=1); pdf.set_font("Arial", "", 8); pdf.cell(60, 6, f" {d.get('n_serie_evap', '---')}", border=1)
            pdf.set_font("Arial", "B", 8); pdf.cell(35, 6, " N° SÉRIE (COND):", border=1); pdf.set_font("Arial", "", 8); pdf.cell(60, 6, f" {d.get('n_serie_cond', '---')}", border=1, ln=True)
            
            pdf.set_font("Arial", "B", 8); pdf.cell(35, 6, " POTÊNCIA (W):", border=1); pdf.set_font("Arial", "", 8); pdf.cell(60, 6, f" {d.get('potencia', '---')}", border=1)
            pdf.set_font("Arial", "B", 8); pdf.cell(35, 6, " LOCAL EVAP.:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(60, 6, f" {d.get('local_evap', '---')}", border=1, ln=True)
            
            pdf.set_font("Arial", "B", 8); pdf.cell(35, 6, " LOCAL COND.:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(60, 6, f" {d.get('local_cond', '---')}", border=1)
            pdf.set_font("Arial", "B", 8); pdf.cell(35, 6, " FLUIDO REF.:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(60, 6, f" {d.get('fluido', '---')}", border=1, ln=True)
            
            pdf.set_font("Arial", "B", 8); pdf.cell(35, 6, " CARGA FLUIDO:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(60, 6, f" {d.get('carga_fluido', '---')}", border=1)
            pdf.set_font("Arial", "B", 8); pdf.cell(35, 6, " TIPO DE ÓLEO:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(60, 6, f" {d.get('tipo_oleo', '---')}", border=1, ln=True)

            pdf.set_font("Arial", "B", 8); pdf.cell(35, 6, " CAPACIDADE (BTU's):", border=1); pdf.set_font("Arial", "", 8); pdf.cell(60, 6, f" {d.get('capacidade_btus', '---')}", border=1)
            pdf.set_font("Arial", "B", 8); pdf.cell(35, 6, " TAG/PATRIMÔNIO:", border=1); pdf.set_font("Arial", "", 8); pdf.cell(60, 6, f" {d.get('tag_id', '---').upper()}", border=1, ln=True)
            pdf.ln(2)

           # --- 4. SEÇÃO 3: MEDIÇÕES DE CAMPO (20 CAMPOS / 4 BLOCOS) ---
            pdf.set_fill_color(*C_PRI); pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 9)
            pdf.cell(190, 7, " 3. MEDIÇÕES DE CAMPO E PERFORMANCE", ln=True, fill=True)
            
            # Substituídos os emojis por texto para evitar erro de Unicode
            blocos_med = [
                ["CICLO FRIGOR.", "SUCÇÃO (PSI)", "TUB. SUCÇÃO", "DESCARGA (PSI)", "TUB. DESCAR.", "T. DESC. COMP"],
                ["AR E AMBIENTE", "RETORNO (°C)", "INSUFLAÇÃO", "AMB. EXT.", "U.R. (%)", "P. ÓLEO (PSI)"],
                ["PARÂMET. ELETR.", "TENSÃO NOM.", "TENSÃO MED.", "CORRENTE MED.", "RLA (A)", "LRA (A)"],
                ["CAPACIT./VENT.", "CAP. NOM. CP", "CAP. LIDO CP", "CAP. NOM. FN", "CAP. LIDO FN", "CORRENTE FAN"]
            ]
            chaves_med = [
                ['p_baixa', 'temp_suc_tubo', 'p_alta', 'temp_desc_tubo', 'temp_desc_comp'],
                ['temp_retorno', 'temp_insuflacao', 'temp_amb_ext', 'umidade_rel', 'pressao_oleo'],
                ['tensao_nom', 'tensao_med', 'corrente_med', 'rla_nom', 'lra_partida'],
                ['cap_nom_comp', 'cap_lido_comp', 'cap_nom_fan', 'cap_lido_fan', 'corrente_fan']
            ]

            for i in range(4):
                pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", "B", 7); pdf.set_fill_color(235, 245, 255)
                # O título do bloco agora é apenas texto
                pdf.cell(30, 5, blocos_med[i][0], border=1, fill=True) 
                for tit in blocos_med[i][1:]: 
                    pdf.cell(32, 5, tit, border=1, align='C', fill=True)
                pdf.ln()
                
                pdf.set_font("Arial", "", 8)
                pdf.cell(30, 6, "VALOR:", border=1, align='C')
                for val in chaves_med[i]: 
                    # d.get() garante que se o campo estiver vazio, não quebra o código
                    valor_campo = str(d.get(val, '---'))
                    pdf.cell(32, 6, f" {valor_campo}", border=1, align='C')
                pdf.ln()
            pdf.ln(2)

            # --- 5. SEÇÃO 4: DIAGNÓSTICO (RETIRADA DO SÍMBOLO DELTA "Δ" PARA EVITAR ERRO) ---
            pdf.set_fill_color(*C_PRI); pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 9)
            pdf.cell(190, 7, " 4. DIAGNÓSTICO DE PERFORMANCE E INTEGRIDADE", ln=True, fill=True)
            
            # Títulos ajustados de "Δ" para "D." ou "DIFF" para compatibilidade total
            titulos_diag = [
                ['SH TOTAL', 'SH ÚTIL', 'SAT. SUCÇÃO', 'SAT. DESCAR.', 'D. T (AR)', 'SC FINAL'],
                ['D. CORRENTE', 'D. TENSÃO', 'RAZÃO COMPR.', 'COP ESTIM.', 'D. CAP. COMP.', 'D. CAP. FAN.']
            ]
            chaves_diag = [
                ['sh_total', 'sh_util', 'sat_suc', 'sat_desc', 'delta_t_ar', 'sc_final'],
                ['delta_corr', 'delta_tens', 'razao_compr', 'cop_estim', 'delta_cap_cp', 'delta_cap_fn']
            ]

            for i in range(2):
                pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", "B", 6.5); pdf.set_fill_color(245, 245, 245)
                for tit in titulos_diag[i]: pdf.cell(31.6, 5, tit, border=1, align='C', fill=True)
                pdf.ln()
                pdf.set_font("Arial", "", 8)
                for val in chaves_diag[i]: pdf.cell(31.6, 6, f" {d.get(val, '---')}", border=1, align='C')
                pdf.ln()
            pdf.ln(2)

            # --- 6. SEÇÃO 5: PARECER TÉCNICO FINAL (CORREÇÃO DE CONTEÚDO) ---
            pdf.set_fill_color(*C_PRI); pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 9)
            pdf.cell(190, 7, " 5. PARECER TÉCNICO FINAL", ln=True, fill=True)
            pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", "", 8.5)
            # Captura o texto real do session_state
            texto_parecer = d.get('parecer_final', 'Nenhuma observação técnica registrada.')
            pdf.multi_cell(190, 5, texto_parecer, border=1)

            # --- 7. ASSINATURAS (SINCRONIZAÇÃO DE DOCUMENTO) ---
            pdf.ln(20)
            y_sig = pdf.get_y()
            pdf.set_draw_color(0,0,0); pdf.set_line_width(0.3)
            pdf.line(20, y_sig, 90, y_sig); pdf.line(110, y_sig, 180, y_sig)
            
            # Técnico
            pdf.set_xy(20, y_sig + 1); pdf.set_font("Arial", "B", 8)
            pdf.cell(70, 4, d.get('tecnico_nome', '').upper(), ln=True, align='C')
            id_tecnico = f"CFT/REG: {d.get('tecnico_registro', '')}" if d.get('tecnico_registro') else f"DOC: {d.get('tecnico_documento', '')}"
            pdf.set_x(20); pdf.set_font("Arial", "", 7); pdf.cell(70, 4, id_tecnico, align='C')

            # Cliente
            pdf.set_xy(110, y_sig + 1); pdf.set_font("Arial", "B", 8)
            pdf.cell(70, 4, n_val.upper(), ln=True, align='C')
            pdf.set_x(110); pdf.set_font("Arial", "", 7); pdf.cell(70, 4, f"CPF/CNPJ: {d_val}", align='C')

            # GERAÇÃO E DOWNLOAD
            pdf_bytes = pdf.output(dest='S')
            st.download_button(
                label="📄 GERAR RELATÓRIO TÉCNICO FINAL",
                data=bytes(pdf_bytes),
                file_name=f"Laudo_MPN_{d.get('tag_id','INS').upper()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")
    else:
        st.error("❌ Dados do Cliente Ausentes")
        st.caption("Preencha Nome e CPF/CNPJ na Aba 1 para liberar o relatório.")

    st.markdown("---")
    if st.button("🗑️ Nova Inspeção (Limpar)", use_container_width=True):
        preservar = ['tecnico_nome', 'tecnico_documento', 'tecnico_registro']
        for k in list(st.session_state.dados.keys()):
            if k not in preservar: st.session_state.dados[k] = ""
        st.rerun()

# ==============================================================================
# FIM DO BLOCO 3 MESCLADO
# ==============================================================================

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
    renderizar_aba_2() # Chama a função que contém o esqueleto da Aba 2

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


# ... fim da função renderizar_aba_diagnosticos ...
    st.session_state.dados['laudo_diag'] = st.text_area(...)

# --- FUNÇÃO DOS GRÁFICOS (COLE AQUI) ---
def renderizar_aba_graficos():
    st.header("📈 Análise Termodinâmica (Mollier)")
    
    d = st.session_state.dados
    fluido = d.get('fluido', 'R410A')
    
    # Busca as pressões reais digitadas na Aba 2 (ou usa padrão se estiver vazio)
    p_baixa_psi = d.get('p_suc_diag', 118.0)
    p_alta_psi = d.get('p_des_diag', 380.0)
    
    # Converte PSI para BAR para o gráfico
    p_baixa = p_baixa_psi * 0.0689476 
    p_alta = p_alta_psi * 0.0689476
    
    st.subheader(f"Diagrama P-h Estimado: {fluido}")
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Simulação da Curva de Saturação
    h_liq = np.linspace(150, 250, 100)
    p_sat = 10 * np.exp(0.02 * (h_liq - 150))
    h_vap = np.linspace(250, 450, 100)
    p_sat_v = 10 * np.exp(-0.015 * (h_vap - 250))
    
    ax.plot(h_liq, p_sat, color='blue', label='Líquido Saturado')
    ax.plot(h_vap, p_sat_v, color='red', label='Vapor Saturado')
    
    # Pontos Dinâmicos baseados no seu preenchimento
    ax.scatter([400], [p_baixa], color='darkblue', s=100, label=f'1. Sucção ({p_baixa_psi} PSI)')
    ax.scatter([450], [p_alta], color='darkred', s=100, label=f'2. Descarga ({p_alta_psi} PSI)')
    
    ax.set_yscale('log')
    ax.set_xlabel("Entalpia (kJ/kg)")
    ax.set_ylabel("Pressão (bar)")
    ax.grid(True, which="both", ls="-", alpha=0.5)
    ax.legend()
    
    st.pyplot(fig)
    st.info("💡 Este diagrama é uma representação técnica do ciclo de compressão do seu ativo.")

# --- INÍCIO DA LÓGICA DE EXIBIÇÃO ---
if aba_selecionada == "📊 Performance (Mollier)":
    renderizar_aba_graficos()

elif aba_selecionada == "Home":
    # --- ABA HOME ---
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2: 
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True) 
        else:
            st.subheader("MPN SOLUÇÕES")

    st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: #0d47a1;">MPN Soluções</h1>
            <p style="color: #1976d2; font-size: 1.2em;">Gestão Inteligente HVAC-R</p>
        </div>
    """, unsafe_allow_html=True)

elif aba_selecionada == "1. Cadastro de Equipamentos":
    renderizar_aba_1()

elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos()

elif aba_selecionada == "Relatórios":
    st.header("📋 Central de Relatórios")
    st.write("O relatório técnico final pode ser gerado no botão azul na barra lateral.")

# ==============================================================================
# 4. LÓGICA DE EXIBIÇÃO DAS ABAS (Onde o app decide o que mostrar)
# ==============================================================================
if aba_selecionada == "📊 Performance (Mollier)":
    renderizar_aba_graficos()

elif aba_selecionada == "Home":
    # --- ABA HOME ---
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Centralização da Logo
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2: 
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True) 
        else:
            st.subheader("MPN SOLUÇÕES")

    # Texto de Boas-vindas
    st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: #0d47a1;">MPN Soluções</h1>
            <p style="color: #1976d2; font-size: 1.2em;">Gestão Inteligente HVAC-R</p>
            <hr>
            <p>Selecione uma opção no menu lateral para iniciar.</p>
        </div>
    """, unsafe_allow_html=True)

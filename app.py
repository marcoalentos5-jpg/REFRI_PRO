
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
    </style>
""", unsafe_allow_html=True)

# 1.1. MOTOR DE SESSÃO (CHAVES VERIFICADAS)

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

# ==============================================================================
# 1.2 FUNÇÃO DA ABA 1: Identificação e Equipamento (VERSÃO FINAL BLINDADA)
# ==============================================================================

def renderizar_aba_1():
    st.subheader("📋 Cadastro de Cliente e Ativo")

    # --- SEÇÃO 1: CLIENTE (COM CORREÇÃO DE CEP) ---
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados.get('nome', ''), key="cli_nome_f")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF/CNPJ", value=st.session_state.dados.get('cpf_cnpj', ''), key="cli_doc_f")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp *", value=st.session_state.dados.get('whatsapp', ''), key="cli_zap_f")

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        st.session_state.dados['celular'] = cx1.text_input("Celular:", value=st.session_state.dados.get('celular', ''), key="cli_cel_f")
        st.session_state.dados['tel_fixo'] = cx2.text_input("Fixo:", value=st.session_state.dados.get('tel_fixo', ''), key="cli_fixo_f")
        st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados.get('email', ''), key="cli_email_f")

        # --- LÓGICA DE CEP ULTRA-RÁPIDA ---
        def renderizar_aba_1():
    st.subheader("📋 Cadastro de Cliente e Ativo")

    # --- SEÇÃO 1: CLIENTE E ENDEREÇO (LOGICA DE CEP BLINDADA) ---
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        # Função interna de atualização automática
        def atualizar_endereco():
            cep = st.session_state.cli_cep_f.strip().replace("-", "").replace(".", "")
            if len(cep) == 8:
                try:
                    dados_cep = buscar_cep(cep)
                    if dados_cep and isinstance(dados_cep, dict) and "erro" not in dados_cep:
                        st.session_state.dados['endereco'] = dados_cep.get('logradouro', '')
                        st.session_state.dados['bairro'] = dados_cep.get('bairro', '')
                        st.session_state.dados['cidade'] = dados_cep.get('localidade', '')
                        st.session_state.dados['uf'] = dados_cep.get('uf', '')
                        st.session_state.dados['cep'] = cep
                except:
                    pass

        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados.get('nome', ''), key="cli_nome_f")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF/CNPJ", value=st.session_state.dados.get('cpf_cnpj', ''), key="cli_doc_f")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp *", value=st.session_state.dados.get('whatsapp', ''), key="cli_zap_f")

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        st.session_state.dados['celular'] = cx1.text_input("Celular:", value=st.session_state.dados.get('celular', ''), key="cli_cel_f")
        st.session_state.dados['tel_fixo'] = cx2.text_input("Fixo:", value=st.session_state.dados.get('tel_fixo', ''), key="cli_fixo_f")
        st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados.get('email', ''), key="cli_email_f")

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        ce1.text_input("CEP *", value=st.session_state.dados.get('cep', ''), key="cli_cep_f", on_change=atualizar_endereco)
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados.get('endereco', ''), key="cli_end_f")
        st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados.get('numero', ''), key="cli_num_f")

        ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4])
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados.get('complemento', ''), key="cli_comp_f")
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados.get('bairro', ''), key="cli_bair_f")
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados.get('cidade', ''), key="cli_cid_f")
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados.get('uf', ''), max_chars=2, key="cli_uf_f")

    # --- SEÇÃO 2: EQUIPAMENTO (LAYOUT FINAL REORDENADO) ---
    st.markdown("### ⚙️ Especificações do Equipamento")
    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3) 
        
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
            fab_val = st.session_state.dados.get('fabricante', 'Carrier')
            fab_idx = fab_list.index(fab_val) if fab_val in fab_list else 0
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_idx, key="fab_f")
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados.get('modelo', ''), key="mod_f")
            
            lista_fluidos = ["R410A", "R134a", "R22", "R32", "R290"]
            f_atual = st.session_state.dados.get('fluido', 'R410A')
            f_idx = lista_fluidos.index(f_atual) if f_atual in lista_fluidos else 0
            st.session_state.dados['fluido'] = st.selectbox("Fluido Refr.:", lista_fluidos, index=f_idx, key="fluid_f")
            
            # POTÊNCIA ABAIXO DO FLUIDO
            st.session_state.dados['potencia'] = st.text_input("Potência (CV/HP):", value=st.session_state.dados.get('potencia', ''), key="pot_f")

        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados.get('serie_evap', ''), key="sevap_f")
            st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados.get('serie_cond', ''), key="scond_f")
            st.session_state.dados['local_cond'] = st.text_input("Localização da Condensadora:", value=st.session_state.dados.get('local_cond', ''), key="lcond_f")
            st.session_state.dados['local_evap'] = st.text_input("Localização da Evaporadora:", value=st.session_state.dados.get('local_evap', ''), key="levap_f")

        with e3:
            lista_caps = {"9.000": 9000, "12.000": 12000, "18.000": 18000, "24.000": 24000, "30.000": 30000, "60.000": 60000}
            cap_sel = st.selectbox("Capacidade (BTU/h):", list(lista_caps.keys()), index=1, key="cap_f")
            st.session_state.dados['btu_nom'] = lista_caps[cap_sel]

            st.session_state.dados['oleo'] = st.selectbox("Tipo de Óleo:", ["POE", "Mineral", "PVE"], key="oleo_f")
            st.session_state.dados['freq'] = st.selectbox("Frequência:", [60, 50], key="freq_f")
            
            # TAG/ID COMO ÚLTIMO CAMPO FÍSICO
            st.session_state.dados['tag_id'] = st.text_input("TAG/ID:", value=st.session_state.dados.get('tag_id', ''), key="tag_f")

            # 9. Óleo e Frequência
            st.session_state.dados['oleo'] = st.selectbox("Tipo de Óleo:", ["POE", "Mineral", "PVE"], key="oleo_f")
            st.session_state.dados['freq'] = st.selectbox("Frequência:", [60, 50], key="freq_f")
            
            # 10. TAG/ID (ÚLTIMO CAMPO)
            st.session_state.dados['tag_id'] = st.text_input("TAG/ID:", value=st.session_state.dados.get('tag_id', ''), key="tag_f")

# --- FUNÇÃO TÉCNICA (Mantenha fora das abas, no escopo principal do código) ---
def f_sat_precisao(p, g):
    if p <= 5: return -50.0
    tabelas = {
        "R410A": {"xp": [90.0, 100.0, 110.0, 122.7, 130.9, 141.7, 150.0, 350.0, 450.0], "fp": [-3.50, -0.29, 2.36, 5.50, 7.40, 9.80, 11.50, 41.50, 54.00]},
        "R32":   {"xp": [90.0, 100.0, 115.0, 140.0, 170.0, 380.0, 480.0], "fp": [-3.66, -0.87, 3.00, 8.50, 14.80, 44.00, 56.50]},
        "R22":   {"xp": [50.0, 60.0, 70.0, 80.0, 100.0, 200.0, 250.0], "fp": [-3.00, 1.50, 5.80, 9.70, 16.50, 38.50, 48.00]},
        "R134a": {"xp": [20.0, 30.0, 40.0, 50.0, 70.0, 150.0, 200.0], "fp": [-8.00, 1.50, 9.50, 16.20, 27.50, 53.00, 65.50]},
        "R290":  {"xp": [40.0, 50.0, 65.0, 80.0, 100.0, 150.0, 190.0], "fp": [-10.5, -4.2, 3.50, 10.20, 17.50, 32.50, 42.00]}
    }
    if g not in tabelas: return 0.0
    return float(np.interp(p, tabelas[g]["xp"], tabelas[g]["fp"]))


# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO SUPREMA - INTEGRADA E BLINDADA)
# ==============================================================================

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    
    # 1. Recuperação Segura de Dados da Aba 1
    fluido = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"❄️ Fluido em Análise: **{fluido}**")

    # --- 1. MEDIÇÕES DE CAMPO (PERSISTÊNCIA TOTAL) ---
    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("**🔵 BAIXA / AR**")
        p_suc = st.number_input("P. Sucção (PSI)", value=st.session_state.dados.get('p_suc', 0.0), format="%.1f", key="ps_vfinal_1")
        st.session_state.dados['p_suc'] = p_suc
        t_suc = st.number_input("T. Tubo Suc. (°C)", value=st.session_state.dados.get('t_suc', 0.0), format="%.1f", key="ts_vfinal_1")
        st.session_state.dados['t_suc'] = t_suc
        t_ret = st.number_input("1. T. Retorno (°C)", value=st.session_state.dados.get('t_ret', 0.0), format="%.1f", key="tr_vfinal_1")
        st.session_state.dados['t_ret'] = t_ret
        t_ins = st.number_input("2. T. Insuflação (°C)", value=st.session_state.dados.get('t_ins', 0.0), format="%.1f", key="ti_vfinal_1")
        st.session_state.dados['t_ins'] = t_ins

    with c2:
        st.markdown("**🔴 ALTA / TENSÃO**")
        p_des = st.number_input("P. Descarga (PSI)", value=st.session_state.dados.get('p_des', 0.0), format="%.1f", key="pd_vfinal_1")
        st.session_state.dados['p_des'] = p_des
        t_liq = st.number_input("T. Tubo Líq. (°C)", value=st.session_state.dados.get('t_liq', 0.0), format="%.1f", key="tl_vfinal_1")
        st.session_state.dados['t_liq'] = t_liq
        v_lin = st.number_input("Tens. Linha (V)", value=st.session_state.dados.get('v_lin', 220.0), key="vl_vfinal_1")
        st.session_state.dados['v_lin'] = v_lin
        v_med = st.number_input("Tens. Medida (V)", value=st.session_state.dados.get('v_med', 220.0), key="vm_vfinal_1")
        st.session_state.dados['v_med'] = v_med

    with c3:
        st.markdown("**⚡ CORRENTE / CARGA**")
        rla = st.number_input("RLA (A)", value=st.session_state.dados.get('rla', 0.0), key="rla_vfinal_1")
        st.session_state.dados['rla'] = rla
        i_med = st.number_input("Corr. Medida (A)", value=st.session_state.dados.get('i_med', 0.0), key="im_vfinal_1")
        st.session_state.dados['i_med'] = i_med
        
        perc_calc = (i_med / rla * 100) if (rla and rla > 0) else 0.0
        st.number_input("Carga do Comp. (%)", value=perc_calc, format="%.1f", disabled=True, key="pc_vfinal_1")
        if perc_calc >= 110.0: st.error(f"🚨 SOBRECARGA: {perc_calc:.1f}%")

    with c4:
        st.markdown("**🔋 CAPACITORES (µF)**")
        cn_c = st.number_input("C. Nom. Comp", value=st.session_state.dados.get('cn_c', 0.0), key="cnc_vf_1")
        st.session_state.dados['cn_c'] = cn_c
        cm_c = st.number_input("C. Lido Comp", value=st.session_state.dados.get('cm_c', 0.0), key="cmc_vf_1")
        st.session_state.dados['cm_c'] = cm_c

    # --- 2. MOTOR DE CÁLCULO (BLINDAGEM CONTRA ERRO LINHA 302) ---
    t_sat_s = f_sat_precisao(p_suc, fluido) if p_suc > 0 else 0.0
    t_sat_d = f_sat_precisao(p_des, fluido) if p_des > 0 else 0.0
    
    sh_total = (t_suc - t_sat_s) if p_suc > 0 else 0.0
    sc_final = (t_sat_d - t_liq) if p_des > 0 else 0.0
    dt_ar = t_ret - t_ins if (t_ret and t_ins) else 0.0
    dif_v = v_lin - v_med
    dif_i = i_med - rla
    d_cap_c = cm_c - cn_c

    # --- 3. RESULTADOS CALCULADOS (PENTA-COLUMN LAYOUT RESTAURADO) ---
    st.markdown("---")
    st.subheader("2. Resultados Calculados")
    res = st.columns(5)
    
    with res[0]:
        st.metric("SH TOTAL", f"{sh_total:.1f} K")
        st.metric("SH ÚTIL", f"{sh_total:.1f} K")
    with res[1]:
        st.metric("SAT. SUCÇÃO", f"{t_sat_s:.1f} °C")
        st.metric("SAT. LÍQUIDO", f"{t_sat_d:.1f} °C")
    with res[2]:
        st.metric("Δ CORRENTE", f"{dif_i:.1f} A")
        st.metric("Δ TENSÃO", f"{dif_v:.1f} V")
    with res[3]:
        st.metric("SC FINAL", f"{sc_final:.1f} K")
        st.metric("ΔT (AR)", f"{dt_ar:.1f} °C")
    with res[4]:
        st.metric("Δ CAP. COMP.", f"{d_cap_c:.1f} µF")

    # --- 4. PARECER TÉCNICO (UNIFICADO) ---
    st.markdown("---")
    st.subheader("3. Parecer Técnico Final")
    
    # Lógica de diagnóstico automático sugerido
    diag_sugestao = ""
    if sh_total > 12 and p_suc > 0: diag_sugestao = "Superaquecimento alto: Possível falta de fluido."
    elif dt_ar < 8 and t_ret > 0: diag_sugestao = "Baixo Delta T: Verificar filtros e serpentina."

    st.session_state.dados['laudo_diag'] = st.text_area(
        "Diagnóstico Final:", 
        value=diag_sugestao if not st.session_state.dados.get('laudo_diag') else st.session_state.dados['laudo_diag'],
        height=150, key="laudo_final_v101"
    )

    # Gerar sugestão automática apenas se o laudo estiver vazio
    if not st.session_state.dados.get('laudo_diag'):
        if sh > 12: sug = "Superaquecimento alto: Possível falta de fluido."
        elif dt_ar < 8 and p_suc > 0: sug = "Baixo Delta T: Verificar filtros e serpentina."
        else: sug = ""
        st.session_state.dados['laudo_diag'] = sug

    st.session_state.dados['laudo_diag'] = st.text_area(
        "Diagnóstico e Observações:", 
        value=st.session_state.dados.get('laudo_diag', ''), 
        height=150, 
        key="laudo_final_v100"
    )

    
    st.markdown("---")
    st.subheader("3. Parecer Técnico Final")
    
    st.session_state.dados['laudo_diag'] = st.text_area(
        "Diagnóstico e Observações:", 
        value=st.session_state.dados.get('laudo_diag', ''), 
        height=150, 
        key="laudo_final_v_perfeito"
    )
    
    # Lógica de diagnóstico automático baseada em simulações de falhas comuns
    diag_previsto = ""
    if sh_total > 12 and p_suc > 0:
        diag_previsto = "Análise: Superaquecimento Elevado. Sugere falta de fluido ou restrição na expansão."
    elif dt_ar < 8 and t_ret > 0:
        diag_previsto = "Análise: Baixo Diferencial de Temperatura. Verificar limpeza de filtros e serpentina."
    elif perc_calc > 110:
        diag_previsto = "Análise: Compressor sobrecarregado. Verificar condensação ou mecânica."

    st.text_area(
        "Relatório de Diagnóstico:", 
        value=diag_previsto if not st.session_state.dados.get('laudo_diag') else st.session_state.dados['laudo_diag'], 
        height=150, 
        key="laudo_v100"
    )
    
    # Lógica de diagnóstico automático preservada
    diag_sugestao = ""
    if sh_total > 12: diag_sugestao = "Superaquecimento alto: Possível falta de fluido."
    elif dt_ar < 8 and t_ret > 0: diag_sugestao = "Baixo Delta T no ar: Verificar filtros e serpentina."
    
    st.session_state.dados['laudo_diag'] = st.text_area(
        "Relatório de Diagnóstico:", 
        value=diag_sugestao if not st.session_state.dados.get('laudo_diag') else st.session_state.dados['laudo_diag'], 
        height=150, 
        key="txt_laudo_vfinal"
    )

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

    # --- BLOCO 2: PROCESSAMENTO (CÁLCULOS TÉCNICOS) ---
    # 1. Pegamos o fluido que foi definido na Aba 1
    fluido_selecionado = st.session_state.dados.get('fluido', 'R410A')

    # 2. Calculamos as Temperaturas de Saturação usando sua função f_sat_precisao
    # t_sat_suc (Baixa) e t_sat_des (Alta)
    p_suc = st.session_state.dados.get('p_suc_psi', 0.0)
    p_alta = st.session_state.dados.get('p_des_psi', 0.0)
    
    t_sat_suc = f_sat_precisao(p_suc, fluido_selecionado)
    t_sat_des = f_sat_precisao(p_alta, fluido_selecionado)

    # 3. Cálculo do SH e SC (Diferencial de temperatura)
    temp_suc = st.session_state.dados.get('t_tubo_suc', 0.0)
    temp_liq = st.session_state.dados.get('t_tubo_liq', 0.0)

    sh = temp_suc - t_sat_suc if temp_suc != 0 else 0.0
    sc = t_sat_des - temp_liq if t_sat_des != 0 else 0.0

    # --- BLOCO 3: EXIBIÇÃO DE RESULTADOS ---
    st.subheader("2. Resultados Calculados")
    res1, res2 = st.columns(2)
    
    with res1:
        st.metric(label="Superaquecimento (SH)", value=f"{sh:.1f} K")
        if temp_suc != 0: # Só valida se houver medição
            if 5 <= sh <= 7: st.success("✅ SH dentro do padrão (5K a 7K)")
            elif sh < 5: st.error("⚠️ SH Baixo: Risco de retorno de líquido")
            else: st.warning("⚠️ SH Alto: Possível falta de fluido ou restrição")

    with res2:
        st.metric(label="Sub-resfriamento (SC)", value=f"{sc:.1f} K")
        if t_sat_des != 0:
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

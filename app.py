
import streamlit as st
import numpy as np
import requests
from datetime import datetime
import urllib.parse
import os 

# ==============================================================================
# 1. FUNÇÕES DE CÁLCULO E INICIALIZAÇÃO (O CÉREBRO)
# ==============================================================================

# Inicialização única do Estado (Session State)
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'tec_nome': '', 'cliente': '', 'nome': '', 'p_baixa': 0.0,
        'p_alta': 0.0, 'temp_sucção': 0.0, 'temp_liquido': 0.0,
        'temp_entrada_ar': 0.0, 'temp_saida_ar': 0.0, 'fluido': 'R410A',
        'laudo_diag': '', 'rla': 0.0, 'i_med': 0.0, 'v_lin': 220.0, 
        'v_med': 220.0, 'cn_c': 0.0, 'cm_c': 0.0, 'tag_id': ''
    }

def calcular_temp_saturacao(pressao, fluido):
    """Calcula a temperatura de saturação aproximada (Ponto de Orvalho)"""
    try:
        p = float(pressao)
        if fluido == "R410A": return round((p / 13.5) - 1.0, 2)
        elif fluido == "R22": return round((p / 7.0) - 13.0, 2)
        elif fluido == "R134a": return round((p / 4.5) - 15.0, 2)
        elif fluido == "R32": return round((p / 14.0) - 2.0, 2)
        elif fluido == "R290": return round((p / 6.0) - 25.0, 2)
        else: return round((p / 12.0), 2)
    except:
        return 0.0

def f_sat_precisao(p, fluido):
    """Apelido para compatibilidade entre as abas"""
    return calcular_temp_saturacao(p, fluido)

# --- FUNÇÕES TÉCNICAS DE APOIO (UTILIDADES) ---

def buscar_cep(cep):
    """Consulta automática de endereço"""
    try:
        cep_limpo = cep.replace("-", "").replace(".", "")
        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def limpar_dados_tecnicos():
    """Zera apenas as medições, mantendo os dados do cliente e técnico"""
    chaves_para_zerar = [
        'p_baixa', 'p_alta', 'temp_sucção', 'temp_liquido', 
        'temp_entrada_ar', 'temp_saida_ar', 'i_med', 'v_med', 'laudo_diag'
    ]
    for chave in chaves_para_zerar:
        st.session_state.dados[chave] = 0.0 if chave != 'laudo_diag' else ""
    st.rerun()


# ==============================================================================
# 1.1. FUNÇÕES TÉCNICAS E DE UTILIDADE (O MOTOR DO APP)
# ==============================================================================

def buscar_cep(cep):
    """Consulta automática de endereço via API"""
    try:
        # Remove caracteres não numéricos
        cep_limpo = ''.join(filter(str.isdigit, str(cep)))
        response = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
        if response.status_code == 200:
            dados = response.json()
            return dados if "erro" not in dados else None
        return None
    except:
        return None

def f_sat_precisao(p, g):
    """
    Calcula a temperatura de saturação exata usando interpolação linear.
    p = Pressão (PSI)
    g = Gás Refrigerante (Fluido)
    """
    if p <= 5: return -50.0  # Proteção contra vácuo ou leitura errada
    
    tabelas = {
        "R410A": {"xp": [90.0, 100.0, 110.0, 122.7, 130.9, 141.7, 150.0, 350.0, 450.0], 
                  "fp": [-3.50, -0.29, 2.36, 5.50, 7.40, 9.80, 11.50, 41.50, 54.00]},
        "R32":   {"xp": [90.0, 100.0, 115.0, 140.0, 170.0, 380.0, 480.0], 
                  "fp": [-3.66, -0.87, 3.00, 8.50, 14.80, 44.00, 56.50]},
        "R22":   {"xp": [50.0, 60.0, 70.0, 80.0, 100.0, 200.0, 250.0], 
                  "fp": [-3.00, 1.50, 5.80, 9.70, 16.50, 38.50, 48.00]},
        "R134a": {"xp": [20.0, 30.0, 40.0, 50.0, 70.0, 150.0, 200.0], 
                  "fp": [-8.00, 1.50, 9.50, 16.20, 27.50, 53.00, 65.50]},
        "R290":  {"xp": [40.0, 50.0, 65.0, 80.0, 100.0, 150.0, 190.0], 
                  "fp": [-10.5, -4.2, 3.50, 10.20, 17.50, 32.50, 42.00]}
    }
    
    if g not in tabelas: 
        # Fallback caso o fluido selecionado não esteja na tabela de precisão
        return round((p / 13.0) - 1.0, 2)
        
    return float(np.interp(p, tabelas[g]["xp"], tabelas[g]["fp"]))

def limpar_dados_tecnicos():
    """Zera as medições mantendo cadastro do cliente"""
    chaves_para_zerar = [
        'p_baixa', 'p_alta', 'temp_sucção', 'temp_liquido', 
        'temp_entrada_ar', 'temp_saida_ar', 'i_med', 'v_med', 'laudo_diag'
    ]
    for chave in chaves_para_zerar:
        st.session_state.dados[chave] = 0.0 if chave != 'laudo_diag' else ""
    st.rerun()

# --- FIM DA SEÇÃO TÉCNICA ---

# ==============================================================================
# 2. RENDERIZAÇÃO DA ABA 1 (CADASTRO)
# ==============================================================================
def renderizar_aba_1():
    st.subheader("📋 Cadastro de Cliente e Ativo")

    # --- SEÇÃO 1: CLIENTE E ENDEREÇO ---
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        def atualizar_endereco():
            # Acessa o valor diretamente da key do widget
            cep = st.session_state.cli_cep_f.strip().replace("-", "").replace(".", "")
            if len(cep) == 8:
                res = buscar_cep(cep) 
                if res:
                    st.session_state.dados.update({
                        'endereco': res.get('logradouro', ''),
                        'bairro': res.get('bairro', ''),
                        'cidade': res.get('localidade', ''),
                        'uf': res.get('uf', ''),
                        'cep': cep
                    })

        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados.get('nome', ''), key="cli_nome_f")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF/CNPJ", value=st.session_state.dados.get('cpf_cnpj', ''), key="cli_doc_f")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp *", value=st.session_state.dados.get('whatsapp', ''), key="cli_zap_f")

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

    # --- SEÇÃO 2: EQUIPAMENTO ---
    st.markdown("### ⚙️ Especificações do Equipamento")
    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3) 
        
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
            # Define o índice padrão para evitar erro de seleção
            fab_index = fab_list.index(st.session_state.dados.get('fabricante', 'LG')) if st.session_state.dados.get('fabricante') in fab_list else 0
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_index, key="fab_f")
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados.get('modelo', ''), key="mod_f")
            
            fluido_opcoes = ["R410A", "R134a", "R22", "R32", "R290"]
            fluido_idx = fluido_opcoes.index(st.session_state.dados.get('fluido', 'R410A')) if st.session_state.dados.get('fluido') in fluido_opcoes else 0
            fluido_sel = st.selectbox("Fluido Refr.:", fluido_opcoes, index=fluido_idx, key="fluid_f")
            st.session_state.dados['fluido'] = fluido_sel
            st.session_state.dados['potencia'] = st.text_input("Potência (CV/HP):", value=st.session_state.dados.get('potencia', ''), key="pot_f")

        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados.get('serie_evap', ''), key="sevap_f")
            st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados.get('serie_cond', ''), key="scond_f")
            st.session_state.dados['local_cond'] = st.text_input("Localização da Condensadora:", value=st.session_state.dados.get('local_cond', ''), key="lcond_f")
            st.session_state.dados['local_evap'] = st.text_input("Localização da Evaporadora:", value=st.session_state.dados.get('local_evap', ''), key="levap_f")

        with e3:
            cap_opcoes = [9000, 12000, 18000, 24000, 30000, 60000]
            cap_idx = cap_opcoes.index(st.session_state.dados.get('btu_nom', 12000)) if st.session_state.dados.get('btu_nom') in cap_opcoes else 1
            st.session_state.dados['btu_nom'] = st.selectbox("Capacidade (BTU/h):", cap_opcoes, index=cap_idx, key="cap_f")
            st.session_state.dados['oleo'] = st.selectbox("Tipo de Óleo:", ["POE", "Mineral", "PVE"], key="oleo_f")
            st.session_state.dados['freq'] = st.selectbox("Frequência:", [60, 50], key="freq_f")
            st.session_state.dados['tag_id'] = st.text_input("TAG/ID:", value=st.session_state.dados.get('tag_id', ''), key="tag_f")

    # --- SEÇÃO 3: MEDIÇÕES TÉCNICAS ---
    st.markdown("### 📊 Performance e Ciclo Frigorífico")
    with st.expander("Dados de Pressão e Temperatura", expanded=True):
        
        # LINHA 1: BAIXA
        st.subheader("❄️ Evaporação (Lado de Baixa)")
        lb1, lb2, lb3 = st.columns(3)
        with lb1:
            p_baixa = st.number_input("Pressão Sucção (PSI)", value=float(st.session_state.dados.get('p_baixa', 118.0)), key="p_baixa_input")
        with lb2:
            t_suc = st.number_input("Temp. Tubo Sucção (°C)", value=float(st.session_state.dados.get('temp_sucção', 12.0)), key="t_suc_input")
        with lb3:
            # Uso da função de precisão que criamos
            t_sat_baixa = f_sat_precisao(p_baixa, fluido_sel)
            st.metric("T. Saturação (Orvalho)", f"{t_sat_baixa:.2f} °C")

        st.markdown("---")

        # LINHA 2: ALTA
        st.subheader("🔥 Condensação (Lado de Alta)")
        la1, la2, la3 = st.columns(3)
        with la1:
            p_alta = st.number_input("Pressão Descarga (PSI)", value=float(st.session_state.dados.get('p_alta', 380.0)), key="p_alta_input")
        with la2:
            t_liq = st.number_input("Temp. Linha Líquido (°C)", value=float(st.session_state.dados.get('temp_liquido', 38.0)), key="t_liq_input")
        with la3:
            # Saturação de Alta também pela função de precisão
            t_sat_alta = f_sat_precisao(p_alta, fluido_sel)
            st.metric("T. Saturação (Bolha)", f"{t_sat_alta:.2f} °C")

        st.markdown("---")

        # LINHA 3: DIFERENCIAL DE AR
        st.subheader("🌬️ Performance Térmica do Ar")
        ar1, ar2, ar3 = st.columns(3)
        with ar1:
            t_in = st.number_input("Temp. Retorno Ar (°C)", value=float(st.session_state.dados.get('temp_entrada_ar', 25.0)), key="t_in_input")
        with ar2:
            t_out = st.number_input("Temp. Insuflamento Ar (°C)", value=float(st.session_state.dados.get('temp_saida_ar', 12.0)), key="t_out_input")
        with ar3:
            delta_t = round(t_in - t_out, 2)
            st.metric("Delta T (Ar)", f"{delta_t} °C")

        # ATUALIZAÇÃO FINAL DOS DADOS (Sincroniza com a Aba de Diagnóstico)
        st.session_state.dados.update({
            'p_baixa': p_baixa, 'temp_sucção': t_suc,
            'p_alta': p_alta, 'temp_liquido': t_liq,
            't_sat_baixa': t_sat_baixa, 't_sat_alta': t_sat_alta,
            'temp_entrada_ar': t_in, 'temp_saida_ar': t_out
        })


# ==============================================================================
def renderizar_aba_2():
    st.header("🔍 Diagnóstico Térmico e de Performance")
    
    # Recuperando os dados salvos na Aba 1
    d = st.session_state.dados
    
    # Cálculos de Ciclo
    sh = round(d.get('temp_sucção', 0) - d.get('t_sat_baixa', 0), 2)
    sc = round(d.get('t_sat_alta', 0) - d.get('temp_liquido', 0), 2)
    dt_ar = round(d.get('temp_entrada_ar', 0) - d.get('temp_saida_ar', 0), 2)

    # --- LINHA 1: MÉTRICAS PRINCIPAIS ---
    col_sh, col_sc, col_dt = st.columns(3)
    
    with col_sh:
        st.metric("Superaquecimento (SH)", f"{sh} °C")
        if 5 <= sh <= 8:
            st.success("✅ SH Ideal: Fluido evaporando totalmente.")
        elif sh > 8:
            st.warning("⚠️ SH Alto: Falta de fluido ou restrição.")
        else:
            st.error("🚨 SH Baixo: Risco de líquido no compressor!")

    with col_sc:
        st.metric("Sub-resfriamento (SC)", f"{sc} °C")
        if 5 <= sc <= 12:
            st.success("✅ SC Ideal: Condensação eficiente.")
        else:
            st.info("ℹ️ SC Fora do padrão: Verifique carga/limpeza.")

    with col_dt:
        st.metric("Delta T do Ar", f"{dt_ar} °C")
        if 8 <= dt_ar <= 12:
            st.success("✅ Troca de Calor OK.")
        else:
            st.warning("⚠️ Diferencial fora da faixa ideal.")

    st.markdown("---")

    # --- LINHA 2: ANÁLISE DO CALOR LATENTE (A "ESPONJA") ---
    st.subheader("🔋 Capacidade de Absorção de Calor")
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        # Lógica visual do poder da "esponja"
        # Quanto menor o SH (dentro da margem), mais líquido ocupa a serpentina = mais calor latente absorvido.
        poder_latente = max(0, min(100, int((1 - (sh/20)) * 100)))
        st.write("**Disponibilidade de Calor Latente (Líquido na Serpentina):**")
        st.progress(poder_latente)
        
        if poder_latente > 70:
            st.info("💡 O fluido está agindo como uma esponja seca, pronto para sugar a umidade e o calor do quarto.")
        else:
            st.warning("💡 A 'esponja' está saturada ou insuficiente. A remoção de umidade será lenta.")

    with c2:
        st.write("**Resumo do Ativo:**")
        st.write(f"🏷️ **TAG:** {d.get('tag_id', 'N/A')}")
        st.write(f"❄️ **Fluido:** {d.get('fluido', 'N/A')}")
        st.write(f"🏢 **Cliente:** {d.get('nome', 'Não Informado')}")

    st.divider()
    st.caption("Nota: Cálculos baseados em aproximações de saturação para fluidos padrão.")

# ==============================================================================
# 3. SIDEBAR E NAVEGAÇÃO (NÍVEL PRINCIPAL)
# ==============================================================================

with st.sidebar:
    st.title("🚀 Painel de Controle")
    aba_selecionada = st.radio("Navegação:", ["Home", "1. Cadastro", "2. Diagnóstico"], key="main_nav")
    
    st.markdown("---")
    st.subheader("👤 Identificação")
    # Salvando Técnico e Cliente no dicionário 'dados'
    st.session_state.dados['tec_nome'] = st.text_input("Técnico:", value=st.session_state.dados.get('tec_nome', ''), key="t_n")
    st.session_state.dados['cliente'] = st.text_input("Cliente/Unidade:", value=st.session_state.dados.get('cliente', ''), key="c_n")
    st.session_state.dados['tec_reg'] = st.text_input("Registro (CFT/CREA):", value=st.session_state.dados.get('tec_reg', ''), key="t_r")

# LÓGICA DE EXIBIÇÃO
if aba_selecionada == "1. Cadastro":
    renderizar_aba_1()
elif aba_selecionada == "2. Diagnóstico":
    st.info("Aba de Diagnóstico pronta para receber cálculos de Superaquecimento.")
# LÓGICA DE EXIBIÇÃO FINAL
if aba_selecionada == "Home":
    st.title("🏠 Bem-vindo ao Refri-Pro")
    st.write("Selecione uma aba no menu lateral para começar.")
    
elif aba_selecionada == "1. Cadastro":
    renderizar_aba_1()
    
elif aba_selecionada == "2. Diagnóstico":
    renderizar_aba_2() # Chama a versão suprema que acabamos de criar

# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO SUPREMA - INTEGRADA E BLINDADA)
# ==============================================================================

def renderizar_aba_2():
    st.header("🔍 Central de Diagnóstico Técnico")
    
    # 1. Recuperação Segura de Dados
    d = st.session_state.dados
    fluido = d.get('fluido', 'R410A')
    st.info(f"❄️ Fluido em Análise: **{fluido}**")

    # --- 1. MEDIÇÕES DE CAMPO (PERSISTÊNCIA TOTAL) ---
    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("**🔵 BAIXA / AR**")
        p_suc = st.number_input("P. Sucção (PSI)", value=float(d.get('p_baixa', 0.0)), format="%.1f", key="ps_vfinal")
        t_suc = st.number_input("T. Tubo Suc. (°C)", value=float(d.get('temp_sucção', 0.0)), format="%.1f", key="ts_vfinal")
        t_ret = st.number_input("1. T. Retorno (°C)", value=float(d.get('temp_entrada_ar', 0.0)), format="%.1f", key="tr_vfinal")
        t_ins = st.number_input("2. T. Insuflação (°C)", value=float(d.get('temp_saida_ar', 0.0)), format="%.1f", key="ti_vfinal")

    with c2:
        st.markdown("**🔴 ALTA / TENSÃO**")
        p_des = st.number_input("P. Descarga (PSI)", value=float(d.get('p_alta', 0.0)), format="%.1f", key="pd_vfinal")
        t_liq = st.number_input("T. Tubo Líq. (°C)", value=float(d.get('temp_liquido', 0.0)), format="%.1f", key="tl_vfinal")
        v_lin = st.number_input("Tens. Linha (V)", value=float(d.get('v_lin', 220.0)), key="vl_vfinal")
        v_med = st.number_input("Tens. Medida (V)", value=float(d.get('v_med', 220.0)), key="vm_vfinal")

    with c3:
        st.markdown("**⚡ CORRENTE / CARGA**")
        rla = st.number_input("RLA (A)", value=float(d.get('rla', 0.0)), key="rla_vfinal")
        i_med = st.number_input("Corr. Medida (A)", value=float(d.get('i_med', 0.0)), key="im_vfinal")
        
        perc_calc = (i_med / rla * 100) if (rla > 0) else 0.0
        st.metric("Carga do Comp. (%)", f"{perc_calc:.1f}%")
        if perc_calc >= 110.0: st.error(f"🚨 SOBRECARGA")

    with c4:
        st.markdown("**🔋 CAPACITORES (µF)**")
        cn_c = st.number_input("C. Nom. Comp", value=float(d.get('cn_c', 0.0)), key="cnc_vf")
        cm_c = st.number_input("C. Lido Comp", value=float(d.get('cm_c', 0.0)), key="cmc_vf")

    # --- 2. MOTOR DE CÁLCULO (Sincronizado com a Aba 1) ---
    # Nota: f_sat_precisao deve estar definida no seu código global
    t_sat_s = calcular_temp_saturacao(p_suc, fluido) if p_suc > 0 else 0.0
    t_sat_d = round((p_des / 11.5) + 12.0, 2) if p_des > 0 else 0.0
    
    sh_total = (t_suc - t_sat_s) if p_suc > 0 else 0.0
    sc_final = (t_sat_d - t_liq) if p_des > 0 else 0.0
    dt_ar = t_ret - t_ins
    dif_v = v_lin - v_med
    d_cap_c = cm_c - cn_c

    # --- 3. RESULTADOS CALCULADOS (PENTA-COLUMN LAYOUT) ---
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
        st.metric("Δ CORRENTE", f"{i_med - rla:.1f} A")
        st.metric("Δ TENSÃO", f"{dif_v:.1f} V")
    with res[3]:
        st.metric("SC FINAL", f"{sc_final:.1f} K")
        st.metric("ΔT (AR)", f"{dt_ar:.1f} °C")
    with res[4]:
        st.metric("Δ CAP. COMP.", f"{d_cap_c:.1f} µF")

    # --- 4. PARECER TÉCNICO (LIMPO E ÚNICO) ---
    st.markdown("---")
    st.subheader("3. Parecer Técnico Final")
    
    # Lógica de diagnóstico automático
    diag_previsto = ""
    if sh_total > 12 and p_suc > 0:
        diag_previsto = "Análise: Superaquecimento Elevado. Sugere falta de fluido ou restrição."
    elif dt_ar < 8 and t_ret > 0:
        diag_previsto = "Análise: Baixo Diferencial de Temperatura. Verificar limpeza de filtros e serpentina."
    elif perc_calc > 110:
        diag_previsto = "Análise: Compressor sobrecarregado. Verificar condensação ou mecânica."
    else:
        diag_previsto = "Análise: Sistema operando dentro dos parâmetros normais."

    # Campo de texto único para o laudo
    d['laudo_diag'] = st.text_area(
        "Diagnóstico e Observações:", 
        value=d.get('laudo_diag', diag_previsto), 
        height=150, 
        key="txt_laudo_final"
    )

    # Sincroniza de volta para o session_state global
    st.session_state.dados.update({
        'p_baixa': p_suc, 'temp_sucção': t_suc, 'p_alta': p_des, 'temp_liquido': t_liq,
        'temp_entrada_ar': t_ret, 'temp_saida_ar': t_ins, 'rla': rla, 'i_med': i_med,
        'v_lin': v_lin, 'v_med': v_med, 'cn_c': cn_c, 'cm_c': cm_c
    })

# ==============================================================================
# 3. SIDEBAR - DADOS DO TÉCNICO E NAVEGAÇÃO (NÍVEL PRINCIPAL)
# ==============================================================================
   # --- Fim da função renderizar_aba_1 (Certifique-se que o código abaixo está FORA dela) ---

# ==============================================================================
# 3. SIDEBAR - DADOS DO TÉCNICO E NAVEGAÇÃO (NÍVEL PRINCIPAL)
# ==============================================================================
    with st.sidebar:
        st.title("🚀 Painel de Controle")

    # A. NAVEGAÇÃO
    opcoes_abas = ["Home", "1. Cadastro de Equipamentos", "2. Diagnósticos", "Relatórios"]
    
    # Adicionei uma KEY única para evitar conflitos de ID do Streamlit
    aba_selecionada = st.radio("Selecione a Aba:", opcoes_abas, key="menu_navegacao")
    
    st.markdown("---")
    
    # B. DADOS DO TÉCNICO RESPONSÁVEL
    st.subheader("👤 Técnico Responsável")
    
    # Inicia as chaves se não existirem para evitar erro de inicialização
    if 'tecnico_nome' not in st.session_state.dados: st.session_state.dados['tecnico_nome'] = ""
    if 'tecnico_documento' not in st.session_state.dados: st.session_state.dados['tecnico_documento'] = ""
    if 'tecnico_registro' not in st.session_state.dados: st.session_state.dados['tecnico_registro'] = ""

    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'], key="tec_nome_sidebar")
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ Técnico:", value=st.session_state.dados['tecnico_documento'], key="tec_doc_sidebar")
    st.session_state.dados['tecnico_registro'] = st.text_input("Inscrição (CFT/CREA):", value=st.session_state.dados['tecnico_registro'], key="tec_reg_sidebar")
    
    st.markdown("---")
    
    # C. VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS
    nome_cli = st.session_state.dados.get('nome', '')
    zap_cli = st.session_state.dados.get('whatsapp', '')
    
    if not nome_cli or not zap_cli:
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
    
    # 1. Recuperação Segura de Dados (Sincronizado com a Aba 1)
    d = st.session_state.dados
    fluido = d.get('fluido', 'R410A')
    st.info(f"❄️ Fluido em Análise: **{fluido}**")

    # --- 1. MEDIÇÕES DE CAMPO ---
    # Aqui usamos os valores que já existem no session_state para não ter que digitar de novo
    st.subheader("1. Medições de Campo")
    col_suc, col_des = st.columns(2)
    
    with col_suc:
        st.markdown("### 🔵 Baixa Pressão")
        # Buscamos 'p_baixa' que foi definido na Aba 1
        p_suc = st.number_input("Pressão de Sucção (PSI):", value=float(d.get('p_baixa', 0.0)), step=1.0, key="p_suc_diag_final")
        t_suc = st.number_input("Temp. Tubulação Sucção (°C):", value=float(d.get('temp_sucção', 0.0)), step=0.1, key="t_suc_diag_final")

    with col_des:
        st.markdown("### 🔴 Alta Pressão")
        # Buscamos 'p_alta' que foi definido na Aba 1
        p_des = st.number_input("Pressão de Descarga (PSI):", value=float(d.get('p_alta', 0.0)), step=1.0, key="p_des_diag_final")
        t_liq = st.number_input("Temp. Tubulação Líquido (°C):", value=float(d.get('temp_liquido', 0.0)), step=0.1, key="t_liq_diag_final")

    st.markdown("---")

    # --- 2. MOTOR DE CÁLCULO ---
    # t_sat_suc (Baixa) e t_sat_des (Alta) usando sua função de precisão
    t_sat_suc = f_sat_precisao(p_suc, fluido) if p_suc > 0 else 0.0
    t_sat_des = f_sat_precisao(p_des, fluido) if p_des > 0 else 0.0

    # Cálculo do SH e SC
    sh = t_suc - t_sat_suc if p_suc > 0 else 0.0
    sc = t_sat_des - t_liq if p_des > 0 else 0.0

    # --- 3. EXIBIÇÃO DE RESULTADOS ---
    st.subheader("2. Resultados Calculados")
    res1, res2 = st.columns(2)
    
    with res1:
        st.metric(label="Superaquecimento (SH)", value=f"{sh:.1f} K")
        if p_suc > 0:
            if 5 <= sh <= 8: 
                st.success("✅ SH Ideal (Fluido 100% Vapor)")
            elif sh < 5: 
                st.error("🚨 SH Baixo: Risco de Golpe de Líquido!")
            else: 
                st.warning("⚠️ SH Alto: Baixa eficiência / Falta de fluido")

    with res2:
        st.metric(label="Sub-resfriamento (SC)", value=f"{sc:.1f} K")
        if p_des > 0:
            if 5 <= sc <= 12: 
                st.success("✅ SC Ideal (Líquido Sub-resfriado)")
            else: 
                st.info("ℹ️ SC fora do padrão: Verifique a condensadora")

    st.markdown("---")

    # --- 4. CONCLUSÃO E LAUDO ---
    st.subheader("3. Parecer Técnico Final")
    
    # Criamos uma sugestão automática baseada nos números
    sugestao = ""
    if sh > 12: sugestao = "Diagnóstico: SH elevado indica falta de carga ou restrição."
    elif sh < 3 and p_suc > 0: sugestao = "Diagnóstico: Risco iminente de quebra do compressor por líquido."
    
    d['laudo_diag'] = st.text_area(
        "Relatório de Diagnóstico:",
        value=d.get('laudo_diag', sugestao),
        placeholder="Descreva as anomalias...",
        key="laudo_final_unico" # Chave única para evitar erro de duplicata
    )

    # Atualiza o dicionário global para garantir que os dados fiquem salvos
    d.update({
        'p_baixa': p_suc, 'temp_sucção': t_suc,
        'p_alta': p_des, 'temp_liquido': t_liq
    })

# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (CONGELADO)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os # Biblioteca para verificar arquivos no sistema

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

# 2. MOTOR DE SESSÃO (CHAVES VERIFICADAS + BLINDAGEM)
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

# CONTADOR DE RESET (Essencial para o botão "Limpar Formulário" funcionar 100%)
if 'count' not in st.session_state:
    st.session_state.count = 0

# LISTA MESTRA PARA TRAVA DE FLUIDO
LISTA_FLUIDOS = ["R410A", "R134a", "R22", "R32", "R290"]

def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, str(cep)))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
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
# 1. FUNÇÃO DA ABA 1: Identificação e Equipamento (VERSÃO COM LAYOUT E MÁSCARAS)
# ==============================================================================

def renderizar_aba_1():
    # Usando o contador global para garantir que os widgets resetem no comando "Limpar"
    c = st.session_state.count
    
    tabs = st.tabs(["📋 Identificação e Equipamento"])
    tab1 = tabs[0]

    with tab1:
        with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
            # --- CAMPOS COM FORMATAÇÃO ---
            c1, c2, c3 = st.columns([2, 1, 1])
            st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key=f"cli_nome_{c}")
            st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF (000.000.000-00)", value=st.session_state.dados['cpf_cnpj'], key=f"cli_doc_{c}")
            st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (XX-X-XXXX-XXXX) *", value=st.session_state.dados['whatsapp'], key=f"cli_zap_{c}")

            cx1, cx2, cx3 = st.columns([1, 1, 2])
            st.session_state.dados['celular'] = cx1.text_input("Cel. (XX-X-XXXX-XXXX):", value=st.session_state.dados['celular'], key=f"cli_cel_{c}")
            st.session_state.dados['tel_fixo'] = cx2.text_input("Fixo (XX-XXXX-XXXX):", value=st.session_state.dados['tel_fixo'], key=f"cli_tel_{c}")
            st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'], key=f"cli_email_{c}")

            st.markdown("---")
            
            # --- SEÇÃO ENDEREÇO (LINHA 1) ---
            ce1, ce2, ce3 = st.columns([1, 2, 1])
            
            # Lógica de CEP corrigida para evitar loops e delays
            cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'], key=f"cli_cep_{c}")
            if cep_input != st.session_state.dados['cep']:
                st.session_state.dados['cep'] = cep_input
                if buscar_cep(cep_input): 
                    st.rerun() # Força a atualização dos campos abaixo imediatamente

            st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'], key=f"cli_end_{c}")
            st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'], key=f"cli_num_{c}")

            # --- SEÇÃO ENDEREÇO (LINHA 2) ---
            ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4]) 
            st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'], key=f"cli_comp_{c}")
            st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'], key=f"cli_bairro_{c}")
            st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'], key=f"cli_cid_{c}")
            st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'], max_chars=2, key=f"cli_uf_{c}")

        # --- SEÇÃO EQUIPAMENTO ---
        col_titulo, col_data = st.columns([3, 1])
        with col_titulo: st.subheader("⚙️ Especificações do Equipamento")
        with col_data: 
            # A data precisa de uma key para resetar também
            st.session_state.dados['data'] = st.text_input("Data da Visita:", value=st.session_state.dados['data'], key=f"data_visita_{c}")

        with st.expander("Detalhes Técnicos do Ativo", expanded=True):
            e1, e2, e3 = st.columns(3)
            with e1:
                fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
                fab_val = st.session_state.dados.get('fabricante', 'Carrier')
                fab_idx = fab_list.index(fab_val) if fab_val in fab_list else 0
                st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_idx, key=f"fab_{c}")
                st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'], key=f"mod_{c}")
                
                lin_list = ["Residencial", "Comercial", "Industrial"]
                lin_idx = lin_list.index(st.session_state.dados['linha']) if st.session_state.dados['linha'] in lin_list else 0
                st.session_state.dados['linha'] = st.selectbox("Linha:", lin_list, index=lin_idx, key=f"lin_{c}")
                
                status_list = ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"]
                stat_idx = status_list.index(st.session_state.dados['status_maquina']) if st.session_state.dados['status_maquina'] in status_list else 0
                st.session_state.dados['status_maquina'] = st.radio("Status:", status_list, index=stat_idx, horizontal=True, key=f"stat_{c}")

            with e2:
                st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'], key=f"sevap_{c}")
                st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados['serie_cond'], key=f"scond_{c}")
                st.session_state.dados['local_evap'] = st.text_input("Local da Evaporadora:", value=st.session_state.dados['local_evap'], key=f"levap_{c}")
                st.session_state.dados['local_cond'] = st.text_input("Local da Condensadora:", value=st.session_state.dados['local_cond'], key=f"lcond_{c}")

            with e3:
                cap_list = ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"]
                cap_idx = cap_list.index(st.session_state.dados['capacidade']) if st.session_state.dados['capacidade'] in cap_list else 1
                st.session_state.dados['capacidade'] = st.selectbox("Capacidade (BTU):", cap_list, index=cap_idx, key=f"cap_{c}")
                
                # LISTA_FLUIDOS definida na Aba 0
                flu_idx = LISTA_FLUIDOS.index(st.session_state.dados['fluido']) if st.session_state.dados['fluido'] in LISTA_FLUIDOS else 0
                st.session_state.dados['fluido'] = st.selectbox("Fluido:", LISTA_FLUIDOS, index=flu_idx, key=f"flu_{c}")
                
                serv_list = ["Manutenção Preventiva", "Manutenção Corretiva", "Instalação", "Infraestrutura"]
                serv_idx = serv_list.index(st.session_state.dados['tipo_servico']) if st.session_state.dados['tipo_servico'] in serv_list else 0
                st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", serv_list, index=serv_idx, key=f"serv_{c}")
                
                st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'], key=f"tag_{c}")

# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO FINAL BLINDADA - R32/RLA/ΔT)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    
   
    # Resgate do Fluido da Aba 1 (Sincronizado)
    fluido = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"❄️ Fluido Refrigerante Selecionado: **{fluido}**")
    
    # --- CSS PARA ALERTAS TÉCNICOS (CONGELADO) ---
    st.markdown("""
        <style>
        .sh-critico { background-color: #ff1744; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
        .sobrecarga { color: #d32f2f; font-weight: bold; font-size: 14px; }
        </style>
    """, unsafe_allow_html=True)

    # --- 1. MEDIÇÕES DE CAMPO (5 COLUNAS - LAYOUT ORIGINAL) ---
    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown("🔵 **EVAPORADORA**")
        p_suc = st.number_input("P. Sucção (PSI)", format="%.2f", step=0.1, key=f"ps_{c}")
        t_suc = st.number_input("T. Tubo Suc. (°C)", format="%.2f", step=0.1, key=f"ts_{c}")
        t_ret = st.number_input("T. Retorno (°C)", format="%.2f", step=0.1, key=f"tr_{c}")
        t_ins = st.number_input("T. Insufla. (°C)", format="%.2f", step=0.1, key=f"ti_{c}")

    with c2:
        st.markdown("🔴 **CONDENSADORA**")
        p_des = st.number_input("P. Desc. (PSI)", format="%.2f", step=0.1, key=f"pd_{c}")
        t_liq = st.number_input("T. Tubo Líq. (°C)", format="%.2f", step=0.1, key=f"tl_{c}")

    with c3:
        st.markdown("⚡ **TENSÃO**")
        v_lin = st.number_input("Tens. Linha (V)", format="%.2f", step=1.0, key=f"vl_{c}")
        v_med = st.number_input("Tens. Medida (V)", format="%.2f", step=1.0, key=f"vm_{c}")

    with c4:
        st.markdown("🔌 **CORRENTE**")
        rla = st.number_input("RLA (A)", format="%.2f", step=0.1, key=f"rla_{c}")
        lra = st.number_input("LRA (A)", format="%.2f", step=0.1, key=f"lra_{c}")
        i_med = st.number_input("Corr. Medida (A)", format="%.2f", step=0.1, key=f"im_{c}")

    with c5:
        st.markdown("🔋 **CAPACIT.**")
        cn_c = st.number_input("C. Nom. Comp", format="%.2f", key=f"cnc_{c}")
        cn_f = st.number_input("C. Nom. Fan", format="%.2f", key=f"cnf_{c}")
        cm_c = st.number_input("C. Med. Comp", format="%.2f", key=f"cmc_{c}")
        cm_f = st.number_input("C. Med. Fan", format="%.2f", key=f"cmf_{c}")

    # --- 2. MOTOR DE CÁLCULO (ASSIMILADO) ---
    def f_sat(p, g):
        if p <= 5: return 0.0
        # Fórmulas de aproximação técnica validadas
        if g == "R410A": return 0.253 * (p**0.8) - 18.5
        if g == "R22": return 0.415 * (p**0.72) - 19.8
        if g == "R32": return 0.245 * (p**0.81) - 19.0
        if g == "R134a": return 0.65 * (p**0.62) - 25.0
        return 0.0

    t_sat_s = f_sat(p_suc, fluido)
    t_sat_d = f_sat(p_des, fluido)
    
    # Cálculos de Performance
    sh = (t_suc - t_sat_s) if p_suc > 0 else 0.0
    sc = (t_sat_d - t_liq) if p_des > 0 else 0.0
    dt_ar = (t_ret - t_ins) if (t_ret > 0 and t_ins > 0) else 0.0
    dif_v = v_lin - v_med
    dif_i = rla - i_med if rla > 0 else 0.0

    st.markdown("---")

    # --- 3. RESULTADOS CALCULADOS ---
    st.subheader("2. Resultados Calculados")
    res1, res2, res3, res4, res5 = st.columns(5)

    with res1:
        st.metric("ΔT Ar (Insufl.)", f"{dt_ar:.2f} °C")
        # Alerta Crítico de SH baixo (Risco de Golpe de Líquido)
        if sh < 5 and p_suc > 0:
            st.markdown(f'<div class="sh-critico">SH: {sh:.2f} K<br>⚠️ RISCO LÍQUIDO</div>', unsafe_allow_html=True)
        else:
            st.metric("SH (Superaq.)", f"{sh:.2f} K")

    with res2:
        st.metric("SC (Sub-resf.)", f"{sc:.2f} K")
        st.caption(f"T. Sat Alta: {t_sat_d:.2f}°C")

    with res3:
        st.metric("Queda Tens.", f"{dif_v:.2f} V")

    with res4:
        st.metric("Dif. RLA", f"{dif_i:.2f} A")
        if i_med > rla and rla > 0:
            st.markdown('<span class="sobrecarga">⚠️ SOBRECARGA</span>', unsafe_allow_html=True)
        st.caption(f"LRA Ref: {lra:.2f} A")

    with res5:
        st.write(f"Δ Comp: {cm_c - cn_c:.2f} µF")
        st.write(f"Δ Fan: {cm_f - cn_f:.2f} µF")

    st.markdown("---")
    st.subheader("3. Parecer Técnico")
    # Salva o texto diretamente no session_state para o PDF
    st.session_state.dados['laudo_diag'] = st.text_area(
        "Notas e Recomendações Técnicas:", 
        value=st.session_state.dados.get('laudo_diag', ''),
        key=f"laudo_text_{c}",
        placeholder="Descreva aqui o estado do sistema, vazamentos encontrados ou peças trocadas..."
    )

# ==============================================================================
# 3. FUNÇÃO DA ABA 3: ASSISTENTE DE CAMPO (IA E DIAGNÓSTICO)
# ==============================================================================

# ==============================================================================
# 3. FUNÇÃO DA ABA 3: ASSISTENTE DE CAMPO (IA E DIAGNÓSTICO)
# ==============================================================================

def renderizar_aba_ia_diagnostico():
    st.header("🕵️ Assistente de Campo: Diagnóstico Dinâmico")
    
    # --- RESGATE DOS DADOS DA ABA 2 (VIA SESSION STATE) ---
    sh = st.session_state.get('sh_val', 0.0)
    sc = st.session_state.get('sc_val', 0.0)
    i_med = st.session_state.get('im_val', 0.0)
    rla = st.session_state.get('rla_val', 0.0)

    # Painel de Monitoramento Rápido
    st.info(f"📊 **Dados Recebidos:** SH: {sh:.1f}K | SC: {sc:.1f}K | Corrente: {i_med}A")

    # ==========================================================================
    # 1. CHECKLIST DE CAMPO (PERGUNTAS DO ASSISTENTE)
    # ==========================================================================
    st.subheader("1. Verificações Físicas (Checklist)")
    c1, c2 = st.columns(2)
    
    with c1:
        vibracao = st.selectbox("Vibração no compressor?", ["Normal", "Leve", "Forte"], key="ia_vib")
        ruido = st.selectbox("Ruído mecânico?", ["Normal", "Metálico", "Sopro/Agudo"], key="ia_ruido")
        sujeira = st.selectbox("Limpeza da Serpentina?", ["Limpa", "Sujeira Leve", "Obstrução Grave"], key="ia_suj")

    with c2:
        ventilador = st.selectbox("Motor Ventilador?", ["Normal", "Lento", "Parado/Travado"], key="ia_fan")
        gelo = st.selectbox("Presença de Gelo?", ["Não", "Linha de Expansão", "Sucção/Compressor"], key="ia_gelo")
        oleo = st.selectbox("Vazamento de Óleo?", ["Não", "Conexões", "Base do Compressor"], key="ia_oleo")

    st.markdown("---")

    # ==========================================================================
    # 2. TABELA DE CAUSAS E CONTRAMEDIDAS (LÓGICA IA)
    # ==========================================================================
    st.subheader("2. Análise de Causas e Contramedidas")
    
    causas_ia = []

    # --- MOTOR DE DECISÃO (LOGICA CRUZADA) ---
    
    # Caso 1: Falta de Fluido
    if sh > 12 and (gelo == "Linha de Expansão" or oleo == "Conexões"):
        causas_ia.append({
            "Causa": "Vazamento / Carga Insuficiente",
            "Evidência": f"SH Alto ({sh}K) + Gelo/Óleo detectado",
            "Ação": "Localizar vazamento com nitrogênio e recompor carga por balança."
        })

    # Caso 2: Falha de Troca Térmica
    if sujeira == "Obstrução Grave" or ventilador == "Parado/Travado":
        causas_ia.append({
            "Causa": "Bloqueio de Condensação",
            "Evidência": "Checklist indica falha no fluxo de ar",
            "Ação": "Realizar limpeza química e testar capacitor do ventilador."
        })

    # Caso 3: Risco de Quebra Mecânica
    if i_med > rla and rla > 0:
        causas_ia.append({
            "Causa": "Sobrecarga Elétrica",
            "Evidência": f"Corrente ({i_med}A) acima do RLA ({rla}A)",
            "Ação": "Verificar tensão de rede e possível desgaste mecânico interno."
        })

    # EXIBIÇÃO FINAL
    if causas_ia:
        st.table(causas_ia)
    else:
        st.success("✅ Parâmetros normais. Continue o monitoramento.")

def renderizar_aba_ia_diagnostico():
    # Usando o contador global para reset de checklist
    c = st.session_state.count
    
    st.header("🕵️ Assistente de Campo: Diagnóstico Dinâmico")
    
    # --- RESGATE DOS DADOS DA ABA 2 (VIA SESSION STATE) ---
    # Importante: As chaves devem bater com as chaves definidas na Aba 2 (ex: ps_{c}, ts_{c})
    # Aqui fazemos o cálculo em tempo real para a IA processar
    fluido = st.session_state.get('dados', {}).get('fluido', 'R410A')
    
    # Pegamos os valores dos widgets da Aba 2 usando a key dinâmica
    p_suc = st.session_state.get(f"ps_{c}", 0.0)
    t_suc = st.session_state.get(f"ts_{c}", 0.0)
    rla = st.session_state.get(f"rla_{c}", 0.0)
    i_med = st.session_state.get(f"im_{c}", 0.0)

    # Recalculamos o SH para a IA (Fórmula assimilada da Aba 2)
    def f_sat_ia(p, g):
        if p <= 5: return 0.0
        if g == "R410A": return 0.253 * (p**0.8) - 18.5
        if g == "R32": return 0.245 * (p**0.81) - 19.0
        if g == "R22": return 0.415 * (p**0.72) - 19.8
        return 0.0

    t_sat_s = f_sat_ia(p_suc, fluido)
    sh = (t_suc - t_sat_s) if p_suc > 5 else 0.0

    # Painel de Monitoramento Rápido
    st.info(f"📊 **Monitoramento em Tempo Real:** SH: {sh:.1f}K | Corrente: {i_med}A | Fluido: {fluido}")

    # ==========================================================================
    # 1. CHECKLIST DE CAMPO (PERGUNTAS DO ASSISTENTE)
    # ==========================================================================
    st.subheader("1. Verificações Físicas (Checklist)")
    c1, c2 = st.columns(2)
    
    with c1:
        vibracao = st.selectbox("Vibração no compressor?", ["Normal", "Leve", "Forte"], key=f"ia_vib_{c}")
        ruido = st.selectbox("Ruído mecânico?", ["Normal", "Metálico", "Sopro/Agudo"], key=f"ia_ruido_{c}")
        sujeira = st.selectbox("Limpeza da Serpentina?", ["Limpa", "Sujeira Leve", "Obstrução Grave"], key=f"ia_suj_{c}")

    with c2:
        ventilador = st.selectbox("Motor Ventilador?", ["Normal", "Lento", "Parado/Travado"], key=f"ia_fan_{c}")
        gelo = st.selectbox("Presença de Gelo?", ["Não", "Linha de Expansão", "Sucção/Compressor"], key=f"ia_gelo_{c}")
        oleo = st.selectbox("Vazamento de Óleo?", ["Não", "Conexões", "Base do Compressor"], key=f"ia_oleo_{c}")

    st.markdown("---")

    # ==========================================================================
    # 2. TABELA DE CAUSAS E CONTRAMEDIDAS (LÓGICA IA)
    # ==========================================================================
    st.subheader("2. Análise de Causas e Contramedidas")
    
    causas_ia = []

    # --- MOTOR DE DECISÃO (LOGICA CRUZADA ASSIMILADA) ---
    
    # Caso 1: Falta de Fluido (Superaquecimento Alto + Sintomas Físicos)
    if sh > 12 and (gelo == "Linha de Expansão" or oleo == "Conexões"):
        causas_ia.append({
            "Causa": "⚠️ Vazamento / Carga Insuficiente",
            "Evidência": f"SH Elevado ({sh:.1f}K) + Gelo/Óleo detectado.",
            "Ação": "Realizar teste de estanqueidade com Nitrogênio e carga por balança."
        })

    # Caso 2: Falha de Troca Térmica (Sujeira ou Fan)
    if sujeira == "Obstrução Grave" or ventilador == "Parado/Travado":
        causas_ia.append({
            "Causa": "🚨 Bloqueio de Condensação / Evaporação",
            "Evidência": "Checklist indica obstrução física ou falha mecânica no ventilador.",
            "Ação": "Limpeza química das serpentinas e verificação do capacitor do motor fan."
        })

    # Caso 3: Risco de Quebra Mecânica (Amperagem)
    if i_med > rla and rla > 0:
        causas_ia.append({
            "Causa": "⚡ Sobrecarga Elétrica (Compressor)",
            "Evidência": f"Corrente Medida ({i_med}A) acima do RLA nominal ({rla}A).",
            "Ação": "Verificar queda de tensão, capacitores de partida e possível desgaste interno."
        })

    # Caso 4: SH Baixo (Risco de Líquido)
    if sh < 5 and p_suc > 10:
        causas_ia.append({
            "Causa": "🌊 Risco de Golpe de Líquido",
            "Evidência": f"Superaquecimento muito baixo ({sh:.1f}K). Líquido retornando ao compressor.",
            "Ação": "Verificar se há excesso de carga ou motor ventilador da evaporadora lento."
        })

    # EXIBIÇÃO FINAL
    if causas_ia:
        st.table(causas_ia)
        # Salva o diagnóstico para o relatório PDF
        st.session_state.dados['diagnostico_ia'] = str(causas_ia)
    else:
        st.success("✅ Parâmetros dentro da normalidade técnica para este fluido. Continue o monitoramento.")

# ==============================================================================
# 4. SIDEBAR - DADOS DO TÉCNICO E NAVEGAÇÃO
# ==============================================================================
with st.sidebar:
    st.title("🚀 Painel de Controle")
    
    # Pegamos o contador global para evitar conflitos de ID
    c = st.session_state.count

    # A. NAVEGAÇÃO E EXIBIÇÃO DAS ABAS
    opcoes_abas = ["Home", "1. Cadastro", "2. Diagnósticos", "3. Assistente de Campo", "Relatórios"]
    
    # Chave dinâmica para o rádio para evitar travamento na navegação
    aba_selecionada = st.radio("Selecione a Aba:", opcoes_abas, key=f"nav_radio_{c}")
    
    st.markdown("---")
    
    # B. DADOS DO TÉCNICO RESPONSÁVEL (Preservados no Reset)
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'], key=f"tec_nom_{c}")
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ Técnico:", value=st.session_state.dados['tecnico_documento'], key=f"tec_doc_{c}")
    st.session_state.dados['tecnico_registro'] = st.text_input("Inscrição (CFT/CREA):", value=st.session_state.dados['tecnico_registro'], key=f"tec_reg_{c}")
    
    st.markdown("---")
    
    # VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS
    # Verificamos se Nome e WhatsApp foram preenchidos para liberar o envio
    cliente_ok = st.session_state.dados.get('nome')
    zap_ok = st.session_state.dados.get('whatsapp')

    if not cliente_ok or not zap_ok:
        st.error("📋 STATUS: PENDENTE (Preencha Cliente e WhatsApp)")
    else:
        st.success("📋 STATUS: PRONTO PARA ENVIO")
        
        # MENSAGEM WHATSAPP - ESTRUTURA ORGANIZADA (UTF-8)
        msg_zap = (
            f"*LAUDO TÉCNICO HVAC*\n\n"
            f"👤 *CLIENTE:* {st.session_state.dados['nome']}\n"
            f"🆔 CPF/CNPJ: {st.session_state.dados['cpf_cnpj']}\n"
            f"📍 END: {st.session_state.dados['endereco']}, {st.session_state.dados['numero']} - {st.session_state.dados['bairro']}\n"
            f"🏙️ {st.session_state.dados['cidade']}/{st.session_state.dados['uf']} | CEP: {st.session_state.dados['cep']}\n"
            f"📞 Contato: {st.session_state.dados['whatsapp']}\n\n"
            f"⚙️ *EQUIPAMENTO:*\n"
            f"📌 TAG: {st.session_state.dados['tag_id']} | Linha: {st.session_state.dados['linha']}\n"
            f"🏭 Fab: {st.session_state.dados['fabricante']} | Mod: {st.session_state.dados['modelo']}\n"
            f"❄️ Cap: {st.session_state.dados['capacidade']} BTU | Fluido: {st.session_state.dados['fluido']}\n"
            f"🛠️ Serviço: {st.session_state.dados['tipo_servico']}\n"
            f"🩺 Status: {st.session_state.dados['status_maquina']}\n\n"
            f"👨‍🔧 *TÉCNICO:* {st.session_state.dados['tecnico_nome']}\n"
            f"📜 Registro: {st.session_state.dados['tecnico_registro']}\n"
            f"📅 Data: {st.session_state.dados['data']}"
        )
        
        # Gerar link com tratamento de caracteres especiais (urllib.parse.quote)
        texto_url = urllib.parse.quote(msg_zap)
        # Limpamos o WhatsApp de caracteres não numéricos para o link wa.me
        zap_limpo = "".join(filter(str.isdigit, st.session_state.dados['whatsapp']))
        link_final = f"https://wa.me/55{zap_limpo}?text={texto_url}"
        
        st.link_button("📲 Enviar Laudo via WhatsApp", link_final, use_container_width=True)

    st.markdown("---")
    
    # LIMPAR FORMULÁRIO (HARD RESET SEM APAGAR O TÉCNICO)
    # Adicionada key única para evitar DuplicateElementId
    if st.button("🗑️ Limpar Formulário", key=f"btn_reset_{c}", use_container_width=True):
        chaves_preservar = ['tecnico_nome', 'tecnico_documento', 'tecnico_registro', 'data']
        
        # Resetamos o dicionário de dados
        for key in list(st.session_state.dados.keys()):
            if key not in chaves_preservar:
                # Valores padrão para chaves específicas
                if key == 'fluido': st.session_state.dados[key] = "R410A"
                elif key == 'fabricante': st.session_state.dados[key] = "Carrier"
                elif key == 'status_maquina': st.session_state.dados[key] = "🟢 Operacional"
                else: st.session_state.dados[key] = ""
        
        # O PULO DO GATO: Incrementa o contador para forçar o Streamlit a redesenhar os widgets
        st.session_state.count += 1
        st.rerun()

# ==============================================================================
# 5. LÓGICA DE EXIBIÇÃO DAS ABAS (ATIVADA)
# ==============================================================================

import streamlit as st
import requests
import urllib.parse
import os
from datetime import datetime

# 1. CONFIGURAÇÃO E ESTILO
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

st.markdown("""
    <style>
    .stTextInput>div>div>input[aria-label="Data da Visita:"] { background-color: #e0f2f1 !important; color: #004d40 !important; font-weight: bold; }
    div.stLinkButton > a { background-color: #25D366 !important; color: white !important; font-weight: bold; border-radius: 8px !important; }
    .sh-critico { background-color: #ff1744; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
    .sobrecarga { color: #d32f2f; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. MOTOR DE SESSÃO
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"), 'cep': '', 'endereco': '', 'bairro': '', 
        'cidade': '', 'uf': '', 'numero': '', 'complemento': '', 'fabricante': 'Carrier', 
        'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial', 'serie_evap': '', 
        'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional', 'laudo_diag': ''
    }

if 'count' not in st.session_state:
    st.session_state.count = 0

LISTA_FLUIDOS = ["R410A", "R134a", "R22", "R32", "R290"]

# 3. FUNÇÕES TÉCNICAS
def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, str(cep)))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
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

# 4. INTERFACE DAS ABAS
def renderizar_aba_1():
    c = st.session_state.count
    st.header("📋 Cadastro de Cliente e Equipamento")
    with st.expander("👤 Identificação", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome/Razão Social *", value=st.session_state.dados['nome'], key=f"n_{c}")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF/CNPJ", value=st.session_state.dados['cpf_cnpj'], key=f"d_{c}")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp *", value=st.session_state.dados['whatsapp'], key=f"w_{c}")
        
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_in = ce1.text_input("CEP *", value=st.session_state.dados['cep'], key=f"cep_{c}")
        if cep_in != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_in
            if buscar_cep(cep_in): st.rerun()
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro", value=st.session_state.dados['endereco'], key=f"ed_{c}")
        st.session_state.dados['numero'] = ce3.text_input("Nº", value=st.session_state.dados['numero'], key=f"num_{c}")

    with st.expander("⚙️ Equipamento", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante", ["Carrier", "Daikin", "LG", "Samsung", "Trane", "York", "Elgin", "Gree"], key=f"f_{c}")
            st.session_state.dados['fluido'] = st.selectbox("Fluido", LISTA_FLUIDOS, key=f"fl_{c}")
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Série EVAP", value=st.session_state.dados['serie_evap'], key=f"se_{c}")
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade", ["9.000", "12.000", "18.000", "24.000", "36.000", "60.000"], key=f"cap_{c}")
        with e3:
            st.session_state.dados['tag_id'] = st.text_input("TAG/ID", value=st.session_state.dados['tag_id'], key=f"tg_{c}")
            st.session_state.dados['status_maquina'] = st.radio("Status", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True, key=f"st_{c}")

def renderizar_aba_2():
    c = st.session_state.count
    st.header("🔍 Diagnóstico Técnico")
    fluido = st.session_state.dados['fluido']
    c1, c2, c3 = st.columns(3)
    with c1:
        ps = st.number_input("P. Sucção (PSI)", key=f"ps_{c}")
        ts = st.number_input("T. Sucção (°C)", key=f"ts_{c}")
    with c2:
        rla = st.number_input("RLA (A)", key=f"rla_{c}")
        im = st.number_input("Corr. Medida (A)", key=f"im_{c}")
    with c3:
        tr = st.number_input("T. Retorno (°C)", key=f"tr_{c}")
        ti = st.number_input("T. Insuflamento (°C)", key=f"ti_{c}")

    sh = ts - f_sat(ps, fluido) if ps > 5 else 0.0
    dt = tr - ti
    st.metric("Superaquecimento", f"{sh:.2f} K")
    st.metric("ΔT Ar", f"{dt:.2f} °C")
    if sh < 5 and ps > 5: st.error("⚠️ RISCO DE GOLPE DE LÍQUIDO")
    st.session_state.dados['laudo_diag'] = st.text_area("Parecer:", value=st.session_state.dados['laudo_diag'], key=f"lt_{c}")

def renderizar_aba_3():
    c = st.session_state.count
    st.header("🕵️ Assistente de Campo IA")
    vibracao = st.selectbox("Vibração?", ["Normal", "Leve", "Forte"], key=f"ia_v_{c}")
    sujeira = st.selectbox("Serpentina?", ["Limpa", "Obstruída"], key=f"ia_s_{c}")
    if sujeira == "Obstruída": st.warning("Ação: Realizar limpeza química imediata.")
    else: st.success("Fluxo de ar normal.")

# 5. SIDEBAR E LOGICA PRINCIPAL
with st.sidebar:
    st.title("REFRI_PRO")
    menu = st.radio("Navegação", ["Home", "1. Cadastro", "2. Diagnóstico", "3. Assistente", "5. Relatórios"])
    st.markdown("---")
    st.session_state.dados['tecnico_nome'] = st.text_input("Técnico:", value=st.session_state.dados['tecnico_nome'])
    if st.button("🗑️ LIMPAR FORMULÁRIO", use_container_width=True):
        for k in st.session_state.dados:
            if k != 'tecnico_nome': st.session_state.dados[k] = ""
        st.session_state.count += 1
        st.rerun()

if menu == "Home":
    st.title("MPN Soluções")
    st.image("logo.png") if os.path.exists("logo.png") else st.info("Bem-vindo")
elif menu == "1. Cadastro": renderizar_aba_1()
elif menu == "2. Diagnóstico": renderizar_aba_2()
elif menu == "3. Assistente": renderizar_aba_3()
elif menu == "5. Relatórios":
    st.header("📊 Relatórios")
    st.write("Pronto para gerar PDF.")

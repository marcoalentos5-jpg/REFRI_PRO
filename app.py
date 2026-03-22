# ==============================================================================
# 0. FUNÇÃO DE TRAVA (MOTOR DO GÁS) - COLOQUE FORA DA FUNÇÃO renderizar_aba_1
# ==============================================================================
def trava_gas_callback():
    """Esta função impede que o gás mude sozinho ao trocar de aba"""
    # Pega o que o técnico selecionou agora
    gas_novo = st.session_state.campo_fluido_v2
    
    # Atualiza o banco de dados principal
    st.session_state.dados['fluido'] = gas_novo
    st.session_state.fluido_travado = gas_novo
    
    # Injeta as pressões na Aba 2 automaticamente apenas na troca
    if gas_novo == "R22":
        st.session_state.ps_v17 = 70.0
        st.session_state.pd_v17 = 210.0
    else:
        st.session_state.ps_v17 = 134.0
        st.session_state.pd_v17 = 340.0

# ==============================================================================
# 1. FUNÇÃO DA ABA 1: Identificação e Equipamento (VERSÃO BLINDADA)
# ==============================================================================
def renderizar_aba_1():
    tabs = st.tabs(["📋 Identificação e Equipamento"])
    tab1 = tabs[0]

    with tab1:
        # --- SEÇÃO CLIENTE (PRESERVADA) ---
        with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key="cli_nome_v2")
            st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF (000.000.000-00)", value=st.session_state.dados['cpf_cnpj'], key="cli_doc_v2")
            st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (XX-X-XXXX-XXXX) *", value=st.session_state.dados['whatsapp'], key="cli_zap_v2")

            cx1, cx2, cx3 = st.columns([1, 1, 2])
            st.session_state.dados['celular'] = cx1.text_input("Cel. (XX-X-XXXX-XXXX):", value=st.session_state.dados['celular'], key="cli_cel_v2")
            st.session_state.dados['tel_fixo'] = cx2.text_input("Fixo (XX-XXXX-XXXX):", value=st.session_state.dados['tel_fixo'], key="cli_tel_v2")
            st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'], key="cli_email_v2")

            st.markdown("---")
            ce1, ce2, ce3 = st.columns([1, 2, 1])
            st.session_state.dados['cep'] = ce1.text_input("CEP *", value=st.session_state.dados['cep'], key="cli_cep_v2")
            st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'], key="cli_end_v2")
            st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'], key="cli_num_v2")

        # --- SEÇÃO EQUIPAMENTO ---
        st.subheader("⚙️ Especificações do Equipamento")
        
        with st.expander("Detalhes Técnicos do Ativo", expanded=True):
            e1, e2, e3 = st.columns(3)
            with e1:
                fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
                # Busca o índice do fabricante já salvo para não resetar
                f_atual = st.session_state.dados.get('fabricante', 'Carrier')
                f_idx = fab_list.index(f_atual) if f_atual in fab_list else 0
                st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=f_idx, key="sel_fab_v2")
                st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'], key="in_mod_v2")

            with e2:
                st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'], key="in_sevap_v2")
                st.session_state.dados['local_evap'] = st.text_input("Local da Evaporadora:", value=st.session_state.dados['local_evap'], key="in_levap_v2")

            with e3:
                # --- O CAMPO QUE ESTAVA DANDO ERRO CORRIGIDO AQUI ---
                lista_fluidos = ["R410A", "R134a", "R22", "R32", "R290"]
                # Pega o que está na memória
                fluido_na_memoria = st.session_state.dados.get('fluido', 'R410A')
                idx_fluido = lista_fluidos.index(fluido_na_memoria) if fluido_na_memoria in lista_fluidos else 0
                
                st.selectbox(
                    "Fluido:", 
                    lista_fluidos, 
                    index=idx_fluido,
                    key="campo_fluido_v2", 
                    on_change=trava_gas_callback # Só altera se o técnico mexer!
                )
                
                st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'], key="in_tag_v2")

        # --- BOTÃO DISCRETO NO FIM DA PÁGINA ---
        st.markdown("---")
        c_vazia, c_btn = st.columns([3, 1])
        with c_btn:
            if st.button("✅ Confirmar Dados", use_container_width=True):
                trava_gas_callback() # Garante a sincronia final
                st.toast("Dados do equipamento travados!", icon="✅")
# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO V11.9 - PROTOCOLO ANTI-RESET)
# ==============================================================================

import streamlit as st
import math

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico (Precisão V18.9)")
    
    # 1. Recupera o fluido da Página 1
    if 'dados' not in st.session_state:
        st.session_state.dados = {'fluido': 'R410A'}
    
    fluido = st.session_state.dados.get('fluido', 'R410A')

    # --- CSS: ESTILO HI-VIS (MANTIDO INTEGRALMENTE) ---
    st.markdown("""
        <style>
        .res-card { 
            background-color: #ffffff; padding: 15px; border-radius: 10px; 
            text-align: center; min-height: 150px;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
            display: flex; flex-direction: column; justify-content: center;
            border-top: 6px solid #1b5e20; 
        }
        .label-res { font-size: 14px; font-weight: 800; color: #333; text-transform: uppercase; margin-bottom: 8px; }
        .valor-res { font-size: 28px; font-weight: 900; color: #1b5e20; margin: 2px 0; }
        .sub-res { font-size: 13px; color: #d32f2f; font-weight: 700; border-top: 2px dotted #eee; padding-top: 8px; margin-top: 5px; }
        .card-bom { border-top-color: #81c784 !important; }
        .card-alerta { border-top-color: #fff176 !important; }
        .card-critico { border-top-color: #e57373 !important; }
        .card-alerta .valor-res { color: #fbc02d !important; }
        .card-critico .valor-res { color: #d32f2f !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- ESTRATÉGIA DE TRAVAMENTO DE MEMÓRIA (O PULO DO GATO) ---
    # Inicializamos as chaves no session_state APENAS SE elas não existirem.
    # Note que NÃO passamos o 'value' dentro do st.number_input abaixo.
    
    config_inicial = {
        "tr_v17": 24.0, "ti_v17": 12.0, "ts_v17": 14.0, "tl_v17": 38.0,
        "vl_v17": 220.0, "vm_v17": 218.0, "rla_v17": 10.0, "im_v17": 9.5,
        "cnc_v17": 35.0, "cmc_v17": 33.0
    }

    for k, v in config_inicial.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Tratamento especial para pressões (sugestão inicial por fluido)
    if "ps_v17" not in st.session_state:
        st.session_state.ps_v17 = 70.0 if fluido == "R22" else 134.0
    if "pd_v17" not in st.session_state:
        st.session_state.pd_v17 = 210.0 if fluido == "R22" else 340.0

    # --- 1. MEDIÇÕES DE CAMPO (6 COLUNAS) ---
    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.markdown("🟢 **AR**")
        t_ret = st.number_input("T. Retorno (°C)", step=0.1, key="tr_v17")
        t_ins = st.number_input("T. Insuf. (°C)", step=0.1, key="ti_v17")
    
    with c2:
        st.markdown("🔵 **EVAPORADORA**")
        p_suc = st.number_input("P. Sucção (PSI)", format="%.1f", key="ps_v17")
        t_suc = st.number_input("T. Tubo Suc. (°C)", format="%.1f", key="ts_v17")
    
    with c3:
        st.markdown("🔴 **CONDENSADORA**")
        p_des = st.number_input("P. Desc. (PSI)", format="%.1f", key="pd_v17")
        t_liq = st.number_input("T. Tubo Líq. (°C)", format="%.1f", key="tl_v17")
    
    with c4:
        st.markdown("⚡ **TENSÃO**")
        v_lin = st.number_input("Tens. Linha (V)", key="vl_v17")
        v_med = st.number_input("Tens. Medida (V)", key="vm_v17")
    
    with c5:
        st.markdown("🔌 **CORRENTE**")
        rla = st.number_input("RLA (A)", key="rla_v17")
        i_med = st.number_input("Corr. Medida (A)", key="im_v17")
    
    with c6:
        st.markdown("🔋 **CAPACIT.**")
        cn_c = st.number_input("Nominal (µF)", key="cnc_v17")
        cm_c = st.number_input("Medida (µF)", key="cmc_v17")

    # --- MOTOR V30.1: MATRIZ DE ALTA PRECISÃO ---
    def f_sat_v17(psi, gas):
        if psi <= 5: return 0.0
        if gas == "R32":
            tsat = (0.000305 * (psi**2)) + (0.1572 * psi) - 19.64
        elif gas == "R22":
            tsat = (0.000035 * (psi**3)) - (0.0064 * (psi**2)) + (0.435 * psi) - 13.9
        else: # R410A
            tsat = (0.000285 * (psi**2)) + (0.15735 * psi) - 18.88
        return round(tsat, 2)

    # Cálculos dinâmicos (acontecem em tempo real conforme digitação)
    ts_s = f_sat_v17(p_suc, fluido)
    ts_d = f_sat_v17(p_des, fluido)
    sh, sc, dt_ar = round(t_suc - ts_s, 2), round(ts_d - t_liq, 2), round(t_ret - t_ins, 1)

    # --- 2. RESULTADOS DO DIAGNÓSTICO (6 COLUNAS) ---
    st.markdown("---")
    st.subheader("2. Resultados do Diagnóstico")
    res_cols = st.columns(6)

    with res_cols[0]:
        st.markdown(f'<div class="res-card card-bom"><div class="label-res">ΔT Ar</div><div class="valor-res">{dt_ar} °C</div><div class="sub-res">Troca</div></div>', unsafe_allow_html=True)
    
    cl_sh = "card-bom" if (5.0 <= sh <= 12.0) else "card-critico"
    if fluido == "R32" and (sh < 5.5 or sh > 7.5): cl_sh = "card-alerta"

    with res_cols[1]:
        st.markdown(f'<div class="res-card {cl_sh}"><div class="label-res">SH Total</div><div class="valor-res">{sh} K</div><div class="sub-res">Sat: {ts_s}°C</div></div>', unsafe_allow_html=True)
    with res_cols[2]:
        st.markdown(f'<div class="res-card card-bom"><div class="label-res">SC Final</div><div class="valor-res">{sc} K</div><div class="sub-res">Sat: {ts_d}°C</div></div>', unsafe_allow_html=True)
    with res_cols[3]:
        st.markdown(f'<div class="res-card card-bom"><div class="label-res">Δ Tens.</div><div class="valor-res">{round(v_lin-v_med,1)} V</div><div class="sub-res">Estável</div></div>', unsafe_allow_html=True)
    with res_cols[4]:
        st.markdown(f'<div class="res-card card-bom"><div class="label-res">Δ RLA</div><div class="valor-res">{round(i_med-rla,2)} A</div><div class="sub-res">Carga</div></div>', unsafe_allow_html=True)
    with res_cols[5]:
        st.markdown(f'<div class="res-card card-bom"><div class="label-res">Δ Cap.</div><div class="valor-res">{round(cm_c-cn_c,1)} µF</div><div class="sub-res">Saúde</div></div>', unsafe_allow_html=True)

    # --- 3. DIAGNÓSTICO INTELIGENTE (ESTÉTICA PREVISTA) ---
    diag_final, bg_diag = "✅ Sistema Operacional em Conformidade", "#81c784"
    
    if fluido == "R22":
        if p_suc < 50.0 or p_suc > 85.0: diag_final, bg_diag = "⚠️ ALERTA: Pressão fora dos padrões R22!", "#fff176"
    else:
        if p_suc <= 110.0 or p_suc >= 150.0:
            diag_final, bg_diag = "⚠️ Pressão Crítica!", "#fff176"

    st.markdown(f'<div style="background-color: {bg_diag}; padding: 18px; border-radius: 10px; color: #000; text-align: center; font-weight: 800; font-size: 18px; margin-top: 20px; border: 1px solid rgba(0,0,0,0.1);">{diag_final}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("3. Parecer Técnico")
    st.text_area("Notas Adicionais:", key="laudo_v17_final", height=100)

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

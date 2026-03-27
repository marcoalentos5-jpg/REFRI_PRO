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
        border: none !important;
        padding: 0.5rem 1rem !important;
        text-decoration: none !important;
        display: inline-block !important;
    }
    /* Estilização para manter o padrão visual do Código Mestre */
    .main { background-color: #f8f9fa; }
    .stTextInput>div>div>input { background-color: #ffffff !important; }
    .stSelectbox>div>div>div { background-color: #ffffff !important; }
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
        'status_maquina': '🟢 Operacional', 'tipo_oleo': 'POE', 'frequencia': 'Inverter',
        'potencia': '', 'carga_gas': '', 'tensao': '220V/1F', 'ultima_maint': datetime.now().strftime("%d/%m/%Y")
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

    # --- SEÇÃO EQUIPAMENTO (ESTRUTURA ÚNICA) ---
    st.markdown("### ⚙️ Especificações do Equipamento")
    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        l1_c1, l1_c2, l1_c3 = st.columns(3)
        with l1_c1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea", "Outro"])
            f_idx = fab_list.index(d['fabricante']) if d['fabricante'] in fab_list else 0
            d['fabricante'] = st.selectbox("Fabricante:", fab_list, index=f_idx, key="eq_f")
        with l1_c2:
            d['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=d.get('serie_evap', ''), key="eq_se")
        with l1_c3:
            d['capacidade'] = st.text_input("Capacidade (BTU/TR):", value=d.get('capacidade', '12.000'), key="eq_ca")

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
    tabelas = {
        "R410A": {"xp": [5, 50, 90, 122, 150, 350, 550], "fp": [-50, -18, -3.5, 5.5, 11.5, 41.5, 64.5]},
        "R32": {"xp": [5, 50, 90, 140, 200, 480, 580], "fp": [-50, -19.5, -3.6, 8.5, 19.8, 56.5, 66.8]},
        "R22": {"xp": [5, 30, 60, 100, 200, 320], "fp": [-50, -15.2, 1.5, 16.5, 38.5, 58.5]},
        "R134a": {"xp": [5, 15, 30, 70, 150, 250], "fp": [-50, -15.5, 1.5, 27.5, 53, 76.2]},
        "R290": {"xp": [5, 20, 65, 100, 150, 250], "fp": [-50, -25.5, 3.5, 17.5, 32.5, 55.2]}
    }
    if g not in tabelas: return 0.0
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
        lra = st.number_input("LRA (A)", value=float(d.get('lra', 0.0)), key="lra_suprema_v1")
        rla = st.number_input("RLA (A)", value=float(d.get('rla', 0.0)), key="rla_suprema_v1")
        i_med = st.number_input("Corr. Medida (A)", value=float(d.get('i_medida', 0.0)), key="im_suprema_v1")
        perc_calc = (i_med / rla * 100) if rla > 0 else 0.0
        st.metric("Carga do Comp. (%)", f"{perc_calc:.1f}%")

    with c4:
        st.markdown("**🔋 CAPACITORES (µF)**")
        cn_c = st.number_input("C. Nom. Comp", value=float(d.get('cn_c', 0.0)), key="cnc_suprema_v1")
        cn_f = st.number_input("C. Nom. Fan", value=float(d.get('cn_f', 0.0)), key="cnf_suprema_v1")
        cm_c = st.number_input("C. Lido Comp", value=float(d.get('cm_c', 0.0)), key="cmc_suprema_v1")
        cm_f = st.number_input("C. Lido Fan", value=float(d.get('cm_f', 0.0)), key="cmf_suprema_v1")

    # --- 2. PROCESSAMENTO TÉCNICO (TRAVA DE SEGURANÇA E CÁLCULOS) ---
    # Só calcula saturação se houver pressão real (> 5 PSI) usando a função f_sat_precisao definida anteriormente
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
    else:
        diag_previsto = "Análise: Sistema operando dentro dos parâmetros normais."

    # Campo Único de Laudo - Integrado ao Session State
    # Usamos o valor existente ou o previsto se o campo estiver vazio
    laudo_atual = d.get('laudo_diag', '')
    d['laudo_diag'] = st.text_area(
        "Diagnóstico e Observações:", 
        value=laudo_atual if laudo_atual else diag_previsto, 
        height=150, 
        key="txt_laudo_suprema_v1"
    )

    # Sincroniza dados de medição de volta para o estado global para persistência entre abas
    d.update({
        'p_baixa': p_suc, 'temp_sucção': t_suc,
        'p_alta': p_des, 'temp_liquido': t_liq,
        'temp_entrada_ar': t_ret, 'temp_saida_ar': t_ins,
        'lra': lra, 'rla': rla, 'i_medida': i_med,
        'cn_c': cn_c, 'cn_f': cn_f, 'cm_c': cm_c, 'cm_f': cm_f
    })

# ==============================================================================
# 3. SIDEBAR - DADOS DO TÉCNICO E NAVEGAÇÃO (ATIVADA ANTES DA EXIBIÇÃO)
# ==============================================================================
with st.sidebar:
    st.title("🚀 Painel de Controle")

    # A. NAVEGAÇÃO E EXIBIÇÃO DAS ABAS
    opcoes_abas = ["Home", "1. Cadastro de Equipamentos", "2. Diagnósticos", "Relatórios"]
    aba_selecionada = st.radio("Selecione a Aba:", opcoes_abas, key="nav_sidebar_v1")
    
    st.markdown("---")
    
    # B. DADOS DO TÉCNICO RESPONSÁVEL
    st.subheader("👤 Técnico Responsável")
    
    st.session_state.dados['tecnico_nome'] = st.text_input(
        "Nome:", 
        value=st.session_state.dados.get('tecnico_nome', 'Marcos Alexandre'), 
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
    st.info(f"📅 Data: {st.session_state.dados.get('data')}")

# ==============================================================================
# 4. LÓGICA DE RENDERIZAÇÃO DAS ABAS
# ==============================================================================
if aba_selecionada == "Home":
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Tenta carregar logo se existir, senão usa placeholder
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        st.markdown(f"""
            <div style='text-align: center;'>
                <h1 style='color: #0d47a1;'>MPN Soluções</h1>
                <p style='color: #1976d2; font-size: 1.2em;'>Sistema HVAC Pro - Gestão Inteligente</p>
                <hr style='width: 50%; margin: auto;'>
                <p style='font-size: 0.9em; color: #666;'>Bem-vindo, {st.session_state.dados['tecnico_nome']}</p>
            </div>
        """, unsafe_allow_html=True)

elif aba_selecionada == "1. Cadastro de Equipamentos":
    renderizar_aba_1()

elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos()

elif aba_selecionada == "Relatórios":
    st.header("📝 Resumo e Envio de Laudo")
    d = st.session_state.dados

    # 1. VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS
    if not d.get('nome') or not d.get('whatsapp'):
        st.warning("⚠️ STATUS: PENDENTE")
        st.error("Preencha o Nome do Cliente e o WhatsApp na Aba '1. Cadastro' para liberar o envio.")
    else:
        st.success("✅ STATUS: PRONTO PARA ENVIO")
        
        # 2. MONTAGEM DA MENSAGEM (ESTRUTURA PROFISSIONAL)
        msg_zap = (
            f"*LAUDO TÉCNICO HVAC - MPN SOLUÇÕES*\n\n"
            f"👤 *CLIENTE:* {d.get('nome', '')}\n"
            f"📍 *END:* {d.get('endereco', '')}, {d.get('numero', '')}\n"
            f"🏙️ {d.get('cidade', '')}/{d.get('uf', '')}\n"
            f"📞 *WhatsApp:* {d.get('whatsapp', '')}\n\n"
            f"⚙️ *EQUIPAMENTO:*\n"
            f"📌 TAG: {d.get('tag_id', 'N/A')}\n"
            f"🏢 Fab: {d.get('fabricante', '')} | Mod: {d.get('modelo', '')}\n"
            f"❄️ Fluido: {d.get('fluido', '')}\n\n"
            f"🩺 *DIAGNÓSTICO E PARECER:*\n"
            f"{d.get('laudo_diag', 'Análise técnica concluída sem observações adicionais.')}\n\n"
            f"👨‍🔧 *TÉCNICO RESPONSÁVEL:* {d.get('tecnico_nome', '')}\n"
            f"🆔 Registro: {d.get('tecnico_registro', 'Não informado')}\n"
            f"📅 *Data da Visita:* {d.get('data', '')}"
        )

        # 3. PRÉ-VISUALIZAÇÃO DO TEXTO
        with st.expander("👁️ Pré-visualização da Mensagem", expanded=True):
            st.code(msg_zap, language=None)

        # 4. GERAÇÃO DO LINK E BOTÃO DE ENVIO
        whatsapp_number = "".join(filter(str.isdigit, d.get('whatsapp', '')))
        texto_url = urllib.parse.quote(msg_zap)
        link_final = f"https://wa.me/55{whatsapp_number}?text={texto_url}"
        
        st.link_button("📲 Enviar Laudo para o WhatsApp do Cliente", link_final, use_container_width=True)

    st.markdown("---")

    # 5. BOTÃO DE LIMPEZA COM PRESERVAÇÃO
    if st.button("🗑️ Limpar Todos os Dados (Novo Atendimento)", use_container_width=True):
        chaves_preservadas = ['tecnico_nome', 'tecnico_documento', 'tecnico_registro', 'data']
        for chave in list(st.session_state.dados.keys()):
            if chave not in chaves_preservadas:
                # Reseta para string vazia ou valor padrão conforme o tipo original
                if isinstance(st.session_state.dados[chave], bool):
                    st.session_state.dados[chave] = False
                elif isinstance(st.session_state.dados[chave], (int, float)):
                    st.session_state.dados[chave] = 0.0
                else:
                    st.session_state.dados[chave] = ""
        
        st.toast("Formulário resetado! Dados do técnico preservados.", icon="🧹")
        st.rerun()

# ==============================================================================
# 4. LÓGICA DE EXIBIÇÃO DAS ABAS (ATIVADA)
# ==============================================================================
if aba_selecionada == "Home":
    # --- NOVA APRESENTAÇÃO DA ABA HOME (COM LOGO MPN SOLUÇÕES) ---
    st.markdown("<br>", unsafe_allow_html=True) 

    # 1. CENTRALIZAÇÃO E EXIBIÇÃO DA LOGOMARCA
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2: 
        NOME_ARQUIVO_LOGO = "logo.png"
        
        # VERIFICAÇÃO ADICIONAL DO ARQUIVO NO DISCO
        if os.path.exists(NOME_ARQUIVO_LOGO):
            try:
                st.image(NOME_ARQUIVO_LOGO, use_container_width=True) 
            except Exception as e:
                st.error(f"⚠️ Erro ao tentar abrir a imagem '{NOME_ARQUIVO_LOGO}'. Verifique se o arquivo está corrompido.")
                st.write(f"Detalhes: {e}")
        else:
            st.error(f"⚠️ Erro: Arquivo '{NOME_ARQUIVO_LOGO}' não encontrado na pasta raiz.")
            st.info("Verifique se o nome do arquivo é EXATAMENTE 'logo.png'.")

    st.markdown("<br><br>", unsafe_allow_html=True) 

    # 2. TÍTULO E BOAS-VINDAS CENTRALIZADOS
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

elif aba_selecionada == "1. Cadastro de Equipamentos":
    renderizar_aba_1() 

elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos() 

elif aba_selecionada == "Relatórios":
    # Aqui entra a lógica de Relatórios que enviamos no bloco anterior
    st.header("📝 Resumo e Envio de Laudo")
    d = st.session_state.dados
    if not d.get('nome') or not d.get('whatsapp'):
        st.error("📋 STATUS: PENDENTE (Preencha Cliente e WhatsApp na Aba Cadastro)")
    else:
        st.success("📋 STATUS: PRONTO PARA ENVIO")
        # Link do WhatsApp e botão de envio ficariam aqui

# ==============================================================================
# 5. FUNÇÕES DE RENDERIZAÇÃO (RECONSTRUÇÃO DA ABA DIAGNÓSTICOS)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    d = st.session_state.dados
    fluido_selecionado = d.get('fluido', 'R410A')
    st.info(f"❄️ Fluido Refrigerante em Análise: **{fluido_selecionado}**")
    st.markdown("---")

    # --- BLOCO 1: ENTRADA DE MEDIÇÕES ---
    st.subheader("1. Medições de Campo")
    col_suc, col_des = st.columns(2)
    
    with col_suc:
        st.markdown("### 🔵 Baixa Pressão")
        pres_suc = st.number_input("Pressão de Sucção (PSI):", min_value=0.0, step=1.0, key="p_suc_diag", value=float(d.get('p_baixa', 0.0)))
        temp_suc = st.number_input("Temp. Tubulação Sucção (°C):", step=0.1, key="t_suc_diag", value=float(d.get('temp_sucção', 0.0)))

    with col_des:
        st.markdown("### 🔴 Alta Pressão")
        pres_des = st.number_input("Pressão de Descarga (PSI):", min_value=0.0, step=1.0, key="p_des_diag", value=float(d.get('p_alta', 0.0)))
        temp_liq = st.number_input("Temp. Tubulação Líquido (°C):", step=0.1, key="t_liq_diag", value=float(d.get('temp_liquido', 0.0)))

    # --- BLOCO 2: PROCESSAMENTO (CÁLCULOS PT) ---
    # Chamada da função de saturação definida no início do código
    t_sat_suc = f_sat_precisao(pres_suc, fluido_selecionado)
    t_sat_des = f_sat_precisao(pres_des, fluido_selecionado)
    
    sh = round(temp_suc - t_sat_suc, 2) if t_sat_suc != -50.0 else 0.0
    sc = round(t_sat_des - temp_liq, 2) if t_sat_des != -50.0 else 0.0

    # --- BLOCO 3: EXIBIÇÃO DE RESULTADOS ---
    st.markdown("---")
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

    # --- BLOCO 4: CONCLUSÃO E LAUDO ---
    st.markdown("---")
    st.subheader("3. Parecer Técnico Final")
    d['laudo_diag'] = st.text_area(
        "Descreva o diagnóstico ou anomalias encontradas:",
        value=d.get('laudo_diag', ''),
        placeholder="Ex: Sistema operando com pressões estáveis...",
        key="laudo_area_diag"
    )
    
    # Sincronização dos dados lidos de volta para o session_state
    d['p_baixa'] = pres_suc
    d['temp_sucção'] = temp_suc
    d['p_alta'] = pres_des
    d['temp_liquido'] = temp_liq

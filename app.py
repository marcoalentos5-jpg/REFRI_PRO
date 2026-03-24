with st.sidebar:
    st.title("🚀 Painel REFRI_PRO")
    
    # ... seu rádio de navegação ...

    st.markdown("---")
    
    # Adicionamos uma KEY ÚNICA para o botão não duplicar no sistema
    if st.button("🗑️ Limpar Formulário", key="btn_limpar_principal", use_container_width=True):
        # 1. Reset do dicionário
        for chave in st.session_state.dados.keys():
            if chave == 'tecnico_nome': continue
            if chave == 'data': 
                st.session_state.dados[chave] = datetime.now().strftime("%d/%m/%Y")
                continue
            st.session_state.dados[chave] = "R410A" if chave == "fluido" else ("Carrier" if chave == "fabricante" else "")
        
        # 2. Incrementa o contador para resetar os widgets das abas
        st.session_state.count += 1
        st.rerun()

    # A. NAVEGAÇÃO E EXIBIÇÃO DAS ABAS (ATIVADA AQUI)
    opcoes_abas = ["Home", "1. Cadastro", "2. Diagnósticos", "3. Assistente de Campo", "Relatórios"]
    
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
    
    # Importante: urllib.parse deve estar no topo do arquivo (import urllib.parse)
    link_final = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar Laudo via WhatsApp", link_final, use_container_width=True)

    st.markdown("---")
    # LIMPAR FORMULÁRIO (PROTEGENDO DADOS DO TÉCNICO)

if st.sidebar.button("🗑️ Limpar Formulário", use_container_width=True):
    # Reset do dicionário mestre
    for chave in st.session_state.dados.keys():
        if chave == 'tecnico_nome': continue
        if chave == 'data': 
            st.session_state.dados[chave] = datetime.now().strftime("%d/%m/%Y")
            continue
        st.session_state.dados[chave] = "R410A" if chave == "fluido" else ("Carrier" if chave == "fabricante" else "")

    # Reset do cache dos widgets (Obrigatório para limpar a tela)
    for k in list(st.session_state.keys()):
        if k not in ['dados', 'tecnico_nome']:
            del st.session_state[k]
    
    st.rerun()

# ==============================================================================
# 5. LÓGICA DE EXIBIÇÃO DAS ABAS (ATIVADA)
# ==============================================================================

# Use a seleção do sidebar para chamar a função correta
if aba_selecionada == "Home":
    # --- APRESENTAÇÃO DA ABA HOME ---
    st.markdown("<br>", unsafe_allow_html=True) 

    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2: 
        NOME_ARQUIVO_LOGO = "logo.png"
        if os.path.exists(NOME_ARQUIVO_LOGO):
            try:
                st.image(NOME_ARQUIVO_LOGO, use_container_width=True) 
            except Exception as e:
                st.error(f"⚠️ Erro ao abrir a imagem: {e}")
        else:
            st.error(f"⚠️ Arquivo '{NOME_ARQUIVO_LOGO}' não encontrado.")

    st.markdown("<br><br>", unsafe_allow_html=True) 

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

elif aba_selecionada == "1. Cadastro":
    renderizar_aba_1() 

elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos() 

elif aba_selecionada == "3. Assistente de Campo":
    renderizar_aba_ia_diagnostico()

elif aba_selecionada == "Relatórios":
    st.header("📊 Página de Relatórios")
    st.write("Em breve: Visualização e exportação de relatórios.")


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

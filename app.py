    if st.button("Gerar Relatório PDF"):
        pdf = FPDF()
        pdf.add_page()
        
        # --- LOGOMARCA E CABEÇALHO ---
        if os.path.exists("logo.png"):
            pdf.image("logo.png", 10, 8, 33)
            pdf.set_x(45)
        
        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(0, 74, 153)
        pdf.cell(145, 10, "RELATÓRIO TÉCNICO DE ENGENHARIA", ln=True, align="R")
        pdf.ln(10)
        
        # --- 1. IDENTIFICAÇÃO DO CLIENTE ---
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 11)
        pdf.set_text_color(0)
        pdf.cell(190, 8, " 1. IDENTIFICAÇÃO DO CLIENTE", ln=True, fill=True)
        
        pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # LINHA ACIMA DO NOME (ORDEM PRIORITÁRIA)
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(85, 8, f"Cliente: {cliente}", border="B")
        
        # DATA EM DESTAQUE
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(225, 225, 225)
        pdf.cell(55, 8, f" DATA: {data_visita.strftime('%d/%m/%Y')} ", border=1, fill=True, align="C")
        
        # CNPJ/CPF DO CLIENTE
        pdf.set_font("Arial", "", 10)
        pdf.cell(50, 8, f"CNPJ/CPF: {doc_cliente}", border="B", ln=True, align="R")
        
        pdf.cell(190, 8, f"Endereço: {endereco}", border="B", ln=True)
        pdf.cell(95, 8, f"WhatsApp: {whatsapp}", border="B")
        pdf.cell(95, 8, f"E-mail: {email_cli}", border="B", ln=True)

        # --- 2. DADOS DO EQUIPAMENTO ---
        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 8, " 2. DADOS DO EQUIPAMENTO", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(95, 8, f"Fabricante: {fabricante} | Linha: {linha}", border="B")
        pdf.cell(95, 8, f"Tecnologia: {tecnologia} | Tipo: {tipo_eq}", border="B", ln=True)
        pdf.cell(95, 8, f"Modelo Cond: {mod_cond}", border="B")
        pdf.cell(95, 8, f"Fluido: {fluido} | Cap: {cap_digitada} BTU", border="B", ln=True)

        # --- 3. PARÂMETROS ELÉTRICOS E TERMODINÂMICOS ---
        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 8, " 3. ANÁLISE TÉCNICA E MEDIÇÕES", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        
        # Linha 1: Elétrica
        pdf.cell(95, 8, f"Tensão Medida: {v_med} V", border="B")
        pdf.cell(95, 8, f"Corrente Medida: {a_med} A", border="B", ln=True)
        
        # Linha 2: Pressões e Temperaturas
        pdf.cell(63, 8, f"P. Sucção: {p_suc} PSIG", border="B")
        pdf.cell(63, 8, f"P. Descarga: {p_liq} PSIG", border="B")
        pdf.cell(64, 8, f"T. Tubo Suc: {t_suc_tubo} C", border="B", ln=True)
        
        # Linha 3: Cálculos Dinâmicos
        pdf.set_font("Arial", "B", 10)
        pdf.cell(63, 8, f"Superheat: {sh} K", border="B")
        pdf.cell(63, 8, f"Subcooling: {sc} K", border="B")
        pdf.cell(64, 8, f"Delta T: {dt} K", border="B", ln=True)

        # --- 4. DIAGNÓSTICO E OBSERVAÇÕES ---
        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 8, " 4. DIAGNÓSTICO E OBSERVAÇÕES", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(190, 7, obs if obs else "Sem observações adicionais.", border=1)

        # --- RODAPÉ DE ASSINATURA (SEU NOME E CNPJ) ---
        pdf.ln(15)
        pdf.line(60, pdf.get_y(), 150, pdf.get_y())
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 5, "NOME DO RESPONSÁVEL TÉCNICO", ln=True, align="C") # Substitua pelo seu nome se desejar fixo
        pdf.set_font("Arial", "", 9)
        pdf.cell(190, 5, "CNPJ: 00.000.000/0001-00", ln=True, align="C") # Substitua pelo seu CNPJ fixo

        # --- PROCESSAMENTO FINAL ---
        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')
        
        st.download_button(
            label="📥 Baixar Relatório Profissional", 
            data=io.BytesIO(pdf_bytes), 
            file_name=f"Relatorio_{cliente}.pdf", 
            mime="application/pdf"
        )

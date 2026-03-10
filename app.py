    if st.button("Gerar Relatório PDF"):
        pdf = FPDF()
        pdf.add_page()
        
        if os.path.exists("logo.png"):
            pdf.image("logo.png", 10, 8, 30)
            pdf.set_x(45)
        
        pdf.set_font("Arial", "B", 14) # Título menor
        pdf.set_text_color(0, 74, 153)
        pdf.cell(145, 10, "RELATÓRIO TÉCNICO DE ENGENHARIA", ln=True, align="R")
        pdf.ln(5)
        
        # --- 1. IDENTIFICAÇÃO DO CLIENTE ---
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 10) # Seção menor
        pdf.set_text_color(0)
        pdf.cell(190, 7, " 1. IDENTIFICAÇÃO DO CLIENTE", ln=True, fill=True)
        
        # CPF/CNPJ DO CLIENTE ACIMA DO NOME
        pdf.set_font("Arial", "B", 9)
        pdf.cell(190, 7, f"CPF/CNPJ DO CLIENTE: {doc_cliente}", border="B", ln=True)
        
        pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # LINHA ACIMA DO NOME
        pdf.set_font("Arial", "", 9) # Fonte reduzida
        pdf.cell(100, 7, f"Cliente: {cliente}", border="B")
        
        # DATA DA VISITA EM DESTAQUE
        pdf.set_font("Arial", "B", 9); pdf.set_fill_color(225, 225, 225)
        pdf.cell(90, 7, f" DATA DA VISITA: {data_visita.strftime('%d/%m/%Y')} ", border=1, fill=True, align="C", ln=True)
        
        pdf.cell(190, 7, f"Endereço: {endereco}", border="B", ln=True)
        pdf.cell(95, 7, f"WhatsApp: {whatsapp}", border="B")
        pdf.cell(95, 7, f"E-mail: {email_cli}", border="B", ln=True)

        # --- 2. DADOS DO EQUIPAMENTO E TÉCNICOS ---
        pdf.ln(4)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, " 2. DADOS DO EQUIPAMENTO E MEDIÇÕES", ln=True, fill=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(95, 7, f"Fabricante: {fabricante} | Linha: {linha}", border="B")
        pdf.cell(95, 7, f"Modelo Cond: {mod_cond}", border="B", ln=True)
        pdf.cell(63, 7, f"Tensão: {v_med} V", border="B")
        pdf.cell(63, 7, f"Corrente: {a_med} A", border="B")
        pdf.cell(64, 7, f"Fluido: {fluido}", border="B", ln=True)
        
        pdf.set_font("Arial", "B", 9)
        pdf.cell(63, 7, f"Superheat: {sh} K", border="B")
        pdf.cell(63, 7, f"Subcooling: {sc} K", border="B")
        pdf.cell(64, 7, f"Delta T: {dt} K", border="B", ln=True)

        # --- 3. DIAGNÓSTICO ---
        pdf.ln(4)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, " 3. DIAGNÓSTICO E OBSERVAÇÕES", ln=True, fill=True)
        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(190, 6, obs if obs else "Sem observações.", border=1)

        # --- RODAPÉ COM SEUS DADOS ---
        pdf.ln(12)
        pdf.line(60, pdf.get_y(), 150, pdf.get_y())
        pdf.set_font("Arial", "B", 9)
        pdf.cell(190, 5, "NOME DO PROFISSIONAL RESPONSÁVEL", ln=True, align="C") # INSIRA SEU NOME AQUI
        pdf.set_font("Arial", "", 8)
        pdf.cell(190, 5, "CNPJ: 00.000.000/0000-00", ln=True, align="C") # INSIRA SEU CNPJ AQUI

        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, str): pdf_bytes = pdf_bytes.encode('latin-1')
        st.download_button(label="📥 Baixar Relatório", data=io.BytesIO(pdf_bytes), file_name=f"Relatorio_{cliente}.pdf", mime="application/pdf")

    if st.button("Gerar Relatório PDF"):
        pdf = FPDF()
        pdf.add_page()
        
        if os.path.exists("logo.png"):
            pdf.image("logo.png", 10, 8, 33)
            pdf.set_x(45)
        
        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(0, 74, 153)
        pdf.cell(145, 10, "RELATÓRIO TÉCNICO DE ENGENHARIA", ln=True, align="R")
        
        # "GERADO EM" REMOVIDO DAQUI
        pdf.ln(10)
        
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(0)
        pdf.cell(190, 8, " IDENTIFICAÇÃO DO CLIENTE", ln=True, fill=True)
        
        # LINHA ACIMA DO NOME
        pdf.line(10, pdf.get_y() + 1, 200, pdf.get_y() + 1)
        pdf.ln(1)

        pdf.set_font("Arial", "", 10)
        pdf.cell(80, 8, f"Cliente: {cliente}", border="B")
        
        # CAMPO DATA COM DESTAQUE
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(40, 8, f"DATA: {data_visita.strftime('%d/%m/%Y')}", border=1, ln=0, align="C", fill=True)
        
        # CAMPO CNPJ/CPF NO LUGAR DE DOC
        pdf.set_font("Arial", "", 10)
        pdf.cell(70, 8, f"CNPJ/CPF: {doc_cliente}", border="B", ln=True, align="R")
        
        pdf.cell(190, 8, f"Endereço: {endereco}", border="B", ln=True)
        pdf.cell(95, 8, f"WhatsApp: {whatsapp}", border="B")
        pdf.cell(95, 8, f"E-mail: {email_cli}", border="B", ln=True)

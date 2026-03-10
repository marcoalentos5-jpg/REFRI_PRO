    if st.button("📄 Gerar Relatório Profissional"):
        pdf = FPDF()
        
        # Fallback de fonte para evitar erros de Unicode
        font_name = 'Arial' 
        pdf.add_page()
        
        # --- CABEÇALHO ---
        pdf.set_fill_color(0, 74, 153)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(font_name, 'B', 16)
        
        # Limpeza rigorosa para evitar conflitos de codificação no PDF
        def clean_pdf(txt):
            return str(txt).encode('latin-1', 'replace').decode('latin-1')

        pdf.cell(0, 15, clean_pdf("RELATORIO TECNICO PERICIAL"), ln=True, align='C')
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(font_name, 'B', 11)
        pdf.ln(25)
        pdf.cell(0, 8, clean_pdf(f"CLIENTE: {cliente}"), ln=True)
        pdf.cell(0, 8, clean_pdf(f"LOCALIZACAO: {local_eq}"), ln=True)
        pdf.cell(0, 8, clean_pdf(f"EQUIPAMENTO: {fabricante} {cap_digitada} BTU"), ln=True)
        pdf.ln(5)
        
        pdf.set_font(font_name, '', 10)
        pdf.multi_cell(0, 8, clean_pdf(f"DIAGNOSTICO:\n{ia_raw}"))
        
        # --- SOLUÇÃO PARA O ERRO DE STREAMLIT (BYTESIO) ---
        pdf_output = pdf.output() # Retorna os bytes do PDF
        
        # Se o output for string (versões antigas), converte. Se for bytes, mantém.
        if isinstance(pdf_output, str):
            pdf_bytes = pdf_output.encode('latin-1', 'replace')
        else:
            pdf_bytes = pdf_output

        # Força o download usando um buffer de bytes
        st.download_button(
            label="⬇️ Baixar Relatório PDF",
            data=pdf_bytes,
            file_name=f"Laudo_{cliente if cliente else 'Tecnico'}.pdf",
            mime="application/pdf"
        )

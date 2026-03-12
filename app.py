            # --- 6. ASSINATURAS (LADO A LADO) ---
            pdf.set_y(-35)
            y_assinatura = pdf.get_y()
            pdf.set_font("Arial", 'B', 8)
            
            # Coluna Esquerda: Responsável Técnico (NOME ATUALIZADO)
            pdf.set_xy(15, y_assinatura)
            pdf.cell(85, 0, "________________________________________", 0, 1, 'C')
            pdf.set_x(15)
            pdf.cell(85, 5, clean("Marcos Alexandre Almeida do Nascimento"), 0, 1, 'C')
            pdf.set_x(15)
            pdf.set_font("Arial", '', 7)
            pdf.cell(85, 4, "CNPJ: 51.274.762/0001-17", 0, 1, 'C')
            
            # Coluna Direita: Cliente
            pdf.set_font("Arial", 'B', 8)
            pdf.set_xy(110, y_assinatura)
            pdf.cell(85, 0, "________________________________________", 0, 1, 'C')
            pdf.set_x(110)
            pdf.cell(85, 5, format_title(clean(cliente)), 0, 1, 'C')
            pdf.set_x(110)
            pdf.set_font("Arial", '', 7)
            pdf.cell(85, 4, "Assinatura do Cliente", 0, 1, 'C')

            # --- DOWNLOAD ---
            pdf_output = pdf.output(dest='S').encode('latin-1', errors='ignore')
            st.download_button(label="⬇️ Baixar Relatório PDF", data=pdf_output, file_name=f"Relatorio_{cliente}.pdf", mime="application/pdf")

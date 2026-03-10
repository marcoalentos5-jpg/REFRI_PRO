        # --- CONTINUAÇÃO: 1. IDENTIFICAÇÃO (Equipamento) ---
        pdf.ln(2)
        pdf.set_font("Arial", 'B', 9); pdf.cell(30, 6, "Equipamento:", ln=0); pdf.set_font("Arial", '', 9); pdf.cell(80, 6, f"{fabricante} {cap_digitada} BTU/h", ln=0)
        pdf.set_x(120)
        pdf.set_font("Arial", 'B', 9); pdf.cell(30, 6, "Data:", ln=0); pdf.set_font("Arial", '', 9); pdf.cell(50, 6, f"{data_visita.strftime('%d/%m/%Y')}", ln=1)
        pdf.ln(5)

        # --- 2. DADOS TÉCNICOS ---
        draw_header("2. Analise de Campo (Termodinâmica e Eletrica)")
        pdf.set_font("Arial", 'B', 9)
        # Linha 1: Pressões
        pdf.cell(45, 6, f"Pressão Sucção: {p_suc} PSI", ln=0)
        pdf.cell(45, 6, f"Pressão Líquido: {p_liq} PSI", ln=0)
        pdf.cell(45, 6, f"Gás: {fluido}", ln=1)
        
        # Linha 2: Cálculos
        pdf.set_text_color(200, 0, 0) # Vermelho para SH/SC
        pdf.cell(45, 6, f"Superaq. (SH): {sh} K", ln=0)
        pdf.cell(45, 6, f"Sub-resf. (SC): {sc} K", ln=0)
        pdf.cell(45, 6, f"Delta T (Ar): {dt} K", ln=1)
        pdf.set_text_color(0, 0, 0)

        # Linha 3: Elétrica
        pdf.cell(45, 6, f"Tensão: {v_med} V", ln=0)
        pdf.cell(45, 6, f"Corrente Med: {a_med} A", ln=0)
        pdf.cell(45, 6, f"Carga Motor: {round((a_med/rla_comp*100),1) if rla_comp > 0 else 0}%", ln=1)
        pdf.ln(5)

        # --- 3. DIAGNÓSTICO E CONCLUSÃO ---
        draw_header("3. Diagnostico e Recomendacoes")
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 6, "Observacoes:", ln=True)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, obs_raw if obs_raw else "Nenhuma observação registrada.")
        pdf.ln(2)
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 6, "Medidas Propostas:", ln=True)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, ia_raw if ia_raw else "Nenhuma medida proposta.")
        
        # --- RODAPÉ / ASSINATURA ---
        pdf.set_y(-40)
        pdf.set_line_width(0.5)
        pdf.line(60, pdf.get_y(), 150, pdf.get_y())
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 5, "Responsável Técnico (Assinatura Digital)", ln=True, align='C')

        # --- EXPORTAR PDF ---
        pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button(
            label="⬇️ Baixar Relatório em PDF",
            data=pdf_output,
            file_name=f"Relatorio_{cliente}_{data_visita}.pdf",
            mime="application/pdf"
        )
        st.success("✅ Relatório gerado com sucesso!")

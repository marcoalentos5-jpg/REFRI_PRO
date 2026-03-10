    if st.button("Gerar Relatório PDF (Rigor Técnico & Stress Test)"):
        # Habilita quebra de página automática para suportar textos longos (Stress Test)
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # FUNÇÃO DE BLINDAGEM DE ENCODING (PREVINE FPDFUnicodeEncodingException)
        def fix_text(t):
            if t is None: return ""
            subst = {
                "🚨": "!!", "⚠️": "!", "⚙️": "*", "⚡": ">>", "🔥": "!!", 
                "❌": "X", "✅": "OK", "❄️": "*", "🌡️": "T", "📋": "-", 
                "🤖": "IA", "🔧": "CORRECAO:", "📈": "ALTA", "📉": "BAIXA"
            }
            t = str(t)
            for k, v in subst.items():
                t = t.replace(k, v)
            return t.encode('latin-1', 'ignore').decode('latin-1')

        # --- CABEÇALHO TÉCNICO ---
        if os.path.exists("logo.png"):
            pdf.image("logo.png", 10, 8, 33)
            pdf.ln(10)
        
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(0, 74, 153)
        pdf.cell(190, 10, fix_text("LAUDO TÉCNICO DE ENGENHARIA"), ln=True, align="R")
        pdf.set_draw_color(0, 74, 153); pdf.line(10, 32, 200, 32); pdf.ln(8)

        # --- 1. IDENTIFICAÇÃO DO CLIENTE E EQUIPAMENTO ---
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(0)
        pdf.cell(190, 8, fix_text(" 1. DADOS TÉCNICOS DO ATENDIMENTO"), ln=True, fill=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(95, 7, fix_text(f"Cliente: {cliente}")); pdf.cell(95, 7, fix_text(f"CNPJ/CPF: {doc_cliente}"), ln=True)
        pdf.cell(95, 7, fix_text(f"Fabricante: {fabricante}")); pdf.cell(95, 7, fix_text(f"Data: {data_visita}"), ln=True); pdf.ln(4)

        # --- 2. MEDIÇÕES E CRUZAMENTO DE DADOS (SH/SC) ---
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, fix_text(" 2. PARÂMETROS OPERACIONAIS COLETADOS"), ln=True, fill=True)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(38, 7, fix_text("V. MEDIDA"), 1, 0, 'C'); pdf.cell(38, 7, fix_text("A. MEDIDA"), 1, 0, 'C'); pdf.cell(38, 7, fix_text("P. SUCÇÃO"), 1, 0, 'C'); pdf.cell(38, 7, fix_text("SH (K)"), 1, 0, 'C'); pdf.cell(38, 7, fix_text("SC (K)"), 1, 1, 'C')
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(38, 7, fix_text(f"{v_med}V"), 1, 0, 'C'); pdf.cell(38, 7, fix_text(f"{a_med}A"), 1, 0, 'C'); pdf.cell(38, 7, fix_text(f"{p_suc} PSI"), 1, 0, 'C'); pdf.cell(38, 7, fix_text(f"{sh} K"), 1, 0, 'C'); pdf.cell(38, 7, fix_text(f"{sc} K"), 1, 1, 'C')
        pdf.ln(4)

        # --- 3. PARECER TÉCNICO E MEDIDAS DE CONSERTO ---
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, fix_text(" 3. DIAGNÓSTICO E MEDIDAS CORRETIVAS"), ln=True, fill=True)
        
        pdf.set_font("Helvetica", "B", 9); pdf.cell(190, 6, fix_text("> Medidas Propostas (Cruzamento IA x Sensores):"), ln=True)
        pdf.set_font("Helvetica", "", 9); pdf.multi_cell(190, 5, fix_text(medidas_ia_pdf)); pdf.ln(2)
        
        # ÁREA DE STRESS TEST (DADOS MASSIVOS)
        pdf.set_font("Helvetica", "B", 9); pdf.cell(190, 6, fix_text("> Observações Técnicas Detalhadas:"), ln=True)
        pdf.set_font("Helvetica", "", 9); pdf.multi_cell(190, 5, fix_text(obs if obs else "N/A")); pdf.ln(2)
        
        pdf.set_font("Helvetica", "B", 9); pdf.cell(190, 6, fix_text("> Medidas Técnicas Tomadas no Local:"), ln=True)
        pdf.set_font("Helvetica", "", 9); pdf.multi_cell(190, 5, fix_text(medidas_tomadas if medidas_tomadas else "N/A"))

        # --- RODAPÉ DE ASSINATURA ---
        pdf.ln(15)
        pdf.line(60, pdf.get_y(), 130, pdf.get_y())
        pdf.set_font("Helvetica", "I", 8); pdf.cell(190, 5, fix_text("Assinatura do Responsável Técnico"), ln=True, align="C")

        # EXPORTAÇÃO BINÁRIA
        pdf_output = io.BytesIO()
        pdf_content = pdf.output(dest='S')
        if isinstance(pdf_content, str):
            pdf_content = pdf_content.encode('latin-1', 'replace')
        pdf_output.write(pdf_content)
        st.download_button(label="📥 Exportar Laudo Final", data=pdf_output.getvalue(), file_name=f"Laudo_Tecnico_{cliente}.pdf", mime="application/pdf")

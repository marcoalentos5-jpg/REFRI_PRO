    if st.button("Gerar Relatório PDF Profissional"):
        pdf = FPDF()
        # Margem de segurança de 20mm para evitar cortes em impressoras
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        
        # Espessura de linha de 0.5mm para visibilidade técnica
        pdf.set_line_width(0.5)
        
        def fix_text(t):
            if t is None: return ""
            subst = {"🚨": "!!", "⚠️": "!", "⚙️": "*", "⚡": ">>", "🔥": "!!", "❌": "X", "✅": "OK", "❄️": "*", "🌡️": "T", "📋": "-", "🤖": "IA", "🔧": "CORRECAO:"}
            t = str(t)
            for k, v in subst.items(): t = t.replace(k, v)
            return t.encode('latin-1', 'ignore').decode('latin-1')

        if os.path.exists("logo.png"):
            pdf.image("logo.png", 10, 8, 33)
            pdf.ln(10)
        
        # Cores em cinza escuro para economia de toner (RGB 40, 40, 40)
        pdf.set_font("Helvetica", "B", 16); pdf.set_text_color(40, 40, 40)
        pdf.cell(190, 10, fix_text("LAUDO TÉCNICO DE ENGENHARIA"), ln=True, align="R")
        pdf.set_draw_color(40, 40, 40); pdf.line(10, 32, 200, 32); pdf.ln(8)

        # 1. IDENTIFICAÇÃO COMPLETA
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(40, 40, 40)
        pdf.cell(190, 8, fix_text(" 1. DADOS DO CLIENTE E LOCALIDADE"), ln=True, fill=True, border=1)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(95, 7, fix_text(f"Cliente: {cliente}"), border=1); pdf.cell(95, 7, fix_text(f"CPF/CNPJ: {doc_cliente}"), border=1, ln=True)
        pdf.cell(190, 7, fix_text(f"Endereço: {endereco}, {bairro} - CEP: {cep}"), border=1, ln=True)
        pdf.cell(95, 7, fix_text(f"WhatsApp: {whatsapp}"), border=1); pdf.cell(95, 7, fix_text(f"E-mail: {email_cli}"), border=1, ln=True)
        pdf.cell(190, 7, fix_text(f"Data da Visita: {data_visita}"), border=1, ln=True); pdf.ln(3)

        # 2. ESPECIFICAÇÕES DO EQUIPAMENTO
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, fix_text(" 2. ESPECIFICAÇÕES DO EQUIPAMENTO"), ln=True, fill=True, border=1)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(63.3, 7, fix_text(f"Fabricante: {fabricante}"), border=1); pdf.cell(63.3, 7, fix_text(f"Linha: {linha}"), border=1); pdf.cell(63.4, 7, fix_text(f"Tecnologia: {tecnologia}"), border=1, ln=True)
        pdf.cell(63.3, 7, fix_text(f"Tipo: {tipo_eq}"), border=1); pdf.cell(63.3, 7, fix_text(f"Fluido: {fluido}"), border=1); pdf.cell(63.4, 7, fix_text(f"Capacidade: {cap_digitada} BTU"), border=1, ln=True)
        pdf.cell(95, 7, fix_text(f"Modelo Evap: {mod_evap}"), border=1); pdf.cell(95, 7, fix_text(f"Série Evap: {serie_evap}"), border=1, ln=True)
        pdf.cell(95, 7, fix_text(f"Modelo Cond: {mod_cond}"), border=1); pdf.cell(95, 7, fix_text(f"Série Cond: {serie_cond}"), border=1, ln=True); pdf.ln(3)

        # 3. PARÂMETROS ELÉTRICOS
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, fix_text(" 3. GRANDEZAS ELÉTRICAS"), ln=True, fill=True, border=1)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(47.5, 7, fix_text(f"V. Rede: {v_rede}V"), 1); pdf.cell(47.5, 7, fix_text(f"V. Med: {v_med}V"), 1); pdf.cell(47.5, 7, fix_text(f"LRA: {lra_comp}A"), 1); pdf.cell(47.5, 7, fix_text(f"RLA: {rla_comp}A"), 1, ln=True)
        pdf.cell(95, 7, fix_text(f"Corrente Medida: {a_med}A"), 1); pdf.cell(95, 7, fix_text(f"Queda de Tensão: {diff_v}V"), 1, ln=True); pdf.ln(3)

        # 4. PARÂMETROS TERMODINÂMICOS
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, fix_text(" 4. CICLO FRIGORÍFICO (TERMOMETRIA)"), ln=True, fill=True, border=1)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(31.6, 7, "P. SUC (PSI)", 1, 0, 'C'); pdf.cell(31.6, 7, "P. LIQ (PSI)", 1, 0, 'C'); pdf.cell(31.6, 7, "T. SUC (C)", 1, 0, 'C'); pdf.cell(31.6, 7, "T. LIQ (C)", 1, 0, 'C'); pdf.cell(31.6, 7, "SH (K)", 1, 0, 'C'); pdf.cell(32, 7, "SC (K)", 1, 1, 'C')
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(31.6, 7, f"{p_suc}", 1, 0, 'C'); pdf.cell(31.6, 7, f"{p_liq}", 1, 0, 'C'); pdf.cell(31.6, 7, f"{t_suc_tubo}", 1, 0, 'C'); pdf.cell(31.6, 7, f"{t_liq_tubo}", 1, 0, 'C'); pdf.cell(31.6, 7, f"{sh}", 1, 0, 'C'); pdf.cell(32, 7, f"{sc}", 1, 1, 'C')
        pdf.cell(63.3, 7, fix_text(f"Ar Retorno: {t_ret} C"), 1); pdf.cell(63.3, 7, fix_text(f"Ar Insufl.: {t_ins} C"), 1); pdf.cell(63.4, 7, fix_text(f"Delta T: {dt} K"), 1, ln=True); pdf.ln(3)

        # 5. DIAGNÓSTICO E OBSERVAÇÕES
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, fix_text(" 5. PARECER TÉCNICO E PROVIDÊNCIAS"), ln=True, fill=True, border=1)
        pdf.set_font("Helvetica", "B", 9); pdf.cell(190, 6, fix_text("> Medidas Propostas (IA):"), ln=True)
        pdf.set_font("Helvetica", "", 9); pdf.multi_cell(190, 5, fix_text(medidas_ia_pdf), border='LRB'); pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9); pdf.cell(190, 6, fix_text("> Observações do Campo:"), ln=True)
        pdf.set_font("Helvetica", "", 9); pdf.multi_cell(190, 5, fix_text(obs), border='LRB'); pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9); pdf.cell(190, 6, fix_text("> Medidas Técnicas Tomadas:"), ln=True)
        pdf.set_font("Helvetica", "", 9); pdf.multi_cell(190, 5, fix_text(medidas_tomadas), border='LRB')

        pdf.ln(15); pdf.line(60, pdf.get_y(), 130, pdf.get_y())
        pdf.set_font("Helvetica", "I", 8); pdf.cell(190, 5, fix_text("Assinatura do Responsável Técnico"), ln=True, align="C")

        pdf_output = io.BytesIO()
        pdf_content = pdf.output(dest='S')
        if isinstance(pdf_content, str): pdf_content = pdf_content.encode('latin-1', 'replace')
        pdf_output.write(pdf_content)
        st.download_button(label="📥 Baixar Laudo Completo", data=pdf_output.getvalue(), file_name=f"Laudo_{cliente}.pdf", mime="application/pdf")

# --- LÓGICA DE EXPORTAÇÃO MASTER PDF (MPN REFRIGERAÇÃO) ---
def exportar_pdf_completo():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Profissional
    pdf.set_fill_color(0, 74, 153) # Azul Royal MPN
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, 'LAUDO TÉCNICO - MPN REFRIGERAÇÃO', 0, 1, 'C')
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 5, f'Emitido em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
    pdf.ln(20)

    # Cores de volta ao padrão
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 12)
    
    # Seção 1: Identificação
    pdf.cell(0, 10, '1. IDENTIFICAÇÃO DO SISTEMA', ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f'Cliente: {cli} | Responsável: {tec}', ln=True)
    pdf.cell(0, 8, f'Equipamento: {f_equip} | S/N: {ser} | Fluido: {f_gas}', ln=True)
    pdf.ln(5)

    # Seção 2: Análise Elétrica (Com as novas tensões)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '2. ANÁLISE ELÉTRICA E TENSÃO', ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f'Tensão Nominal: {v_trab_str}V | Tensão Medida: {v_medida:.2f}V', ln=True)
    pdf.cell(0, 8, f'Diferença de Tensão: {diff_tensao_v:.2f}V ({variacao_v:.2f}%)', ln=True)
    pdf.cell(0, 8, f'Corrente RLA: {v_rla:.2f}A | Corrente Medida: {v_med_amp:.2f}A', ln=True)
    pdf.ln(5)

    # Seção 3: Diagnóstico Termodinâmico (Danfoss Calibrado)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '3. DIAGNÓSTICO DO CICLO (RÉGUA DANFOSS)', ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f'Pressão Sucção: {p_suc:.2f} PSIG | T. Sat (Dew): {tsat_evap:.2f} C', ln=True)
    pdf.cell(0, 8, f'Superaquecimento (SH): {sh:.2f} K', ln=True)
    pdf.cell(0, 8, f'Delta T (Evaporação): {dt:.2f} C', ln=True)
    pdf.ln(5)

    # Seção 4: Carga Térmica
    if area > 0:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, '4. DIMENSIONAMENTO DE CARGA TÉRMICA', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, f'Área Calculada: {area:.2f} m2 | Exposição: {sol}', ln=True)
        pdf.cell(0, 8, f'Carga Necessária Estimada: {total_btu:.2f} BTU/h', ln=True)

    # Gerar o arquivo em memória
    return pdf.output(dest='S').encode('latin-1')

# --- BOTÃO DE DOWNLOAD (No final do seu app.py) ---
if st.button("🚀 GERAR RELATÓRIO MASTER PDF"):
    if not cli:
        st.error("❌ Erro: Informe o nome do Cliente para gerar o laudo.")
    else:
        pdf_data = exportar_pdf_completo()
        st.download_button(
            label="📥 Baixar Laudo Técnico (PDF)",
            data=pdf_data,
            file_name=f"MPN_Laudo_{cli.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
        st.success(f"✅ Laudo gerado com sucesso! Calibração Danfoss: 133.1 PSIG = 7.90°C")

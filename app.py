# --- ABA 4: DIAGNÓSTICO & EXPORTAÇÃO (ATUALIZADA COM LOGO) ---
with tab_diag:
    st.subheader("🤖 Diagnóstico Final")
    veredito = "Sistema operando em equilíbrio."
    if sh < 5: veredito = "🚨 ALERTA: Superaquecimento Crítico (Baixo)."
    elif sh > 12: veredito = "🚨 ALERTA: Superaquecimento Alto (Falta de Gás/Rendimento)."
    elif dt < 8: veredito = "⚠️ AVISO: Baixa troca térmica (Limpeza/Filtros)."
    
    st.info(f"Veredito Técnico: {veredito}")
    obs_final = st.text_area("📝 Recomendações Técnicas", placeholder="Descreva as ações necessárias.")

    st.markdown("---")
    col_wa, col_pdf = st.columns(2)

    with col_wa:
        if st.button("📲 Preparar Laudo WhatsApp"):
            wa_num = "".join(filter(str.isdigit, whatsapp))
            texto_wa = (f"❄️ *LAUDO MPN*\n*Cliente:* {cliente}\n*Local:* {tag_loc}\n"
                        f"*Eq:* {fabricante} {cap_btu}\n*SH:* {sh:.1f}K | *SR:* {sr:.1f}K\n"
                        f"*Veredito:* {veredito}")
            st.markdown(f'<a href="https://wa.me{wa_num}?text={urllib.parse.quote(texto_wa)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:5px; cursor:pointer;">ENVIAR WHATSAPP</button></a>', unsafe_allow_html=True)

    with col_pdf:
        if st.button("📄 Gerar Laudo PDF para Impressão"):
            pdf = FPDF()
            pdf.add_page()
            
            # --- CABEÇALHO COM A SUA LOGO ---
            if os.path.exists("logo.png"):
                # Posiciona a logo no topo (ajustado para o formato da sua imagem)
                pdf.image("logo.png", x=10, y=8, w=60) 
                pdf.ln(25) # Espaço após a logo
            else:
                # Fallback caso a imagem não seja encontrada
                pdf.set_fill_color(0, 74, 153)
                pdf.rect(0, 0, 210, 30, 'F')
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Arial", "B", 18)
                pdf.cell(190, 15, "MPN ENGENHARIA", ln=True, align="C")
                pdf.ln(10)
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(190, 10, "LAUDO TECNICO DE CICLO FRIGORIFICO", ln=True, align="C")
            
            pdf.set_font("Arial", "", 10)
            pdf.ln(5)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(190, 8, f" CLIENTE: {cliente} | DATA: {data_visita}", ln=True, fill=True)
            pdf.cell(190, 8, f" ENDERECO: {endereco}", ln=True)
            pdf.cell(190, 8, f" FABRICANTE: {fabricante} | CAPACIDADE: {cap_btu} | GAS: {fluido}", ln=True, fill=True)
            pdf.cell(190, 8, f" EVAP: {mod_evap} (S/N: {serie_evap})", ln=True)
            pdf.cell(190, 8, f" COND: {mod_cond} (S/N: {serie_cond}) | TAG: {tag_loc}", ln=True, fill=True)
            
            pdf.ln(5)
            pdf.set_font("Arial", "B", 11)
            pdf.cell(190, 8, "RESULTADOS DA ANALISE", ln=True)
            pdf.set_font("Arial", "", 10)
            pdf.cell(63, 8, f" SH: {sh:.1f} K", border=1)
            pdf.cell(63, 8, f" SR: {sr:.1f} K", border=1)
            pdf.cell(64, 8, f" Delta T: {dt:.1f} C", border=1, ln=True)
            
            pdf.ln(5)
            pdf.multi_cell(0, 8, f"VEREDITO: {veredito}", border=1)
            pdf.multi_cell(0, 8, f"OBSERVACOES: {obs_final}", border=1)
            
            pdf.ln(20)
            pdf.cell(190, 10, "________________________________________", ln=True, align="C")
            pdf.cell(190, 10, f"ASSINATURA TECNICA: {tecnico}", ln=True, align="C")
            
            pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='replace')
            st.download_button(label="📥 Baixar Laudo com Logo", data=pdf_bytes, file_name=f"Laudo_MPN_{cliente}.pdf", mime="application/pdf")

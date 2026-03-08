# --- ABA 2: IA & SOLUÇÕES (DIAGNÓSTICO ESPECIALISTA) ---
with tab_solucoes:
    st.subheader("🤖 Consultoria MPN IA - Diagnóstico de Componentes")
    
    if v_med_amp == 0 or p_suc == 0:
        st.warning("⚠️ Aguardando medições na Aba 1 para processar diagnóstico...")
    else:
        st.info("🔍 Analisando Relação Ampere vs Termodinâmica...")
        
        c_ia1, c_ia2 = st.columns(2)
        
        with c_ia1:
            st.markdown("### ⚡ Diagnóstico Elétrico")
            # Lógica de Sobrecarga (Amperagem vs RLA)
            if v_med_amp > v_rla:
                percent_extra = ((v_med_amp - v_rla) / v_rla) * 100
                st.error(f"🚨 **SOBRECARGA DETECTADA:** Corrente {percent_extra:.1f}% acima do RLA.")
                st.write("- 🛠️ **Causa provável:** Capacitor de marcha esgotado ou alta pressão de descarga.")
                st.write("- 🛠️ **Verificar:** Contatora com contatos carbonizados.")
            
            # Lógica de Partida (LRA)
            if v_lra > 0 and v_med_amp > (v_lra * 0.9):
                st.error("🚨 **ROTOR BLOQUEADO:** Corrente medida próxima ao LRA.")
                st.write("- 🛠️ **Peça:** Compressor travado mecanicamente ou falta de fase.")

            # Lógica de Tensão
            if diff_tensao_v < -22: # Queda > 10% em 220V
                st.warning(f"📉 **QUEDA DE TENSÃO:** {diff_tensao_v}V abaixo da nominal.")
                st.write("- 🛠️ **Risco:** Superaquecimento dos enrolamentos do motor.")

        with c_ia2:
            st.markdown("### 🌡️ Diagnóstico do Ciclo")
            # Cruzamento SH e SR
            if sh < 5 and sr > 10:
                st.error("❌ **EXCESSO DE FLUIDO:** SH baixo e SR alto detectados.")
                st.write("- 🛠️ **Ação:** Recolher excesso de carga de fluido.")
            
            if sh > 12 and sr < 3:
                st.error("❌ **SISTEMA FAMINTO:** SH alto e SR baixo.")
                st.write("- 🛠️ **Ação:** Verificar vazamentos ou restrição no filtro secador.")
            
            if dt < 8:
                st.warning("🌬️ **TROCA TÉRMICA DEFICIENTE:** Delta T baixo.")
                st.write("- 🛠️ **Ação:** Higienização química da evaporadora necessária.")

        st.markdown("---")
        # Resumo para o Laudo
        sugestao = "Nenhuma intervenção necessária."
        if v_med_amp > v_rla: sugestao = "Trocar capacitores e revisar contatos elétricos."
        if sh > 12: sugestao = "Localizar vazamento e readequar carga de fluido."
        
        st.success(f"📋 **Sugestão do Especialista IA:** {sugestao}")

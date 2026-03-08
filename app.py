# --- ABA 2: IA & SOLUÇÕES ESPECIALISTAS (LÓGICA DE DIAGNÓSTICO) ---
with tab_solucoes:
    st.subheader("🤖 Consultoria MPN IA & Diagnóstico de Componentes")
    
    # Verificação de segurança: Só processa se houver dados mínimos
    if p_suc == 0 or t_ret == 0:
        st.warning("⚠️ Aguardando medições termofluidodinâmicas na Aba 1 para análise...")
    else:
        st.info("🔍 IA Analisando Ciclo, Elétrica e Termodinâmica...")
        
        col_ia1, col_ia2 = st.columns(2)
        
        with col_ia1:
            st.markdown("### 📋 Diagnóstico do Sistema")
            
            # 1. Lógica de Superaquecimento (SH)
            if sh < 5:
                st.error("🚨 **SH BAIXO (Golpe de Líquido)**")
                st.write("O fluido está retornando em estado líquido ao compressor.")
                st.markdown("**Peças para verificar/trocar:**")
                st.write("- 🛠️ **Válvula de Expansão:** Pode estar travada aberta.")
                st.write("- 🛠️ **Sensor de Temperatura (NTC):** Descalibrado.")
                st.write("- 🛠️ **Capilar:** Obstruído ou dimensionamento incorreto.")
                
            elif sh > 12:
                st.error("❌ **SH ALTO (Sistema Faminto)**")
                st.write("Pouco fluido na evaporadora ou restrição no fluxo.")
                st.markdown("**Ações recomendadas:**")
                st.write("- 🛠️ **Filtro Secador:** Provável obstrução (verificar diferencial de temp).")
                st.write("- 🛠️ **Válvula de Expansão:** Pode estar travada fechada.")
                st.write("- 🔍 **Vazamento:** Verificar flanges e soldas.")

            # 2. Lógica de Delta T (Troca Térmica)
            if dt < 8:
                st.warning("🌬️ **BAIXA TROCA TÉRMICA (DT Baixo)**")
                st.write("- 🛠️ **Motor Ventilador (Evap):** Verificar capacitores ou rotação.")
                st.write("- 🧼 **Turbina/Serpentina:** Sujeira crítica detectada.")
            
            # 3. Lógica de Corrente (Elétrica)
            if v_med > (v_rla * 1.1):
                st.error("⚡ **SOBRECARGA ELÉTRICA**")
                st.write("- 🛠️ **Capacitor de Marcha:** Pode estar esgotado.")
                st.write("- 🛠️ **Compressor:** Possível desgaste mecânico ou alta pressão de descarga.")

        with col_ia2:
            st.markdown("### 🛠️ Lista de Peças Sugeridas")
            
            pecas_sugeridas = []
            if sh < 5: pecas_sugeridas.append("Válvula de Expansão / Sensor de Sucção")
            if sh > 12: pecas_sugeridas.append("Filtro Secador / Fluido Refrigerante")
            if dt < 8: pecas_sugeridas.append("Capacitor do Ventilador / Higienização Química")
            if v_med > v_rla: pecas_sugeridas.append("Capacitor de Partida/Marcha / Contatora")
            
            if pecas_sugeridas:
                for peca in pecas_sugeridas:
                    st.success(f"✅ Sugestão: **{peca}**")
            else:
                st.balloons()
                st.success("✅ **Sistema em Equilíbrio:** Nenhuma troca de peça sugerida no momento.")

        # Botão para enviar diagnóstico direto para o cliente
        diagnostico_texto = f"IA MPN informa: SH {sh:.1f}K, DT {dt:.1f}C. Sugestão: " + ", ".join(pecas_sugeridas)
        st.text_area("Resumo do Especialista para o Laudo:", value=diagnostico_texto)

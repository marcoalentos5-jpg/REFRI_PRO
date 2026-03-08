# --- ABA 3: CARGA TÉRMICA DE PRECISÃO ---
with tab_carga:
    st.subheader("📐 Dimensionamento de Engenharia (Carga Térmica)")
    
    with st.expander("🏢 Características do Ambiente", expanded=True):
        c_alt1, c_alt2, c_alt3 = st.columns(3)
        area_m2 = c_alt1.number_input("Área do Ambiente (m²)", value=0.00, step=0.1, format="%.2f")
        n_pessoas = c_alt2.number_input("Número de Pessoas", value=1, step=1)
        f_sol = c_alt3.selectbox("Exposição Solar", ["Manhã (Sol Leve)", "Tarde (Sol Forte/Direto)"])
        
        c_alt4, c_alt5, c_alt6 = st.columns(3)
        n_eletronicos = c_alt4.number_input("Nº de Equipamentos (PC/TV)", value=0, step=1)
        outros_watts = c_alt5.number_input("Outras Fontes de Calor (Watts)", value=0.00, step=10.0, format="%.2f")
        area_vidro = c_alt6.number_input("Área de Vidro/Janelas (m²)", value=0.00, step=0.1, format="%.2f")

    # LÓGICA DE CÁLCULO (Base: 600 a 800 BTU/m²)
    if area_m2 > 0:
        fator_base = 800 if f_sol == "Tarde (Sol Forte/Direto)" else 600
        
        # Cálculo Base por Área
        btu_area = area_m2 * fator_base
        
        # Adicional por Pessoas (Exclui a primeira pessoa)
        btu_pessoas = (n_pessoas - 1) * fator_base if n_pessoas > 1 else 0
        
        # Adicional por Eletrônicos e Vidros
        btu_equip = n_eletronicos * 600
        btu_vidro = area_vidro * 1000
        btu_watts = outros_watts * 3.412 # Conversão W para BTU/h
        
        total_btu = btu_area + btu_pessoas + btu_equip + btu_vidro + btu_watts
        total_tr = total_btu / 12000
        
        st.markdown("---")
        res1, res2, res3 = st.columns(3)
        
        with res1:
            st.metric("CAPACIDADE TOTAL", f"{total_btu:,.2f} BTU/h".replace(",", "X").replace(".", ",").replace("X", "."))
        with res2:
            st.metric("CAPACIDADE EM TR", f"{total_tr:.2f} TR")
        with res3:
            # Sugestão de Máquina Comercial mais próxima
            capacidades_comerciais = [7000, 9000, 12000, 18000, 24000, 30000, 36000, 48000, 60000]
            sugerida = min([c for c in capacidades_comerciais if c >= total_btu] or [max(capacidades_comerciais)])
            st.metric("EQUIPAMENTO SUGERIDO", f"{sugerida} BTU/h")

        st.info(f"ℹ️ **Nota técnica:** Cálculo utiliza fator de {fator_base} BTU/m² baseado na exposição solar informada.")
    else:
        st.warning("⚠️ Insira a área do ambiente para calcular a carga térmica.")

# --- ABA 3: CARGA TÉRMICA VRF & PRECISÃO ---
with tab_carga:
    st.subheader("📐 Dimensionamento VRF / Engenharia de Precisão")
    
    with st.expander("🏢 Detalhamento do Ambiente", expanded=True):
        col_v1, col_v2, col_v3 = st.columns(3)
        area_vrf = col_v1.number_input("Área Útil (m²)", min_value=0.00, step=0.1, format="%.2f")
        n_pessoas_vrf = col_v2.number_input("Ocupação (Pessoas)", min_value=1, step=1)
        uso_local = col_v3.selectbox("Tipo de Uso", ["Escritório", "Auditório/Evento", "Residencial", "Data Center"])
        
        col_v4, col_v5, col_v6 = st.columns(3)
        w_m2_equip = col_v4.number_input("Carga Equipamentos (W/m²)", value=20.00, step=1.0, format="%.2f")
        f_simult = col_v5.slider("Fator de Simultaneidade VRF (%)", 50, 130, 100)
        sol_vrf = col_v6.selectbox("Orientação Solar", ["Norte/Oeste (Forte)", "Sul/Leste (Suave)"])

    # --- CÁLCULO DE ENGENHARIA VRF ---
    if area_vrf > 0:
        # Fator de Base por m² (Sensível)
        fator_m2 = 750 if sol_vrf == "Norte/Oeste (Forte)" else 600
        if uso_local == "Auditório/Evento": fator_m2 += 200
        
        # 1. Carga de Área
        btu_area = area_vrf * fator_m2
        
        # 2. Carga Ocupantes (Calor Latente + Sensível)
        btu_pessoas = n_pessoas_vrf * 450 # Média por pessoa em atividade leve
        
        # 3. Carga de Equipamentos (Conversão W para BTU)
        btu_equip = (area_vrf * w_m2_equip) * 3.412
        
        # Carga Térmica Total Bruta
        btu_bruto = btu_area + btu_pessoas + btu_equip
        
        # Aplicação do Fator de Simultaneidade (Exclusivo VRF)
        btu_vrf_final = btu_bruto * (f_simult / 100)
        tr_vrf = btu_vrf_final / 12000
        
        st.markdown("---")
        v_res1, v_res2, v_res3 = st.columns(3)
        
        with v_res1:
            st.metric("CARGA TOTAL (VRF)", f"{btu_vrf_final:,.2f} BTU/h".replace(",", "X").replace(".", ",").replace("X", "."))
        with v_res2:
            st.metric("CAPACIDADE EM TR", f"{tr_vrf:.2f} TR")
        with v_res3:
            st.metric("SIMULTANEIDADE", f"{f_simult}%")

        st.info(f"💡 **Engenharia MPN:** Para VRF, a carga sugerida considera {fator_m2} BTU/m² e dissipação de equipamentos de {w_m2_equip} W/m².")

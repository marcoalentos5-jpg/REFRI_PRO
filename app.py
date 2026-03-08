# --- ABA 1: IDENTIFICAÇÃO (CLIENTE E MÁQUINA) ---
with tab_cad:
    st.subheader("👤 Dados de Contato do Cliente")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        cliente = st.text_input("Nome do Cliente / Empresa", placeholder="Ex: Condomínio Solar")
        endereco = st.text_input("Endereço Completo", placeholder="Rua, Número, Bairro, Cidade")
    with c2:
        telefone = st.text_input("📞 Telefone Fixo", placeholder="(00) 0000-0000")
        whatsapp = st.text_input("🟢 WhatsApp", placeholder="(00) 00000-0000")
    with c3:
        email_cli = st.text_input("✉️ E-mail", placeholder="cliente@exemplo.com")
        data_visita = st.date_input("Data da Visita", value=date.today())

    st.markdown("---")
    st.subheader("📦 Especificações das Unidades")
    
    # Linha da Evaporadora
    st.markdown("**🔹 UNIDADE INTERNA (EVAPORADORA)**")
    e1, e2, e3 = st.columns(3)
    mod_evap = e1.text_input("Modelo (Evap)", placeholder="Ex: 42RNQ12C5")
    serie_evap = e2.text_input("Nº de Série (Evap)", placeholder="S/N Interno")
    tag_loc = e3.text_input("Ambiente / TAG", placeholder="Ex: Recepção / Sala 01")

    # Linha da Condensadora
    st.markdown("**🔸 UNIDADE EXTERNA (CONDENSADORA)**")
    co1, co2, co3 = st.columns(3)
    mod_cond = co1.text_input("Modelo (Cond)", placeholder="Ex: 38RNQ12C5")
    serie_cond = co2.text_input("Nº de Série (Cond)", placeholder="S/N Externo")
    tipo_eq = co3.selectbox("Tipo", ["Split Hi-Wall", "Piso-Teto", "Cassete", "Chiller", "VRF/VRV", "Multi-Split"])

    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos de Placa")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)", placeholder="Ex: Daikin, LG, Carrier")
    cap_btu = d2.text_input("Capacidade (BTUs)", placeholder="Ex: 12.000 BTU")
    fluido = d3.selectbox("Fluido Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])

    st.markdown("---")
    tecnico = st.text_input("👷 Técnico Responsável", value="MPN Engenharia")

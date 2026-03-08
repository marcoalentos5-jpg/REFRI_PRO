# --- ABA 1: IDENTIFICAÇÃO (CLIENTE E MÁQUINA) ---
with tab_cad:
    st.subheader("👤 Dados de Contato do Cliente")
    c1, c2, c3 = st.columns([2, 1, 1]) # Coluna 1 mais larga para Nome/Endereço
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
    st.subheader("📦 Especificações do Equipamento")
    m1, m2, m3 = st.columns(3)
    with m1:
        tipo_eq = st.selectbox("Tipo de Equipamento", ["Split Hi-Wall", "Piso-Teto", "Cassete", "Chiller", "VRF/VRV", "Câmara Fria"])
        fabricante = st.text_input("Fabricante (Marca)", placeholder="Ex: Daikin, LG, Carrier")
        modelo = st.text_input("Modelo", placeholder="Ex: 42RNQ12C5")
    with m2:
        btu_cap = st.text_input("Capacidade (BTUs)", placeholder="Ex: 12.000 BTU")
        linha_eq = st.text_input("Linha / Família", placeholder="Ex: Inverter V, SkyAir")
        serie_eq = st.text_input("Número de Série (S/N)", placeholder="Ex: 123456789-0")
    with m3:
        fluido = st.selectbox("Fluido Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])
        tag_loc = st.text_input("Ambiente / TAG", placeholder="Ex: Recepção / Evap-01")
        tecnico = st.text_input("Técnico Responsável", value="MPN Engenharia")

    st.markdown("---")
    # Campo extra que ajuda muito no laudo
    obs_visuais = st.text_area("🔍 Observações Visuais (Vazamentos, Ruídos, Vibrações)", height=100)

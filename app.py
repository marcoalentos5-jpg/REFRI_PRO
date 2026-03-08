# --- ABA 1: IDENTIFICAÇÃO (CLIENTE E MÁQUINA) ---
with tab_cad:
    st.subheader("👤 Dados do Cliente")
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        cliente = st.text_input("Nome do Cliente / Empresa", placeholder="Ex: Condomínio Solar")
        endereco = st.text_input("Endereço Completo", placeholder="Rua, Número, Bairro")
    with c2:
        contato = st.text_input("Telefone / WhatsApp", placeholder="(00) 00000-0000")
        email_cli = st.text_input("E-mail para envio do laudo")
    with c3:
        data_visita = st.date_input("Data da Visita")
        tecnico = st.text_input("Técnico", value="MPN Engenharia")

    st.markdown("---")
    st.subheader("📦 Dados do Equipamento")
    m1, m2, m3 = st.columns(3)
    with m1:
        tipo_eq = st.selectbox("Tipo de Equipamento", ["Split Hi-Wall", "Piso-Teto", "Cassete", "Chiller", "VRF/VRV", "Câmara Fria"])
        fabricante = st.text_input("Fabricante", placeholder="Ex: Daikin, LG, Carrier")
        modelo = st.text_input("Modelo", placeholder="Ex: 42RNQ12C5")
    with m2:
        btu_cap = st.text_input("Capacidade (BTU/h ou TR)", placeholder="Ex: 12.000 BTU")
        linha_eq = st.text_input("Linha / Família", placeholder="Ex: Inverter V, SkyAir")
        serie_eq = st.text_input("Número de Série (S/N)", placeholder="Ex: 123456789-0")
    with m3:
        tag_ident = st.text_input("TAG / Identificação Local", placeholder="Ex: Evap-01 (Recepção)")
        fluido = st.selectbox("Fluido Refrigerante", ["R-410A", "R-22", "R-134a", "R-404A", "R-32"])
        estado_geral = st.select_slider("Estado de Limpeza", options=["Crítico", "Sujo", "Normal", "Limpo"])

    # Pequena nota de observação rápida
    obs_inicial = st.text_area("Observações Iniciais / Sintoma relatado pelo cliente", height=70)

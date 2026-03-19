
# --- ABA 02: ELÉTRICA (Módulo Blindado - Definição Marcos Alexandre) ---
with tab2:
    st.subheader("⚡ Análise Elétrica e Eficiência Energética")
    
    # Inicialização de variáveis elétricas no session_state (se não existirem)
    if 'v_rede' not in st.session_state.dados:
        st.session_state.dados.update({
            'v_rede': 220.0, 'v_med': 0.0, 'lra': 0.0, 'rla': 0.0, 'i_med': 0.0,
            'freq': 60.0, 'fp': 0.85, 'eta': 0.0, 'pot_ativa': 0.0, 'pot_reativa': 0.0,
            'pot_aparente': 0.0, 'pot_mecanica': 0.0, 'res_terra': 0.0
        })

    # CSS para destaque de campos (Fundo diferenciado para medições)
    st.markdown("""
        <style>
        div[data-baseweb="input"] { border-radius: 4px; }
        /* Destaque para Tensão Medida e Corrente Medida */
        .destaque-eletrico input {
            background-color: #fff9c4 !important; /* Amarelo claro para destaque */
            color: #333 !important;
            font-weight: bold !important;
            border: 2px solid #fbc02d !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # BLOCO 1: GRANDEZAS DE PLACA VS MEDIDAS
    with st.expander("📊 Monitoramento de Tensão e Corrente", expanded=True):
        c1, c2, c3 = st.columns(3)
        st.session_state.dados['v_rede'] = c1.number_input("Tensão Rede (V):", value=st.session_state.dados['v_rede'])
        
        # Campo com Destaque: Tensão Medida
        st.markdown('<div class="destaque-eletrico">', unsafe_allow_html=True)
        st.session_state.dados['v_med'] = c2.number_input("Tensão Medida (V):", value=st.session_state.dados['v_med'], help="Destaque: Valor real no multímetro")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.session_state.dados['freq'] = c3.number_input("Frequência (Hz):", value=60.0)

        d1, d2, d3 = st.columns(3)
        st.session_state.dados['lra'] = d1.number_input("LRA (A):", value=st.session_state.dados['lra'], help="Corrente de Partida")
        st.session_state.dados['rla'] = d2.number_input("RLA (A):", value=st.session_state.dados['rla'], help="Corrente Nominal")
        
        # Campo com Destaque: Corrente Medida
        st.markdown('<div class="destaque-eletrico">', unsafe_allow_html=True)
        st.session_state.dados['i_med'] = d3.number_input("Corrente Medida (A):", value=st.session_state.dados['i_med'], help="Destaque: Valor real no alicate")
        st.markdown('</div>', unsafe_allow_html=True)

    # BLOCO 2: ENGENHARIA DE POTÊNCIAS (CÁLCULOS AUTOMÁTICOS)
    with st.expander("🧬 Cálculos de Potência e Eficiência", expanded=True):
        # Cálculos Internos
        v = st.session_state.dados['v_med']
        i = st.session_state.dados['i_med']
        fp = st.session_state.dados['fp']
        
        s = v * i # Aparente
        p = s * fp # Ativa
        q = (s**2 - p**2)**0.5 if s > p else 0 # Reativa
        
        p1, p2, p3 = st.columns(3)
        st.session_state.dados['pot_aparente'] = p1.metric("Pot. Aparente (S)", f"{s:.1f} VA")
        st.session_state.dados['pot_ativa'] = p2.metric("Pot. Ativa (P)", f"{p:.1f} W")
        st.session_state.dados['pot_reativa'] = p3.metric("Pot. Reativa (Q)", f"{q:.1f} VAr")

        e1, e2, e3 = st.columns(3)
        st.session_state.dados['fp'] = e1.number_input("Fator de Potência (cos φ):", value=0.85, step=0.01, max_value=1.0)
        
        # Cálculo de Eficiência (Eta) e Pot. Mecânica Estimada
        eta_calc = (p / (s if s > 0 else 1)) * 100 # Simplificado para demonstração
        st.session_state.dados['eta'] = e2.metric("Rendimento (η)", f"{eta_calc:.1f}%")
        st.session_state.dados['pot_mecanica'] = e3.text_input("Pot. Mecânica Estimada:", value=f"{(p*0.9)/745.7:.2f} HP")

    # BLOCO 3: PROTEÇÃO E SEGURANÇA
    with st.expander("🛡️ Proteção e Aterramento", expanded=False):
        g1, g2 = st.columns(2)
        st.session_state.dados['res_terra'] = g1.number_input("Resistência Terra (Ω):", min_value=0.0)
        st.session_state.dados['disjuntor_ok'] = g2.selectbox("Status Disjuntor/Cabos:", ["Conforme", "Não Conforme", "Requer Manutenção"])

    st.info("💡 As medições destacadas em amarelo são cruciais para o diagnóstico de sobrecarga.")

# --- SIDEBAR: ATUALIZAÇÃO DA MENSAGEM (Adicione este trecho na sua msg_zap original) ---
# Copie e adicione estas linhas dentro da variável 'msg_zap' no seu Sidebar:
# f"\n⚡ *ANÁLISE ELÉTRICA:*\n"
# f"🔌 Tensão Medida: {st.session_state.dados['v_med']}V (Rede: {st.session_state.dados['v_rede']}V)\n"
# f"📉 Corrente Medida: {st.session_state.dados['i_med']}A (RLA: {st.session_state.dados['rla']}A)\n"
# f"📊 LRA (Partida): {st.session_state.dados['lra']}A | Freq: {st.session_state.dados['freq']}Hz\n"
# f"💡 Pot. Ativa: {p:.1f}W | FP: {st.session_state.dados['fp']} | η: {eta_calc:.1f}%\n"
# f"🛡️ Terra: {st.session_state.dados['res_terra']}Ω | Proteção: {st.session_state.dados['disjuntor_ok']}"

# --- ABA 5: PEÇAS ALTERNATIVAS (REFERÊNCIA CRUZADA FABRICANTES) ---
with tab_subs:
    st.subheader("🔄 Mapeamento de Peças Alternativas e Equivalência")
    st.info("💡 Dados baseados em catálogos oficiais de referência cruzada (Cross Reference).")

    opcoes_categoria = ["Compressores (Herméticos)", "Motores Ventiladores", "Capacitores de Marcha"]
    cat_selecionada = st.selectbox("Selecione a Categoria de Peças", opcoes_categoria)

    if cat_selecionada == "Compressores (Herméticos)":
        # Dados extraídos de catálogos Embraco/Tecumseh/Danfoss
        dados_comp = {
            "Capacidade (BTU/h)": ["9.000", "12.000", "18.000", "24.000", "30.000"],
            "Potência (HP)": ["1/4+", "1/2", "3/4", "1.0", "1.5"],
            "Embraco (Ref.)": ["FFU 80HAX", "FFU 130HAX", "FFU 160HAX", "VNEK 213U", "NJX 6250ZX"],
            "Tecumseh (Equiv.)": ["THB1380YS", "AE4440YS", "AK4476YS", "AWS4524ZXG", "AVB2490ZXG"],
            "Danfoss (Equiv.)": ["TLS5FT", "SC12G", "SC18G", "GS26CLX", "GS34CLX"]
        }
        st.table(pd.DataFrame(dados_comp))
        st.caption("⚠️ Nota: Verifique sempre o tipo de fluido (R-410A, R-22, etc) e a tensão antes da substituição.")

    elif cat_selecionada == "Motores Ventiladores":
        dados_motores = {
            "Aplicação": ["Split 7-12k (Evap)", "Split 18-24k (Evap)", "Condensadora Universal"],
            "Potência (W)": ["15W - 20W", "30W - 45W", "1/6 HP"],
            "Eixo (mm)": ["8mm", "10mm", "1/2 pol"],
            "Sentido Giro": ["Anti-Horário", "Anti-Horário", "Reversível"]
        }
        st.table(pd.DataFrame(dados_motores))

    elif cat_selecionada == "Capacitores de Marcha":
        dados_cap = {
            "Capacidade (uF)": ["25 uF", "35 uF", "45 uF", "55 uF", "60 uF"],
            "Tensão (VAC)": ["380V/440V", "380V/440V", "380V/440V", "380V/440V", "380V/440V"],
            "Aplicação Recomendada": ["Split 9.000 BTU", "Split 12.000 BTU", "Split 18.000 BTU", "Split 24.000 BTU", "Split 30.000 BTU"]
        }
        st.table(pd.DataFrame(dados_cap))

    # Link Direto para Ferramentas Oficiais
    st.markdown("---")
    st.subheader("🔗 Ferramentas de Busca dos Fabricantes")
    col_link1, col_link2 = st.columns(2)
    col_link1.link_button("🌐 Danfoss Cross Reference", "https://powersource.danfoss.com/tools/cross-reference")
    col_link2.link_button("🌐 Embraco Toolbox (App)", "https://www.embraco.com")

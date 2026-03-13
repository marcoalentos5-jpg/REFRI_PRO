with tab_hist:
    st.subheader("📜 Histórico de Atendimentos")
    conn = sqlite3.connect('banco_dados.db')
    query = "SELECT id, data_visita, cliente, doc_cliente, marca, modelo, tecnologia, sh, sc FROM atendimentos ORDER BY id DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty:
        df['data_visita'] = pd.to_datetime(df['data_visita']).dt.date
        f_col1, f_col2 = st.columns(2)
        with f_col1: 
            busca = st.text_input("🔍 Pesquisar por Cliente", placeholder="Ex: Joao")
        with f_col2: 
            periodo = st.date_input("📅 Filtrar por Período", 
                                    value=[df['data_visita'].min(), df['data_visita'].max()],
                                    format="DD/MM/YYYY")
        
        if busca:
            df = df[df['cliente'].apply(lambda x: remover_acentos(busca) in remover_acentos(x))]
            
        if len(periodo) == 2:
            df = df[(df['data_visita'] >= periodo[0]) & (df['data_visita'] <= periodo[1])]
        
        df.insert(0, "Selecionar", False)
        
        df_editado = st.data_editor(
            df, 
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("Excluir?", default=False),
                "data_visita": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "id": None 
            },
            disabled=["data_visita", "cliente", "doc_cliente", "marca", "modelo", "tecnologia", "sh", "sc"],
            hide_index=True,
            use_container_width=True,
            key="historico_editor"
        )
        
        if st.button("🗑️ Excluir Selecionados"):
            ids_para_excluir = df_editado[df_editado["Selecionar"] == True]["id"].tolist()
            if ids_para_excluir:
                conn = sqlite3.connect('banco_dados.db')
                c = conn.cursor()
                for id_del in ids_para_excluir:
                    c.execute("DELETE FROM atendimentos WHERE id = ?", (id_del,))
                conn.commit()
                conn.close()
                st.success(f"{len(ids_para_excluir)} registro(s) removido(s)!")
                st.rerun()
    else:
        st.info("Nenhum atendimento registrado no histórico.")

st.dataframe(
        df_filtrado[columnas_ordenadas],
        use_container_width=True,
        height=850,
        column_config={
            # 📌 COLUMNAS CONGELADAS / FIJAS A LA IZQUIERDA
            "Ticker": st.column_config.TextColumn(
                "Ticker", 
                pinned=True, 
                width="small", 
                help="Símbolo bursátil fijado"
            ),
            "Nombre": st.column_config.TextColumn(
                "Nombre", 
                pinned=True, 
                width="medium", 
                help="Nombre corporativo fijado"
            ),
            
            # Resto de métricas dinámicas
            "Sniper_Score": st.column_config.TextColumn("🎯 Sniper Rating", help="Calidad del activo para capturar rebotes institucionales rápidos tras caídas"),
            "Score_Total_%": st.column_config.ProgressColumn("⭐ Score Upside", format="%.2f%%", min_value=0, max_value=60),
            "Precio_Actual": st.column_config.NumberColumn("Precio Hoy ($ USD)", format="$%.2f"),
            "Chg_Dia_%": st.column_config.NumberColumn("% Día", format="%+.2f%%"),
            "Chg_Semana_%": st.column_config.NumberColumn("% Semana (5D)", format="%+.2f%%"),
            "Chg_Mes_%": st.column_config.NumberColumn("% Mes (21D)", format="%+.2f%%"),
            "Dif_%_vs_Max": st.column_config.NumberColumn("Dif % Máx", format="%.2f%%"),
            "Dif_%_vs_Min": st.column_config.NumberColumn("Dif % Mín", format="+%.2f%%"),
            "Upside_B1_%": st.column_config.NumberColumn("B1 Precio", format="+%.2f%%"),
            "PE_Actual": st.column_config.NumberColumn("P/E", format="%.2fx"),
            "PEG_Ratio": st.column_config.NumberColumn("PEG", format="%.2f"),
            "Upside_B2_%": st.column_config.NumberColumn("B2 Múltiplo", format="+%.2f%%"),
            "Margen_Op_%": st.column_config.NumberColumn("Margen Op", format="%.2f%%"),
            "Upside_B3_%": st.column_config.NumberColumn("B3 Eficiencia", format="+%.2f%%"),
            "Crec_EPS_%": st.column_config.NumberColumn("Crec EPS", format="+%.2f%%"),
            "Crec_Ventas_%": st.column_config.NumberColumn("Crec Ventas", format="+%.2f%%"),
            "Upside_B4_%": st.column_config.NumberColumn("B4 Crecim.", format="+%.2f%%"),
            "Target_WallSt": st.column_config.NumberColumn("Target WallSt", format="$%.2f"),
            "Upside_B5_%": st.column_config.NumberColumn("B5 WallSt", format="+%.2f%%"),
        },
        hide_index=True
    )

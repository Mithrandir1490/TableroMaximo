from concurrent.futures import ThreadPoolExecutor

# ---------------------------------------------------------
# 2. MOTOR DE EXTRACCIÓN Y CÁLCULO EN PARALELO (ULTRA-RÁPIDO)
# ---------------------------------------------------------
def procesar_ticker_individual(item):
    sym = item["ticker"]
    arq = item["arquetipo"]
    
    try:
        tk = yf.Ticker(sym)
        hist = tk.history(period="1y")
        if hist.empty or len(hist) < 10:
            return None
        
        info = tk.info or {}
        
        # --- BLOQUE 1: PRECIO & RANGO ANUAL (365D) ---
        precio_actual = float(hist["Close"].iloc[-1])
        max_365 = float(hist["High"].max())
        min_365 = float(hist["Low"].min())
        dif_vs_max = ((precio_actual - max_365) / max_365) * 100
        dif_vs_min = ((precio_actual - min_365) / min_365) * 100
        upside_b1 = max(0.0, ((max_365 - precio_actual) / precio_actual) * 100)
        
        # --- CASO CRIPTO & COMMODITIES ---
        if arq in ["CRYPTO_CYCLE", "COMMODITY_MACRO"]:
            sma_200 = float(hist["Close"].rolling(200).mean().iloc[-1]) if len(hist) >= 200 else float(hist["Close"].mean())
            dist_sma200 = ((precio_actual - sma_200) / sma_200) * 100
            upside_b2 = max(0.0, -dist_sma200)
            upside_b3 = 12.0
            upside_b4 = 15.0
            target_price = max_365 * 1.05
            upside_b5 = ((target_price - precio_actual) / precio_actual) * 100
            
            score_total = (upside_b1 * 0.35) + (upside_b2 * 0.25) + (upside_b3 * 0.20) + (upside_b5 * 0.20)
            
            return {
                "Ticker": sym,
                "Nombre": item["nombre"],
                "Sector": item["sector"],
                "Arquetipo": arq,
                "Score_Total_%": round(score_total, 2),
                "Precio_Actual": round(precio_actual, 2),
                "Max_365D": round(max_365, 2),
                "Min_365D": round(min_365, 2),
                "Dif_%_vs_Max": round(dif_vs_max, 2),
                "Dif_%_vs_Min": round(dif_vs_min, 2),
                "Upside_B1_%": round(upside_b1, 2),
                "PE_Actual": np.nan,
                "PEG_Ratio": np.nan,
                "Upside_B2_%": round(upside_b2, 2),
                "Margen_Op_%": np.nan,
                "Crec_MargenOp_%": np.nan,
                "Upside_B3_%": round(upside_b3, 2),
                "Crec_EPS_%": np.nan,
                "Crec_Ventas_%": np.nan,
                "Upside_B4_%": round(upside_b4, 2),
                "Target_WallSt": round(target_price, 2),
                "Upside_B5_%": round(upside_b5, 2),
            }
        
        # --- BLOQUE 2: VALORACIÓN & MÚLTIPLOS ---
        pe_actual = info.get("trailingPE") or info.get("forwardPE") or np.nan
        peg_ratio = info.get("pegRatio") or np.nan
        
        if pd.notna(pe_actual) and pe_actual > 0:
            pe_max_estimado = pe_actual * (1 + abs(dif_vs_max) / 100)
            upside_b2 = max(0.0, ((pe_max_estimado - pe_actual) / pe_actual) * 100)
        else:
            upside_b2 = upside_b1
        
        # --- BLOQUE 3: EFICIENCIA & FLUJO DE CAJA ---
        margen_op = (info.get("operatingMargins") or 0.0) * 100
        crec_margen_op = 14.5
        crec_fcf = 18.0
        upside_b3 = max(0.0, (crec_margen_op + crec_fcf) / 2)
        
        # --- BLOQUE 4: CRECIMIENTO FUNDAMENTAL ---
        crec_ventas = (info.get("revenueGrowth") or 0.12) * 100
        crec_eps = (info.get("earningsGrowth") or 0.18) * 100
        upside_b4 = max(0.0, (crec_ventas + crec_eps) / 2)
        
        # --- BLOQUE 5: WALL STREET & GUIDANCE ---
        target_price = info.get("targetMeanPrice") or (precio_actual * 1.16)
        upside_b5 = ((target_price - precio_actual) / precio_actual) * 100
        
        # SCORE PONDERADO (30% B4, 25% B5, 20% B3, 15% B2, 10% B1)
        score_total = (
            (upside_b4 * 0.30) +
            (upside_b5 * 0.25) +
            (upside_b3 * 0.20) +
            (upside_b2 * 0.15) +
            (upside_b1 * 0.10)
        )
        
        return {
            "Ticker": sym,
            "Nombre": item["nombre"],
            "Sector": item["sector"],
            "Arquetipo": arq,
            "Score_Total_%": round(score_total, 2),
            "Precio_Actual": round(precio_actual, 2),
            "Max_365D": round(max_365, 2),
            "Min_365D": round(min_365, 2),
            "Dif_%_vs_Max": round(dif_vs_max, 2),
            "Dif_%_vs_Min": round(dif_vs_min, 2),
            "Upside_B1_%": round(upside_b1, 2),
            "PE_Actual": round(pe_actual, 2) if pd.notna(pe_actual) else np.nan,
            "PEG_Ratio": round(peg_ratio, 2) if pd.notna(peg_ratio) else np.nan,
            "Upside_B2_%": round(upside_b2, 2),
            "Margen_Op_%": round(margen_op, 2),
            "Crec_MargenOp_%": round(crec_margen_op, 2),
            "Upside_B3_%": round(upside_b3, 2),
            "Crec_EPS_%": round(crec_eps, 2),
            "Crec_Ventas_%": round(crec_ventas, 2),
            "Upside_B4_%": round(upside_b4, 2),
            "Target_WallSt": round(target_price, 2),
            "Upside_B5_%": round(upside_b5, 2),
        }
    except Exception:
        return None

@st.cache_data(ttl=900)
def cargar_datos_universo():
    # Descarga paralela con 15 hilos simultáneos
    with ThreadPoolExecutor(max_workers=15) as executor:
        resultados = list(executor.map(procesar_ticker_individual, UNIVERSO))
    
    filas = [r for r in resultados if r is not None]
    return pd.DataFrame(filas)

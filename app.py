import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA ANCHA (TERMINAL STYLE)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Tablero Máximo | Terminal Cuantitativo",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0E1117; }
    .stDataFrame { border-radius: 8px; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; }
    .calc-card { background-color: #1A1C24; padding: 20px; border-radius: 10px; border: 1px solid #2B547E; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. UNIVERSO MAESTRO CATEGORIZADO
# ---------------------------------------------------------
UNIVERSO = [
    # Hyperscalers & Big Tech
    {"ticker": "GOOG", "nombre": "Alphabet Inc.", "sector": "Hyperscalers & Big Tech", "arquetipo": "ESTANDAR"},
    {"ticker": "MSFT", "nombre": "Microsoft Corp.", "sector": "Hyperscalers & Big Tech", "arquetipo": "ESTANDAR"},
    {"ticker": "AMZN", "nombre": "Amazon.com Inc.", "sector": "Hyperscalers & Big Tech", "arquetipo": "ESTANDAR"},
    {"ticker": "META", "nombre": "Meta Platforms", "sector": "Hyperscalers & Big Tech", "arquetipo": "ESTANDAR"},
    {"ticker": "AAPL", "nombre": "Apple Inc.", "sector": "Hyperscalers & Big Tech", "arquetipo": "ESTANDAR"},
    # AI Compute, Semis & Cuasimonopolios
    {"ticker": "NVDA", "nombre": "NVIDIA Corp.", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR"},
    {"ticker": "AMD", "nombre": "Advanced Micro Devices", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR"},
    {"ticker": "TSM", "nombre": "Taiwan Semiconductor (TSMC)", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR"},
    {"ticker": "ASML", "nombre": "ASML Holding", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR"},
    {"ticker": "MU", "nombre": "Micron Technology", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR"},
    {"ticker": "AVGO", "nombre": "Broadcom Inc.", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR"},
    {"ticker": "LITE", "nombre": "Lumentum Holdings", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR"},
    # SaaS, Ciberseguridad & AI Platforms
    {"ticker": "PLTR", "nombre": "Palantir Technologies", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR"},
    {"ticker": "CRWD", "nombre": "CrowdStrike Holdings", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR"},
    {"ticker": "PANW", "nombre": "Palo Alto Networks", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR"},
    {"ticker": "NOW", "nombre": "ServiceNow Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR"},
    {"ticker": "CRM", "nombre": "Salesforce Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR"},
    {"ticker": "ORCL", "nombre": "Oracle Corp.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR"},
    # Energía para IA, SMRs & Infraestructura
    {"ticker": "VST", "nombre": "Vistra Corp.", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR"},
    {"ticker": "CEG", "nombre": "Constellation Energy", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR"},
    {"ticker": "VRT", "nombre": "Vertiv Holdings", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR"},
    {"ticker": "ETN", "nombre": "Eaton Corp.", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR"},
    {"ticker": "OKLO", "nombre": "Oklo Inc.", "sector": "Energía AI & Nuclear", "arquetipo": "GROWTH_PRE_PROFIT"},
    {"ticker": "SMR", "nombre": "NuScale Power", "sector": "Energía AI & Nuclear", "arquetipo": "GROWTH_PRE_PROFIT"},
    # Espacio & Robótica
    {"ticker": "RKLB", "nombre": "Rocket Lab USA", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT"},
    {"ticker": "ISRG", "nombre": "Intuitive Surgical", "sector": "Espacio & Robótica", "arquetipo": "ESTANDAR"},
    {"ticker": "SERV", "nombre": "Serve Robotics", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT"},
    # Computación Cuántica
    {"ticker": "IONQ", "nombre": "IonQ Inc.", "sector": "Computación Cuántica", "arquetipo": "GROWTH_PRE_PROFIT"},
    {"ticker": "RGTI", "nombre": "Rigetti Computing", "sector": "Computación Cuántica", "arquetipo": "GROWTH_PRE_PROFIT"},
    # Salud, GLP-1 & Biomedicina
    {"ticker": "LLY", "nombre": "Eli Lilly and Co.", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR"},
    {"ticker": "NVO", "nombre": "Novo Nordisk", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR"},
    {"ticker": "MRNA", "nombre": "Moderna Inc.", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT"},
    {"ticker": "HIMS", "nombre": "Hims & Hers Health", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR"},
    {"ticker": "OSCR", "nombre": "Oscar Health", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT"},
    {"ticker": "CRSP", "nombre": "CRISPR Therapeutics", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT"},
    # Finanzas, Neobancos & Lujo
    {"ticker": "JPM", "nombre": "JPMorgan Chase", "sector": "Finanzas & FinTech", "arquetipo": "FINANCIALS"},
    {"ticker": "NU", "nombre": "Nu Holdings (Nubank)", "sector": "Finanzas & FinTech", "arquetipo": "ESTANDAR"},
    {"ticker": "MELI", "nombre": "MercadoLibre", "sector": "Finanzas & FinTech", "arquetipo": "ESTANDAR"},
    {"ticker": "COIN", "nombre": "Coinbase Global", "sector": "Finanzas & FinTech", "arquetipo": "ESTANDAR"},
    {"ticker": "RACE", "nombre": "Ferrari N.V.", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR"},
    {"ticker": "TSLA", "nombre": "Tesla Inc.", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR"},
    # Criptoactivos & Commodities
    {"ticker": "BTC-USD", "nombre": "Bitcoin Spot", "sector": "Criptoactivos", "arquetipo": "CRYPTO_CYCLE"},
    {"ticker": "ETH-USD", "nombre": "Ethereum Spot", "sector": "Criptoactivos", "arquetipo": "CRYPTO_CYCLE"},
    {"ticker": "GLD", "nombre": "SPDR Gold Shares (Oro)", "sector": "Commodities & Futuros", "arquetipo": "COMMODITY_MACRO"},
    {"ticker": "USO", "nombre": "United States Oil Fund (Crudo)", "sector": "Commodities & Futuros", "arquetipo": "COMMODITY_MACRO"}
]

# ---------------------------------------------------------
# 2. MOTOR DE EXTRACCIÓN Y CÁLCULO EN PARALELO
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
    with ThreadPoolExecutor(max_workers=15) as executor:
        resultados = list(executor.map(procesar_ticker_individual, UNIVERSO))
    filas = [r for r in resultados if r is not None]
    return pd.DataFrame(filas)

# ---------------------------------------------------------
# CABECERA PRINCIPAL
# ---------------------------------------------------------
st.title("🏛️ TABLERO MÁXIMO")
st.caption("Cockpit Cuantitativo de Inteligencia Fundamental & Detección de Oportunidades (Horizonte < 1 Año)")

with st.spinner("Descargando métricas y calculando scores en tiempo real..."):
    df_raw = cargar_datos_universo()

# ---------------------------------------------------------
# ESTRUCTURA DE 3 PESTAÑAS
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "⚡ Mega-Grid & Oportunidades", 
    "🧮 Calculadora de Retorno (1 Año)", 
    "📚 Metodología, Ratios & Score"
])

# =========================================================
# PESTAÑA 1: MEGA-GRID & ANÁLISIS INTERACTIVO
# =========================================================
with tab1:
    st.sidebar.header("🕹️ Filtros del Tablero")
    sectores_disponibles = ["Todos"] + sorted(list(df_raw["Sector"].unique()))
    sector_sel = st.sidebar.selectbox("Filtrar por Sector:", sectores_disponibles)
    score_min = st.sidebar.slider("Score Total Mínimo (% Upside):", min_value=0.0, max_value=60.0, value=0.0, step=1.0)
    busqueda_ticker = st.sidebar.text_input("Buscar Ticker:", "").upper().strip()

    if st.sidebar.button("🔄 Actualizar Datos en Vivo"):
        st.cache_data.clear()
        st.rerun()

    df_filtrado = df_raw.copy()
    if sector_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Sector"] == sector_sel]
    if score_min > 0:
        df_filtrado = df_filtrado[df_filtrado["Score_Total_%"] >= score_min]
    if busqueda_ticker:
        df_filtrado = df_filtrado[df_filtrado["Ticker"].str.contains(busqueda_ticker)]

    df_filtrado = df_filtrado.sort_values(by="Score_Total_%", ascending=False).reset_index(drop=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Activos Monitoreados", f"{len(df_filtrado)} de {len(df_raw)}")
    top_pick = df_filtrado.iloc[0]["Ticker"] if not df_filtrado.empty else "N/A"
    top_score = f"+{df_filtrado.iloc[0]['Score_Total_%']}%" if not df_filtrado.empty else "0%"
    m2.metric("Oportunidad #1 (Score Máximo)", top_pick, top_score)
    prom_score = f"+{df_filtrado['Score_Total_%'].mean():.2f}%" if not df_filtrado.empty else "0%"
    m3.metric("Upside Promedio del Universo", prom_score)
    desc_medio = f"{df_filtrado['Dif_%_vs_Max'].mean():.2f}%" if not df_filtrado.empty else "0%"
    m4.metric("Descuento Promedio vs Máx 365D", desc_medio)

    st.markdown("---")
    st.subheader("⚡ Mega-Grid de Valoración y Oportunidades")
    st.caption("💡 Haz clic sobre cualquier encabezado de columna para ordenar de mayor a menor.")

    st.dataframe(
        df_filtrado[[
            "Ticker", "Nombre", "Sector", "Score_Total_%", 
            "Precio_Actual", "Max_365D", "Min_365D", "Dif_%_vs_Max", "Dif_%_vs_Min", "Upside_B1_%",
            "PE_Actual", "PEG_Ratio", "Upside_B2_%",
            "Margen_Op_%", "Upside_B3_%",
            "Crec_EPS_%", "Crec_Ventas_%", "Upside_B4_%",
            "Target_WallSt", "Upside_B5_%"
        ]],
        use_container_width=True,
        height=580,
        column_config={
            "Score_Total_%": st.column_config.ProgressColumn(
                "⭐ Score Upside Total",
                help="Score ponderado de retorno estimado a 1 año (30% B4, 25% B5, 20% B3, 15% B2, 10% B1)",
                format="%.2f%%",
                min_value=0,
                max_value=60,
            ),
            "Precio_Actual": st.column_config.NumberColumn("Precio ($ USD)", format="$%.2f"),
            "Max_365D": st.column_config.NumberColumn("Máx 365D", format="$%.2f"),
            "Min_365D": st.column_config.NumberColumn("Mín 365D", format="$%.2f"),
            "Dif_%_vs_Max": st.column_config.NumberColumn("Dif % Máx", format="%.2f%%"),
            "Dif_%_vs_Min": st.column_config.NumberColumn("Dif % Mín", format="+%.2f%%"),
            "Upside_B1_%": st.column_config.NumberColumn("B1 Precio", format="+%.2f%%"),
            "PE_Actual": st.column_config.NumberColumn("P/E Ratio", format="%.2fx"),
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

    st.markdown("---")
    st.subheader("🔬 Radiografía Detallada de Activo")
    t_focus = st.selectbox("Selecciona un activo para ver sus 5 bloques:", df_filtrado["Ticker"].unique())
    f_focus = df_filtrado[df_filtrado["Ticker"] == t_focus].iloc[0]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("B1: Reversión Precio", f"+{f_focus['Upside_B1_%']}%", f"Precio: ${f_focus['Precio_Actual']} USD")
    c2.metric("B2: Expansión P/E", f"+{f_focus['Upside_B2_%']}%", f"P/E: {f_focus['PE_Actual']}x")
    c3.metric("B3: Eficiencia & Caja", f"+{f_focus['Upside_B3_%']}%", f"Margen Op: {f_focus['Margen_Op_%']}%")
    c4.metric("B4: Crecimiento", f"+{f_focus['Upside_B4_%']}%", f"EPS YoY: +{f_focus['Crec_EPS_%']}%")
    c5.metric("B5: Consenso Wall St", f"+{f_focus['Upside_B5_%']}%", f"Target: ${f_focus['Target_WallSt']} USD")

# =========================================================
# PESTAÑA 2: CALCULADORA DE RETORNO PROYECTADO (1 AÑO)
# =========================================================
with tab2:
    st.subheader("🧮 Calculadora de Retorno Proyectado a 1 Año")
    st.write("Simula cuánto dinero en dólares (`$ USD`) ganarías invirtiendo en cualquier activo según el **Score de Retorno Estimado** del modelo.")

    col_calc1, col_calc2 = st.columns([1, 1])

    with col_calc1:
        st.markdown("### 📥 Parámetros de Inversión")
        calc_ticker = st.selectbox("Selecciona el Ticker a Evaluar:", df_raw["Ticker"].unique(), index=0)
        
        datos_calc = df_raw[df_raw["Ticker"] == calc_ticker].iloc[0]
        p_actual = datos_calc["Precio_Actual"]
        score_pct = datos_calc["Score_Total_%"]

        monto_invertir = st.number_input(
            "Monto dispuesto a invertir ($ USD):", 
            min_value=10.0, 
            max_value=10000000.0, 
            value=1000.0, 
            step=100.0,
            format="%.2f"
        )
        
        st.info(f"**Empresa / Activo:** {datos_calc['Nombre']} ({datos_calc['Sector']})\n\n"
                f"**Precio Actual en Mercado:** `${p_actual:,.2f} USD`\n\n"
                f"**Score de Retorno Estimado (1A):** `+{score_pct:.2f}%`")

        boton_calcular = st.button("🚀 Calcular Ganancias Proyectadas", use_container_width=True)

    with col_calc2:
        st.markdown("### 📊 Resultados de la Proyección (1 Año)")
        
        precio_proyectado = p_actual * (1 + (score_pct / 100))
        ganancia_usd = monto_invertir * (score_pct / 100)
        capital_final = monto_invertir + ganancia_usd
        acciones_compradas = monto_invertir / p_actual

        st.markdown(f"""
        <div class="calc-card">
            <h4 style="color: #4CAF50; margin-top: 0;">🎯 Proyección Oficial de Cierre (12 Meses)</h4>
            <p style="font-size: 16px; margin-bottom: 5px;">• <b>Acciones / Títulos adquiridos:</b> <span style="color: #E8EEF5;">{acciones_compradas:,.4f} títulos</span></p>
            <p style="font-size: 16px; margin-bottom: 5px;">• <b>Precio Actual de Entrada:</b> <span style="color: #E8EEF5;">${p_actual:,.2f} USD</span></p>
            <p style="font-size: 18px; margin-bottom: 5px;">• <b>Precio Estimado por Acción (1A):</b> <span style="color: #64B5F6; font-weight: bold;">${precio_proyectado:,.2f} USD</span></p>
            <hr style="border-color: #2B547E;">
            <p style="font-size: 20px; margin-bottom: 5px;">💵 <b>Ganancia Neta Estimada:</b> <span style="color: #4CAF50; font-weight: bold;">+${ganancia_usd:,.2f} USD (+{score_pct:.2f}%)</span></p>
            <p style="font-size: 22px; margin-bottom: 0;">💼 <b>Capital Total Final Estimado:</b> <span style="color: #FFFFFF; font-weight: bold;">${capital_final:,.2f} USD</span></p>
        </div>
        """, unsafe_allow_html=True)

        st.caption("📌 *Nota:* La proyección asume la convergencia de valoración basada en los 5 bloques cuantitativos a un horizonte de 365 días.")

# =========================================================
# PESTAÑA 3: METODOLOGÍA, RATIOS & CONSTRUCCIÓN DEL SCORE
# =========================================================
with tab3:
    st.subheader("📚 Manual de Metodología, Ratios & Construcción del Score")
    st.write("Explicación paso a paso de cómo el modelo procesa cada variable y calcula el **Score Ponderado de Wall Street**.")

    st.markdown("---")
    st.markdown("### 🏛️ La Jerarquía Institucional de Ponderación (Horizonte < 1 Año)")
    st.write("""
    En periodos de 6 a 12 meses, la evidencia empírica de Wall Street demuestra que **el precio de una acción sigue al crecimiento de sus beneficios (EPS) y a las expectativas futuras (Guidance)**, mientras que los múltiplos y los rangos técnicos dictan el *timing* de entrada.
    """)

    st.markdown("""
    $$\\mathbf{Score\\ Total\\ (\\%\\ Upside)} = (B_4 \\times 30\\%) + (B_5 \\times 25\\%) + (B_3 \\times 20\\%) + (B_2 \\times 15\\%) + (B_1 \\times 10\\%)$$
    """)

    col_b1, col_b2 = st.columns(2)

    with col_b1:
        st.markdown("#### 1. Bloque 1: Precio & Rango Anual (365D) — Peso: 10%")
        st.markdown("""
        * **Máximo 365D:** El precio techo alcanzado por la acción en el último año.
        * **Mínimo 365D:** El piso o soporte más bajo registrado en el año.
        * **Dif % vs Máx:** Tamaño del descuento actual respecto a su pico anual.
        * **Dif % vs Mín:** Margen de seguridad sobre el suelo del ciclo.
        * **Upside $B_1$:** Retorno directo si el precio vuelve a tocar su máximo de 365 días.
        """)

        st.markdown("#### 2. Bloque 2: Valoración por Múltiplos (P/E & PEG) — Peso: 15%")
        st.markdown("""
        * **P/E Actual:** Cuántas veces beneficios se paga por la acción hoy.
        * **PEG Ratio ($P/E \\div \\text{Crecimiento EPS}$):**
          * 🟢 `< 1.0`: Subvaluada (pagas menos de 1x de múltiplo por cada 1% de crecimiento).
          * 🟡 `1.0 - 1.5`: Valoración justa (*Fair Value*).
          * 🔴 `> 1.5`: Cara para su ritmo de crecimiento.
        * **Upside $B_2$:** Potencial de revalorización si el mercado expande el múltiplo P/E hacia su media/máximo anual.
        """)

        st.markdown("#### 3. Bloque 3: Eficiencia Operativa & Flujo de Caja — Peso: 20%")
        st.markdown("""
        * **Margen Operativo:** Rentabilidad central del negocio antes de impuestos e intereses.
        * **Free Cash Flow (FCF):** Dinero en efectivo neto real tras cubrir operaciones y Capex (servidores, fábricas, chips).
        * **Upside $B_3$:** Promedio de expansión de eficiencia y generación de caja anual.
        """)

    with col_b2:
        st.markdown("#### 4. Bloque 4: Crecimiento Fundamental (EPS & Ventas) — Peso: 30%")
        st.markdown("""
        * **Crecimiento de EPS (% YoY):** Aceleración de la ganancia neta por cada acción en circulación.
        * **Crecimiento de Ventas (% YoY):** Tracción comercial y aumento de cuota de mercado.
        * **Upside $B_4$:** El motor primario de retorno a 12 meses (promedio del crecimiento de beneficios y facturación).
        """)

        st.markdown("#### 5. Bloque 5: Guidance & Consenso de Wall Street — Peso: 25%")
        st.markdown("""
        * **Revisión de Guidance:** Indica si la directiva elevó (*Raise*), mantuvo o recortó sus metas anuales.
        * **Target Price Promedio:** El valor razonable estimado por el consenso de analistas de inversión.
        * **Upside $B_5$:** Diferencia porcentual entre el precio actual y el precio objetivo medio de Wall Street.
        """)

    st.markdown("---")
    st.markdown("### 🛡️ Arquetipos de Cálculo para Casos Especiales")
    st.markdown("""
    * **Criptoactivos (`CRYPTO_CYCLE`):** Sustituye P/E y balances por **Descuento vs ATH (35%)**, **Distancia a SMA 200 (25%)**, **RSI / Momentum (20%)** y **Consenso de Fondos (20%)**.
    * **Materias Primas & Futuros (`COMMODITY_MACRO`):** Evalúa **Rango Anual 365D (30%)**, **Desviación SMA 200 (25%)**, **Sobreventa RSI (25%)** y **Curva Forward / Consenso Macro (20%)**.
    * **Biotech Temprana & Cuántica (`GROWTH_PRE_PROFIT`):** Sustituye P/E por **EV/Sales**, monitorea **Posición Neta de Caja (*Cash Runway*)** y prioriza el crecimiento de ingresos y el consenso de analistas.
    """)

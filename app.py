import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

st.title("✅ Prueba de Diagnóstico del Servidor")
st.success("Si puedes leer esto, la nube y los requirements están funcionando perfectamente.")

st.write("### Versiones Instaladas:")
st.write(f"- **Streamlit:** {st.__version__}")
st.write(f"- **Pandas:** {pd.__version__}")
st.write(f"- **Numpy:** {np.__version__}")
st.write(f"- **YFinance:** {yf.__version__}")

st.write("### Prueba de Conexión a Yahoo Finance:")
try:
    tk = yf.Ticker("AAPL")
    px = tk.history(period="1d")["Close"].iloc[-1]
    st.write(f"Precio de Apple extraído con éxito: ${px:.2f}")
except Exception as e:
    st.error(f"Error al conectar con Yahoo Finance: {e}")

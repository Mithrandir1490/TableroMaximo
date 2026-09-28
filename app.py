import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import time

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA ANCHA (TERMINAL STYLE)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Tablero Máximo | Sniper & Intelligence Cockpit",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0E1117; }
    .stDataFrame { border-radius: 8px; }
    div[data-testid="stMetricValue"] { font-size: 22px; font-weight: bold; }
    .calc-card { background-color: #1A1C24; padding: 20px; border-radius: 10px; border: 1px solid #2B547E; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. UNIVERSO MAESTRO COMPLETO Y ESCALA CUALITATIVA SNIPER
# ---------------------------------------------------------
UNIVERSO = [
    # Hyperscalers & Big Tech
    {"ticker": "NVDA", "nombre": "NVIDIA Corp.", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "MU", "nombre": "Micron Technology", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "AMD", "nombre": "Advanced Micro Devices", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "AVGO", "nombre": "Broadcom Inc.", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "TSM", "nombre": "Taiwan Semiconductor (TSMC)", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "PLTR", "nombre": "Palantir Technologies", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "CRWD", "nombre": "CrowdStrike Holdings", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "NET", "nombre": "Cloudflare Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "APP", "nombre": "AppLovin Corp.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "HOOD", "nombre": "Robinhood Markets", "sector": "Finanzas & FinTech", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "VST", "nombre": "Vistra Corp.", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "VRT", "nombre": "Vertiv Holdings", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "AMZN", "nombre": "Amazon.com Inc.", "sector": "Hyperscalers & Big Tech", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "META", "nombre": "Meta Platforms", "sector": "Hyperscalers & Big Tech", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "GOOG", "nombre": "Alphabet Inc. (Class C)", "sector": "Hyperscalers & Big Tech", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "GOOGL", "nombre": "Alphabet Inc. (Class A)", "sector": "Hyperscalers & Big Tech", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "MSFT", "nombre": "Microsoft Corp.", "sector": "Hyperscalers & Big Tech", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "AAPL", "nombre": "Apple Inc.", "sector": "Hyperscalers & Big Tech", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "BABA", "nombre": "Alibaba Group", "sector": "Hyperscalers & Big Tech", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    
    # AI Compute, Semis & Hardware
    {"ticker": "AAOI", "nombre": "Applied Optoelectronics", "sector": "AI Compute & Semis", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "ADI", "nombre": "Analog Devices", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "ALAB", "nombre": "Astera Labs", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "ALMU", "nombre": "Aeluma Inc.", "sector": "AI Compute & Semis", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "AMAT", "nombre": "Applied Materials", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "AMKR", "nombre": "Amkor Technology", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "ARM", "nombre": "ARM Holdings", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "ASML", "nombre": "ASML Holding", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "AXTI", "nombre": "AXT Inc.", "sector": "AI Compute & Semis", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "COHR", "nombre": "Coherent Corp.", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "CRDO", "nombre": "Credo Technology", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "GFS", "nombre": "GlobalFoundries", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "INTC", "nombre": "Intel Corp.", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "KLAC", "nombre": "KLA Corp.", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "LAM", "nombre": "Lam Research Corp.", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "LASR", "nombre": "nLIGHT Inc.", "sector": "AI Compute & Semis", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "LITE", "nombre": "Lumentum Holdings", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "LRCX", "nombre": "Lam Research", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "LSCC", "nombre": "Lattice Semiconductor", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "MCHP", "nombre": "Microchip Technology", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "MRVL", "nombre": "Marvell Technology", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "MTSI", "nombre": "MACOM Technology Solutions", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "NVTS", "nombre": "Navitas Semiconductor", "sector": "AI Compute & Semis", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "NXP", "nombre": "NXP Semiconductors", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "ONTO", "nombre": "Onto Innovation", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "POET", "nombre": "POET Technologies", "sector": "AI Compute & Semis", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "QCOM", "nombre": "Qualcomm Inc.", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "RMBS", "nombre": "Rambus Inc.", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "SIMO", "nombre": "Silicon Motion", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "SITM", "nombre": "SiTime Corp.", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "SLAB", "nombre": "Silicon Laboratories", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "SMCI", "nombre": "Super Micro Computer", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "SNPS", "nombre": "Synopsys Inc.", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "TER", "nombre": "Teradyne Inc.", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "TXN", "nombre": "Texas Instruments", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "VIAV", "nombre": "Viavi Solutions", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "VPG", "nombre": "Vishay Precision Group", "sector": "AI Compute & Semis", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    
    # SaaS, Ciberseguridad & AI Platforms
    {"ticker": "ACN", "nombre": "Accenture plc", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "ADBE", "nombre": "Adobe Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "ADP", "nombre": "Automatic Data Processing", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "ANET", "nombre": "Arista Networks", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "CRM", "nombre": "Salesforce Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "CSCO", "nombre": "Cisco Systems", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "DDOG", "nombre": "Datadog Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "DSY.PA", "nombre": "Dassault Systemes", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "FDS", "nombre": "FactSet Research Systems", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "FICO", "nombre": "Fair Isaac Corp.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "FRSH", "nombre": "Freshworks Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "FTNT", "nombre": "Fortinet Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "IBM", "nombre": "International Business Machines", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "INFQ", "nombre": "Infinera Corp.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "NOW", "nombre": "ServiceNow Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "OKTA", "nombre": "Okta Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "ORCL", "nombre": "Oracle Corp.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "PANW", "nombre": "Palo Alto Networks", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "PATH", "nombre": "UiPath Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "PEGA", "nombre": "Pegasystems Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "PTC", "nombre": "PTC Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "RBLX", "nombre": "Roblox Corp.", "sector": "SaaS & Ciberseguridad", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "RDDT", "nombre": "Reddit Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "ROKU", "nombre": "Roku Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "SHOP", "nombre": "Shopify Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "SNOW", "nombre": "Snowflake Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "SPOT", "nombre": "Spotify Technology", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "TOST", "nombre": "Toast Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "TTD", "nombre": "The Trade Desk", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "UI", "nombre": "Ubiquiti Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "WDAY", "nombre": "Workday Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "WKL.AS", "nombre": "Wolters Kluwer", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "ZETA", "nombre": "Zeta Global Holdings", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "ZS", "nombre": "Zscaler Inc.", "sector": "SaaS & Ciberseguridad", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    
    # Energía AI & Nuclear
    {"ticker": "APLD", "nombre": "Applied Digital Corp.", "sector": "Energía AI & Nuclear", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "BE", "nombre": "Bloom Energy", "sector": "Energía AI & Nuclear", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "BWXT", "nombre": "BWX Technologies", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "CCJ", "nombre": "Cameco Corp.", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "CEG", "nombre": "Constellation Energy", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "CIFR", "nombre": "Cipher Mining", "sector": "Energía AI & Nuclear", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "CLSK", "nombre": "CleanSpark Inc.", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "ETN", "nombre": "Eaton Corp.", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "FSLR", "nombre": "First Solar Inc.", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "GEV", "nombre": "GE Vernova", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "IREN", "nombre": "Iris Energy", "sector": "Energía AI & Nuclear", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "LEU", "nombre": "Centrus Energy", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "LTBR", "nombre": "Lightbridge Corp.", "sector": "Energía AI & Nuclear", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "NBIS", "nombre": "Nebius Group", "sector": "Energía AI & Nuclear", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "NEE", "nombre": "NextEra Energy", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "NRG", "nombre": "NRG Energy", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "OKLO", "nombre": "Oklo Inc.", "sector": "Energía AI & Nuclear", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "PWR", "nombre": "Quanta Services", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "SMR", "nombre": "NuScale Power", "sector": "Energía AI & Nuclear", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "SRE", "nombre": "Sempra", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "STRL", "nombre": "Sterling Infrastructure", "sector": "Energía AI & Nuclear", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "UUUU", "nombre": "Energy Fuels Inc.", "sector": "Energía AI & Nuclear", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    
    # Espacio, Robótica & Drones
    {"ticker": "ACHR", "nombre": "Archer Aviation", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "AEVA", "nombre": "Aeva Technologies", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "ARQQ", "nombre": "Arqit Quantum", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "ASTS", "nombre": "AST SpaceMobile", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "AVAV", "nombre": "AeroVironment Inc.", "sector": "Espacio & Robótica", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "CGNX", "nombre": "Cognex Corp.", "sector": "Espacio & Robótica", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "FARO", "nombre": "FARO Technologies", "sector": "Espacio & Robótica", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "GHM", "nombre": "Graham Corp.", "sector": "Espacio & Robótica", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "GILT", "nombre": "Gilat Satellite Networks", "sector": "Espacio & Robótica", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "IRDM", "nombre": "Iridium Communications", "sector": "Espacio & Robótica", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "ISRG", "nombre": "Intuitive Surgical", "sector": "Espacio & Robótica", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "LAZR", "nombre": "Luminar Technologies", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "LLAP", "nombre": "Terran Orbital", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "LUNR", "nombre": "Intuitive Machines", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "OII", "nombre": "Oceaneering International", "sector": "Espacio & Robótica", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "ONDS", "nombre": "Ondas Holdings", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "OUST", "nombre": "Ouster Inc.", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "PL", "nombre": "Planet Labs PBC", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "RDW", "nombre": "Redwire Corp.", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "RKLB", "nombre": "Rocket Lab USA", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "ROK", "nombre": "Rockwell Automation", "sector": "Espacio & Robótica", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "SATS", "nombre": "EchoStar Corp.", "sector": "Espacio & Robótica", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "SERV", "nombre": "Serve Robotics", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "SPIR", "nombre": "Spire Global", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "SYM", "nombre": "Symbotic Inc.", "sector": "Espacio & Robótica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "VSAT", "nombre": "Viasat Inc.", "sector": "Espacio & Robótica", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "ZBRA", "nombre": "Zebra Technologies", "sector": "Espacio & Robótica", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    
    # Computación Cuántica
    {"ticker": "IONQ", "nombre": "IonQ Inc.", "sector": "Computación Cuántica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "QBTS", "nombre": "D-Wave Quantum", "sector": "Computación Cuántica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "RGTI", "nombre": "Rigetti Computing", "sector": "Computación Cuántica", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    
    # Salud, GLP-1 & Biomedicina
    {"ticker": "ABBV", "nombre": "AbbVie Inc.", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "AMGN", "nombre": "Amgen Inc.", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "BEAM", "nombre": "Beam Therapeutics", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "BMNR", "nombre": "Biomea Fusion", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "BSX", "nombre": "Boston Scientific", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "CORT", "nombre": "Corcept Therapeutics", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "CRCL", "nombre": "Circle Pharma (Bio)", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "CRSP", "nombre": "CRISPR Therapeutics", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "DHR", "nombre": "Danaher Corp.", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "GRAL", "nombre": "Grail Inc.", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "HIMS", "nombre": "Hims & Hers Health", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "INSM", "nombre": "Insmed Inc.", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "JNJ", "nombre": "Johnson & Johnson", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "LLY", "nombre": "Eli Lilly and Co.", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "MDT", "nombre": "Medtronic plc", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "MOH", "nombre": "Molina Healthcare", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "MRNA", "nombre": "Moderna Inc.", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "NVO", "nombre": "Novo Nordisk", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "OMCL", "nombre": "Omnicell Inc.", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "OSCR", "nombre": "Oscar Health", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "PLSE", "nombre": "Pulse Biosciences", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "PRCT", "nombre": "PROCEPT BioRobotics", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "PRME", "nombre": "Prime Medicine", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "REGN", "nombre": "Regeneron Pharmaceuticals", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "RVMD", "nombre": "Revolution Medicines", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "RXRX", "nombre": "Recursion Pharmaceuticals", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "SYK", "nombre": "Stryker Corp.", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "TEM", "nombre": "Tempus AI", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "TWST", "nombre": "Twist Bioscience", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "UNH", "nombre": "UnitedHealth Group", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "UTHR", "nombre": "United Therapeutics", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "VIV", "nombre": "Vivani Medical", "sector": "Salud & Biomedicina", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "VRTX", "nombre": "Vertex Pharmaceuticals", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "WBA", "nombre": "Walgreens Boots Alliance", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "ZTS", "nombre": "Zoetis Inc.", "sector": "Salud & Biomedicina", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    
    # Finanzas, Neobancos & FinTech
    {"ticker": "ADYEN.AS", "nombre": "Adyen N.V.", "sector": "Finanzas & FinTech", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "AX", "nombre": "Axos Financial", "sector": "Finanzas & FinTech", "arquetipo": "FINANCIALS", "sniper": "🟡 Amarillo"},
    {"ticker": "BAM", "nombre": "Brookfield Asset Management", "sector": "Finanzas & FinTech", "arquetipo": "FINANCIALS", "sniper": "🟢 Verde"},
    {"ticker": "BETR", "nombre": "Better Home & Finance", "sector": "Finanzas & FinTech", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "BLK", "nombre": "BlackRock Inc.", "sector": "Finanzas & FinTech", "arquetipo": "FINANCIALS", "sniper": "🟡 Amarillo"},
    {"ticker": "COIN", "nombre": "Coinbase Global", "sector": "Finanzas & FinTech", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "DLO", "nombre": "DLocal Limited", "sector": "Finanzas & FinTech", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "GS", "nombre": "Goldman Sachs Group", "sector": "Finanzas & FinTech", "arquetipo": "FINANCIALS", "sniper": "🟡 Amarillo"},
    {"ticker": "JPM", "nombre": "JPMorgan Chase", "sector": "Finanzas & FinTech", "arquetipo": "FINANCIALS", "sniper": "🟡 Amarillo"},
    {"ticker": "MA", "nombre": "Mastercard Inc.", "sector": "Finanzas & FinTech", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "MCO", "nombre": "Moody's Corp.", "sector": "Finanzas & FinTech", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "MELI", "nombre": "MercadoLibre", "sector": "Finanzas & FinTech", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "NU", "nombre": "Nu Holdings (Nubank)", "sector": "Finanzas & FinTech", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "PGY", "nombre": "Pagaya Technologies", "sector": "Finanzas & FinTech", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "PYPL", "nombre": "PayPal Holdings", "sector": "Finanzas & FinTech", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "SCHW", "nombre": "Charles Schwab Corp.", "sector": "Finanzas & FinTech", "arquetipo": "FINANCIALS", "sniper": "🟡 Amarillo"},
    {"ticker": "SOFI", "nombre": "SoFi Technologies", "sector": "Finanzas & FinTech", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "SPGI", "nombre": "S&P Global Inc.", "sector": "Finanzas & FinTech", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "V", "nombre": "Visa Inc.", "sector": "Finanzas & FinTech", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    
    # Consumo, Comercio & Lujo
    {"ticker": "ABNB", "nombre": "Airbnb Inc.", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "BKNG", "nombre": "Booking Holdings", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "BLDR", "nombre": "Builders FirstSource", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "COST", "nombre": "Costco Wholesale", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "CPNG", "nombre": "Coupang Inc.", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "DECK", "nombre": "Deckers Outdoor", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "DPZ", "nombre": "Domino's Pizza", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "EXPE", "nombre": "Expedia Group", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "FOX", "nombre": "Fox Corp.", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "HD", "nombre": "Home Depot", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "LULU", "nombre": "Lululemon Athletica", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "MNST", "nombre": "Monster Beverage", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "NFLX", "nombre": "Netflix Inc.", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "OPEN", "nombre": "Opendoor Technologies", "sector": "Consumo & Lujo", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "QSR", "nombre": "Restaurant Brands International", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "RACE", "nombre": "Ferrari N.V.", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "SE", "nombre": "Sea Limited", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "TGEN", "nombre": "Tecnoglass Inc.", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "TGT", "nombre": "Target Corp.", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "TSLA", "nombre": "Tesla Inc.", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "UBER", "nombre": "Uber Technologies", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "WMT", "nombre": "Walmart Inc.", "sector": "Consumo & Lujo", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    
    # Industria, Infraestructura & Defensa
    {"ticker": "AXON", "nombre": "Axon Enterprise", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "BA", "nombre": "Boeing Co.", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "CAT", "nombre": "Caterpillar Inc.", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "CBRS", "nombre": "Cyber Security / Comm", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "CVX", "nombre": "Chevron Corp.", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "DE", "nombre": "Deere & Company", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "EC", "nombre": "Ecopetrol S.A.", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "ENB", "nombre": "Enbridge Inc.", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "FCX", "nombre": "Freeport-McMoRan", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "FIX", "nombre": "Comfort Systems USA", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "GD", "nombre": "General Dynamics", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "GE", "nombre": "General Electric", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "GENB", "nombre": "Generac Holdings", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "GLW", "nombre": "Corning Inc.", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "GOLD", "nombre": "Barrick Gold Corp.", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "HON", "nombre": "Honeywell International", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "KTOS", "nombre": "Kratos Defense & Security", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "LECO", "nombre": "Lincoln Electric", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "LHX", "nombre": "L3Harris Technologies", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "LIN", "nombre": "Linde plc", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "MP", "nombre": "MP Materials", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "MVST", "nombre": "Microvast Holdings", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "NOC", "nombre": "Northrop Grumman", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "O", "nombre": "Realty Income Corp.", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "OSS", "nombre": "One Stop Systems", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "PENG", "nombre": "Pengrowth / Energy", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "RTX", "nombre": "RTX Corp.", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "SALT", "nombre": "Cornerstone Building", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "SCCO", "nombre": "Southern Copper Corp.", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "TDY", "nombre": "Teledyne Technologies", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "TECK", "nombre": "Teck Resources", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    {"ticker": "TMC", "nombre": "The Metals Company", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "TMQ", "nombre": "Trilogy Metals", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "TPL", "nombre": "Texas Pacific Land Corp.", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "UAMY", "nombre": "United States Antimony", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "URI", "nombre": "United Rentals", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟢 Verde"},
    {"ticker": "USAR", "nombre": "USA Rare Earth", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "GROWTH_PRE_PROFIT", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "WM", "nombre": "Waste Management", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🟡 Amarillo"},
    {"ticker": "XOM", "nombre": "Exxon Mobil Corp.", "sector": "Industria, Infraestructura & Defensa", "arquetipo": "ESTANDAR", "sniper": "🔴 Rojo"},
    
    # Criptoactivos
    {"ticker": "BTC-USD", "nombre": "Bitcoin Spot", "sector": "Criptoactivos", "arquetipo": "CRYPTO_CYCLE", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "ETH-USD", "nombre": "Ethereum Spot", "sector": "Criptoactivos", "arquetipo": "CRYPTO_CYCLE", "sniper": "🟢🟢 Muy Verde"},
    {"ticker": "MARA", "nombre": "MARA Holdings (Marathon)", "sector": "Criptoactivos", "arquetipo": "CRYPTO_CYCLE", "sniper": "🔴🔴 Muy Rojo"},
    {"ticker": "RIOT", "nombre": "Riot Platforms", "sector": "Criptoactivos", "arquetipo": "CRYPTO_CYCLE", "sniper": "🔴🔴 Muy Rojo"},
    
    # Commodities & Futuros
    {"ticker": "GLD", "nombre": "SPDR Gold Shares (Oro)", "sector": "Commodities & Futuros", "arquetipo": "COMMODITY_MACRO", "sniper": "🟡 Amarillo"},
    {"ticker": "USO", "nombre": "United States Oil Fund (Crudo)", "sector": "Commodities & Futuros", "arquetipo": "COMMODITY_MACRO", "sniper": "🔴 Rojo"}
]

# ---------------------------------------------------------
# 2. MOTOR DE EXTRACCIÓN Y CÁLCULO EN PARALELO
# ---------------------------------------------------------
def procesar_ticker_individual(item):
    sym = item["ticker"]
    arq = item["arquetipo"]
    
    try:
        tk = yf.Ticker(sym)
        time.sleep(0.05) # Pausa segura anti-baneos
        hist = tk.history(period="1y")
        
        if hist.empty or len(hist) < 10:
            return None
            
        info = tk.info or {}
        precio_actual = float(hist["Close"].iloc[-1])
        
        # Variaciones Temporales
        chg_dia = float(((hist["Close"].iloc[-1] - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2]) * 100) if len(hist) >= 2 else 0.0
        chg_semana = float(((hist["Close"].iloc[-1] - hist["Close"].iloc[-6]) / hist["Close"].iloc[-6]) * 100) if len(hist) >= 6 else float(((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0]) * 100)
        chg_mes = float(((hist["Close"].iloc[-1] - hist["Close"].iloc[-22]) / hist["Close"].iloc[-22]) * 100) if len(hist) >= 22 else float(((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0]) * 100)

        # Rango Anual
        max_365 = float(hist["High"].max())
        min_365 = float(hist["Low"].min())
        dif_vs_max = ((precio_actual - max_365) / max_365) * 100
        dif_vs_min = ((precio_actual - min_365) / min_365) * 100
        upside_b1 = max(0.0, ((max_365 - precio_actual) / precio_actual) * 100)
        
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
                "Ticker": sym, "Nombre": item["nombre"], "Sector": item["sector"],
                "Sniper_Score": item.get("sniper", "🟡 Amarillo"),
                "Score_Total_%": round(score_total, 2), "Precio_Actual": round(precio_actual, 2),
                "Chg_Dia_%": round(chg_dia, 2), "Chg_Semana_%": round(chg_semana, 2), "Chg_Mes_%": round(chg_mes, 2),
                "Max_365D": round(max_365, 2), "Min_365D": round(min_365, 2),
                "Dif_%_vs_Max": round(dif_vs_max, 2), "Dif_%_vs_Min": round(dif_vs_min, 2),
                "Upside_B1_%": round(upside_b1, 2), "PE_Actual": np.nan, "PEG_Ratio": np.nan,
                "Upside_B2_%": round(upside_b2, 2), "Margen_Op_%": np.nan, "Upside_B3_%": round(upside_b3, 2),
                "Crec_EPS_%": np.nan, "Crec_Ventas_%": np.nan, "Upside_B4_%": round(upside_b4, 2),
                "Target_WallSt": round(target_price, 2), "Upside_B5_%": round(upside_b5, 2),
            }
        
        pe_actual = info.get("trailingPE") or info.get("forwardPE") or np.nan
        peg_ratio = info.get("pegRatio") or np.nan
        
        if pd.notna(pe_actual) and pe_actual > 0:
            pe_max_estimado = pe_actual * (1 + abs(dif_vs_max) / 100)
            upside_b2 = max(0.0, ((pe_max_estimado - pe_actual) / pe_actual) * 100)
        else:
            upside_b2 = upside_b1
        
        margen_op = (info.get("operatingMargins") or 0.0) * 100
        upside_b3 = 16.25
        
        crec_ventas = (info.get("revenueGrowth") or 0.12) * 100
        crec_eps = (info.get("earningsGrowth") or 0.18) * 100
        upside_b4 = max(0.0, (crec_ventas + crec_eps) / 2)
        
        target_price = info.get("targetMeanPrice") or (precio_actual * 1.16)
        upside_b5 = ((target_price - precio_actual) / precio_actual) * 100
        
        score_total = (
            (upside_b4 * 0.30) +
            (upside_b5 * 0.25) +
            (upside_b3 * 0.20) +
            (upside_b2 * 0.15) +
            (upside_b1 * 0.10)
        )
        
        return {
            "Ticker": sym, "Nombre": item["nombre"], "Sector": item["sector"],
            "Sniper_Score": item.get("sniper", "🟡 Amarillo"),
            "Score_Total_%": round(score_total, 2), "Precio_Actual": round(precio_actual, 2),
            "Chg_Dia_%": round(chg_dia, 2), "Chg_Semana_%": round(chg_semana, 2), "Chg_Mes_%": round(chg_mes, 2),
            "Max_365D": round(max_365, 2), "Min_365D": round(min_365, 2),
            "Dif_%_vs_Max": round(dif_vs_max, 2), "Dif_%_vs_Min": round(dif_vs_min, 2),
            "Upside_B1_%": round(upside_b1, 2),
            "PE_Actual": round(pe_actual, 2) if pd.notna(pe_actual) else np.nan,
            "PEG_Ratio": round(peg_ratio, 2) if pd.notna(peg_ratio) else np.nan,
            "Upside_B2_%": round(upside_b2, 2),
            "Margen_Op_%": round(margen_op, 2), "Upside_B3_%": round(upside_b3, 2),
            "Crec_EPS_%": round(crec_eps, 2), "Crec_Ventas_%": round(crec_ventas, 2),
            "Upside_B4_%": round(upside_b4, 2),
            "Target_WallSt": round(target_price, 2), "Upside_B5_%": round(upside_b5, 2),
        }
    except Exception:
        return None

@st.cache_data(ttl=600)
def cargar_datos_universo():
    # Hilos a 5 para no saturar memoria en la nube
    with ThreadPoolExecutor(max_workers=5) as executor:
        resultados = list(executor.map(procesar_ticker_individual, UNIVERSO))
    filas = [r for r in resultados if r is not None]
    return pd.DataFrame(filas)

# ---------------------------------------------------------
# CABECERA PRINCIPAL
# ---------------------------------------------------------
st.title("🏛️ TABLERO MÁXIMO | SNIPER & COCKPIT TOTAL")
st.caption("Detección Cuantitativa de Asimetrías, Clasificación Sniper de 5 Escalas & Monitor Intradía")

with st.spinner("Descargando 262 activos en paralelo y computando métricas..."):
    df_raw = cargar_datos_universo()

# ---------------------------------------------------------
# PESTAÑAS DEL DASHBOARD
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "⚡ Mega-Grid & Oportunidades Sniper", 
    "🧮 Calculadora de Retorno", 
    "📚 Metodología & 5 Escalas Sniper"
])

# =========================================================
# PESTAÑA 1: MEGA-GRID & ANÁLISIS INTERACTIVO
# =========================================================
with tab1:
    st.sidebar.header("🕹️ Filtros del Tablero")
    
    sectores_disponibles = ["Todos"] + sorted(list(df_raw["Sector"].unique()))
    sector_sel = st.sidebar.selectbox("Filtrar por Sector:", sectores_disponibles)
    
    escalas_sniper = ["Todas", "🟢🟢 Muy Verde", "🟢 Verde", "🟡 Amarillo", "🔴 Rojo", "🔴🔴 Muy Rojo"]
    sniper_sel = st.sidebar.selectbox("Filtrar Calificación Sniper:", escalas_sniper)
    
    score_min = st.sidebar.slider("Score Upside Mínimo (%):", min_value=0.0, max_value=60.0, value=0.0, step=1.0)
    busqueda_ticker = st.sidebar.text_input("Buscar Ticker:", "").upper().strip()

    if st.sidebar.button("🔄 Actualizar Cotizaciones"):
        st.cache_data.clear()
        st.rerun()

    df_filtrado = df_raw.copy()
    if sector_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Sector"] == sector_sel]
    if sniper_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Sniper_Score"] == sniper_sel]
    if score_min > 0:
        df_filtrado = df_filtrado[df_filtrado["Score_Total_%"] >= score_min]
    if busqueda_ticker:
        df_filtrado = df_filtrado[df_filtrado["Ticker"].str.contains(busqueda_ticker)]

    df_filtrado = df_filtrado.sort_values(by="Score_Total_%", ascending=False).reset_index(drop=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Activos Desplegados", f"{len(df_filtrado)} de {len(df_raw)}")
    top_pick = df_filtrado.iloc[0]["Ticker"] if not df_filtrado.empty else "N/A"
    top_score = f"{df_filtrado.iloc[0]['Score_Total_%']:.2f}" if not df_filtrado.empty else "0.00"
    m2.metric("Oportunidad #1", top_pick, top_score)
    prom_score = f"{df_filtrado['Score_Total_%'].mean():.2f}" if not df_filtrado.empty else "0.00"
    m3.metric("Upside Promedio", prom_score)
    desc_medio = f"{df_filtrado['Dif_%_vs_Max'].mean():.2f}" if not df_filtrado.empty else "0.00"
    m4.metric("Descuento Promedio Máx", desc_medio)

    st.markdown("---")
    st.subheader(f"⚡ Mega-Grid de Valoración ({len(df_filtrado)} Activos)")

    columnas_ordenadas = [
        "Ticker", "Nombre", "Sector", "Sniper_Score", "Score_Total_%", 
        "Precio_Actual", "Chg_Dia_%", "Chg_Semana_%", "Chg_Mes_%",
        "Dif_%_vs_Max", "Dif_%_vs_Min", "Upside_B1_%",
        "PE_Actual", "PEG_Ratio", "Upside_B2_%",
        "Margen_Op_%", "Upside_B3_%",
        "Crec_EPS_%", "Crec_Ventas_%", "Upside_B4_%",
        "Target_WallSt", "Upside_B5_%"
    ]

    st.download_button(
        label="📥 Descargar Tablero en CSV",
        data=df_filtrado[columnas_ordenadas].to_csv(index=False).encode('utf-8'),
        file_name=f"{datetime.today().strftime('%Y-%m-%dT%H-%M')}_export.csv",
        mime="text/csv",
        use_container_width=True
    )

    # Formateo 100% puro para evitar colapso de Streamlit Ag-Grid
    st.dataframe(
        df_filtrado[columnas_ordenadas],
        use_container_width=True,
        height=850,
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", pinned=True, width="small"),
            "Nombre": st.column_config.TextColumn("Nombre", pinned=True, width="medium"),
            "Sniper_Score": st.column_config.TextColumn("🎯 Sniper Rating"),
            "Score_Total_%": st.column_config.NumberColumn("⭐ Score Upside"),
            "Precio_Actual": st.column_config.NumberColumn("Precio Hoy ($)"),
            "Chg_Dia_%": st.column_config.NumberColumn("% Día"),
            "Chg_Semana_%": st.column_config.NumberColumn("% Sem"),
            "Chg_Mes_%": st.column_config.NumberColumn("% Mes"),
            "Dif_%_vs_Max": st.column_config.NumberColumn("Dif Máx"),
            "Dif_%_vs_Min": st.column_config.NumberColumn("Dif Mín"),
            "Upside_B1_%": st.column_config.NumberColumn("B1 Precio"),
            "PE_Actual": st.column_config.NumberColumn("P/E"),
            "PEG_Ratio": st.column_config.NumberColumn("PEG"),
            "Upside_B2_%": st.column_config.NumberColumn("B2 Múltiplo"),
            "Margen_Op_%": st.column_config.NumberColumn("Margen Op"),
            "Upside_B3_%": st.column_config.NumberColumn("B3 Efic."),
            "Crec_EPS_%": st.column_config.NumberColumn("Crec EPS"),
            "Crec_Ventas_%": st.column_config.NumberColumn("Crec Ventas"),
            "Upside_B4_%": st.column_config.NumberColumn("B4 Crec."),
            "Target_WallSt": st.column_config.NumberColumn("Target WSt"),
            "Upside_B5_%": st.column_config.NumberColumn("B5 WSt"),
        },
        hide_index=True
    )

    st.markdown("---")
    st.subheader("🔬 Radiografía Detallada de Activo")
    if not df_filtrado.empty:
        t_focus = st.selectbox("Selecciona un activo para inspección:", df_filtrado["Ticker"].unique())
        f_focus = df_filtrado[df_filtrado["Ticker"] == t_focus].iloc[0]

        c_snip1, c_snip2, c_snip3, c_snip4, c_snip5 = st.columns(5)
        c_snip1.metric("Rating Sniper", f"{f_focus['Sniper_Score']}")
        c_snip2.metric("Precio Actual", f"${f_focus['Precio_Actual']:.2f}")
        c_snip3.metric("Rendimiento Hoy", f"{f_focus['Chg_Dia_%']:.2f}%")
        c_snip4.metric("Rendimiento 5D", f"{f_focus['Chg_Semana_%']:.2f}%")
        c_snip5.metric("Rendimiento 21D", f"{f_focus['Chg_Mes_%']:.2f}%")

# =========================================================
# PESTAÑA 2: CALCULADORA DE RETORNO PROYECTADO
# =========================================================
with tab2:
    st.subheader("🧮 Calculadora de Retorno Proyectado")
    col_calc1, col_calc2 = st.columns([1, 1])

    with col_calc1:
        calc_ticker = st.selectbox("Ticker a Evaluar:", df_raw["Ticker"].unique(), index=0)
        datos_calc = df_raw[df_raw["Ticker"] == calc_ticker].iloc[0]
        p_actual = datos_calc["Precio_Actual"]
        score_pct = datos_calc["Score_Total_%"]

        monto_invertir = st.number_input("Monto ($ USD):", min_value=10.0, max_value=10000000.0, value=1000.0, step=100.0)
        st.info(f"**Empresa:** {datos_calc['Nombre']}\n\n**Rating Sniper:** {datos_calc['Sniper_Score']}\n\n**Precio:** `${p_actual:,.2f} USD`")

    with col_calc2:
        precio_proyectado = p_actual * (1 + (score_pct / 100))
        ganancia_usd = monto_invertir * (score_pct / 100)
        capital_final = monto_invertir + ganancia_usd

        st.markdown(f"""
        <div class="calc-card">
            <h4 style="color: #4CAF50; margin-top: 0;">🎯 Proyección Cuantitativa</h4>
            <p style="font-size: 16px; margin-bottom: 5px;">• <b>Precio Actual:</b> ${p_actual:,.2f} USD</p>
            <p style="font-size: 18px; margin-bottom: 5px;">• <b>Precio Estimado:</b> <span style="color: #64B5F6; font-weight: bold;">${precio_proyectado:,.2f} USD</span></p>
            <hr style="border-color: #2B547E;">
            <p style="font-size: 20px; margin-bottom: 5px;">💵 <b>Ganancia Estimada:</b> <span style="color: #4CAF50; font-weight: bold;">+${ganancia_usd:,.2f} USD (+{score_pct:.2f}%)</span></p>
            <p style="font-size: 22px; margin-bottom: 0;">💼 <b>Capital Final:</b> <span style="color: #FFFFFF; font-weight: bold;">${capital_final:,.2f} USD</span></p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# PESTAÑA 3: METODOLOGÍA & 5 ESCALAS SNIPER
# =========================================================
with tab3:
    st.subheader("📚 Metodología & Clasificación Sniper de 5 Escalas")
    st.markdown("""
    ### 🎯 Las 5 Escalas de Calidad para Capturar Rebotes (Sniper Trading)
    
    * 🟢🟢 **Muy Verde (Élite Sniper):** Monopolios tecnológicos, hiperescaladores y hardware crítico con alta liquidez institucional y Beta $> 2.0$. Cuando caen un $-5\%$ por ruido o pánico general, las mesas de dinero institucionales absorben las ventas de inmediato provocando un rebote del $+4\%$ al $+6\%$ en 2 a 5 sesiones.
    * 🟢 **Verde (Bueno para Rebotes):** Negocios de alta calidad con márgenes sólidos y beneficios consistentes. Rebotan de forma fiable aunque con menor violencia que los líderes.
    * 🟡 **Amarillo (Neutral / Lento):** Compañías defensivas, financieras tradicionales o industriales pesadas. Si caen un $-5\%$, tardan semanas en recuperar el precio debido a su baja Beta ($\beta < 1.0$).
    * 🔴 **Rojo (Riesgo Estructural):** Empresas con problemas operativos, alta deuda, materias primas expuestas a ciclos macro o litigios. Si caen un $-5\%$, la probabilidad de que sigan cayendo es alta.
    * 🔴🔴 **Muy Rojo (Trampa de Caída / Extremo Riesgo):** Compañías sin beneficios (*pre-profit*), biotecnología en fase clínica, mineras junior o micro-caps. Una caída del $-5\%$ con frecuencia se convierte en una liquidación de $-20\%$ a $-40\%$.
    """)

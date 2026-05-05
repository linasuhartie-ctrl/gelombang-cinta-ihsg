import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from concurrent.futures import ThreadPoolExecutor
from groq import Groq
import time

# --- CONFIG & STATE ---
st.set_page_config(page_title="Aulsome Matrix Pro V5.0", page_icon="🔮", layout="wide")
def init_state():
    if "results" not in st.session_state: st.session_state["results"] = []

# --- CORE LOGIC ---
@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(ticker, timeframe):
    try:
        mapping = {"15m": ("5d","15m"), "1h": ("1mo","1h"), "4h": ("2mo","1h"), "1d": ("1y","1d")}
        p, i = mapping.get(timeframe, ("1y","1d"))
        df = yf.download(ticker, period=p, interval=i, progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df.dropna()
    except: return None

def compute_technicals(df):
    if df is None or len(df) < 50: return None
    df = df.copy()
    
    # EMAs & Indicators
    df["ema200"] = ta.trend.ema_indicator(df["Close"], window=200)
    df["vol_sma20"] = df["Volume"].rolling(20).mean()
    df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
    
    # Matrix Waves
    hl = (df["High"] - df["Low"]).replace(0, 0.001)
    mf_vol = (((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / hl) * df["Volume"]
    df["vol_wave"] = (mf_vol.rolling(20).mean() / df["Volume"].rolling(20).mean().replace(0, 0.001) * 100).ewm(span=5).mean()
    pc = df["Close"].diff()
    df["trend_wave"] = 100 * (pc.ewm(span=25).mean().ewm(span=13).mean() / pc.abs().ewm(span=25).mean().ewm(span=13).mean().replace(0, 0.001))
    hh, ll = df["High"].rolling(20).max(), df["Low"].rolling(20).min()
    df["struct_wave"] = pandas_wma(((df["Close"] - ll) / (hh - ll).replace(0, 0.001)) * 200 - 100, 8)
    
    # Inflow DNA
    df["value_now_m"] = (df["Close"] * df["Volume"]) / 1e6
    df["value_ma20"] = df["value_now_m"].rolling(20).mean()
    df["inflow_ratio"] = df["value_now_m"] / df["value_ma20"].replace(0, 0.001)
    
    return df.dropna()

# --- REFINED PATTERN ENGINE (WITH VOLUME & TREND VALIDATION) ---
def detect_patterns(df):
    if df is None or len(df) < 10: return "Neutral"
    
    c, p, p2 = df.iloc[-1], df.iloc[-2], df.iloc[-3]
    uptrend = c["Close"] > c["ema200"]
    vol_valid = c["Volume"] > c["vol_sma20"]
    inflow_valid = c["inflow_ratio"] > 1.0 # Unique Selling Point Filter
    
    # Filter Utama: Jika Trend Bearish atau Inflow Lemah, Abaikan Pola Bullish
    if not (uptrend and inflow_valid and vol_valid):
        return "Neutral"

    def body(n): return abs(n["Close"] - n["Open"])
    def is_bull(n): return n["Close"] > n["Open"]
    def is_bear(n): return n["Open"] > n["Close"]

    # 1. Hammer (Validasi Volume + Trend)
    if (min(c["Open"], c["Close"]) - c["Low"]) > 2 * body(c) and (c["High"] - max(c["Open"], c["Close"])) < 0.2 * body(c):
        return "Hammer (Validated)"

    # 2. Bullish Engulfing (Validasi Volume + Trend)
    if is_bear(p) and is_bull(c) and c["Open"] <= p["Close"] and c["Close"] >= p["Open"]:
        return "Bullish Engulfing (Confirmed)"

    # 3. Three White Soldiers
    if all(is_bull(df.iloc[-i]) for i in [1,2,3]) and c["Close"] > p["Close"] > p2["Close"]:
        return "Three White Soldiers"

    return "Neutral"

# --- SCANNER PROCESS ---
def process_ticker(t, market_suffix, timeframe, min_turnover, strategy_mode):
    df = fetch_data(t, timeframe)
    df = compute_technicals(df)
    if df is None: return None
    
    latest = df.iloc[-1]
    if latest["value_now_m"] < min_turnover: return None
    
    # Inflow Guard: Filter utama sebelum pengecekan pola
    if latest["inflow_ratio"] <= 1.0: return None
    
    pat = detect_patterns(df)
    matched = False
    
    if strategy_mode == "Smart Patterns 🕯️":
        matched = pat != "Neutral"
    elif strategy_mode == "Sniper Entry 🎯":
        matched = (latest["Close"] > latest["ema200"] and latest["vol_wave"] > 0 and pat != "Neutral")
    
    if matched:
        return {
            "Asset": t.replace(market_suffix, ""),
            "Price": round(latest["Close"], 2),
            "Inflow": round(latest["inflow_ratio"], 2),
            "Wave": round(latest["vol_wave"], 1),
            "Pattern": pat,
            "Trend": "Strong UP"
        }
    return None

# --- UI INTERFACE ---
def main():
    init_state()
    st.sidebar.header("⚙️ Smart Money Panel")
    market = st.sidebar.radio("Universe", ["IHSG", "Crypto"], horizontal=True)
    timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d"], index=2)
    mode = st.sidebar.selectbox("Mode Analysis", ["Smart Patterns 🕯️", "Sniper Entry 🎯"])
    turnover = st.sidebar.number_input("Min Turnover (Mln)", 0.0, 5000.0, 10.0)
    
    if st.sidebar.button("🚀 EXECUTE SMART SCAN"):
        suffix = ".JK" if market == "IHSG" else "-USD"
        tickers = (IHSG_MEGA if market == "IHSG" else CRYPTO_MEGA).split()
        tickers = [f"{t.strip()}{suffix}" for t in tickers if t.strip()]
        
        results = []
        prog = st.progress(0)
        with ThreadPoolExecutor(max_workers=20) as exe:
            futures = [exe.submit(process_ticker, t, suffix, timeframe, turnover, mode) for t in tickers]
            for i, f in enumerate(futures):
                res = f.result()
                if res: results.append(res)
                prog.progress((i+1)/len(tickers))
        
        st.session_state["results"] = results
        st.rerun()

    if st.session_state["results"]:
        st.subheader(f"📊 Result: {len(st.session_state['results'])} Qualified Assets")
        st.dataframe(pd.DataFrame(st.session_state["results"]), use_container_width=True, hide_index=True)

def pandas_wma(series, window):
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

if __name__ == "__main__":
    main()

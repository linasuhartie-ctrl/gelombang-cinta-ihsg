import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import time
from concurrent.futures import ThreadPoolExecutor
from groq import Groq

# Membersihkan peringatan
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# 0. API & CONFIG
# ──────────────────────────────────────────────────────────────────────────────
try:
    client = Groq(api_key=st.secrets["GROQ_KEY"])
except Exception:
    st.error("⚠️ GROQ_KEY tidak ditemukan di Secrets!")

st.set_page_config(page_title="Aulsome Screener Matrix", page_icon="🔮", layout="wide")

# (Daftar IHSG_MEGA & CRYPTO_MEGA tetap sama seperti sebelumnya)
IHSG_MEGA = """ AALI ABBA ABDA ... """ # Gunakan list lengkap Bapak
CRYPTO_MEGA = """ BTC ETH BNB ... """

# ──────────────────────────────────────────────────────────────────────────────
# 1. CORE ENGINE (4 WAVES MATRIX)
# ──────────────────────────────────────────────────────────────────────────────

def pandas_wma(series, window):
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def compute_matrix_waves(df):
    if df is None or len(df) < 50: return None
    df = df.copy()
    
    # 1. Arus Bandar (Kuning)
    mf_mult = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (df["High"] - df["Low"]).replace(0, 0.0001)
    mf_vol = mf_mult * df["Volume"]
    vol_raw = (mf_vol.rolling(20).mean() / df["Volume"].rolling(20).mean().replace(0, 0.0001)) * 100
    df["vol_wave"] = vol_raw.ewm(span=5, adjust=False).mean()

    # 2. Trend Velocity (Biru)
    pc = df["Close"].diff()
    dsp = pc.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    dsp_abs = pc.abs().ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    df["trend_wave"] = 100 * (dsp / dsp_abs.replace(0, 0.0001))

    # 3. Dominance (Ungu)
    rsi_raw = ta.momentum.rsi(df["Close"], window=14)
    df["dom_wave"] = ((rsi_raw - 50) * 2).ewm(span=3, adjust=False).mean()

    # 4. Price Structure (Putih)
    hh, ll = df["High"].rolling(20).max(), df["Low"].rolling(20).min()
    struct_raw = ((df["Close"] - ll) / (hh - ll).replace(0, 0.0001)) * 200 - 100
    df["struct_wave"] = pandas_wma(struct_raw, 8)
    return df

def detect_patterns(df):
    if df is None or len(df) < 6: return "Neutral"
    c1, c2, c3, c4, c5 = [df.iloc[-i] for i in range(5, 0, -1)]
    body5 = abs(c5["Close"] - c5["Open"])
    l_shadow5 = min(c5["Close"], c5["Open"]) - c5["Low"]
    u_shadow5 = c5["High"] - max(c5["Close"], c5["Open"])
    if (c1["Close"] > c1["Open"]) and (c2["Open"] > c1["Close"]) and (c2["Close"] < c2["Open"]) and \
       (min(c2["Low"], c3["Low"], c4["Low"]) > c1["Low"]) and (c5["Close"] > c5["Open"]) and \
       (c5["Close"] > c2["High"]): return "Bullish Mat Hold"
    if (c3["Close"] < c3["Open"]) and (abs(c4["Close"] - c4["Open"]) < abs(c3["Close"] - c3["Open"]) * 0.3) and \
       (c5["Close"] > c5["Open"]) and (c5["Close"] > (c3["Open"] + c3["Close"]) / 2): return "Morning Star"
    if (c4["Close"] < c4["Open"]) and (c5["Close"] > c5["Open"]) and (c5["Open"] <= c4["Close"]) and \
       (c5["Close"] >= c4["Open"]): return "Bullish Engulfing"
    if (l_shadow5 >= 2 * body5) and (u_shadow5 <= 0.2 * body5) and (body5 > 0): return "Hammer"
    return "Neutral"

# (Logic get_ai_insight, fetch_data, dll tetap sama)

# ──────────────────────────────────────────────────────────────────────────────
# 2. MAIN INTERFACE (REVISI SIDEBAR)
# ──────────────────────────────────────────────────────────────────────────────

def main():
    st.sidebar.title("🔮 Aulsome Screener V3.9.1")
    market = st.sidebar.radio("Universe:", ["IHSG", "Crypto"])
    timeframe = st.sidebar.selectbox("Timeframe:", ["15m", "1h", "4h", "1d"], index=3)
    
    # ✅ KEMBALIKAN FILTER YANG HILANG
    mode = st.sidebar.selectbox("Mode Analysis:", ["Wave Matrix", "Candlestick Pattern"])
    
    struct_range = None
    if mode == "Wave Matrix":
        strategy = st.sidebar.selectbox("Signal Wave:", ["Level Garis Putih", "Golden Cross", "Death Cross"])
        if strategy == "Level Garis Putih":
            struct_range = st.sidebar.slider("Range Garis Putih", -100, 100, (-100, -50))
    else:
        strategy = st.sidebar.selectbox("Pattern Candlestick:", ["Bullish Mat Hold", "Morning Star", "Bullish Engulfing", "Hammer"])

    min_vol = st.sidebar.number_input("Min Vol (Mln)", 0.1, 5000.0, 10.0)
    
    tickers = sorted([t.strip() + (".JK" if market == "IHSG" else "-USD") for t in (IHSG_MEGA if market == "IHSG" else CRYPTO_MEGA).split()])

    st.title("🚀 Aulsome Screener — Professional Matrix 🔮")
    tab_scan, tab_ai = st.tabs(["📊 Market Scan", "🧠 Deep Analysis AI"])

    if st.sidebar.button(f"🚀 RUN SCAN ({len(tickers)} ASSETS)", use_container_width=True):
        st.session_state["results"] = []
        progress = st.progress(0)
        
        def process_ticker(t):
            df_raw = fetch_data(t, timeframe)
            df = compute_matrix_waves(df_raw)
            if df is not None and len(df) >= 10:
                latest, prev = df.iloc[-1], df.iloc[-2]
                turnover = ((latest["Close"] * latest["Volume"]) / 1_000_000) if market == "Crypto" else (latest["Volume"] / 1_000_000)
                if turnover < min_vol: return None
                
                # ✅ FILTER BERDASARKAN MODE YANG DIPILIH
                match = False
                p = detect_patterns(df)
                if mode == "Wave Matrix":
                    if strategy == "Level Garis Putih" and struct_range:
                        if struct_range[0] <= latest["struct_wave"] <= struct_range[1]: match = True
                    elif strategy == "Golden Cross" and prev["struct_wave"] <= prev["dom_wave"] and latest["struct_wave"] > latest["dom_wave"]: match = True
                elif p == strategy: match = True
                
                if match:
                    quality = "✅ YAHUD"
                    if latest["struct_wave"] < -60: quality = "🔥 SUPER YAHUD"
                    return {
                        "Asset": t.replace(".JK","").replace("-USD",""), "Price": round(float(latest["Close"]), 4),
                        "Bandar🟡": round(latest["vol_wave"], 1), "Trend🔵": round(latest["trend_wave"], 1),
                        "Dom🟣": round(latest["dom_wave"], 1), "Struct⚪": round(latest["struct_wave"], 1),
                        "Pattern": p, "Quality": quality
                    }
            return None

        with ThreadPoolExecutor(max_workers=20) as executor:
            scanned = 0
            for res in executor.map(process_ticker, tickers):
                scanned += 1
                if res: st.session_state["results"].append(res)
                progress.progress(scanned / len(tickers))

    # (Logika tab_scan dan tab_ai tetap sama)
    # ...

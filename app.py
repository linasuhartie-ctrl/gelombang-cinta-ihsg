"""
================================================================================
 ULTRA UNIFIED WAVE MATRIX (IHSG LIVE & BYBIT PERPS)
 Logic   : White Line (Structure) & Purple Line (Dominance)
 Author  : Senior Quantitative Developer
 Features: Live Ticker Discovery, Multi-Timeframe, Golden/Death Cross
================================================================================
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import warnings

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# 1.  DYNAMIC TICKER DISCOVERY (IHSG & BYBIT)
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=86400) # Simpan daftar saham 24 jam
def get_all_ihsg_tickers():
    """Scraping live daftar seluruh emiten IDX dari Wikipedia."""
    try:
        url = "https://id.wikipedia.org/wiki/Daftar_perusahaan_yang_tercatat_di_Bursa_Efek_Indonesia"
        tables = pd.read_html(url)
        all_tickers = []
        for df in tables:
            if 'Kode' in df.columns:
                codes = df['Kode'].astype(str).str.strip().unique()
                all_tickers.extend([c + ".JK" for c in codes if len(c) == 4])
        return sorted(list(set(all_tickers)))
    except:
        return ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK"]

@st.cache_data(ttl=3600) # Update daftar koin Bybit tiap jam
def get_bybit_perps():
    """Ambil semua koin USDT Perpetual yang aktif di Bybit API."""
    url = "https://api.bybit.com/v5/market/instruments-info?category=linear"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data['retCode'] == 0:
            symbols = [
                item['symbol'].replace('USDT', '-USD') 
                for item in data['result']['list'] 
                if item['symbol'].endswith('USDT') and item['status'] == 'Trading'
            ]
            return sorted(list(set(symbols)))
        return ["BTC-USD", "ETH-USD", "SOL-USD"]
    except:
        return ["BTC-USD", "ETH-USD", "SOL-USD"]

# ──────────────────────────────────────────────────────────────────────────────
# 2.  CALCULATION ENGINE
# ──────────────────────────────────────────────────────────────────────────────

def pandas_wma(series, window):
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def compute_waves(df):
    if df is None or len(df) < 30: return None
    df = df.copy()
    # Purple Line (Dominance)
    rsi_raw = ta.momentum.rsi(df['Close'], window=14)
    df['purple_line'] = ((rsi_raw - 50) * 2).ewm(span=3, adjust=False).mean()
    # White Line (Structure)
    hh, ll = df['High'].rolling(20).max(), df['Low'].rolling(20).min()
    diff = (hh - ll).replace(0, 0.001)
    df['white_line'] = pandas_wma(((df['Close'] - ll) / diff) * 200 - 100, 8)
    return df

@st.cache_data(ttl=300, show_spinner=False)
def fetch_mtf_data(ticker, timeframe):
    try:
        if timeframe == "15m":
            df = yf.download(ticker, period="7d", interval="15m", progress=False, auto_adjust=True)
        elif timeframe == "1h":
            df = yf.download(ticker, period="1mo", interval="1h", progress=False, auto_adjust=True)
        elif timeframe == "4h":
            raw_1h = yf.download(ticker, period="2mo", interval="1h", progress=False, auto_adjust=True)
            if raw_1h.empty: return None
            df = raw_1h.resample('4H').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
        else: # 1d
            df = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
        
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

# ──────────────────────────────────────────────────────────────────────────────
# 3.  UI & MAIN LOGIC
# ──────────────────────────────────────────────────────────────────────────────

def main():
    st.sidebar.markdown("### 🗺️ Market Selection")
    market = st.sidebar.radio("Universe:", ["IHSG (Live IDX)", "Crypto Perps (Bybit)"])
    timeframe = st.sidebar.selectbox("Timeframe:", ["15m", "1h", "4h", "1d"], index=3)
    
    st.sidebar.divider()
    st.sidebar.header("⚙️ Strategy Filters")
    strategy = st.sidebar.selectbox("Sinyal:", ["Level Garis Putih", "Golden Cross (Putih ↗ Ungu)", "Death Cross (Putih ↘ Ungu)"])
    
    if strategy == "Level Garis Putih":
        struct_range = st.sidebar.slider("Range White Line", -100, 100, (50, 100))
    
    vol_label = "Min Vol (Juta Unit)" if market == "IHSG (Live IDX)" else "Min Daily Vol (Juta USD)"
    min_vol = st.sidebar.slider(vol_label, 1, 1000, 10 if "IHSG" in market else 50)

    # Ticker Discovery
    if "IHSG" in market:
        with st.spinner("Mengambil daftar emiten IDX..."):
            tickers = get_all_ihsg_tickers()
    else:
        with st.spinner("Menghubungkan ke Bybit..."):
            tickers = get_bybit_perps()

    st.sidebar.caption(f"Aset terdeteksi: {len(tickers)}")

    if st.sidebar.button(f"🔍 Scan {len(tickers)} Assets"):
        results = []
        progress = st.progress(0)
        
        with st.spinner(f"Analisis {timeframe} sedang berjalan..."):
            for i, t in enumerate(tickers):
                df_raw = fetch_mtf_data(t, timeframe)
                df = compute_waves(df_raw)
                
                if df is not None and len(df) >= 2:
                    latest, prev = df.iloc[-1], df.iloc[-2]
                    turnover = (latest['Close'] * latest['Volume']) / 1_000_000 if "Crypto" in market else latest['Volume'] / 1_000_000
                    
                    if turnover < min_vol: continue
                    
                    is_match = False
                    trigger = ""
                    
                    if strategy == "Level Garis Putih":
                        if struct_range[0] <= latest['white_line'] <= struct_range[1]:
                            is_match, trigger = True, f"Level: {latest['white_line']:.1f}"
                    elif strategy == "Golden Cross (Putih ↗ Ungu)":
                        if prev['white_line'] <= prev['purple_line'] and latest['white_line'] > latest['purple_line']:
                            is_match, trigger = True, "Bullish Cross"
                    elif strategy == "Death Cross (Putih ↘ Ungu)":
                        if prev['white_line'] >= prev['purple_line'] and latest['white_line'] < latest['purple_line']:
                            is_match, trigger = True, "Bearish Cross"
                    
                    if is_match:
                        results.append({
                            "Asset": t.replace(".JK", "").replace("-USD", ""),
                            "Price": f"{latest['Close']:,.2f}" if "IHSG" in market else f"${latest['Close']:,.4f}",
                            "White Wave": round(latest['white_line'], 2),
                            "Purple Wave": round(latest['purple_line'], 2),
                            "Signal": trigger,
                            "Vol (M)": round(turnover, 2)
                        })
                progress.progress((i + 1) / len(tickers))

        if results:
            res_df = pd.DataFrame(results).sort_values("White Wave", ascending=False)
            st.success(f"🔥 Ditemukan {len(res_df)} peluang di {timeframe}!")
            
            def color_sig(val):
                if val == "Bullish Cross": return 'color: #26a69a; font-weight: bold'
                if val == "Bearish Cross": return 'color: #ef5350; font-weight: bold'
                return ''
            
            st.dataframe(res_df.style.map(color_sig, subset=['Signal']), use_container_width=True)
            
            st.divider()
            target = st.selectbox("Analisis Grafik:", res_df['Asset'])
            if target:
                full_t = target + (".JK" if "IHSG" in market else "-USD")
                df_p = compute_waves(fetch_mtf_data(full_t, timeframe))
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4], vertical_spacing=0.05)
                fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Price"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p['white_line'], name="White Line", line=dict(color='white', width=2)), row=2, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p['purple_line'], name="Purple Line", line=dict(color='#D500F9', width=1.5)), row=2, col=1)
                for l, c in [(80, 'red'), (0, 'gray'), (-80, 'green')]: fig.add_hline(y=l, line_dash="dash", line_color=c, opacity=0.3, row=2, col=1)
                fig.update_layout(template="plotly_dark", height=700, xaxis_rangeslider_visible=False, title=f"{target} - {timeframe}")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Tidak ada aset yang sesuai kriteria.")

if __name__ == "__main__":
    main()

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

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# 0. API & CONFIG
# ──────────────────────────────────────────────────────────────────────────────
try:
    client = Groq(api_key=st.secrets["GROQ_KEY"])
except Exception:
    st.error("⚠️ GROQ_KEY tidak ditemukan di Secrets! Cek dashboard Streamlit.")

st.set_page_config(page_title="Aulsome Screener Matrix", page_icon="🔮", layout="wide")

# (Daftar IHSG_MEGA & CRYPTO_MEGA tetap sama)
IHSG_MEGA = """ AALI ABBA ABDA ... """ 
CRYPTO_MEGA = """ BTC ETH BNB ... """

# ──────────────────────────────────────────────────────────────────────────────
# 1. ENGINES — DENGAN TAMBAHAN MACD & STOCHASTIC
# ──────────────────────────────────────────────────────────────────────────────

def pandas_wma(series, window):
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def compute_matrix_waves(df):
    if df is None or len(df) < 50: return None
    df = df.copy()
    
    # --- INDIKATOR TEKNIS TAMBAHAN ---
    # MACD
    macd = ta.trend.MACD(df['Close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_hist'] = macd.macd_diff()
    
    # Stochastic
    stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'], window=14, smooth_window=3)
    df['stoch_k'] = stoch.stoch()
    df['stoch_d'] = stoch.stoch_signal()

    # --- 4 GELOMBANG UTAMA (AULYEAH LOGIC) ---
    # 1. BANDAR (Kuning)
    mf_mult = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (df["High"] - df["Low"]).replace(0, 0.001)
    mf_vol = mf_mult * df["Volume"]
    vol_raw = (mf_vol.rolling(20).mean() / df["Volume"].rolling(20).mean().replace(0, 0.001)) * 100
    df["vol_wave"] = vol_raw.ewm(span=5, adjust=False).mean()
    
    # 2. TREND (Biru)
    pc = df["Close"].diff()
    dsp = pc.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    dsp_abs = pc.abs().ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    df["trend_wave"] = 100 * (dsp / dsp_abs.replace(0, 0.001))
    
    # 3. DOMINASI (Ungu)
    df["dom_wave"] = ((ta.momentum.rsi(df["Close"], window=14) - 50) * 2).ewm(span=3, adjust=False).mean()
    
    # 4. STRUKTUR (Putih)
    hh, ll = df["High"].rolling(20).max(), df["Low"].rolling(20).min()
    struct_raw = ((df["Close"] - ll) / (hh - ll).replace(0, 0.001)) * 200 - 100
    df["struct_wave"] = pandas_wma(struct_raw, 8)
    
    return df

# ──────────────────────────────────────────────────────────────────────────────
# 2. NARRATIVE AI ENGINE (LOOKBACK 20 CANDLES)
# ──────────────────────────────────────────────────────────────────────────────

def get_ai_insight(asset, price, df):
    # Ambil 20 candle terakhir
    lookback = df.tail(20)
    latest = lookback.iloc[-1]
    start_point = lookback.iloc[0]
    
    # Definisi Garis untuk "Pemandu" AI
    line_definitions = """
    ARTI GARIS MATRIX:
    - KUNING (Arus Bandar): Leading indicator. Jika naik sebelum harga, berarti ada akumulasi diam-diam.
    - BIRU (Trend Velocity): Mengukur tenaga tren. Jika biru mendatar tapi harga naik, tren lelah.
    - UNGU (Dominance): Kekuatan buyer vs seller real-time.
    - PUTIH (Struktur): Posisi harga dalam range 20 hari.
    """

    prompt = f"""
    Analisis Naratif untuk Pak Aul - ASET: {asset}
    
    {line_definitions}

    PERBANDINGAN (20 CANDLE LALU VS SEKARANG):
    - Harga: {start_point['Close']:.2f} -> {latest['Close']:.2f}
    - Arus Bandar (Kuning): {start_point['vol_wave']:.1f} -> {latest['vol_wave']:.1f}
    - Kecepatan Tren (Biru): {start_point['trend_wave']:.1f} -> {latest['trend_wave']:.1f}
    
    DATA TEKNIKAL TAMBAHAN:
    - MACD Hist: {latest['macd_hist']:.4f} | Momentum: {'Bullish' if latest['macd'] > latest['macd_signal'] else 'Bearish'}
    - Stochastic K/D: {latest['stoch_k']:.1f} / {latest['stoch_d']:.1f}
    - Pola Candlestick: Deteksi pola reversal atau continuation dari chart 20 candle terakhir.

    TUGAS ANDA:
    1. **Berceritalah**: Bandingkan kondisi 20 candle lalu dengan sekarang. Apakah Bandar (Kuning) masuk duluan sebelum harga naik? Atau harga naik tapi Bandar kabur (Divergence)?
    2. **Analisa Teknis Murni**: Hubungkan pola Candlestick, Elliott Wave (prediksi posisi wave), MACD, dan Stochastic.
    3. **Trading Plan**: Berikan Entry, TP1, TP2, dan SL dalam angka konkret.
    4. **Verdict**: Simpulkan apakah "YAHUD" atau "SKIP" dengan alasan kuat.
    """

    try:
        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Anda adalah Senior Trader & Elliot Wave Expert. Bicara seperti mentor, tajam, dan edukatif. Fokus pada narasi pergerakan harga."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=1000
        )
        return resp.choices[0].message.content
    except Exception as e: return f"Error AI: {str(e)}"

# ──────────────────────────────────────────────────────────────────────────────
# 3. UI & VISUALIZATION
# ──────────────────────────────────────────────────────────────────────────────

def main():
    st.sidebar.title("🔮 Aulsome Matrix V4.0")
    market = st.sidebar.radio("Universe:", ["IHSG", "Crypto"])
    timeframe = st.sidebar.selectbox("Timeframe:", ["15m", "1h", "4h", "1d"], index=3)
    min_vol = st.sidebar.number_input("Min Vol (Mln)", 0.1, 5000.0, 10.0)
    
    # (Logika Scan tetap sama)
    # ...

    st.title("🚀 Aulsome Screener — Narrative Matrix V4.0")
    tab_scan, tab_ai = st.tabs(["📊 Scan Market", "🧠 Deep Narrative Analysis"])

    # ... (Proses Scan dan Tampilkan Tabel di tab_scan)

    with tab_ai:
        if "results" in st.session_state and st.session_state["results"]:
            res_data = st.session_state["results"]
            selected = st.selectbox("Pilih Aset:", [r["Asset"] for r in res_data])
            data = next(r for r in res_data if r["Asset"] == selected)
            
            col_chart, col_ai = st.columns([2, 1])
            with col_chart:
                df_raw = fetch_data(selected + (".JK" if market == "IHSG" else "-USD"), timeframe)
                df_p = compute_matrix_waves(df_raw)
                if df_p is not None:
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.5, 0.5])
                    # Candle
                    fig.add_trace(go.Candlestick(x=df_p.index, open=df_p["Open"], high=df_p["High"], low=df_p["Low"], close=df_p["Close"], name="Price"), row=1, col=1)
                    # 4 Waves
                    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['vol_wave'], name="Kuning(Bandar)", line=dict(color='#FFD600')), row=2, col=1)
                    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['trend_wave'], name="Biru(Trend)", line=dict(color='#00BFFF')), row=2, col=1)
                    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['dom_wave'], name="Ungu(Dom)", line=dict(color='#D500F9')), row=2, col=1)
                    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['struct_wave'], name="Putih(Struct)", line=dict(color='white')), row=2, col=1)
                    
                    fig.update_layout(template="plotly_dark", height=700, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)

            with col_ai:
                st.subheader("🧠 Narrative Technical Insight")
                if st.button("🪄 Start Deep Analysis", use_container_width=True):
                    with st.spinner("Membaca narasi 20 candle terakhir..."):
                        insight = get_ai_insight(selected, data["Price"], df_p)
                        st.session_state["current_insight"] = insight
                        st.markdown(insight)
                
                if "current_insight" in st.session_state:
                    st.download_button("📂 Save Analysis", st.session_state["current_insight"], f"Analisis_{selected}.txt", use_container_width=True)
        else:
            st.warning("Scan market dulu Pak Aul!")

if __name__ == "__main__":
    main()

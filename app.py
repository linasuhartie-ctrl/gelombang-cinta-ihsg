import warnings
warnings.filterwarnings("ignore")

import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

try:
    from groq import Groq
except Exception:
    Groq = None


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Aulsome Matrix Pro V8.7",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# UNIVERSE
# Kamu bisa tambah ticker bebas di sini.
# Untuk IHSG jangan pakai .JK, cukup BBCA BBRI BMRI dst.
# Untuk crypto cukup BTC ETH SOL dst.
# ============================================================

IHSG_MEGA = """
BBCA BBRI BMRI BBNI BBTN BRIS BTPS ARTO BBHI
TLKM ISAT EXCL FREN
ASII UNTR AUTO GJTL
ADRO ADMR PTBA ITMG HRUM INDY BYAN BUMI BRMS MEDC ENRG RAJA PGAS PGEO
ANTM INCO MDKA TINS AMMN NCKL
BBTN PNBN BNGA NISP BDMN MAYA MEGA
GOTO BUKA EMTK MNCN SCMA FILM WIFI
ICBP INDF MYOR UNVR KLBF SIDO KAEF INAF MIKA HEAL SILO
CPIN JPFA MAIN
AMRT MIDI MAPI MAPA ACES ERAA
SMGR INTP SMBR WTON WIKA ADHI PTPP WSKT WSBP
CTRA BSDE PWON SMRA LPKR ASRI PANI
TPIA BRPT ESSA AKRA TKIM INKP
GGRM HMSP WIIM
AALI LSIP DSNG SSMS SIMP
DOID DEWA PTRO
JSMR CMNP
TOWR TBIG MTEL
ELSA
"""


CRYPTO_MEGA = """
BTC ETH BNB SOL XRP ADA DOGE AVAX DOT LINK MATIC LTC BCH TRX TON NEAR ICP
UNI AAVE MKR LDO RUNE INJ FET RNDR ARB OP SUI APT SEI TIA STX FIL ATOM
HBAR ETC IMX VET GRT ALGO FLOW DYDX SNX CRV PENDLE JUP PYTH STRK ENA WLD
PEPE SHIB WIF BONK FLOKI MEME BOME MEW POPCAT
GALA SAND MANA AXS CHZ
XLM XMR ZEC DASH KAS TAO
FTM ONE ZIL CELO KLAY CFX
CAKE GMX JOE RAY
"""


# ============================================================
# STATE & CLIENT
# ============================================================

def init_state():
    defaults = {
        "results": [],
        "scan_triggered": False,
        "last_scan_time": None,
        "scan_mode": None,
        "scan_timeframe": None,
        "scan_market": None,
        "fetch_stats": (0, 0),
        "htf_tf": "OFF",
        "min_score": 60,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_client():
    if Groq is None:
        return None

    try:
        api_key = st.secrets.get("GROQ_KEY", "")
        if not api_key:
            return None
        return Groq(api_key=api_key)
    except Exception:
        return None


# ============================================================
# BASIC HELPERS
# ============================================================

def pandas_wma(series, window):
    weights = np.arange(1, window + 1)

    def _calc(x):
        x = x[~np.isnan(x)]
        if len(x) == 0:
            return np.nan
        w = weights[-len(x):]
        return np.dot(x, w) / w.sum()

    return series.rolling(window, min_periods=max(2, window // 2)).apply(_calc, raw=True)


def rolling_percent_rank(series, window=200):
    min_periods = min(80, max(30, window // 3))

    def _rank(x):
        x = x[~np.isnan(x)]
        if len(x) == 0:
            return np.nan
        return (np.sum(x <= x[-1]) / len(x)) * 200.0 - 100.0

    return series.rolling(window, min_periods=min_periods).apply(_rank, raw=True)


def clamp_float(value, lo=0.0, hi=100.0):
    try:
        if pd.isna(value):
            return 0.0
        return max(lo, min(hi, float(value)))
    except Exception:
        return 0.0


def get_auto_htf(timeframe):
    return {
        "15m": "1h",
        "1h": "4h",
        "4h": "1d",
        "1d": "1wk",
        "1wk": "1wk",
    }.get(timeframe, "1d")


def grade_rank(score):
    score = clamp_float(score, 0, 100)

    if score >= 85:
        return "🔥 SNIPER"
    if score >= 75:
        return "💎 PRIME"
    if score >= 65:
        return "✅ READY"
    if score >= 50:
        return "⚠️ WATCH"

    return "❌ SKIP"


def grade_signal(score):
    return grade_rank(score)


# ============================================================
# DATA FETCH
# ============================================================

def normalize_symbol(ticker, market):
    t = ticker.strip().upper()

    if market == "Crypto":
        if t.endswith("-USD"):
            return t
        return f"{t}-USD"

    if market == "IHSG":
        if t.endswith(".JK"):
            return t
        return f"{t}.JK"

    return t


def display_symbol(symbol, market):
    if market == "Crypto":
        return symbol.replace("-USD", "")
    if market == "IHSG":
        return symbol.replace(".JK", "")
    return symbol


def extract_symbol_df(df_all, symbol):
    if df_all is None or df_all.empty:
        return None

    df = df_all.copy()

    if isinstance(df.columns, pd.MultiIndex):
        try:
            if symbol in df.columns.get_level_values(0):
                df = df[symbol].copy()
            elif symbol in df.columns.get_level_values(1):
                df = df.xs(symbol, axis=1, level=1).copy()
        except Exception:
            pass

        if isinstance(df.columns, pd.MultiIndex):
            for lvl in range(df.columns.nlevels):
                vals = set(df.columns.get_level_values(lvl))
                if {"Open", "High", "Low", "Close"}.issubset(vals):
                    df.columns = df.columns.get_level_values(lvl)
                    break

    if isinstance(df.columns, pd.MultiIndex):
        return None

    needed = ["Open", "High", "Low", "Close", "Volume"]

    if not set(needed).issubset(set(df.columns)):
        return None

    df = df[needed].copy()
    df = df.dropna()

    return df


def resample_if_needed(df, timeframe):
    if df is None or df.empty:
        return df

    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    if timeframe == "4h":
        df = df.resample("4h").agg({
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum",
        }).dropna()

    return df


@st.cache_data(ttl=600, show_spinner=False)
def fetch_batch(tickers, timeframe, market):
    tf_map = {
        "15m": ("5d", "15m"),
        "1h": ("1mo", "1h"),
        "4h": ("3mo", "1h"),
        "1d": ("2y", "1d"),
        "1wk": ("5y", "1wk"),
    }

    period, interval = tf_map.get(timeframe, ("2y", "1d"))
    data = {}

    symbols = [normalize_symbol(t, market) for t in tickers]

    if market == "Crypto":
        symbols_text = " ".join(symbols)

        for attempt in range(3):
            try:
                df_all = yf.download(
                    symbols_text,
                    period=period,
                    interval=interval,
                    progress=False,
                    auto_adjust=True,
                    group_by="ticker",
                    threads=True,
                )

                if df_all is None or df_all.empty:
                    time.sleep(2)
                    continue

                for symbol in symbols:
                    df = extract_symbol_df(df_all, symbol)

                    if df is None and len(symbols) == 1:
                        df = extract_symbol_df(df_all, symbols[0])

                    df = resample_if_needed(df, timeframe)

                    if df is not None and len(df) >= 80:
                        data[display_symbol(symbol, market)] = df

                break

            except Exception:
                time.sleep(3)

        return data

    # IHSG lebih aman download satu-satu untuk menghindari rate/multiindex kacau.
    for symbol in symbols:
        for attempt in range(2):
            try:
                df_raw = yf.download(
                    symbol,
                    period=period,
                    interval=interval,
                    progress=False,
                    auto_adjust=True,
                    threads=False,
                )

                df = extract_symbol_df(df_raw, symbol)
                df = resample_if_needed(df, timeframe)

                if df is not None and len(df) >= 80:
                    data[display_symbol(symbol, market)] = df

                break

            except Exception:
                time.sleep(1)

        time.sleep(0.05)

    return data


# ============================================================
# MATRIX TECHNICAL ENGINE
# ============================================================

def compute_technicals(df):
    if df is None or len(df) < 80:
        return None

    try:
        df = df.copy()

        df["close_position"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"] + 1e-9)

        df["ema20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["ema50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["ema200"] = df["Close"].ewm(span=200, adjust=False).mean()

        df["rsi"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()

        df["atr"] = ta.volatility.AverageTrueRange(
            df["High"],
            df["Low"],
            df["Close"],
            window=14,
        ).average_true_range()

        # 1. Smart Money Flow Wave
        hl = (df["High"] - df["Low"]).replace(0, np.nan)
        mf_mult = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / hl
        mf_vol = mf_mult * df["Volume"]

        vol_raw = (
            mf_vol.rolling(20, min_periods=10).mean()
            / df["Volume"].rolling(20, min_periods=10).mean().replace(0, np.nan)
        ) * 100

        df["vol_wave"] = vol_raw.ewm(span=5, adjust=False).mean()

        # 2. Trend Velocity Wave
        pc = df["Close"].diff()
        ds_pc = pc.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
        ds_abs_pc = pc.abs().ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()

        df["trend_wave"] = 100 * (ds_pc / ds_abs_pc.replace(0, np.nan))

        # 3. Bull/Bear Dominance Wave
        df["dom_wave"] = ((df["rsi"] - 50) * 2).ewm(span=3, adjust=False).mean()

        # 4. Price Structure Wave
        hh = df["High"].rolling(20, min_periods=10).max()
        ll = df["Low"].rolling(20, min_periods=10).min()
        struct_raw = ((df["Close"] - ll) / (hh - ll).replace(0, np.nan)) * 200 - 100

        df["struct_wave"] = pandas_wma(struct_raw, 8)

        # Legacy conversion flags
        df["max_buy"] = (
            (df["vol_wave"] > 80)
            & (df["trend_wave"] > 80)
            & (df["dom_wave"] > 80)
            & (df["struct_wave"] > 80)
        )

        df["max_sell"] = (
            (df["vol_wave"] < -80)
            & (df["trend_wave"] < -80)
            & (df["dom_wave"] < -80)
            & (df["struct_wave"] < -80)
        )

        df["cross_up"] = (
            (df["vol_wave"] > 0)
            & (df["trend_wave"] > 0)
            & (df["dom_wave"] > 0)
            & (df["struct_wave"] > 0)
        )

        df["cross_down"] = (
            (df["vol_wave"] < 0)
            & (df["trend_wave"] < 0)
            & (df["dom_wave"] < 0)
            & (df["struct_wave"] < 0)
        )

        # Liquidity / inflow
        df["value_now_m"] = (df["Close"] * df["Volume"]) / 1e6
        df["value_ma20"] = df["value_now_m"].rolling(20, min_periods=10).mean()
        df["inflow_ratio"] = df["value_now_m"] / df["value_ma20"].replace(0, np.nan)

        # Normalized waves
        norm_len = 200

        df["vol_n"] = rolling_percent_rank(df["vol_wave"], norm_len).fillna(df["vol_wave"].clip(-100, 100))
        df["trend_n"] = rolling_percent_rank(df["trend_wave"], norm_len).fillna(df["trend_wave"].clip(-100, 100))
        df["dom_n"] = rolling_percent_rank(df["dom_wave"], norm_len).fillna(df["dom_wave"].clip(-100, 100))
        df["struct_n"] = rolling_percent_rank(df["struct_wave"], norm_len).fillna(df["struct_wave"].clip(-100, 100))

        # Weighted Matrix Score
        df["matrix_score"] = (
            df["vol_n"] * 0.30
            + df["trend_n"] * 0.25
            + df["dom_n"] * 0.20
            + df["struct_n"] * 0.25
        ).clip(-100, 100)

        df["matrix_slope"] = df["matrix_score"].diff().fillna(0)
        df["matrix_accel"] = df["matrix_slope"].diff().fillna(0)

        # Agreement engine
        df["bull_count"] = (
            (df["vol_n"] > 0).astype(int)
            + (df["trend_n"] > 0).astype(int)
            + (df["dom_n"] > 0).astype(int)
            + (df["struct_n"] > 0).astype(int)
        )

        df["bear_count"] = (
            (df["vol_n"] < 0).astype(int)
            + (df["trend_n"] < 0).astype(int)
            + (df["dom_n"] < 0).astype(int)
            + (df["struct_n"] < 0).astype(int)
        )

        # Regime
        adx_ind = ta.trend.ADXIndicator(
            df["High"],
            df["Low"],
            df["Close"],
            window=14,
        )

        df["adx"] = adx_ind.adx()

        bb_basis = df["Close"].rolling(20, min_periods=10).mean()
        bb_dev = df["Close"].rolling(20, min_periods=10).std() * 2.0

        df["bb_width"] = (
            ((bb_basis + bb_dev) - (bb_basis - bb_dev)).abs()
            / bb_basis.abs().replace(0, np.nan)
        ) * 100

        df["bb_width_avg"] = df["bb_width"].rolling(100, min_periods=20).mean()
        df["compression"] = df["bb_width"] < df["bb_width_avg"]

        # Phase warning
        df["pre_breakout_bull"] = (
            df["compression"]
            & (df["matrix_score"] > 0)
            & (df["matrix_slope"] > 0)
            & (df["bull_count"] >= 3)
        )

        df["pre_breakout_bear"] = (
            df["compression"]
            & (df["matrix_score"] < 0)
            & (df["matrix_slope"] < 0)
            & (df["bear_count"] >= 3)
        )

        df["accumulation"] = (
            (df["vol_n"] > 10)
            & (df["struct_n"] < 0)
            & (df["trend_n"] > df["trend_n"].shift(1))
            & (df["dom_n"] > df["dom_n"].shift(1))
            & (df["matrix_slope"] > 0)
        )

        df["distribution"] = (
            (df["vol_n"] < -10)
            & (df["struct_n"] > 0)
            & (df["trend_n"] < df["trend_n"].shift(1))
            & (df["dom_n"] < df["dom_n"].shift(1))
            & (df["matrix_slope"] < 0)
        )

        df["bull_exhaustion"] = (
            (df["matrix_score"] >= 75)
            & (df["matrix_slope"] < 0)
            & (df["matrix_accel"] < 0)
        )

        df["bear_exhaustion"] = (
            (df["matrix_score"] <= -75)
            & (df["matrix_slope"] > 0)
            & (df["matrix_accel"] > 0)
        )

        # Simple matrix divergence
        div_lookback = 20

        prev_high = df["High"].shift(1).rolling(div_lookback, min_periods=10).max()
        prev_low = df["Low"].shift(1).rolling(div_lookback, min_periods=10).min()

        prev_matrix_high = df["matrix_score"].shift(1).rolling(div_lookback, min_periods=10).max()
        prev_matrix_low = df["matrix_score"].shift(1).rolling(div_lookback, min_periods=10).min()

        df["bear_div_matrix"] = (
            (df["High"] > prev_high)
            & (df["matrix_score"] < prev_matrix_high)
            & (df["matrix_score"] > 35)
        )

        df["bull_div_matrix"] = (
            (df["Low"] < prev_low)
            & (df["matrix_score"] > prev_matrix_low)
            & (df["matrix_score"] < -35)
        )

        df["bull_score"] = df["matrix_score"]

        needed_cols = [
            "Close",
            "ema20",
            "ema50",
            "ema200",
            "rsi",
            "atr",
            "vol_n",
            "trend_n",
            "dom_n",
            "struct_n",
            "matrix_score",
            "matrix_slope",
            "adx",
        ]

        return df.dropna(subset=needed_cols)

    except Exception:
        return None


# ============================================================
# LPM SMART MONEY
# ============================================================

def compute_lpm_metrics(df, big_vol_mult=1.5, exhaust_level=90.0):
    if df is None or len(df) < 80:
        return None

    df = df.copy()

    vol_length = 20
    smooth_len = 5
    max_rel_vol = 4.0
    atr_len = 14
    spread_limit = 0.8
    absorb_boost = 0.25
    vp_lookback = 50
    lookback = 50
    dte_len = 14
    div_left = 3
    div_right = 3
    trend_pivot_len = 5
    trend_smooth = 3

    avg_vol = df["Volume"].rolling(vol_length, min_periods=10).mean()
    rel_vol_raw = (df["Volume"] / avg_vol.replace(0, np.nan)).fillna(0)
    rel_vol = rel_vol_raw.clip(upper=max_rel_vol)

    is_big_money = rel_vol_raw >= big_vol_mult
    vol_weight = (rel_vol - 1.0).clip(lower=0.0)

    vol_sum = df["Volume"].rolling(vp_lookback, min_periods=20).sum().replace(0, np.nan)
    poc = (df["Close"] * df["Volume"]).rolling(vp_lookback, min_periods=20).sum() / vol_sum

    vp_std = df["Close"].rolling(vp_lookback, min_periods=20).std()
    vah = poc + vp_std * 1.036
    val = poc - vp_std * 1.036

    in_va = (df["Close"] >= val) & (df["Close"] <= vah)
    above_vah = df["Close"] > vah
    below_val = df["Close"] < val

    rng = df["High"] - df["Low"]
    rng_safe = rng.replace(0, np.nan)

    intra_pressure = (
        ((df["Close"] - df["Low"]) - (df["High"] - df["Close"]))
        / rng_safe
    ).fillna(0)

    if "atr" in df.columns:
        atr_val = df["atr"]
    else:
        atr_val = ta.volatility.AverageTrueRange(
            df["High"],
            df["Low"],
            df["Close"],
            window=atr_len,
        ).average_true_range()

    small_spread = rng <= atr_val * spread_limit
    close_upper = (df["Close"] >= df["Low"] + rng * 0.60) & (rng > 0)
    close_lower = (df["Close"] <= df["Low"] + rng * 0.40) & (rng > 0)

    down_pressure = (df["Close"] <= df["Close"].shift(1)) | (df["High"] < df["High"].shift(1))
    up_pressure = (df["Close"] >= df["Close"].shift(1)) | (df["Low"] > df["Low"].shift(1))

    buy_abs_base = is_big_money & small_spread & close_upper & down_pressure
    sell_abs_base = is_big_money & small_spread & close_lower & up_pressure

    buy_absorption = buy_abs_base & (below_val | in_va)
    sell_absorption = sell_abs_base & (above_vah | in_va)

    abs_adj = pd.Series(0.0, index=df.index)
    abs_adj[buy_absorption] = absorb_boost
    abs_adj[sell_absorption] = -absorb_boost

    pressure_adj = (intra_pressure + abs_adj).clip(-1.0, 1.0)

    lpm_raw = pressure_adj * df["Volume"] * vol_weight
    lpm_cum = lpm_raw.fillna(0).cumsum()
    lpm_smooth = lpm_cum.ewm(span=smooth_len, adjust=False).mean()
    lpm_momentum = lpm_smooth.diff()

    lpm_high = lpm_smooth.rolling(lookback, min_periods=20).max()
    lpm_low = lpm_smooth.rolling(lookback, min_periods=20).min()

    denom = lpm_high - lpm_low

    lpm_norm = pd.Series(50.0, index=df.index)
    valid = (denom > 0) & denom.notna()

    lpm_norm[valid] = (
        (lpm_smooth[valid] - lpm_low[valid])
        / denom[valid]
    ) * 100.0

    lpm_norm = lpm_norm.clip(0, 100)

    confidence = lpm_norm.ewm(span=5, adjust=False).mean()
    conf_change = confidence.diff()
    conf_slope = conf_change.ewm(span=dte_len, adjust=False).mean()

    dist_exhaust = exhaust_level - confidence
    dte = pd.Series(np.nan, index=df.index)

    dte_mask = (dist_exhaust > 0) & (conf_slope > 0)
    dte[dte_mask] = dist_exhaust[dte_mask] / conf_slope[dte_mask]

    is_exhausted = confidence >= exhaust_level
    no_buildup = (conf_slope <= 0) & (confidence < exhaust_level)

    def find_pivots(series, left, right, high=True):
        window = left + right + 1

        if high:
            roll = series.rolling(window=window, center=True).max()
            return (series == roll) & (series > series.shift(left))

        roll = series.rolling(window=window, center=True).min()
        return (series == roll) & (series < series.shift(left))

    price_pivot_low = find_pivots(df["Low"], div_left, div_right, high=False)
    price_pivot_high = find_pivots(df["High"], div_left, div_right, high=True)

    bull_div = pd.Series(False, index=df.index)
    bear_div = pd.Series(False, index=df.index)

    low_idx = df.index[price_pivot_low].tolist()
    high_idx = df.index[price_pivot_high].tolist()

    if len(low_idx) >= 2:
        for i in range(1, len(low_idx)):
            c_idx = low_idx[i]
            p_idx = low_idx[i - 1]

            if (
                df.loc[c_idx, "Low"] < df.loc[p_idx, "Low"]
                and lpm_smooth.loc[c_idx] > lpm_smooth.loc[p_idx]
            ):
                bull_div.loc[c_idx] = True

    if len(high_idx) >= 2:
        for i in range(1, len(high_idx)):
            c_idx = high_idx[i]
            p_idx = high_idx[i - 1]

            if (
                df.loc[c_idx, "High"] > df.loc[p_idx, "High"]
                and lpm_smooth.loc[c_idx] < lpm_smooth.loc[p_idx]
            ):
                bear_div.loc[c_idx] = True

    lpm_smooth_trend = lpm_norm.ewm(span=trend_smooth, adjust=False).mean()

    lpm_state = pd.Series("NEUTRAL", index=df.index)

    strong_accum = (confidence >= 75) & (lpm_momentum > 0) & (~is_exhausted)
    accumulation = bull_div | buy_absorption | ((confidence >= 60) & (lpm_momentum > 0) & is_big_money)
    distribution = bear_div | sell_absorption | ((confidence <= 25) & (lpm_momentum < 0))

    lpm_state[is_exhausted] = "EXHAUSTED"
    lpm_state[strong_accum] = "STRONG ACCUM"
    lpm_state[accumulation & ~strong_accum & ~is_exhausted] = "ACCUMULATION"
    lpm_state[distribution & ~is_exhausted] = "DISTRIBUTION"
    lpm_state[no_buildup & ~is_exhausted] = "NO BUILDUP"

    vp_pos = pd.Series("NEUTRAL", index=df.index)
    vp_pos[above_vah] = "ABOVE VAH"
    vp_pos[below_val] = "BELOW VAL"
    vp_pos[in_va & ~above_vah & ~below_val] = "IN VALUE AREA"

    latest_norm = lpm_norm.iloc[-1]
    trend_status = "IN RANGE"

    ph = find_pivots(lpm_smooth_trend, trend_pivot_len, trend_pivot_len, high=True)
    pl = find_pivots(lpm_smooth_trend, trend_pivot_len, trend_pivot_len, high=False)

    ph_idx = df.index[ph].tolist()
    pl_idx = df.index[pl].tolist()

    if len(ph_idx) >= 1 and latest_norm > lpm_smooth_trend.loc[ph_idx[-1]]:
        trend_status = "ABOVE HIGH"
    elif len(pl_idx) >= 1 and latest_norm < lpm_smooth_trend.loc[pl_idx[-1]]:
        trend_status = "BELOW LOW"

    df["lpm_norm"] = lpm_norm
    df["lpm_confidence"] = confidence
    df["lpm_momentum"] = lpm_momentum
    df["lpm_state"] = lpm_state
    df["lpm_trend_status"] = trend_status
    df["rel_vol"] = rel_vol_raw
    df["is_big_money"] = is_big_money
    df["buy_absorption"] = buy_absorption
    df["sell_absorption"] = sell_absorption
    df["bull_div"] = bull_div
    df["bear_div"] = bear_div
    df["dte"] = dte
    df["is_exhausted"] = is_exhausted
    df["vp_position"] = vp_pos
    df["lpm_smooth_trend"] = lpm_smooth_trend
    df["lpm_raw_smooth"] = lpm_smooth
    df["poc"] = poc
    df["vah"] = vah
    df["val"] = val

    return df


def lpm_sniper_score(df):
    if df is None or len(df) < 50:
        return 0, {}

    latest = df.iloc[-1]

    score = 0
    breakdown = {}

    state_map = {
        "STRONG ACCUM": 40,
        "ACCUMULATION": 25,
        "DISTRIBUTION": -20,
        "EXHAUSTED": -10,
        "NO BUILDUP": -5,
        "NEUTRAL": 0,
    }

    state_pts = state_map.get(latest.get("lpm_state", "NEUTRAL"), 0)
    breakdown["LPM State"] = state_pts
    score += state_pts

    buy_abs_pts = 25 if latest.get("buy_absorption", False) else 0
    breakdown["Buy Absorption"] = buy_abs_pts
    score += buy_abs_pts

    bull_div_pts = 20 if latest.get("bull_div", False) else 0
    breakdown["Bull Divergence"] = bull_div_pts
    score += bull_div_pts

    big_money_pts = 10 if latest.get("is_big_money", False) else 0
    breakdown["Big Money"] = big_money_pts
    score += big_money_pts

    vp = latest.get("vp_position", "NEUTRAL")
    vp_pts = 5 if vp == "BELOW VAL" else 3 if vp == "IN VALUE AREA" else 0
    breakdown["VP Position"] = vp_pts
    score += vp_pts

    mom_pts = 5 if latest.get("lpm_momentum", 0) > 0 else 0
    breakdown["LPM Momentum"] = mom_pts
    score += mom_pts

    not_exh_pts = 5 if not latest.get("is_exhausted", False) else 0
    breakdown["Not Exhausted"] = not_exh_pts
    score += not_exh_pts

    score = max(0, min(100, score))

    return score, breakdown


def grade_lpm(score):
    if score >= 90:
        return "🔥 SNIPER"
    if score >= 80:
        return "💎 PRIME"
    if score >= 70:
        return "✅ STRONG"
    if score >= 60:
        return "⚠️ WATCH"
    return "❌ SKIP"


# ============================================================
# MATRIX SCREENER ENGINE
# ============================================================

def matrix_regime(latest):
    adx = clamp_float(latest.get("adx", 0), 0, 100)
    compression = bool(latest.get("compression", False))

    if compression and adx < 22:
        return "COMPRESSION"
    if adx >= 25:
        return "TRENDING"
    if adx < 16:
        return "CHOPPY"

    return "TRANSITION"


def matrix_warning(latest):
    warn = []

    if bool(latest.get("bear_div_matrix", False)):
        warn.append("Bear Div")
    if bool(latest.get("bull_div_matrix", False)):
        warn.append("Bull Div")
    if bool(latest.get("bull_exhaustion", False)):
        warn.append("Bull Exhaust")
    if bool(latest.get("bear_exhaustion", False)):
        warn.append("Bear Exhaust")
    if bool(latest.get("distribution", False)):
        warn.append("Distribution")
    if bool(latest.get("accumulation", False)):
        warn.append("Accumulation")
    if bool(latest.get("pre_breakout_bull", False)):
        warn.append("Pre-Breakout Bull")
    if bool(latest.get("pre_breakout_bear", False)):
        warn.append("Pre-Breakout Bear")

    return " | ".join(warn[:3]) if warn else "Clear"


def matrix_screener_metrics(df, htf_df=None, use_lpm=False):
    if df is None or len(df) < 3:
        return {
            "Rank": 0,
            "Long Rank": 0,
            "Short Rank": 0,
            "State": "NO DATA",
            "Side": "NEUTRAL",
            "Grade": "❌ SKIP",
            "Matrix": 0,
            "HTF Score": 0,
            "Agreement": "0/4 Mixed",
            "Regime": "UNKNOWN",
            "Warning": "No data",
            "ADX": 0,
            "Slope": 0,
            "Accel": 0,
            "Breakdown": {},
            "LPM Score": 0,
        }

    latest = df.iloc[-1]

    matrix = clamp_float(latest.get("matrix_score", 0), -100, 100)
    slope = clamp_float(latest.get("matrix_slope", 0), -100, 100)
    accel = clamp_float(latest.get("matrix_accel", 0), -100, 100)

    adx = clamp_float(latest.get("adx", 0), 0, 100)
    rsi = clamp_float(latest.get("rsi", 50), 0, 100)
    inflow = clamp_float(latest.get("inflow_ratio", 1), 0, 10)

    bull_count = int(clamp_float(latest.get("bull_count", 0), 0, 4))
    bear_count = int(clamp_float(latest.get("bear_count", 0), 0, 4))

    htf_score = 0.0

    if htf_df is not None and len(htf_df) >= 3 and "matrix_score" in htf_df.columns:
        htf_score = clamp_float(htf_df.iloc[-1].get("matrix_score", 0), -100, 100)

    if bull_count > bear_count:
        agreement = f"{bull_count}/4 Bull"
    elif bear_count > bull_count:
        agreement = f"{bear_count}/4 Bear"
    else:
        agreement = f"{bull_count}/4 Mixed"

    regime = matrix_regime(latest)
    warning = matrix_warning(latest)

    close = clamp_float(latest.get("Close", 0), 0, 10**12)
    ema20 = clamp_float(latest.get("ema20", close), 0, 10**12)
    ema50 = clamp_float(latest.get("ema50", close), 0, 10**12)
    ema200 = clamp_float(latest.get("ema200", close), 0, 10**12)

    long_matrix = clamp_float((matrix + 100) / 2, 0, 100)
    short_matrix = clamp_float((-matrix + 100) / 2, 0, 100)

    long_agree = (bull_count / 4) * 100
    short_agree = (bear_count / 4) * 100

    long_slope = clamp_float((slope + 8) / 16 * 100, 0, 100)
    short_slope = clamp_float((-slope + 8) / 16 * 100, 0, 100)

    htf_long = clamp_float((htf_score + 100) / 2, 0, 100)
    htf_short = clamp_float((-htf_score + 100) / 2, 0, 100)

    trend_long = 100 if ema20 > ema50 > ema200 else 75 if close > ema50 else 45
    trend_short = 100 if ema20 < ema50 < ema200 else 75 if close < ema50 else 45

    regime_score = (
        80 if regime == "TRENDING"
        else 75 if regime == "COMPRESSION"
        else 55 if regime == "TRANSITION"
        else 35
    )

    flow_score = clamp_float((inflow * 45) + 10, 0, 100)

    long_rank = (
        long_matrix * 0.34
        + long_agree * 0.16
        + long_slope * 0.12
        + htf_long * 0.16
        + trend_long * 0.10
        + regime_score * 0.07
        + flow_score * 0.05
    )

    short_rank = (
        short_matrix * 0.34
        + short_agree * 0.16
        + short_slope * 0.12
        + htf_short * 0.16
        + trend_short * 0.10
        + regime_score * 0.07
        + flow_score * 0.05
    )

    long_bonus = 0.0
    short_bonus = 0.0
    long_penalty = 0.0
    short_penalty = 0.0

    # Bullish bonuses
    if bool(latest.get("pre_breakout_bull", False)):
        long_bonus += 8
    if bool(latest.get("accumulation", False)):
        long_bonus += 8
    if bool(latest.get("bull_div_matrix", False)):
        long_bonus += 5

    # Bearish bonuses
    if bool(latest.get("pre_breakout_bear", False)):
        short_bonus += 8
    if bool(latest.get("distribution", False)):
        short_bonus += 8
    if bool(latest.get("bear_div_matrix", False)):
        short_bonus += 5

    # Long penalties
    if bool(latest.get("bear_div_matrix", False)):
        long_penalty += 10
    if bool(latest.get("distribution", False)):
        long_penalty += 8
    if bool(latest.get("bull_exhaustion", False)):
        long_penalty += 12
    if htf_score < -20:
        long_penalty += 8
    if rsi > 78:
        long_penalty += 5

    # Short penalties
    if bool(latest.get("bull_div_matrix", False)):
        short_penalty += 10
    if bool(latest.get("accumulation", False)):
        short_penalty += 8
    if bool(latest.get("bear_exhaustion", False)):
        short_penalty += 12
    if htf_score > 20:
        short_penalty += 8
    if rsi < 22:
        short_penalty += 5

    if adx < 15 and regime != "COMPRESSION":
        long_penalty += 6
        short_penalty += 6

    lpm_score = 0

    if use_lpm and "lpm_state" in latest.index:
        try:
            lpm_score, _ = lpm_sniper_score(df)
        except Exception:
            lpm_score = 0

        lpm_state = str(latest.get("lpm_state", "NEUTRAL"))

        if lpm_state in ["STRONG ACCUM", "ACCUMULATION"]:
            long_bonus += min(12, lpm_score / 7)
            short_penalty += 8

        if lpm_state == "DISTRIBUTION":
            short_bonus += 10
            long_penalty += 10

        if bool(latest.get("buy_absorption", False)):
            long_bonus += 5
            short_penalty += 4

        if bool(latest.get("sell_absorption", False)):
            short_bonus += 5
            long_penalty += 4

        if bool(latest.get("bull_div", False)):
            long_bonus += 5

        if bool(latest.get("bear_div", False)):
            short_bonus += 5

        if bool(latest.get("is_exhausted", False)):
            if matrix > 0:
                long_penalty += 5
            if matrix < 0:
                short_penalty += 5

    long_rank = clamp_float(long_rank + long_bonus - long_penalty, 0, 100)
    short_rank = clamp_float(short_rank + short_bonus - short_penalty, 0, 100)

    if long_rank >= short_rank + 5:
        side = "LONG"
        rank = long_rank
    elif short_rank >= long_rank + 5:
        side = "SHORT"
        rank = short_rank
    else:
        side = "NEUTRAL"
        rank = max(long_rank, short_rank)

    if side == "LONG":
        if bool(latest.get("bull_exhaustion", False)) and matrix >= 65:
            state = "TOO LATE / BULL EXHAUST"
        elif (
            long_rank >= 85
            and matrix > 20
            and slope > 0
            and bull_count >= 3
            and htf_score >= -10
            and not bool(latest.get("bear_div_matrix", False))
        ):
            state = "BUY READY"
        elif long_rank >= 78 and matrix > 45 and bull_count >= 3 and regime == "TRENDING":
            state = "STRONG TREND"
        elif long_rank >= 65 and slope > 0 and bull_count >= 3:
            state = "WATCHLIST"
        else:
            state = "WAIT LONG"

    elif side == "SHORT":
        if bool(latest.get("bear_exhaustion", False)) and matrix <= -65:
            state = "TOO LATE / BEAR EXHAUST"
        elif (
            short_rank >= 85
            and matrix < -20
            and slope < 0
            and bear_count >= 3
            and htf_score <= 10
            and not bool(latest.get("bull_div_matrix", False))
        ):
            state = "SELL READY"
        elif short_rank >= 78 and matrix < -45 and bear_count >= 3 and regime == "TRENDING":
            state = "STRONG DOWNTREND"
        elif short_rank >= 65 and slope < 0 and bear_count >= 3:
            state = "SHORT WATCH"
        else:
            state = "WAIT SHORT"

    else:
        state = "COIL / WAIT" if regime == "COMPRESSION" else "NEUTRAL"

    breakdown = {
        "Matrix Core": round(long_matrix if side != "SHORT" else short_matrix, 1),
        "Agreement": round(long_agree if side != "SHORT" else short_agree, 1),
        "Slope": round(long_slope if side != "SHORT" else short_slope, 1),
        "HTF": round(htf_long if side != "SHORT" else htf_short, 1),
        "Trend Filter": round(trend_long if side != "SHORT" else trend_short, 1),
        "Regime": round(regime_score, 1),
        "Flow": round(flow_score, 1),
        "Long Bonus": round(long_bonus, 1),
        "Long Penalty": round(long_penalty, 1),
        "Short Bonus": round(short_bonus, 1),
        "Short Penalty": round(short_penalty, 1),
    }

    return {
        "Rank": round(rank, 1),
        "Long Rank": round(long_rank, 1),
        "Short Rank": round(short_rank, 1),
        "State": state,
        "Side": side,
        "Grade": grade_rank(rank),
        "Matrix": round(matrix, 1),
        "HTF Score": round(htf_score, 1),
        "Agreement": agreement,
        "Regime": regime,
        "Warning": warning,
        "ADX": round(adx, 1),
        "Slope": round(slope, 2),
        "Accel": round(accel, 2),
        "Breakdown": breakdown,
        "LPM Score": round(lpm_score, 1),
    }


def ultimate_confluence_score(df):
    metrics = matrix_screener_metrics(df)
    return int(metrics.get("Long Rank", 0)), metrics.get("Breakdown", {})


def calc_trade_plan(latest, side="LONG"):
    entry = clamp_float(latest.get("Close", 0), 0, 10**12)
    atr = clamp_float(latest.get("atr", 0), 0, 10**12)

    if atr <= 0:
        atr = max(entry * 0.025, 1e-9)

    side = "SHORT" if side == "SHORT" else "LONG"

    if side == "SHORT":
        sl = entry + atr * 1.5
        tp1 = entry - atr * 2.5
        tp2 = entry - atr * 4.0
        risk = sl - entry
        reward = entry - tp1
    else:
        sl = entry - atr * 1.5
        tp1 = entry + atr * 2.5
        tp2 = entry + atr * 4.0
        risk = entry - sl
        reward = tp1 - entry

    rr = round(reward / risk, 2) if risk > 0 else 0

    return {
        "side": side,
        "entry": entry,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "rr": rr,
    }


# ============================================================
# SCANNER
# ============================================================

def scan_ticker(ticker, df_dict, htf_dict=None, use_lpm=False, lpm_params=None):
    df_raw = df_dict.get(ticker)

    if df_raw is None:
        return None, False

    df = compute_technicals(df_raw)

    if df is None or len(df) < 50:
        return None, False

    if use_lpm:
        try:
            df = compute_lpm_metrics(
                df,
                **(lpm_params or {"big_vol_mult": 1.5, "exhaust_level": 90.0}),
            )
        except Exception:
            df = None

        if df is None or len(df) < 50:
            return None, False

    htf_df = None

    if htf_dict:
        htf_raw = htf_dict.get(ticker)

        if htf_raw is not None:
            htf_tmp = compute_technicals(htf_raw)

            if htf_tmp is not None and len(htf_tmp) >= 30:
                htf_df = htf_tmp

    latest = df.iloc[-1]

    metrics = matrix_screener_metrics(
        df,
        htf_df=htf_df,
        use_lpm=use_lpm,
    )

    if metrics["Side"] in ["LONG", "SHORT"]:
        plan_side = metrics["Side"]
    else:
        plan_side = "LONG" if metrics["Long Rank"] >= metrics["Short Rank"] else "SHORT"

    trade_plan = calc_trade_plan(latest, side=plan_side)

    conv = (
        "MAX BUY"
        if latest.get("max_buy", False)
        else "CROSS UP"
        if latest.get("cross_up", False)
        else "MAX SELL"
        if latest.get("max_sell", False)
        else "CROSS DOWN"
        if latest.get("cross_down", False)
        else "-"
    )

    result = {
        "Ticker": ticker,
        "Close": round(latest.get("Close", 0), 4),
        "State": metrics["State"],
        "Side": metrics["Side"],
        "Rank": metrics["Rank"],
        "Grade": metrics["Grade"],
        "Long Rank": metrics["Long Rank"],
        "Short Rank": metrics["Short Rank"],
        "Matrix": metrics["Matrix"],
        "HTF Score": metrics["HTF Score"],
        "Agreement": metrics["Agreement"],
        "Regime": metrics["Regime"],
        "Warning": metrics["Warning"],
        "ADX": metrics["ADX"],
        "Slope": metrics["Slope"],
        "Inflow": round(latest.get("inflow_ratio", 0), 2),
        "RSI": round(latest.get("rsi", 0), 1),
        "Conv": conv,
        "🟡 VolN": round(latest.get("vol_n", 0), 1),
        "🔵 TrendN": round(latest.get("trend_n", 0), 1),
        "🟣 DomN": round(latest.get("dom_n", 0), 1),
        "⚪ StructN": round(latest.get("struct_n", 0), 1),
        "_df": df,
        "_htf_df": htf_df,
        "_metrics": metrics,
        "_conf_bd": metrics.get("Breakdown", {}),
        "_trade_plan": trade_plan,
    }

    if use_lpm and "lpm_norm" in df.columns:
        try:
            lpm_score, lpm_bd = lpm_sniper_score(df)
            lpm_grade = grade_lpm(lpm_score)
        except Exception:
            lpm_score, lpm_bd, lpm_grade = 0, {}, "❌ SKIP"

        result.update({
            "LPM Score": round(lpm_score, 1),
            "LPM Grade": lpm_grade,
            "LPM State": latest.get("lpm_state", "N/A"),
            "BuyAbs": "YES" if latest.get("buy_absorption", False) else "NO",
            "SellAbs": "YES" if latest.get("sell_absorption", False) else "NO",
            "BullDiv": "YES" if latest.get("bull_div", False) else "NO",
            "BearDiv": "YES" if latest.get("bear_div", False) else "NO",
            "_lpm_bd": lpm_bd,
        })

    return result, True


def run_scan(tickers, timeframe, market, mode, lpm_params=None, min_score=0, use_htf=True):
    results = []

    progress = st.progress(0)
    status = st.empty()

    with st.spinner("📡 Mengunduh data utama..."):
        df_dict = fetch_batch(tickers, timeframe, market)

    htf_dict = {}
    htf_tf = get_auto_htf(timeframe)

    if use_htf and htf_tf != timeframe:
        with st.spinner(f"📡 Mengunduh HTF confirmation ({htf_tf})..."):
            htf_dict = fetch_batch(tickers, htf_tf, market)

    total = max(len(tickers), 1)
    success = 0
    fail = 0

    use_lpm = mode == "LPM + Matrix"

    for i, ticker in enumerate(tickers):
        ticker = ticker.strip().upper()

        r, ok = scan_ticker(
            ticker,
            df_dict,
            htf_dict=htf_dict,
            use_lpm=use_lpm,
            lpm_params=lpm_params,
        )

        if ok:
            success += 1

            if mode == "Long Only":
                passed = r["Long Rank"] >= min_score and r["Long Rank"] >= r["Short Rank"] - 3
            elif mode == "Short Only":
                passed = r["Short Rank"] >= min_score and r["Short Rank"] >= r["Long Rank"] - 3
            else:
                passed = r["Rank"] >= min_score

            if passed:
                results.append(r)

        else:
            fail += 1

        progress.progress((i + 1) / total)

        htf_txt = f" | HTF {htf_tf}" if use_htf and htf_tf != timeframe else ""

        status.text(
            f"Analisis {i + 1}/{total}{htf_txt} | "
            f"✅ {success} | ❌ {fail} | Lolos {len(results)}"
        )

    progress.empty()
    status.empty()

    st.session_state["fetch_stats"] = (success, fail)
    st.session_state["htf_tf"] = htf_tf if use_htf else "OFF"

    return results


# ============================================================
# CHART
# ============================================================

def plot_chart(df, ticker, trade_plan, metrics=None):
    has_lpm = "lpm_norm" in df.columns

    rows = 3 if has_lpm else 2
    heights = [0.48, 0.27, 0.25] if has_lpm else [0.58, 0.42]

    titles = [
        "Price + EMA + Trade Plan",
        "🌊 Matrix Score + Normalized Waves",
    ]

    if has_lpm:
        titles.append("🧠 LPM Smart Money")

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.035,
        row_heights=heights,
        subplot_titles=titles,
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price",
        ),
        row=1,
        col=1,
    )

    for ema, color in [
        ("ema20", "cyan"),
        ("ema50", "yellow"),
        ("ema200", "orange"),
    ]:
        if ema in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[ema],
                    name=ema.upper(),
                    line=dict(color=color, width=1),
                ),
                row=1,
                col=1,
            )

    entry = trade_plan["entry"]
    sl = trade_plan["sl"]
    tp1 = trade_plan["tp1"]
    tp2 = trade_plan["tp2"]
    side = trade_plan.get("side", "LONG")

    fig.add_hline(
        y=entry,
        line_dash="dash",
        line_color="white",
        row=1,
        col=1,
        annotation_text=f"{side} Entry {entry:.4f}",
    )

    fig.add_hline(
        y=sl,
        line_dash="dot",
        line_color="red",
        row=1,
        col=1,
        annotation_text=f"SL {sl:.4f}",
    )

    fig.add_hline(
        y=tp1,
        line_dash="dot",
        line_color="lime",
        row=1,
        col=1,
        annotation_text=f"TP1 {tp1:.4f}",
    )

    fig.add_hline(
        y=tp2,
        line_dash="dot",
        line_color="green",
        row=1,
        col=1,
        annotation_text=f"TP2 {tp2:.4f}",
    )

    if has_lpm and "poc" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["poc"],
                name="POC",
                line=dict(color="white", width=1, dash="dash"),
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["vah"],
                name="VAH",
                line=dict(color="red", width=1, dash="dot"),
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["val"],
                name="VAL",
                line=dict(color="green", width=1, dash="dot"),
            ),
            row=1,
            col=1,
        )

    wave_cols = [
        ("matrix_score", "Matrix", "#FFFFFF", 4),
        ("vol_n", "🟡 VolN", "#FFD600", 1.6),
        ("trend_n", "🔵 TrendN", "#00BFFF", 1.6),
        ("dom_n", "🟣 DomN", "#D500F9", 1.6),
        ("struct_n", "⚪ StructN", "#9E9E9E", 1.6),
    ]

    for col, name, color, width in wave_cols:
        if col in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    name=name,
                    line=dict(color=color, width=width),
                ),
                row=2,
                col=1,
            )

    matrix_levels = [
        (75, "rgba(0,255,0,0.45)", "Bull Extreme"),
        (20, "rgba(0,255,0,0.25)", None),
        (0, "gray", None),
        (-20, "rgba(255,0,0,0.25)", None),
        (-75, "rgba(255,0,0,0.45)", "Bear Extreme"),
    ]

    for y, color, text in matrix_levels:
        fig.add_hline(
            y=y,
            line_dash="dash" if y not in [75, -75] else "solid",
            line_color=color,
            row=2,
            col=1,
            annotation_text=text,
        )

    if "pre_breakout_bull" in df.columns:
        idx = df.index[df["pre_breakout_bull"]]

        if len(idx):
            fig.add_trace(
                go.Scatter(
                    x=idx,
                    y=df.loc[idx, "matrix_score"],
                    mode="markers",
                    marker=dict(color="lime", size=8, symbol="triangle-up"),
                    name="Pre BO Bull",
                ),
                row=2,
                col=1,
            )

    if "pre_breakout_bear" in df.columns:
        idx = df.index[df["pre_breakout_bear"]]

        if len(idx):
            fig.add_trace(
                go.Scatter(
                    x=idx,
                    y=df.loc[idx, "matrix_score"],
                    mode="markers",
                    marker=dict(color="red", size=8, symbol="triangle-down"),
                    name="Pre BO Bear",
                ),
                row=2,
                col=1,
            )

    if has_lpm:
        lpm_color = "#00ff88" if df["lpm_momentum"].iloc[-1] >= 0 else "#ff3860"

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["lpm_norm"],
                name="LPM Norm",
                line=dict(color=lpm_color, width=2),
            ),
            row=3,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["lpm_confidence"],
                name="Confidence",
                line=dict(color="rgba(255,255,255,0.65)", width=1),
            ),
            row=3,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["lpm_smooth_trend"],
                name="LPM Trend",
                line=dict(color="rgba(255,255,0,0.45)", width=1),
            ),
            row=3,
            col=1,
        )

        if "buy_absorption" in df.columns:
            idx = df.index[df["buy_absorption"]]

            if len(idx):
                fig.add_trace(
                    go.Scatter(
                        x=idx,
                        y=[8] * len(idx),
                        mode="markers",
                        marker=dict(color="aqua", size=8),
                        name="Buy Absorb",
                    ),
                    row=3,
                    col=1,
                )

        if "sell_absorption" in df.columns:
            idx = df.index[df["sell_absorption"]]

            if len(idx):
                fig.add_trace(
                    go.Scatter(
                        x=idx,
                        y=[92] * len(idx),
                        mode="markers",
                        marker=dict(color="orange", size=8),
                        name="Sell Absorb",
                    ),
                    row=3,
                    col=1,
                )

        fig.add_hline(
            y=50,
            line_dash="dot",
            line_color="gray",
            row=3,
            col=1,
        )

        fig.add_hline(
            y=75,
            line_dash="dash",
            line_color="rgba(0,255,0,0.5)",
            row=3,
            col=1,
            annotation_text="Accum",
        )

        fig.add_hline(
            y=90,
            line_dash="dash",
            line_color="rgba(255,165,0,0.5)",
            row=3,
            col=1,
            annotation_text="Exhaust",
        )

    subtitle = ""

    if metrics:
        subtitle = (
            f" | {metrics.get('State')} | {metrics.get('Side')} | "
            f"Rank {metrics.get('Rank')} | Warning: {metrics.get('Warning')}"
        )

    fig.update_layout(
        title=f"{ticker} — Aulsome Matrix Screener{subtitle}",
        template="plotly_dark",
        height=980 if has_lpm else 780,
        xaxis_rangeslider_visible=False,
        showlegend=True,
        paper_bgcolor="#0a0a0a",
        plot_bgcolor="#0a0a0a",
    )

    return fig


# ============================================================
# AI PROMPT
# ============================================================

def build_ai_prompt(ticker, df, metrics, trade_plan, lpm_data=None):
    latest = df.iloc[-1]

    lpm_section = ""

    if lpm_data and "lpm_norm" in df.columns:
        dte_val = latest.get("dte", np.nan)
        dte_str = f"{dte_val:.1f}" if not pd.isna(dte_val) else "N/A"

        lpm_section = f"""
🧠 LPM SMART MONEY:
- LPM Score: {lpm_data.get('score', 0)}/100 ({lpm_data.get('grade', 'N/A')})
- LPM Norm: {latest.get('lpm_norm', 0):.1f} | Confidence: {latest.get('lpm_confidence', 0):.1f}%
- State: {latest.get('lpm_state', 'N/A')} | Trend: {latest.get('lpm_trend_status', 'N/A')}
- Rel Volume: {latest.get('rel_vol', 0):.2f}x | Big Money: {'YES' if latest.get('is_big_money', False) else 'NO'}
- Buy Absorption: {'YES' if latest.get('buy_absorption', False) else 'NO'}
- Sell Absorption: {'YES' if latest.get('sell_absorption', False) else 'NO'}
- VP Position: {latest.get('vp_position', 'N/A')} | DTE: {dte_str} bars
"""

    return f"""Anda adalah trader profesional. Analisis {ticker} memakai Matrix Screener state-based berikut.

📊 PRICE
- Close: {latest.get('Close', 0):.4f}
- RSI: {latest.get('rsi', 0):.1f}
- ATR: {latest.get('atr', 0):.4f}
- Inflow: {latest.get('inflow_ratio', 0):.2f}x
- EMA20/50/200: {latest.get('ema20', 0):.4f} / {latest.get('ema50', 0):.4f} / {latest.get('ema200', 0):.4f}

🌊 MATRIX SCREENER
- State: {metrics.get('State')} | Side: {metrics.get('Side')} | Grade: {metrics.get('Grade')}
- Rank: {metrics.get('Rank')} | Long Rank: {metrics.get('Long Rank')} | Short Rank: {metrics.get('Short Rank')}
- Matrix Score: {metrics.get('Matrix')} | HTF Score: {metrics.get('HTF Score')}
- Agreement: {metrics.get('Agreement')} | Regime: {metrics.get('Regime')} | Warning: {metrics.get('Warning')}
- ADX: {metrics.get('ADX')} | Slope: {metrics.get('Slope')} | Accel: {metrics.get('Accel')}

NORMALIZED WAVES
- VolN: {latest.get('vol_n', 0):.1f}
- TrendN: {latest.get('trend_n', 0):.1f}
- DomN: {latest.get('dom_n', 0):.1f}
- StructN: {latest.get('struct_n', 0):.1f}
{lpm_section}

💰 PLAN
- Side: {trade_plan.get('side')}
- Entry: {trade_plan.get('entry'):.4f}
- SL: {trade_plan.get('sl'):.4f}
- TP1: {trade_plan.get('tp1'):.4f}
- TP2: {trade_plan.get('tp2'):.4f}
- RR: 1:{trade_plan.get('rr')}

INSTRUKSI:
1. Beri verdict: BUY READY / SELL READY / WATCH / WAIT / AVOID.
2. Jelaskan alasan dari Matrix Score, HTF, agreement, slope, regime, dan warning.
3. Sebutkan risiko utama jika ada divergence, exhaustion, distribution, atau choppy regime.
4. Beri strategi entry yang realistis dan invalidation level.
5. Maksimal 220 kata, bahasa Indonesia, padat dan actionable."""


# ============================================================
# MAIN APP
# ============================================================

def main():
    init_state()

    st.title("🌊 Aulsome Matrix Pro V8.7")
    st.caption("State-Based Matrix Screener | Long/Short Rank | HTF Confirmation | LPM Smart Money")

    with st.sidebar:
        st.header("⚙️ Configuration")

        market = st.selectbox(
            "Market",
            ["Crypto", "IHSG"],
            index=0,
        )

        timeframe = st.selectbox(
            "Timeframe",
            ["15m", "1h", "4h", "1d", "1wk"],
            index=3,
        )

        mode = st.radio(
            "Scan Mode",
            ["Matrix Screener", "Long Only", "Short Only", "LPM + Matrix"],
            index=0,
        )

        use_htf = st.checkbox(
            "Use Auto HTF Confirmation",
            value=True,
        )

        if use_htf:
            st.caption(f"Auto HTF: `{get_auto_htf(timeframe)}`")
        else:
            st.caption("Auto HTF: `OFF`")

        min_score = st.slider(
            "Min Rank",
            0,
            100,
            60,
            5,
        )

        base_universe = IHSG_MEGA.split() if market == "IHSG" else CRYPTO_MEGA.split()
        max_universe = max(5, len(base_universe))

        universe_size = st.slider(
            "Universe Size",
            5,
            max_universe,
            min(50, max_universe),
            5,
        )

        custom_symbols = st.text_area(
            "Custom symbols optional",
            placeholder="BTC ETH SOL atau BBCA BBRI BMRI",
            height=80,
        )

        lpm_params = {
            "big_vol_mult": 1.5,
            "exhaust_level": 90.0,
        }

        if mode == "LPM + Matrix":
            with st.expander("🧠 LPM Settings", expanded=False):
                lpm_params["big_vol_mult"] = st.slider(
                    "Big Volume Multiplier",
                    1.0,
                    3.0,
                    1.5,
                    0.1,
                )

                lpm_params["exhaust_level"] = st.slider(
                    "Exhaustion Level",
                    70.0,
                    98.0,
                    90.0,
                    1.0,
                )

        run_button = st.button(
            "🚀 RUN MATRIX SCAN",
            use_container_width=True,
            type="primary",
        )

        if run_button:
            if custom_symbols.strip():
                tickers = [
                    x.strip().upper()
                    for x in custom_symbols.replace(",", " ").split()
                    if x.strip()
                ]
            else:
                tickers = base_universe[:universe_size]

            with st.spinner(f"Scanning {len(tickers)} tickers..."):
                st.session_state["results"] = run_scan(
                    tickers=tickers,
                    timeframe=timeframe,
                    market=market,
                    mode=mode,
                    lpm_params=lpm_params if mode == "LPM + Matrix" else None,
                    min_score=min_score,
                    use_htf=use_htf,
                )

                st.session_state["scan_triggered"] = True
                st.session_state["last_scan_time"] = datetime.now().strftime("%H:%M:%S")
                st.session_state["scan_mode"] = mode
                st.session_state["scan_timeframe"] = timeframe
                st.session_state["scan_market"] = market
                st.session_state["min_score"] = min_score

    if not st.session_state["scan_triggered"]:
        st.info("👈 Atur parameter di sidebar, lalu klik RUN MATRIX SCAN.")
        return

    results = st.session_state["results"]

    if not results:
        succ, fail = st.session_state.get("fetch_stats", (0, 0))

        st.warning(
            f"❌ Tidak ada ticker yang lolos. Data OK: {succ}, Gagal: {fail}. "
            f"Coba turunkan Min Rank atau ganti timeframe."
        )

        return

    mode = st.session_state.get("scan_mode", "Matrix Screener")

    if mode == "Long Only":
        sort_key = "Long Rank"
    elif mode == "Short Only":
        sort_key = "Short Rank"
    else:
        sort_key = "Rank"

    results = sorted(
        results,
        key=lambda x: x.get(sort_key, 0),
        reverse=True,
    )

    succ, fail = st.session_state.get("fetch_stats", (0, 0))
    htf_tf = st.session_state.get("htf_tf", "OFF")

    st.success(
        f"✅ {len(results)} lolos | Data OK: {succ} | Gagal: {fail} | "
        f"Mode: {mode} | TF: {st.session_state.get('scan_timeframe')} | "
        f"HTF: {htf_tf} | {st.session_state['last_scan_time']}"
    )

    m1, m2, m3, m4, m5 = st.columns(5)

    m1.metric("Total", len(results))
    m2.metric("BUY READY", sum(1 for r in results if r.get("State") == "BUY READY"))
    m3.metric("SELL READY", sum(1 for r in results if r.get("State") == "SELL READY"))
    m4.metric("WATCH", sum(1 for r in results if "WATCH" in r.get("State", "")))
    m5.metric("Avg Rank", f"{np.mean([r.get('Rank', 0) for r in results]):.1f}")

    df_display = pd.DataFrame([
        {k: v for k, v in r.items() if not k.startswith("_")}
        for r in results
    ])

    ordered_cols = [
        "Ticker",
        "Close",
        "State",
        "Side",
        "Rank",
        "Grade",
        "Long Rank",
        "Short Rank",
        "Matrix",
        "HTF Score",
        "Agreement",
        "Regime",
        "Warning",
        "ADX",
        "Slope",
        "Inflow",
        "RSI",
        "LPM Score",
        "LPM Grade",
        "LPM State",
        "🟡 VolN",
        "🔵 TrendN",
        "🟣 DomN",
        "⚪ StructN",
        "Conv",
    ]

    ordered_cols = [c for c in ordered_cols if c in df_display.columns]

    state_options = ["ALL"] + sorted(df_display["State"].dropna().unique().tolist())

    state_filter = st.selectbox(
        "Filter State",
        state_options,
        index=0,
    )

    if state_filter == "ALL":
        view_df = df_display
    else:
        view_df = df_display[df_display["State"] == state_filter]

    st.dataframe(
        view_df[ordered_cols],
        use_container_width=True,
        height=430,
    )

    st.download_button(
        "📥 Download CSV",
        view_df[ordered_cols].to_csv(index=False),
        f"matrix_scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv",
    )

    st.markdown("#### 🔎 Detail Ticker")

    selected = st.selectbox(
        "Pilih Ticker",
        [r["Ticker"] for r in results],
    )

    sel = next(r for r in results if r["Ticker"] == selected)

    metrics = sel["_metrics"]
    plan = sel["_trade_plan"]

    d1, d2, d3, d4, d5, d6 = st.columns(6)

    d1.metric("State", sel["State"])
    d2.metric("Side", sel["Side"])
    d3.metric("Rank", f"{sel['Rank']}", sel["Grade"])
    d4.metric("Matrix", f"{sel['Matrix']}")
    d5.metric("HTF", f"{sel['HTF Score']}")
    d6.metric("Regime", sel["Regime"])

    w1, w2, w3, w4, w5 = st.columns(5)

    w1.metric("🟡 VolN", f"{sel['🟡 VolN']}")
    w2.metric("🔵 TrendN", f"{sel['🔵 TrendN']}")
    w3.metric("🟣 DomN", f"{sel['🟣 DomN']}")
    w4.metric("⚪ StructN", f"{sel['⚪ StructN']}")
    w5.metric("Warning", sel["Warning"])

    st.info(
        f"💰 {plan['side']} Plan | Entry `{plan['entry']:.4f}` | "
        f"SL `{plan['sl']:.4f}` | TP1 `{plan['tp1']:.4f}` | "
        f"TP2 `{plan['tp2']:.4f}` | RR 1:{plan['rr']}"
    )

    if "LPM Score" in sel:
        l1, l2, l3, l4 = st.columns(4)

        l1.metric(
            "LPM Score",
            f"{sel.get('LPM Score', 0)}",
            sel.get("LPM Grade", ""),
        )

        l2.metric(
            "LPM State",
            sel.get("LPM State", ""),
        )

        l3.metric(
            "BuyAbs / SellAbs",
            f"{sel.get('BuyAbs', 'NO')} / {sel.get('SellAbs', 'NO')}",
        )

        l4.metric(
            "BullDiv / BearDiv",
            f"{sel.get('BullDiv', 'NO')} / {sel.get('BearDiv', 'NO')}",
        )

    with st.expander("📊 Rank Breakdown"):
        st.json(metrics.get("Breakdown", {}))

    if "_lpm_bd" in sel:
        with st.expander("🧠 LPM Breakdown"):
            st.json(sel.get("_lpm_bd", {}))

    st.plotly_chart(
        plot_chart(
            sel["_df"],
            sel["Ticker"],
            plan,
            metrics=metrics,
        ),
        use_container_width=True,
    )

    st.markdown("#### 🧠 AI Analysis")

    if st.button("Generate AI Analysis", use_container_width=True):
        client = get_client()

        if not client:
            st.error("Groq API key tidak ditemukan di Streamlit secrets atau package `groq` belum terinstall.")
        else:
            with st.spinner("AI menganalisis Matrix Screener..."):
                try:
                    lpm_data = None

                    if "LPM Score" in sel:
                        lpm_data = {
                            "score": sel.get("LPM Score", 0),
                            "grade": sel.get("LPM Grade", ""),
                        }

                    prompt = build_ai_prompt(
                        sel["Ticker"],
                        sel["_df"],
                        metrics,
                        plan,
                        lpm_data=lpm_data,
                    )

                    resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                        temperature=0.3,
                        max_tokens=700,
                    )

                    st.markdown(resp.choices[0].message.content)

                except Exception as e:
                    st.error(f"AI error: {e}")


if __name__ == "__main__":
    main()
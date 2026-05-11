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
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIG & UNIVERSE
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Aulsome Matrix Pro V7.1",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

IHSG_MEGA = """AALI ABBA ABDA ABMM ACES ACST ADCP ADES ADHI ADMF ADMG ADMR ADRO AGII AGRO AHAP AISA AKPI AKRA ALDO ALKA ALMI AMAG AMAN AMAR AMFG AMIN AMMN AMRT ANJT ANTM APEX APLN ARCI ARGO ARII ARNA ARTA ARTI ARTO ASBI ASGR ASII ASRI ASRM ASSA ATIC AUTO AVIA BABP BACA BAJA BALI BANK BAPA BATA BBCA BBHI BBKP BBLD BBMD BBNI BBRI BBRM BBTN BBYB BCAP BCIC BDMN BEKS BELL BESS BEST BFIN BGTG BINA BIPI BIPP BIRD BISI BJBR BJTM BKDP BKSL BLTA BMAS BMHS BMRI BMSR BMTR BNBA BNBR BNGA BNII BNLI BOBA BOLA BPFI BRIS BREN BRMS BRNA BRPT BSDE BSIM BSSR BSWD BTEK BTEL BTON BTPN BTPS BUDI BUKK BULL BUMI BVIC BWPT BYAN CAKK CAMP CARS CASH CASS CCSI CEKA CENT CFIN CINT CITA CITY CLEO CMNP CMPP CNKO CNTX COAL CPIN CPRO CSAP CSRA CTBN CTRA DART DAYA DCII DEAL DEWA DFAM DGIK DILD DIVA DKFT DLTA DMMX DMND DNAR DNET DOID DPNS DSFI DSNG DSSA DUTI DYAN EAST EKAD ELSA EMDE EMTK ENRG EPMT ERAA ESSA ETWA EXCL FAST FASW FILM FIRE FISH FMII FOOD FORU FORZ FPNI FREN GAMA GDST GDYR GEMA GEMS GGRM GIAA GJTL GLOB GLVA GMFI GMTD GOLD GOOD GOTO GPRA GSMF GTBO GWSA GZCO HADE HAIS HDFA HEAL HERO HEXA HITS HKMU HMSP HOKI HOME HRME HRTA HRUM IATA IBST ICBP ICON IDEA IGAR IIKP IKAI IMAS IMJS IMPC INAF INAI INCF INCI INCO INDF INDO INDR INDS INDY INPC INPS INRU INTA INTP IPCC IPCM IPOL IPTV IRRA ISAT ISSP ITIC ITMG JAKS JAST JAWA JAYA JECC JGLE JIHD JKON JMAS JSPT JTPE KAEF KBLI KBLM KBLV KDSI KEEN KEJU KIAS KICI KIJA KINO KIOS KKGI KLBF KOBX KOIN KONI KPIG KRYA LAMI LCGP LEAD LINK LION LMAS LMPI LMSH LPCK LPGI LPIN LPKR LPLI LPPF LSIP LTLS MAIN MAMI MAPA MAPB MAPI MARK MASA MAYA MBAP MBSS MBTO MCAS MCOR MDIA MDKA MDLN MDRN MEDC MEGA MERK META MFIN MICE MIDI MIKA MINA MIRA MITI MKPI MLBI MLIA MLPL MLPT MMLP MNCN MOLI MORA MPMX MPPA MSIN MSKY MTDL MTEL MTLA MTMH MTPS MTRA MTSM MYOH MYOR MYRX MYTX NANO NELY NFCX NIPS NIRO NISP NOBU NRCA NZIA OASA OBMD OMED OMRE ONIX PADI PALM PAMG PANI PANR PANS PBSA PCAR PEGE PEHA PGAS PGEO PGLI PICO PJAA PKPK PLAS PLIN PNBN PNBS PNIN PNLF PNSE POLA POLI POLL POLY POOL PORT PRAS PRDA PSAB PSDN PSGO PSKT PTBA PTPP PTPW PUDA PURA PWON PYFA PZZA RAJA RALS RANC RBMS RDTX REAL RELI RICY RIGS RIMO RMBA ROCK ROTI RSGK RUIS SAFE SAME SAMF SAPX SCCO SCMA SCNP SDMU SDPC SFAN SGER SGRO SHID SIDO SILO SIMA SIMP SINI SIPD SKBM SKLT SKYB SMAR SMBR SMCB SMDR SMGR SMIL SMKL SMMA SMMT SMRA SMRU SMSM SOBI SOHO SONA SOSS SOTO SPMA SQMI SRAJ SRIL SRSN SRTG SSIA SSMS SSTM STTP SUGI SULI SUPR SURE SWAT TAXI TAYS TBIG TBLA TBMS TCID TCPI TEBE TECH TELE TFCO TGKA TIFA TINS TIRA TIRT TKIM TLDN TLKM TMAS TMPO TNCA TOBA TOYS TPIA TPMA TRAM TRIL TRIM TRIN TRIS TRJA TRST TRUK TSPC TUGU TURI ULTJ UNIC UNIT UNSP UNTR UNVR URBN VCGG VICO VINS VIVA VKTR VOKS VRNA WAPO WEHA WEGE WIFI WIKA WINS WOMF WOOD WSBP WSKT WTON YELO YPAS ZATA ZBRA ZINC ZONE ZYRX"""
CRYPTO_MEGA = """BTC ETH BNB SOL XRP ADA DOGE AVAX DOT MATIC LINK SHIB LTC NEAR UNI APT ARB OP TIA SUI FET RNDR STX FIL ATOM IMX HBAR ETC ICP PEPE WIF BONK ORDI INJ THETA LDO VET BEAM SEI AAVE MKR RUNE GALA EGLD ALGO FLOW DYDX CRV SNX PENDLE JUP PYTH STRK W ENA ROSE AGIX STG AXS SAND MANA CHZ MINA KAVA GRT AGLD JASMY TRX KAS XLM XMR BCH BSV LUNC LUNA USTC JTO 1INCH MASK ENS BLUR GLM AKT NOS IO AEVO ZK ZRO LISTA NOT BB PIXEL PORTAL XAI ACE SATS FLOKI MEME LADYS TURBO PEOPLE TRB GAS ARK WAVES ONT ONG NEO QTUM DGB SC XVG HOT RVN CKB SLP GNS PERP GMX WOO ZRX KNC LRC SUSHI BAKE JOE CAKE PORK BRETT BOME MEW MYRO WEN COQ KDA OSMO RETH LPT ALT MANTA ONDO RIF NTRN PAI SKL METIS SCRT CFX ACH TRU HOOK MAGIC GAL CORE EDU ID COMBO RDNT HIFI MAV PUNDIX BEL FRONT C98 MTL REEF ATA ALICE PROM DAR CHR SXP STEEM KMD STRAX ADX ICX OGN NKN DENT KEY MFT DATA VTHO STMX IQ UTK OXT ANKR CTSI COS TROY PIVX SYS SCR GFT QKC IOTX CTXC DOCK MITH TFUEL GTC MLN BOND FOR LINA DEGO EPS AUTO TKO TVK QUICK ERN RAMP PHA BAR CITY ASR JUV ATM OG PSG SANTOS LAZIO ALPINE FLOW MIR ANC ZEN RARE CLV ALPHA FIS SPELL CHESS QI GHST VOXEL BNX NMR VIB AST OAX DUSK LSK ARDR LOOM REQ AKRO POLS HARD STPT OOKI UNFI WING MOB MOVR SYN HIGH"""

# ──────────────────────────────────────────────────────────────────────────────
# 2. CORE ENGINE
# ──────────────────────────────────────────────────────────────────────────────
def init_state():
    if "results" not in st.session_state: st.session_state["results"] = []
    if "scan_triggered" not in st.session_state: st.session_state["scan_triggered"] = False
    if "last_scan_time" not in st.session_state: st.session_state["last_scan_time"] = None
    if "scan_mode" not in st.session_state: st.session_state["scan_mode"] = None

def get_client():
    try: return Groq(api_key=st.secrets.get("GROQ_KEY", ""))
    except: return None

def pandas_wma(series, window):
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

@st.cache_data(ttl=600, show_spinner=False)
def fetch_data(ticker, timeframe):
    try:
        mapping = {"15m": ("5d", "15m"), "1h": ("1mo", "1h"), "4h": ("2mo", "4h"), "1d": ("2y", "1d")}
        period, interval = mapping.get(timeframe, ("2y", "1d"))
        df = yf.download(ticker.upper(), period=period, interval=interval, progress=False, auto_adjust=True)
        if df.empty or len(df) < 100: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df.dropna()
    except Exception:
        return None

def compute_technicals(df):
    if df is None or len(df) < 100: return None
    try:
        df = df.copy()
        df["ema20"] = ta.trend.ema_indicator(df["Close"], window=20)
        df["ema50"] = ta.trend.ema_indicator(df["Close"], window=50)
        df["ema200"] = ta.trend.ema_indicator(df["Close"], window=200)
        df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
        df["atr"] = ta.volatility.AverageTrueRange(df["High"], df["Low"], df["Close"], window=14).average_true_range()

        hl = (df["High"] - df["Low"]).replace(0, 0.001)
        mf_vol = (((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / hl) * df["Volume"]
        df["vol_wave"] = (mf_vol.rolling(20).mean() / df["Volume"].rolling(20).mean().replace(0, 0.001) * 100).ewm(span=5).mean()
        df["dom_wave"] = ((df["rsi"] - 50) * 2).ewm(span=3).mean()
        hh, ll = df["High"].rolling(20).max(), df["Low"].rolling(20).min()
        df["struct_wave"] = pandas_wma(((df["Close"] - ll) / (hh - ll).replace(0, 0.001)) * 200 - 100, 8)

        df["value_now_m"] = (df["Close"] * df["Volume"]) / 1e6
        df["value_ma20"] = df["value_now_m"].rolling(20).mean()
        df["inflow_ratio"] = df["value_now_m"] / df["value_ma20"].replace(0, 0.001)

        df["bull_score"] = (
            (df["vol_wave"] > 0).astype(int) * 25 +
            (df["dom_wave"] > 0).astype(int) * 20 +
            (df["inflow_ratio"] > 1.1).astype(int) * 25 +
            (df["struct_wave"] > -50).astype(int) * 30
        ).clip(upper=100)

        # ─── BSJP / BPJS metrics ───
        # Close position dalam daily range (0-1, makin tinggi = makin kuat closing)
        df["close_position"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"]).replace(0, 0.001)
        # Open position dalam previous daily range
        df["gap_pct"] = (df["Open"] - df["Close"].shift(1)) / df["Close"].shift(1) * 100
        # Intraday return (open → close)
        df["intraday_return"] = (df["Close"] - df["Open"]) / df["Open"] * 100
        # Overnight return (prev close → today open)
        df["overnight_return"] = (df["Open"] - df["Close"].shift(1)) / df["Close"].shift(1) * 100

        # Historical hit rate (rolling 20 days)
        df["gap_up_rate"] = (df["overnight_return"] > 0).rolling(20).mean() * 100      # BSJP edge
        df["intraday_win_rate"] = (df["intraday_return"] > 0).rolling(20).mean() * 100  # BPJS edge
        df["avg_overnight"] = df["overnight_return"].rolling(20).mean()                 # avg gap up
        df["avg_intraday"] = df["intraday_return"].rolling(20).mean()                   # avg intraday

        return df.dropna()
    except Exception:
        return None

def detect_patterns(df):
    if df is None or len(df) < 5: return "Neutral"
    c, p, p2 = df.iloc[-1], df.iloc[-2], df.iloc[-3]
    body_c = abs(c["Close"] - c["Open"])
    range_c = max(c["High"] - c["Low"], 0.001)
    range_p = max(p["High"] - p["Low"], 0.001)
    upper_shadow_c = c["High"] - max(c["Close"], c["Open"])
    lower_shadow_c = min(c["Close"], c["Open"]) - c["Low"]

    if (p2["Close"] < p2["Open"]) and (abs(p["Close"] - p["Open"]) <= range_p * 0.3) \
       and (c["Close"] > c["Open"]) and (c["Close"] >= (p2["Open"] + p2["Close"]) / 2):
        return "Morning Star"
    if p["Close"] < p["Open"] and c["Close"] > c["Open"] and c["Close"] >= p["Open"] and c["Open"] <= p["Close"]:
        return "Bullish Engulfing"
    if p["Close"] < p["Open"] and c["Close"] > c["Open"] and c["Low"] > p["Low"] and c["High"] < p["High"]:
        return "Bullish Harami"
    if p["Close"] < p["Open"] and c["Close"] > c["Open"] and abs(c["Low"] - p["Low"]) <= (range_c * 0.05):
        return "Tweezer Bottom"
    if body_c <= range_c * 0.1 and upper_shadow_c <= range_c * 0.1 and c["Low"] < min(c["Close"], c["Open"]):
        return "Dragonfly Doji"
    if lower_shadow_c > 2 * body_c and (c["rsi"] < 40 or (c["Close"] > c["Open"] and upper_shadow_c <= body_c * 0.2)):
        return "Hammer"
    return "Neutral"

# ──────────────────────────────────────────────────────────────────────────────
# 3. CONFLUENCE & BSJP/BPJS ENGINE
# ──────────────────────────────────────────────────────────────────────────────
def ultimate_confluence_score(df):
    if df is None or len(df) < 200: return 0, {}
    latest, prev, prev2 = df.iloc[-1], df.iloc[-2], df.iloc[-3]
    breakdown = {}

    trend_pts = 0
    if latest["ema50"] > latest["ema200"]: trend_pts += 10
    if latest["Close"] > latest["ema50"]: trend_pts += 5
    if latest["ema20"] > latest["ema50"]: trend_pts += 5
    breakdown["Trend"] = trend_pts

    struct_pts = 0
    if latest["struct_wave"] <= -70: struct_pts += 12
    elif latest["struct_wave"] <= -50: struct_pts += 6
    if latest["struct_wave"] > prev["struct_wave"]: struct_pts += 8
    breakdown["Structure"] = struct_pts

    flow_pts = 0
    if latest["vol_wave"] > prev["vol_wave"] > prev2["vol_wave"]: flow_pts += 10
    if latest["vol_wave"] > 0: flow_pts += 5
    if latest["inflow_ratio"] >= 1.5: flow_pts += 10
    elif latest["inflow_ratio"] >= 1.2: flow_pts += 5
    breakdown["SmartMoney"] = flow_pts

    mom_pts = 0
    if latest["dom_wave"] > prev["dom_wave"]: mom_pts += 8
    if 30 < latest["rsi"] < 65: mom_pts += 6
    if prev["rsi"] < 35 and latest["rsi"] > prev["rsi"]: mom_pts += 6
    breakdown["Momentum"] = mom_pts

    pa_pts = 0
    pattern = detect_patterns(df)
    if pattern in ["Morning Star", "Bullish Engulfing"]: pa_pts += 10
    elif pattern in ["Hammer", "Dragonfly Doji", "Tweezer Bottom"]: pa_pts += 7
    elif pattern == "Bullish Harami": pa_pts += 5
    vol_avg = df["Volume"].rolling(20).mean().iloc[-1]
    if latest["Volume"] > vol_avg * 1.5: pa_pts += 5
    breakdown["PriceAction"] = pa_pts

    return trend_pts + struct_pts + flow_pts + mom_pts + pa_pts, breakdown

def grade_signal(score):
    if score >= 85: return "🔥 SNIPER"
    elif score >= 75: return "💎 ULTIMATE"
    elif score >= 65: return "✅ STRONG"
    elif score >= 50: return "⚠️ WATCH"
    return "❌ SKIP"

def calc_trade_plan(latest):
    entry = latest["Close"]
    atr = latest["atr"]
    sl = entry - (atr * 1.5)
    tp1 = entry + (atr * 2.5)
    tp2 = entry + (atr * 4.0)
    rr = round((tp1 - entry) / (entry - sl), 2) if (entry - sl) > 0 else 0
    return entry, sl, tp1, tp2, rr

# ─── BSJP: Beli Sore Jual Pagi ───
def bsjp_score(df):
    """Score 0-100 untuk strategi Beli Sore Jual Pagi."""
    if df is None or len(df) < 30: return 0, {}
    latest, prev = df.iloc[-1], df.iloc[-2]
    bd = {}
    score = 0

    # 1. Strong closing (30 pts) — candle ditutup di area atas
    if latest["close_position"] >= 0.8: score += 20
    elif latest["close_position"] >= 0.65: score += 12
    if latest["Close"] > latest["Open"]: score += 10
    bd["Closing Strength"] = score

    # 2. Historical gap-up edge (25 pts)
    gap_pts = 0
    if latest["gap_up_rate"] >= 65: gap_pts += 15
    elif latest["gap_up_rate"] >= 55: gap_pts += 10
    elif latest["gap_up_rate"] >= 50: gap_pts += 5
    if latest["avg_overnight"] > 0.3: gap_pts += 10
    elif latest["avg_overnight"] > 0: gap_pts += 5
    bd["Gap-Up Edge"] = gap_pts
    score += gap_pts

    # 3. Late-day accumulation (25 pts)
    acc_pts = 0
    if latest["vol_wave"] > prev["vol_wave"]: acc_pts += 10
    if latest["inflow_ratio"] >= 1.3: acc_pts += 10
    elif latest["inflow_ratio"] >= 1.1: acc_pts += 5
    if latest["vol_wave"] > 0: acc_pts += 5
    bd["Accumulation"] = acc_pts
    score += acc_pts

    # 4. Trend & momentum support (20 pts)
    trend_pts = 0
    if latest["Close"] > latest["ema20"]: trend_pts += 5
    if latest["ema20"] > latest["ema50"]: trend_pts += 5
    if latest["dom_wave"] > 0: trend_pts += 5
    if 40 < latest["rsi"] < 70: trend_pts += 5
    bd["Trend Support"] = trend_pts
    score += trend_pts

    return min(score, 100), bd

# ─── BPJS: Beli Pagi Jual Sore ───
def bpjs_score(df):
    """Score 0-100 untuk strategi Beli Pagi Jual Sore."""
    if df is None or len(df) < 30: return 0, {}
    latest, prev = df.iloc[-1], df.iloc[-2]
    bd = {}
    score = 0

    # 1. Intraday bullish edge (30 pts)
    intra_pts = 0
    if latest["intraday_win_rate"] >= 65: intra_pts += 18
    elif latest["intraday_win_rate"] >= 55: intra_pts += 12
    elif latest["intraday_win_rate"] >= 50: intra_pts += 6
    if latest["avg_intraday"] > 0.5: intra_pts += 12
    elif latest["avg_intraday"] > 0: intra_pts += 6
    bd["Intraday Edge"] = intra_pts
    score += intra_pts

    # 2. Range expansion (20 pts) — volatilitas naik = peluang besar
    range_pts = 0
    atr_now = latest["atr"]
    atr_avg = df["atr"].rolling(10).mean().iloc[-1]
    if atr_now > atr_avg * 1.2: range_pts += 12
    elif atr_now > atr_avg: range_pts += 6
    if latest["Volume"] > df["Volume"].rolling(20).mean().iloc[-1] * 1.3: range_pts += 8
    bd["Range Expansion"] = range_pts
    score += range_pts

    # 3. Momentum thrust (25 pts)
    mom_pts = 0
    if latest["dom_wave"] > prev["dom_wave"]: mom_pts += 10
    if latest["dom_wave"] > 0: mom_pts += 5
    if latest["rsi"] > 50 and latest["rsi"] < 70: mom_pts += 10
    bd["Momentum"] = mom_pts
    score += mom_pts

    # 4. Trend alignment (25 pts)
    trend_pts = 0
    if latest["Close"] > latest["ema20"] > latest["ema50"]: trend_pts += 15
    elif latest["Close"] > latest["ema20"]: trend_pts += 8
    if latest["inflow_ratio"] >= 1.2: trend_pts += 10
    elif latest["inflow_ratio"] >= 1.0: trend_pts += 5
    bd["Trend Alignment"] = trend_pts
    score += trend_pts

    return min(score, 100), bd

def grade_bsjp_bpjs(score):
    if score >= 80: return "🔥 PRIME"
    elif score >= 70: return "💎 STRONG"
    elif score >= 60: return "✅ VALID"
    elif score >= 50: return "⚠️ WATCH"
    return "❌ SKIP"

# ──────────────────────────────────────────────────────────────────────────────
# 4. AI PROMPT
# ──────────────────────────────────────────────────────────────────────────────
def build_ai_prompt(asset, df, timeframe, confluence_data=None):
    lookback = df.tail(30).copy()
    cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'ema20', 'ema50', 'ema200', 'vol_wave', 'struct_wave', 'inflow_ratio', 'rsi']
    data_str = lookback[cols].to_string()

    confluence_section = ""
    if confluence_data:
        score, breakdown = confluence_data
        confluence_section = f"""
CONFLUENCE SCORE: {score}/100 — Grade: {grade_signal(score)}
- Trend: {breakdown.get('Trend',0)}/20
- Structure: {breakdown.get('Structure',0)}/20
- Smart Money: {breakdown.get('SmartMoney',0)}/25
- Momentum: {breakdown.get('Momentum',0)}/20
- Price Action: {breakdown.get('PriceAction',0)}/15
"""

    return f"""
Anda adalah Senior Technical Analyst dengan spesialisasi *Market Structure* dan *Order Flow*.
Tugas Anda memberikan analisis objektif untuk {asset} ({timeframe}).

{confluence_section}

DEFINISI INDIKATOR:
- struct_wave (Putih): Market Structure. <= -80 jenuh jual, >= 80 jenuh beli.
- vol_wave (Kuning): Volume Flow / Akumulasi Bandar.
- dom_wave (Ungu): Momentum Buyer vs Seller.
- inflow_ratio: > 1.0 uang besar masuk.

DATA MARKET (Last 30 Periods):
{data_str}

INSTRUKSI:
1. MARKET STRUCTURE & EMA stacking
2. MOMENTUM & FLOW analysis
3. CONFLUENCE VALIDATION
4. ELLIOTT WAVE hipotesis
5. VERDICT: [SUPER YAHUD / YAHUD / WATCHLIST / WEAK / SKIP]
6. TRADING PLAN: Entry, SL, TP1, TP2, R:R

Format Markdown profesional, evidence-based.
"""

# ──────────────────────────────────────────────────────────────────────────────
# 5. MAIN APP
# ──────────────────────────────────────────────────────────────────────────────
def main():
    init_state()
    st.title("🏆 Aulsome Matrix Pro V7.1")
    st.caption("Ultimate Confluence + BSJP/BPJS Edition")

    with st.sidebar:
        st.header("🎯 Strategy Panel")
        market = st.radio("Universe", ["IHSG", "Crypto"], horizontal=True)
        timeframe = st.selectbox("Timeframe", ["1h", "4h", "1d"], index=2)

        st.markdown("---")
        mode = st.selectbox("Metode Screening", [
            "🏆 Ultimate Confluence (Pro)",
            "🌅 BSJP — Beli Sore Jual Pagi",
            "🌇 BPJS — Beli Pagi Jual Sore",
            "Wave Matrix 🌊",
            "Candlestick Pattern 🕯️",
            "Inflow Detector 💰",
            "Sniper Filter 🎯"
        ])

        strategy, wave_threshold, min_score = None, -80, 75

        if mode == "🏆 Ultimate Confluence (Pro)":
            min_score = st.slider("Min Confluence Score", 50, 95, 75)
            st.caption("💡 65+ Strong | 75+ Ultimate | 85+ Sniper")
        elif mode == "🌅 BSJP — Beli Sore Jual Pagi":
            min_score = st.slider("Min BSJP Score", 50, 95, 70)
            st.caption("🌅 Entry closing, exit opening besok | 60+ Valid | 70+ Strong | 80+ Prime")
            if market == "Crypto":
                st.warning("⚠️ BSJP/BPJS dirancang untuk saham IHSG (sesi jelas). Crypto 24/7 — gunakan dengan hati-hati.")
        elif mode == "🌇 BPJS — Beli Pagi Jual Sore":
            min_score = st.slider("Min BPJS Score", 50, 95, 70)
            st.caption("🌇 Entry opening, exit closing | 60+ Valid | 70+ Strong | 80+ Prime")
            if market == "Crypto":
                st.warning("⚠️ BSJP/BPJS dirancang untuk saham IHSG. Crypto 24/7 — gunakan dengan hati-hati.")
        elif mode == "Wave Matrix 🌊":
            strategy = st.selectbox("Signal", ["Bullish Reversal (Bottoming)", "Bearish Reversal (Topping)", "Bullish Continuation", "Bearish Continuation"])
            wave_threshold = st.slider("White Threshold", -100, 100, -80 if "Bullish" in strategy else 80)
        elif mode == "Candlestick Pattern 🕯️":
            strategy = st.selectbox("Pattern", ["Bullish Engulfing", "Dragonfly Doji", "Morning Star", "Hammer", "Bullish Harami", "Tweezer Bottom", "Any Bullish Pattern"])
        elif mode == "Inflow Detector 💰":
            strategy = st.selectbox("Level", ["High Inflow (≥1.5x)", "Accumulation (≥1.2x + Vol↑)"])

        st.markdown("---")
        use_trend = st.checkbox("📈 Uptrend Only (EMA200)", value=True)
        min_turnover = st.number_input("💰 Min Turnover (Mln)", 1.0, 5000.0, 10.0)
        max_workers = st.slider("🔧 Concurrency", 5, 40, 20)

        if st.button("🚀 EXECUTE FULL SCAN", type="primary", use_container_width=True):
            st.session_state["scan_triggered"] = True
            st.session_state["scan_mode"] = mode
            st.rerun()

    if st.session_state["scan_triggered"]:
        st.session_state["scan_triggered"] = False
        suffix = ".JK" if market == "IHSG" else "-USD"
        tickers_raw = (IHSG_MEGA if market == "IHSG" else CRYPTO_MEGA).split()
        tickers = [f"{t.strip()}{suffix}" for t in tickers_raw if t.strip()]

        # Force daily timeframe for BSJP/BPJS
        effective_tf = "1d" if mode in ["🌅 BSJP — Beli Sore Jual Pagi", "🌇 BPJS — Beli Pagi Jual Sore"] else timeframe

        results = []
        prog = st.progress(0)

        def process_ticker(t):
            df = compute_technicals(fetch_data(t, effective_tf))
            if df is None: return None
            latest, prev = df.iloc[-1], df.iloc[-2]
            if latest["value_now_m"] < min_turnover: return None

            pattern = detect_patterns(df)
            matched = False
            extra = {}

            if mode == "🏆 Ultimate Confluence (Pro)":
                score, breakdown = ultimate_confluence_score(df)
                matched = score >= min_score
                if matched:
                    entry, sl, tp1, tp2, rr = calc_trade_plan(latest)
                    extra = {
                        "Confluence": score, "Grade": grade_signal(score),
                        "Trend": breakdown["Trend"], "Struct": breakdown["Structure"],
                        "SmartMoney": breakdown["SmartMoney"], "Momentum": breakdown["Momentum"],
                        "PriceAction": breakdown["PriceAction"],
                        "Entry": round(entry, 4), "SL": round(sl, 4),
                        "TP1": round(tp1, 4), "TP2": round(tp2, 4), "R:R": rr
                    }

            elif mode == "🌅 BSJP — Beli Sore Jual Pagi":
                score, bd = bsjp_score(df)
                matched = score >= min_score
                if matched:
                    target_pct = max(latest["avg_overnight"], 0.5)
                    extra = {
                        "BSJP Score": score, "Grade": grade_bsjp_bpjs(score),
                        "ClosingPos": f"{latest['close_position']*100:.0f}%",
                        "GapUpRate": f"{latest['gap_up_rate']:.0f}%",
                        "AvgOvernight": f"{latest['avg_overnight']:.2f}%",
                        "BuyClose": round(latest["Close"], 4),
                        "TargetOpen": round(latest["Close"] * (1 + target_pct/100), 4),
                        "ExpectedGain%": round(target_pct, 2),
                        "ClosingStr": bd["Closing Strength"],
                        "GapEdge": bd["Gap-Up Edge"],
                        "Accum": bd["Accumulation"],
                    }

            elif mode == "🌇 BPJS — Beli Pagi Jual Sore":
                score, bd = bpjs_score(df)
                matched = score >= min_score
                if matched:
                    target_pct = max(latest["avg_intraday"], 0.8)
                    # Estimasi entry = open hari ini, atau close kemarin sebagai proxy
                    est_entry = latest["Close"]  # akan entry di open besok
                    extra = {
                        "BPJS Score": score, "Grade": grade_bsjp_bpjs(score),
                        "IntradayWR": f"{latest['intraday_win_rate']:.0f}%",
                        "AvgIntraday": f"{latest['avg_intraday']:.2f}%",
                        "ATR": round(latest["atr"], 4),
                        "EstEntry": round(est_entry, 4),
                        "TargetClose": round(est_entry * (1 + target_pct/100), 4),
                        "ExpectedGain%": round(target_pct, 2),
                        "IntraEdge": bd["Intraday Edge"],
                        "RangeExp": bd["Range Expansion"],
                        "Momentum": bd["Momentum"],
                    }

            elif mode == "Wave Matrix 🌊":
                if strategy == "Bullish Reversal (Bottoming)":
                    matched = latest["struct_wave"] <= wave_threshold and (latest["dom_wave"] > prev["dom_wave"] or latest["vol_wave"] > prev["vol_wave"])
                elif strategy == "Bearish Reversal (Topping)":
                    matched = latest["struct_wave"] >= wave_threshold and latest["vol_wave"] < prev["vol_wave"]
                elif "Bullish Continuation" in strategy:
                    matched = latest["vol_wave"] > 0 and latest["vol_wave"] > latest["dom_wave"] > latest["struct_wave"]
                elif "Bearish Continuation" in strategy:
                    matched = latest["vol_wave"] < 0 and latest["vol_wave"] < latest["dom_wave"] < latest["struct_wave"]
            elif mode == "Candlestick Pattern 🕯️":
                matched = (pattern != "Neutral") if strategy == "Any Bullish Pattern" else (pattern == strategy)
            elif mode == "Inflow Detector 💰":
                matched = latest["inflow_ratio"] >= 1.5 if "High" in strategy else (latest["inflow_ratio"] > 1.2 and latest["vol_wave"] > 0)
            elif mode == "Sniper Filter 🎯":
                matched = latest["Volume"] > (df["Volume"].rolling(20).mean().iloc[-1] * 1.3) and pattern != "Neutral"

            if use_trend and "Bearish" not in str(strategy) and latest["Close"] < latest["ema200"]:
                matched = False

            if matched:
                base = {
                    "Asset": t.replace(suffix, ""),
                    "Price": round(latest["Close"], 4),
                    "Score": int(latest["bull_score"]),
                    "Inflow": round(latest["inflow_ratio"], 2),
                    "White": round(latest["struct_wave"], 1),
                    "Yellow": round(latest["vol_wave"], 1),
                    "Purple": round(latest["dom_wave"], 1),
                    "Pattern": pattern
                }
                base.update(extra)
                return base
            return None

        with ThreadPoolExecutor(max_workers=max_workers) as exe:
            for i, res in enumerate(exe.map(process_ticker, tickers)):
                if res: results.append(res)
                prog.progress((i + 1) / len(tickers))

        sort_keys = {
            "🏆 Ultimate Confluence (Pro)": "Confluence",
            "🌅 BSJP — Beli Sore Jual Pagi": "BSJP Score",
            "🌇 BPJS — Beli Pagi Jual Sore": "BPJS Score"
        }
        sk = sort_keys.get(mode, "Score")
        st.session_state["results"] = sorted(results, key=lambda x: x.get(sk, 0), reverse=True)
        st.session_state["last_scan_time"] = datetime.now().strftime("%H:%M:%S")
        st.rerun()

    tab_res, tab_deep = st.tabs(["📊 Screening Results", "📈 Deep Analysis"])

    with tab_res:
        if st.session_state["last_scan_time"]:
            st.success(f"✅ Last scan at {st.session_state['last_scan_time']} | Mode: {st.session_state.get('scan_mode', 'N/A')}")
        if st.session_state["results"]:
            df_res = pd.DataFrame(st.session_state["results"])
            st.dataframe(df_res, use_container_width=True, hide_index=True)

            if "Confluence" in df_res.columns:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("🔥 Sniper (85+)", len(df_res[df_res["Confluence"] >= 85]))
                c2.metric("💎 Ultimate (75-84)", len(df_res[(df_res["Confluence"] >= 75) & (df_res["Confluence"] < 85)]))
                c3.metric("✅ Strong (65-74)", len(df_res[(df_res["Confluence"] >= 65) & (df_res["Confluence"] < 75)]))
                c4.metric("📊 Total", len(df_res))
            elif "BSJP Score" in df_res.columns:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("🔥 Prime (80+)", len(df_res[df_res["BSJP Score"] >= 80]))
                c2.metric("💎 Strong (70-79)", len(df_res[(df_res["BSJP Score"] >= 70) & (df_res["BSJP Score"] < 80)]))
                c3.metric("✅ Valid (60-69)", len(df_res[(df_res["BSJP Score"] >= 60) & (df_res["BSJP Score"] < 70)]))
                c4.metric("📊 Total", len(df_res))
                st.info("🌅 **BSJP Playbook**: Beli di pre-closing (jam 15:45-16:00). Exit di opening besok (jam 09:00-09:30). Stop loss: jika gap down >1%.")
            elif "BPJS Score" in df_res.columns:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("🔥 Prime (80+)", len(df_res[df_res["BPJS Score"] >= 80]))
                c2.metric("💎 Strong (70-79)", len(df_res[(df_res["BPJS Score"] >= 70) & (df_res["BPJS Score"] < 80)]))
                c3.metric("✅ Valid (60-69)", len(df_res[(df_res["BPJS Score"] >= 60) & (df_res["BPJS Score"] < 70)]))
                c4.metric("📊 Total", len(df_res))
                st.info("🌇 **BPJS Playbook**: Beli di opening (jam 09:00-09:15). Exit di pre-closing (jam 15:45-16:00). Stop loss: jika harga turun >1.5% dari entry.")

            csv = df_res.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", csv, f"scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")
        else:
            st.info("Gunakan sidebar untuk memulai scan.")

    with tab_deep:
        if st.session_state["results"]:
            selected = st.selectbox("🎯 Select Asset", [r["Asset"] for r in st.session_state["results"]])
            suffix = ".JK" if market == "IHSG" else "-USD"
            df_p = compute_technicals(fetch_data(selected + suffix, timeframe))

            if df_p is not None:
                score, breakdown = ultimate_confluence_score(df_p)
                entry, sl, tp1, tp2, rr = calc_trade_plan(df_p.iloc[-1])
                bsjp_s, bsjp_bd = bsjp_score(df_p)
                bpjs_s, bpjs_bd = bpjs_score(df_p)

                st.markdown(f"### {grade_signal(score)} Confluence: **{score}/100** | 🌅 BSJP: **{bsjp_s}** | 🌇 BPJS: **{bpjs_s}**")

                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Trend", f"{breakdown.get('Trend',0)}/20")
                col2.metric("Structure", f"{breakdown.get('Structure',0)}/20")
                col3.metric("Smart Money", f"{breakdown.get('SmartMoney',0)}/25")
                col4.metric("Momentum", f"{breakdown.get('Momentum',0)}/20")
                col5.metric("Price Action", f"{breakdown.get('PriceAction',0)}/15")

                st.markdown("#### 🌅🌇 BSJP / BPJS Stats")
                bc1, bc2, bc3, bc4 = st.columns(4)
                latest = df_p.iloc[-1]
                bc1.metric("Gap-Up Rate (20d)", f"{latest['gap_up_rate']:.0f}%")
                bc2.metric("Avg Overnight", f"{latest['avg_overnight']:.2f}%")
                bc3.metric("Intraday WR (20d)", f"{latest['intraday_win_rate']:.0f}%")
                bc4.metric("Avg Intraday", f"{latest['avg_intraday']:.2f}%")

                st.markdown("#### 🎯 Trade Plan (ATR-based)")
                tc1, tc2, tc3, tc4, tc5 = st.columns(5)
                tc1.metric("Ent
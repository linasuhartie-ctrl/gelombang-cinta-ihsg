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
        df["close_position"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"]).replace(0, 0.001)
        df["gap_pct"] = (df["Open"] - df["Close"].shift(1)) / df["Close"].shift(1) * 100
        df["intraday_return"] = (df["Close"] - df["Open"]) / df["Open"] * 100
        df["overnight_return"] = (df["Open"] - df["Close"].shift(1)) / df["Close"].shift(1) * 100
        df["gap_up_rate"] = (df["overnight_return"] > 0).rolling(20).mean() * 100
        df["intraday_win_rate"] = (df["intraday_return"] > 0).rolling(20).mean() * 100
        df["avg_overnight"] = df["overnight_return"].rolling(20).mean()
        df["avg_intraday"] = df["intraday_return"].rolling(20).mean()

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

def bsjp_score(df):
    """Score 0-100 untuk Beli Sore Jual Pagi."""
    if df is None or len(df) < 30: return 0, {}
    latest, prev = df.iloc[-1], df.iloc[-2]
    bd = {}

    cs_pts = 0
    if latest["close_position"] >= 0.8: cs_pts += 20
    elif latest["close_position"] >= 0.65: cs_pts += 12
    if latest["Close"] > latest["Open"]: cs_pts += 10
    bd["Closing Strength"] = cs_pts

    gap_pts = 0
    if latest["gap_up_rate"] >= 65: gap_pts += 15
    elif latest["gap_up_rate"] >= 55: gap_pts += 10
    elif latest["gap_up_rate"] >= 50: gap_pts += 5
    if latest["avg_overnight"] > 0.3: gap_pts += 10
    elif latest["avg_overnight"] > 0: gap_pts += 5
    bd["Gap-Up Edge"] = gap_pts

    acc_pts = 0
    if latest["vol_wave"] > prev["vol_wave"]: acc_pts += 10
    if latest["inflow_ratio"] >= 1.3: acc_pts += 10
    elif latest["inflow_ratio"] >= 1.1: acc_pts += 5
    if latest["vol_wave"] > 0: acc_pts += 5
    bd["Accumulation"] = acc_pts

    trend_pts = 0
    if latest["Close"] > latest["ema20"]: trend_pts += 5
    if latest["ema20"] > latest["ema50"]: trend_pts += 5
    if latest["dom_wave"] > 0: trend_pts += 5
    if 40 < latest["rsi"] < 70: trend_pts += 5
    bd["Trend Support"] = trend_pts

    total = min(cs_pts + gap_pts + acc_pts + trend_pts, 100)
    return total, bd

def bpjs_score(df):
    """Score 0-100 untuk Beli Pagi Jual Sore."""
    if df is None or len(df) < 30: return 0, {}
    latest, prev = df.iloc[-1], df.iloc[-2]
    bd = {}

    intra_pts = 0
    if latest["intraday_win_rate"] >= 65: intra_pts += 18
    elif latest["intraday_win_rate"] >= 55: intra_pts += 12
    elif latest["intraday_win_rate"] >= 50: intra_pts += 6
    if latest["avg_intraday"] > 0.5: intra_pts += 12
    elif latest["avg_intraday"] > 0: intra_pts += 6
    bd["Intraday Edge"] = intra_pts

    range_pts = 0
    atr_now = latest["atr"]
    atr_avg = df["atr"].rolling(10).mean().iloc[-1]
    if atr_now > atr_avg * 1.2: range_pts += 12
    elif atr_now > atr_avg: range_pts += 6
    if latest["Volume"] > df["Volume"].rolling(20).mean().iloc[-1] * 1.3: range_pts += 8
    bd["Range Expansion"] = range_pts

    mom_pts = 0
    if latest["dom_wave"] > prev["dom_wave"]: mom_pts += 10
    if latest["dom_wave"] > 0: mom_pts += 5
    if 50 < latest["rsi"] < 70: mom_pts += 10
    bd["Momentum"] = mom_pts

    trend_pts = 0
    if latest["Close"] > latest["ema20"] > latest["ema50"]: trend_pts += 15
    elif latest["Close"] > latest["ema20"]: trend_pts += 8
    if latest["inflow_ratio"] >= 1.2: trend_pts += 10
    elif latest["inflow_ratio"] >= 1.0: trend_pts += 5
    bd["Trend Alignment"] = trend_pts

    total = min(intra_pts + range_pts + mom_pts + trend_pts, 100)
    return total, bd

def grade_bsjp_bpjs(score):
    if score >= 80: return "🔥 PRIME"
    elif score >= 70: return "💎 STRONG"
    elif score >= 60: return "✅ VALID"
    elif score >= 50: return "⚠️ WATCH"
    return "❌ SKIP"
    
    # ──────────────────────────────────────────────────────────────────────────────
# 4. AI PROMPT
# ──────────────────────────────────────────────────────────────────────────────
def build_ai_prompt(ticker, df, conf_score, conf_bd, pattern, trade_plan, bsjp, bpjs):
    latest = df.iloc[-1]
    entry, sl, tp1, tp2, rr = trade_plan
    bs_score, _ = bsjp
    bp_score, _ = bpjs

    return f"""Anda adalah trader profesional. Analisis {ticker} berdasarkan DATA KONKRIT berikut:

📊 PRICE ACTION:
- Close: {latest['Close']:.2f} | Open: {latest['Open']:.2f} | High: {latest['High']:.2f} | Low: {latest['Low']:.2f}
- Pattern terdeteksi: {pattern}
- Close Position: {latest['close_position']*100:.1f}% (>80% = strong close)

📈 INDIKATOR:
- RSI: {latest['rsi']:.1f} | ATR: {latest['atr']:.2f}
- EMA20: {latest['ema20']:.2f} | EMA50: {latest['ema50']:.2f} | EMA200: {latest['ema200']:.2f}
- Vol Wave: {latest['vol_wave']:.1f} | Dom Wave: {latest['dom_wave']:.1f} | Struct Wave: {latest['struct_wave']:.1f}
- Inflow Ratio: {latest['inflow_ratio']:.2f}x | Bull Score: {latest['bull_score']:.0f}/100

🎯 CONFLUENCE BREAKDOWN (Total: {conf_score}/100 → {grade_signal(conf_score)}):
- Trend: {conf_bd.get('Trend',0)}/20
- Structure: {conf_bd.get('Structure',0)}/20
- Smart Money: {conf_bd.get('SmartMoney',0)}/25
- Momentum: {conf_bd.get('Momentum',0)}/20
- Price Action: {conf_bd.get('PriceAction',0)}/15

⏰ INTRADAY STRATEGY:
- BSJP (Beli Sore Jual Pagi): {bs_score}/100 → {grade_bsjp_bpjs(bs_score)}
  • Gap-Up Rate (20D): {latest['gap_up_rate']:.0f}% | Avg Overnight: {latest['avg_overnight']:.2f}%
- BPJS (Beli Pagi Jual Sore): {bp_score}/100 → {grade_bsjp_bpjs(bp_score)}
  • Intraday Win Rate (20D): {latest['intraday_win_rate']:.0f}% | Avg Intraday: {latest['avg_intraday']:.2f}%

💰 TRADE PLAN (ATR-based):
- Entry: {entry:.2f} | SL: {sl:.2f} | TP1: {tp1:.2f} | TP2: {tp2:.2f} | R:R = 1:{rr}

INSTRUKSI:
1. Berikan kesimpulan VERDICT (BUY / WAIT / AVOID) dengan alasan berbasis data di atas.
2. Highlight 2-3 confluence terkuat dan 1-2 risk factor.
3. Rekomendasikan strategi: Swing (confluence) atau Intraday (BSJP/BPJS) — pilih yang skornya paling kuat.
4. Maksimal 200 kata, bahasa Indonesia, padat & actionable. Tanpa disclaimer panjang."""

# ──────────────────────────────────────────────────────────────────────────────
# 5. SCANNER
# ──────────────────────────────────────────────────────────────────────────────
def scan_ticker(ticker, timeframe, market):
    try:
        symbol = f"{ticker}.JK" if market == "IHSG" else f"{ticker}-USD"
        df = fetch_data(symbol, timeframe)
        df = compute_technicals(df)
        if df is None or len(df) < 200: return None

        latest = df.iloc[-1]
        conf_score, conf_bd = ultimate_confluence_score(df)
        bs_score, bs_bd = bsjp_score(df)
        bp_score, bp_bd = bpjs_score(df)
        pattern = detect_patterns(df)
        trade_plan = calc_trade_plan(latest)

        return {
            "Ticker": ticker,
            "Symbol": symbol,
            "Close": round(latest["Close"], 2),
            "RSI": round(latest["rsi"], 1),
            "Bull Score": int(latest["bull_score"]),
            "Confluence": conf_score,
            "Grade": grade_signal(conf_score),
            "BSJP": bs_score,
            "BSJP Grade": grade_bsjp_bpjs(bs_score),
            "BPJS": bp_score,
            "BPJS Grade": grade_bsjp_bpjs(bp_score),
            "Pattern": pattern,
            "Inflow": round(latest["inflow_ratio"], 2),
            "_df": df,
            "_conf_bd": conf_bd,
            "_bs_bd": bs_bd,
            "_bp_bd": bp_bd,
            "_trade_plan": trade_plan,
        }
    except Exception:
        return None

def run_scan(tickers, timeframe, market, min_conf, min_bsjp, min_bpjs, mode):
    results = []
    progress = st.progress(0)
    status = st.empty()
    total = len(tickers)

    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(scan_ticker, t, timeframe, market): t for t in tickers}
        for i, f in enumerate(futures):
            try:
                r = f.result(timeout=30)
                if r:
                    if mode == "Confluence" and r["Confluence"] >= min_conf: results.append(r)
                    elif mode == "BSJP" and r["BSJP"] >= min_bsjp: results.append(r)
                    elif mode == "BPJS" and r["BPJS"] >= min_bpjs: results.append(r)
                    elif mode == "ALL":
                        if r["Confluence"] >= min_conf or r["BSJP"] >= min_bsjp or r["BPJS"] >= min_bpjs:
                            results.append(r)
            except Exception:
                pass
            progress.progress((i + 1) / total)
            status.text(f"Scanning {i+1}/{total}...")

    progress.empty()
    status.empty()
    return results

# ──────────────────────────────────────────────────────────────────────────────
# 6. CHART
# ──────────────────────────────────────────────────────────────────────────────
def plot_chart(df, ticker, trade_plan):
    entry, sl, tp1, tp2, _ = trade_plan
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                        row_heights=[0.6, 0.2, 0.2],
                        subplot_titles=("Price + EMA", "RSI", "Wave Matrix"))

    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"],
                                  low=df["Low"], close=df["Close"], name="Price"), row=1, col=1)
    for ema, color in [("ema20", "orange"), ("ema50", "blue"), ("ema200", "red")]:
        fig.add_trace(go.Scatter(x=df.index, y=df[ema], name=ema.upper(),
                                  line=dict(color=color, width=1)), row=1, col=1)

    fig.add_hline(y=entry, line_dash="dash", line_color="white", row=1, col=1, annotation_text=f"Entry {entry:.2f}")
    fig.add_hline(y=sl, line_dash="dot", line_color="red", row=1, col=1, annotation_text=f"SL {sl:.2f}")
    fig.add_hline(y=tp1, line_dash="dot", line_color="lime", row=1, col=1, annotation_text=f"TP1 {tp1:.2f}")
    fig.add_hline(y=tp2, line_dash="dot", line_color="green", row=1, col=1, annotation_text=f"TP2 {tp2:.2f}")

    fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], name="RSI", line=dict(color="purple")), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["vol_wave"], name="Vol Wave", line=dict(color="cyan")), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["dom_wave"], name="Dom Wave", line=dict(color="yellow")), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["struct_wave"], name="Struct Wave", line=dict(color="magenta")), row=3, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="gray", row=3, col=1)

    fig.update_layout(title=f"{ticker} — Aulsome Matrix Pro V7.1",
                       template="plotly_dark", height=800, xaxis_rangeslider_visible=False, showlegend=True)
    return fig

# ──────────────────────────────────────────────────────────────────────────────
# 7. MAIN APP
# ──────────────────────────────────────────────────────────────────────────────
def main():
    init_state()
    st.title("🏆 Aulsome Matrix Pro V7.1")
    st.caption("Ultimate Confluence + BSJP/BPJS Intraday Engine")

    with st.sidebar:
        st.header("⚙️ Configuration")
        market = st.selectbox("Market", ["IHSG", "Crypto"])
        timeframe = st.selectbox("Timeframe", ["1d", "4h", "1h", "15m"], index=0)
        mode = st.radio("Scan Mode", ["Confluence", "BSJP", "BPJS", "ALL"], index=0)

        st.markdown("---")
        st.subheader("🎯 Thresholds")
        min_conf = st.slider("Min Confluence", 0, 100, 65, 5)
        min_bsjp = st.slider("Min BSJP", 0, 100, 60, 5)
        min_bpjs = st.slider("Min BPJS", 0, 100, 60, 5)

        st.markdown("---")
        universe_size = st.slider("Universe Size", 50, 800, 200, 50)

        if st.button("🚀 RUN SCAN", use_container_width=True, type="primary"):
            tickers_raw = IHSG_MEGA if market == "IHSG" else CRYPTO_MEGA
            tickers = tickers_raw.split()[:universe_size]
            with st.spinner(f"Scanning {len(tickers)} tickers..."):
                st.session_state["results"] = run_scan(tickers, timeframe, market, min_conf, min_bsjp, min_bpjs, mode)
                st.session_state["scan_triggered"] = True
                st.session_state["last_scan_time"] = datetime.now().strftime("%H:%M:%S")
                st.session_state["scan_mode"] = mode

    if st.session_state["scan_triggered"]:
        results = st.session_state["results"]
        if not results:
            st.warning("Tidak ada ticker yang lolos filter. Coba turunkan threshold.")
            return

        sort_key = {"Confluence": "Confluence", "BSJP": "BSJP", "BPJS": "BPJS", "ALL": "Confluence"}[st.session_state["scan_mode"]]
        results = sorted(results, key=lambda x: x[sort_key], reverse=True)

        st.success(f"✅ {len(results)} ticker lolos | Mode: {st.session_state['scan_mode']} | Last scan: {st.session_state['last_scan_time']}")

        df_display = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in results])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Signals", len(results))
        c2.metric("🔥 Sniper (≥85)", sum(1 for r in results if r["Confluence"] >= 85))
        c3.metric("BSJP Prime (≥80)", sum(1 for r in results if r["BSJP"] >= 80))
        c4.metric("BPJS Prime (≥80)", sum(1 for r in results if r["BPJS"] >= 80))

        st.dataframe(df_display, use_container_width=True, height=400)
        st.download_button("📥 Download CSV", df_display.to_csv(index=False), "aulsome_scan.csv", "text/csv")

        st.markdown("---")
        st.subheader("🔬 Deep Analysis")
        selected = st.selectbox("Pilih Ticker", [r["Ticker"] for r in results])
        sel = next(r for r in results if r["Ticker"] == selected)

        cA, cB, cC = st.columns(3)
        cA.metric("Confluence", f"{sel['Confluence']}/100", sel["Grade"])
        cB.metric("BSJP", f"{sel['BSJP']}/100", sel["BSJP Grade"])
        cC.metric("BPJS", f"{sel['BPJS']}/100", sel["BPJS Grade"])

        with st.expander("📊 Confluence Breakdown"):
            st.json(sel["_conf_bd"])
        with st.expander("🌅 BSJP Breakdown"):
            st.json(sel["_bs_bd"])
        with st.expander("🌇 BPJS Breakdown"):
            st.json(sel["_bp_bd"])

        entry, sl, tp1, tp2, rr = sel["_trade_plan"]
        st.info(f"💰 **Trade Plan** — Entry: `{entry:.2f}` | SL: `{sl:.2f}` | TP1: `{tp1:.2f}` | TP2: `{tp2:.2f}` | R:R = `1:{rr}`")

        st.plotly_chart(plot_chart(sel["_df"], sel["Ticker"], sel["_trade_plan"]), use_container_width=True)

        st.markdown("---")
        st.subheader("🤖 AI Analyst (Groq)")
        if st.button("🧠 Generate AI Analysis", use_container_width=True):
            client = get_client()
            if client is None:
                st.error("Groq API key tidak ditemukan. Tambahkan `GROQ_KEY` di Streamlit Secrets.")
            else:
                with st.spinner("AI sedang menganalisis..."):
                    try:
                        prompt = build_ai_prompt(
                            sel["Ticker"], sel["_df"], sel["Confluence"], sel["_conf_bd"],
                            sel["Pattern"], sel["_trade_plan"],
                            (sel["BSJP"], sel["_bs_bd"]), (sel["BPJS"], sel["_bp_bd"])
                        )
                        resp = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.3,
                            max_tokens=600,
                        )
                        st.markdown(resp.choices[0].message.content)
                    except Exception as e:
                        st.error(f"AI error: {e}")
    else:
        st.info("👈 Konfigurasi di sidebar lalu klik **RUN SCAN** untuk memulai.")

if __name__ == "__main__":
    main()
    
mport warnings
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
st.set_page_config(page_title="Aulsome Matrix Pro V8.0", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")

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
    """V7.3: 4 Gelombang ASLI sesuai Pine Script Aul Wave."""
    if df is None or len(df) < 100: return None
    try:
        df = df.copy()
        df["ema20"] = ta.trend.ema_indicator(df["Close"], window=20)
        df["ema50"] = ta.trend.ema_indicator(df["Close"], window=50)
        df["ema200"] = ta.trend.ema_indicator(df["Close"], window=200)
        df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
        df["atr"] = ta.volatility.AverageTrueRange(df["High"], df["Low"], df["Close"], window=14).average_true_range()

        # ════════════════════════════════════════════════════════════════
        # 🌊 AUL WAVE 4 GELOMBANG ASLI (sesuai Pine Script @yucuppucuy)
        # ════════════════════════════════════════════════════════════════

        # 1️⃣ VOL WAVE (KUNING) — Smart Money Flow / Chaikin Money Flow
        hl = (df["High"] - df["Low"]).replace(0, 1e-9)
        mf_mult = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / hl
        mf_vol = mf_mult * df["Volume"]
        vol_raw = (mf_vol.rolling(20).mean() / df["Volume"].rolling(20).mean().replace(0, 1e-9)) * 100
        df["vol_wave"] = vol_raw.ewm(span=5, adjust=False).mean()

        # 2️⃣ TREND WAVE (BIRU) — True Strength Index (TSI)
        pc = df["Close"].diff()
        ds_pc = pc.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
        ds_abs_pc = pc.abs().ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
        df["trend_wave"] = 100 * (ds_pc / ds_abs_pc.replace(0, 1e-9))

        # 3️⃣ DOM WAVE (UNGU) — Bull/Bear Dominance dari RSI
        df["dom_wave"] = ((df["rsi"] - 50) * 2).ewm(span=3, adjust=False).mean()

        # 4️⃣ STRUCT WAVE (PUTIH) — Price Structure 20-bar
        hh = df["High"].rolling(20).max()
        ll = df["Low"].rolling(20).min()
        struct_raw = ((df["Close"] - ll) / (hh - ll).replace(0, 1e-9)) * 200 - 100
        df["struct_wave"] = pandas_wma(struct_raw, 8)

        # ════════════════════════════════════════════════════════════════
        # KONVERGENSI (sesuai Pine Script)
        # ════════════════════════════════════════════════════════════════
        df["max_buy"] = ((df["vol_wave"] > 80) & (df["trend_wave"] > 80) & 
                         (df["dom_wave"] > 80) & (df["struct_wave"] > 80))
        df["max_sell"] = ((df["vol_wave"] < -80) & (df["trend_wave"] < -80) & 
                          (df["dom_wave"] < -80) & (df["struct_wave"] < -80))
        df["cross_up"] = ((df["vol_wave"] > 0) & (df["trend_wave"] > 0) & 
                          (df["dom_wave"] > 0) & (df["struct_wave"] > 0))
        df["cross_down"] = ((df["vol_wave"] < 0) & (df["trend_wave"] < 0) & 
                            (df["dom_wave"] < 0) & (df["struct_wave"] < 0))

        # Inflow & supporting
        df["value_now_m"] = (df["Close"] * df["Volume"]) / 1e6
        df["value_ma20"] = df["value_now_m"].rolling(20).mean()
        df["inflow_ratio"] = df["value_now_m"] / df["value_ma20"].replace(0, 1e-9)

        # Bull Score composite (untuk grading internal)
        df["bull_score"] = (
            df["vol_wave"].clip(-100, 100) / 100 * 25 +
            df["trend_wave"].clip(-100, 100) / 100 * 25 +
            df["dom_wave"].clip(-100, 100) / 100 * 25 +
            df["struct_wave"].clip(-100, 100) / 100 * 25
        ).clip(-100, 100)

        # BSJP / BPJS metrics
        df["close_position"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"]).replace(0, 1e-9)
        df["candle_range_pct"] = (df["High"] - df["Low"]) / df["Close"] * 100
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
    body_p = abs(p["Close"] - p["Open"])
    range_c = max(c["High"] - c["Low"], 0.001)
    range_p = max(p["High"] - p["Low"], 0.001)
    upper_shadow_c = c["High"] - max(c["Close"], c["Open"])
    lower_shadow_c = min(c["Close"], c["Open"]) - c["Low"]

    if (p2["Close"] < p2["Open"]) and (body_p <= range_p * 0.3) and (body_p <= p["Close"] * 0.01)        and (c["Close"] > c["Open"]) and (c["Close"] >= (p2["Open"] + p2["Close"]) / 2):
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
# 2B. LPM SMART MONEY ENGINE (Pine Script v6 Translation)
# ──────────────────────────────────────────────────────────────────────────────
def compute_lpm_metrics(df,
                        vol_length=20, big_vol_mult=1.5, smooth_len=5, max_rel_vol=4.0,
                        use_absorption=True, atr_len=14, spread_limit=0.8, absorb_boost=0.25,
                        use_vp=True, vp_lookback=50, vp_value_area=70.0,
                        lookback=50, dte_len=14, exhaust_level=90.0,
                        div_left=3, div_right=3, require_vol_confirm=False,
                        trend_pivot_len=5, trend_smooth=3):
    """Compute LPM + DTE + VP metrics from Pine Script v6 (@yucuppucuy)."""
    if df is None or len(df) < max(200, lookback + vp_lookback + 20):
        return None

    df = df.copy()

    # 1. Relative Volume
    avg_vol = df["Volume"].rolling(vol_length).mean()
    rel_vol_raw = (df["Volume"] / avg_vol.replace(0, np.nan)).fillna(0)
    rel_vol = rel_vol_raw.clip(upper=max_rel_vol)
    is_big_money = rel_vol_raw >= big_vol_mult
    vol_weight = (rel_vol - 1.0).clip(lower=0.0)

    # 2. Volume Profile
    if use_vp:
        vol_sum = df["Volume"].rolling(vp_lookback).sum().replace(0, np.nan)
        poc = (df["Close"] * df["Volume"]).rolling(vp_lookback).sum() / vol_sum
        vp_std = df["Close"].rolling(vp_lookback).std()
        vp_mult_map = {90: 1.645, 80: 1.282, 70: 1.036, 60: 0.842, 50: 0.674}
        vp_mult = 1.036
        for k, v in sorted(vp_mult_map.items(), reverse=True):
            if vp_value_area >= k:
                vp_mult = v
                break
        vah = poc + vp_std * vp_mult
        val = poc - vp_std * vp_mult
        in_va = (df["Close"] >= val) & (df["Close"] <= vah)
        above_vah = df["Close"] > vah
        below_val = df["Close"] < val
    else:
        poc = df["Close"].rolling(vp_lookback).mean()
        vah = poc
        val = poc
        in_va = pd.Series(True, index=df.index)
        above_vah = pd.Series(False, index=df.index)
        below_val = pd.Series(False, index=df.index)

    # 3. Intra-bar Liquidity Pressure
    rng = df["High"] - df["Low"]
    rng_safe = rng.replace(0, np.nan)
    intra_pressure = (((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / rng_safe).fillna(0)

    # 4. Absorption Logic
    atr_val = df["atr"] if "atr" in df.columns else ta.volatility.AverageTrueRange(
        df["High"], df["Low"], df["Close"], window=atr_len).average_true_range()
    small_spread = rng <= atr_val * spread_limit
    close_upper = (df["Close"] >= df["Low"] + rng * 0.60) & (rng > 0)
    close_lower = (df["Close"] <= df["Low"] + rng * 0.40) & (rng > 0)
    down_pressure = (df["Close"] <= df["Close"].shift(1)) | (df["High"] < df["High"].shift(1))
    up_pressure = (df["Close"] >= df["Close"].shift(1)) | (df["Low"] > df["Low"].shift(1))

    buy_abs_base = is_big_money & small_spread & close_upper & down_pressure
    sell_abs_base = is_big_money & small_spread & close_lower & up_pressure

    if use_vp:
        buy_absorption = buy_abs_base & (below_val | in_va)
        sell_absorption = sell_abs_base & (above_vah | in_va)
    else:
        buy_absorption = buy_abs_base
        sell_absorption = sell_abs_base

    abs_adj = pd.Series(0.0, index=df.index)
    abs_adj[buy_absorption] = absorb_boost
    abs_adj[sell_absorption] = -absorb_boost

    pressure_adj = (intra_pressure + abs_adj).clip(-1.0, 1.0)

    # 5. LPM Raw -> Cumulative -> Smooth
    lpm_raw = pressure_adj * df["Volume"] * vol_weight
    lpm_cum = lpm_raw.fillna(0).cumsum()
    lpm_smooth = lpm_cum.ewm(span=smooth_len, adjust=False).mean()
    lpm_momentum = lpm_smooth.diff()

    # 6. Normalize 0-100
    lpm_high = lpm_smooth.rolling(lookback).max()
    lpm_low = lpm_smooth.rolling(lookback).min()
    denom = lpm_high - lpm_low
    lpm_norm = pd.Series(50.0, index=df.index)
    valid = (denom > 0) & denom.notna()
    lpm_norm[valid] = ((lpm_smooth[valid] - lpm_low[valid]) / denom[valid]) * 100.0
    lpm_norm = lpm_norm.clip(0, 100)

    # 7. Confidence Score
    confidence = lpm_norm.ewm(span=5, adjust=False).mean()

    # 8. DTE (Distance To Exhaustion)
    conf_change = confidence.diff()
    conf_slope = conf_change.ewm(span=dte_len, adjust=False).mean()
    dist_exhaust = exhaust_level - confidence
    dte = pd.Series(np.nan, index=df.index)
    dte_mask = (dist_exhaust > 0) & (conf_slope > 0)
    dte[dte_mask] = dist_exhaust[dte_mask] / conf_slope[dte_mask]

    is_exhausted = confidence >= exhaust_level
    no_buildup = (conf_slope <= 0) & (confidence < exhaust_level)

    # 9. Pivot-based Divergence
    def find_pivots(series, left, right, high=True):
        window = left + right + 1
        if high:
            roll = series.rolling(window=window, center=True).max()
            pivots = (series == roll) & (series > series.shift(left))
        else:
            roll = series.rolling(window=window, center=True).min()
            pivots = (series == roll) & (series < series.shift(left))
        return pivots

    price_pivot_low = find_pivots(df["Low"], div_left, div_right, high=False)
    price_pivot_high = find_pivots(df["High"], div_left, div_right, high=True)

    bull_div = pd.Series(False, index=df.index)
    bear_div = pd.Series(False, index=df.index)

    low_idx = df.index[price_pivot_low].tolist()
    high_idx = df.index[price_pivot_high].tolist()

    if len(low_idx) >= 2:
        for i in range(1, len(low_idx)):
            c_idx, p_idx = low_idx[i], low_idx[i-1]
            if (df.loc[c_idx, "Low"] < df.loc[p_idx, "Low"]) and                (lpm_smooth.loc[c_idx] > lpm_smooth.loc[p_idx]):
                if (not require_vol_confirm) or is_big_money.loc[c_idx]:
                    bull_div.loc[c_idx] = True

    if len(high_idx) >= 2:
        for i in range(1, len(high_idx)):
            c_idx, p_idx = high_idx[i], high_idx[i-1]
            if (df.loc[c_idx, "High"] > df.loc[p_idx, "High"]) and                (lpm_smooth.loc[c_idx] < lpm_smooth.loc[p_idx]):
                if (not require_vol_confirm) or is_big_money.loc[c_idx]:
                    bear_div.loc[c_idx] = True

    # 10. Trend Status (pivot on LPM normalized smooth)
    lpm_smooth_trend = lpm_norm.ewm(span=trend_smooth, adjust=False).mean()
    lpm_ph = find_pivots(lpm_smooth_trend, trend_pivot_len, trend_pivot_len, high=True)
    lpm_pl = find_pivots(lpm_smooth_trend, trend_pivot_len, trend_pivot_len, high=False)

    ph_idx = df.index[lpm_ph].tolist()
    pl_idx = df.index[lpm_pl].tolist()

    last_ph = lpm_smooth_trend.loc[ph_idx[-1]] if len(ph_idx) >= 1 else np.nan
    last_pl = lpm_smooth_trend.loc[pl_idx[-1]] if len(pl_idx) >= 1 else np.nan

    latest_norm = lpm_norm.iloc[-1]
    if not np.isnan(last_ph) and latest_norm > last_ph:
        trend_status = "ABOVE HIGH"
    elif not np.isnan(last_pl) and latest_norm < last_pl:
        trend_status = "BELOW LOW"
    else:
        trend_status = "IN RANGE"

    # 11. State Logic
    strong_accum = (confidence >= 75) & (lpm_momentum > 0) & (~is_exhausted)
    accumulation = bull_div | buy_absorption | ((confidence >= 60) & (lpm_momentum > 0) & is_big_money)
    distribution = bear_div | sell_absorption | ((confidence <= 25) & (lpm_momentum < 0))

    lpm_state = pd.Series("NEUTRAL", index=df.index)
    lpm_state[is_exhausted] = "EXHAUSTED"
    lpm_state[strong_accum] = "STRONG ACCUM"
    lpm_state[accumulation & ~strong_accum & ~is_exhausted] = "ACCUMULATION"
    lpm_state[distribution & ~is_exhausted] = "DISTRIBUTION"
    lpm_state[no_buildup & ~is_exhausted] = "NO BUILDUP"

    # VP Position label
    vp_pos = pd.Series("NEUTRAL", index=df.index)
    vp_pos[above_vah] = "ABOVE VAH"
    vp_pos[below_val] = "BELOW VAL"
    vp_pos[in_va & ~above_vah & ~below_val] = "IN VALUE AREA"

    # Assign to df
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
    df["no_buildup"] = no_buildup
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
    bd = {}
    score = 0

    state_map = {"STRONG ACCUM": 40, "ACCUMULATION": 25, "DISTRIBUTION": -20, "EXHAUSTED": -10, "NO BUILDUP": -5, "NEUTRAL": 0}
    state_pts = state_map.get(latest["lpm_state"], 0)
    bd["LPM State"] = state_pts
    score += state_pts

    abs_pts = 25 if latest["buy_absorption"] else 0
    bd["Buy Absorption"] = abs_pts
    score += abs_pts

    div_pts = 20 if latest["bull_div"] else 0
    bd["Bull Divergence"] = div_pts
    score += div_pts

    bm_pts = 10 if latest["is_big_money"] else 0
    bd["Big Money"] = bm_pts
    score += bm_pts

    vp_pts = 5 if latest["vp_position"] == "BELOW VAL" else (3 if latest["vp_position"] == "IN VALUE AREA" else 0)
    bd["VP Position"] = vp_pts
    score += vp_pts

    mom_pts = 5 if latest["lpm_momentum"] > 0 else 0
    bd["LPM Momentum"] = mom_pts
    score += mom_pts

    exh_pts = 5 if not latest["is_exhausted"] else 0
    bd["Not Exhausted"] = exh_pts
    score += exh_pts

    return max(0, min(100, score)), bd

def grade_lpm(score):
    if score >= 90: return "🔥 SNIPER"
    elif score >= 80: return "💎 PRIME"
    elif score >= 70: return "✅ STRONG"
    elif score >= 60: return "⚠️ WATCH"
    return "❌ SKIP"

# ──────────────────────────────────────────────────────────────────────────────
# 3. AUL WAVE FILTER — 4 GELOMBANG dengan MIN-MAX
# ──────────────────────────────────────────────────────────────────────────────
def check_aul_wave_filter(df, f):
    """Filter 4 gelombang dengan range (min-max) + opsi rising + konvergensi."""
    if df is None or len(df) < 5: return False
    latest, prev = df.iloc[-1], df.iloc[-2]

    if f["yellow_enabled"]:
        if not (f["yellow_min"] <= latest["vol_wave"] <= f["yellow_max"]): return False
        if f["yellow_rising"] and not (latest["vol_wave"] > prev["vol_wave"]): return False
    if f["blue_enabled"]:
        if not (f["blue_min"] <= latest["trend_wave"] <= f["blue_max"]): return False
        if f["blue_rising"] and not (latest["trend_wave"] > prev["trend_wave"]): return False
    if f["purple_enabled"]:
        if not (f["purple_min"] <= latest["dom_wave"] <= f["purple_max"]): return False
        if f["purple_rising"] and not (latest["dom_wave"] > prev["dom_wave"]): return False
    if f["white_enabled"]:
        if not (f["white_min"] <= latest["struct_wave"] <= f["white_max"]): return False
        if f["white_rising"] and not (latest["struct_wave"] > prev["struct_wave"]): return False
    if f["require_cross_up"] and not latest["cross_up"]: return False
    if f["require_max_buy"] and not latest["max_buy"]: return False
    return True

# ──────────────────────────────────────────────────────────────────────────────
# 4. CONFLUENCE ENGINE
# ──────────────────────────────────────────────────────────────────────────────
def ultimate_confluence_score(df):
    if df is None or len(df) < 200: return 0, {}
    latest, prev, prev2 = df.iloc[-1], df.iloc[-2], df.iloc[-3]
    breakdown = {}

    trend_pts = 0
    if latest["ema50"] > latest["ema200"]: trend_pts += 10
    if latest["Close"] > latest["ema50"]: trend_pts += 5
    if latest["ema20"] > latest["ema50"]: trend_pts += 5
    if latest["trend_wave"] > 0: trend_pts = min(trend_pts + 3, 20)
    breakdown["Trend"] = trend_pts

    struct_pts = 0
    if latest["struct_wave"] <= -40: struct_pts += 12
    elif latest["struct_wave"] <= -20: struct_pts += 6
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

    total = trend_pts + struct_pts + flow_pts + mom_pts + pa_pts
    if struct_pts >= 15 and mom_pts >= 15:
        total -= 5
        breakdown["CorrelationPenalty"] = -5
    return max(total, 0), breakdown

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
    if df is None or len(df) < 30: return 0, {}
    latest, prev = df.iloc[-1], df.iloc[-2]
    bd = {}
    cs_pts = 0
    if latest["candle_range_pct"] >= 1.0:
        if latest["close_position"] >= 0.8: cs_pts += 20
        elif latest["close_position"] >= 0.65: cs_pts += 12
    else: cs_pts += 3
    if latest["Close"] > latest["Open"]: cs_pts += 10
    bd["Closing Strength"] = cs_pts

    gap_pts = 0
    if latest["gap_up_rate"] >= 65: gap_pts += 12
    elif latest["gap_up_rate"] >= 55: gap_pts += 8
    elif latest["gap_up_rate"] >= 50: gap_pts += 4
    gap_pts += int(min(max(latest["avg_overnight"], 0) * 5, 13))
    if latest["avg_overnight"] > 0.3: gap_pts += 5
    elif latest["avg_overnight"] > 0: gap_pts += 2
    bd["Gap-Up Edge"] = gap_pts

    acc_pts = 0
    if latest["vol_wave"] > prev["vol_wave"]: acc_pts += 8
    if latest["inflow_ratio"] >= 1.3: acc_pts += 8
    elif latest["inflow_ratio"] >= 1.1: acc_pts += 4
    if latest["vol_wave"] > 0: acc_pts += 4
    bd["Accumulation"] = acc_pts

    trend_pts = 0
    if latest["Close"] > latest["ema20"]: trend_pts += 5
    if latest["ema20"] > latest["ema50"]: trend_pts += 4
    if latest["dom_wave"] > 0: trend_pts += 3
    if 40 < latest["rsi"] < 70: trend_pts += 3
    bd["Trend Support"] = trend_pts

    return min(cs_pts + gap_pts + acc_pts + trend_pts, 100), bd

def bpjs_score(df):
    if df is None or len(df) < 30: return 0, {}
    latest, prev = df.iloc[-1], df.iloc[-2]
    bd = {}
    intra_pts = 0
    if latest["intraday_win_rate"] >= 65: intra_pts += 12
    elif latest["intraday_win_rate"] >= 55: intra_pts += 8
    elif latest["intraday_win_rate"] >= 50: intra_pts += 4
    if latest["avg_intraday"] > 0.5: intra_pts += 8
    elif latest["avg_intraday"] > 0: intra_pts += 4
    recent = df["intraday_return"].tail(20)
    wins = recent[recent > 0]; losses = recent[recent < 0]
    if len(wins) > 0 and len(losses) > 0:
        pf = wins.mean() / abs(losses.mean())
        if pf >= 2.0: intra_pts += 15
        elif pf >= 1.5: intra_pts += 10
        elif pf >= 1.0: intra_pts += 5
    bd["Intraday Edge"] = intra_pts

    range_pts = 0
    atr_avg = df["atr"].rolling(10).mean().iloc[-1]
    if latest["Close"] > latest["Open"] or latest["dom_wave"] > 0:
        if latest["atr"] > atr_avg * 1.2: range_pts += 12
        elif latest["atr"] > atr_avg: range_pts += 6
    if latest["Volume"] > df["Volume"].rolling(20).mean().iloc[-1] * 1.3: range_pts += 8
    bd["Range Expansion"] = range_pts

    mom_pts = 0
    if latest["dom_wave"] > prev["dom_wave"]: mom_pts += 10
    if latest["dom_wave"] > 0: mom_pts += 5
    if 50 < latest["rsi"] < 70: mom_pts += 10
    bd["Momentum"] = mom_pts

    trend_pts = 0
    if latest["Close"] > latest["ema20"] > latest["ema50"]: trend_pts += 12
    elif latest["Close"] > latest["ema20"]: trend_pts += 6
    if latest["inflow_ratio"] >= 1.2: trend_pts += 8
    elif latest["inflow_ratio"] >= 1.0: trend_pts += 4
    bd["Trend Alignment"] = trend_pts

    return min(intra_pts + range_pts + mom_pts + trend_pts, 100), bd

def grade_bsjp_bpjs(score):
    if score >= 80: return "🔥 PRIME"
    elif score >= 70: return "💎 STRONG"
    elif score >= 60: return "✅ VALID"
    elif score >= 50: return "⚠️ WATCH"
    return "❌ SKIP"

# ──────────────────────────────────────────────────────────────────────────────
# 5. AI PROMPT
# ──────────────────────────────────────────────────────────────────────────────
def build_ai_prompt(ticker, df, conf_score, conf_bd, pattern, trade_plan, bsjp, bpjs, lpm_data=None):
    latest = df.iloc[-1]
    entry, sl, tp1, tp2, rr = trade_plan
    bs_score, _ = bsjp
    bp_score, _ = bpjs
    conv = "🔥 MAX BUY" if latest["max_buy"] else ("🌅 CROSS UP" if latest["cross_up"] else 
           ("🔻 MAX SELL" if latest["max_sell"] else ("🌇 CROSS DOWN" if latest["cross_down"] else "—")))

    lpm_section = ""
    if lpm_data and "lpm_norm" in latest:
        dte_val = latest["dte"]
        dte_str = f"{dte_val:.1f}" if not pd.isna(dte_val) else "N/A"
        lpm_section = f"""
🧠 LPM SMART MONEY (Pine Script v6 @yucuppucuy):
- LPM Norm: {latest['lpm_norm']:.1f} | Confidence: {latest['lpm_confidence']:.1f}%
- State: {latest['lpm_state']} | Trend: {latest['lpm_trend_status']}
- Rel Volume: {latest['rel_vol']:.2f}x | Big Money: {'YES' if latest['is_big_money'] else 'NO'}
- Buy Absorption: {'YES' if latest['buy_absorption'] else 'NO'} | Sell Absorption: {'YES' if latest['sell_absorption'] else 'NO'}
- Bull Divergence: {'YES' if latest['bull_div'] else 'NO'} | Bear Divergence: {'YES' if latest['bear_div'] else 'NO'}
- VP Position: {latest['vp_position']} | DTE: {dte_str} bars
- LPM Sniper Score: {lpm_data.get('score', 0)}/100 ({lpm_data.get('grade', 'N/A')})
"""

    return f"""Anda adalah trader profesional. Analisis {ticker} berdasarkan DATA KONKRIT:

📊 PRICE: Close {latest['Close']:.2f} | Pattern: {pattern} | Close Pos: {latest['close_position']*100:.1f}%

🌊 AUL WAVE 4 GELOMBANG (Pine Script @yucuppucuy):
- 🟡 Vol Wave (Kuning/Smart Money): {latest['vol_wave']:.1f}
- 🔵 Trend Wave (Biru/TSI): {latest['trend_wave']:.1f}
- 🟣 Dom Wave (Ungu/RSI Power): {latest['dom_wave']:.1f}
- ⚪ Struct Wave (Putih/Position): {latest['struct_wave']:.1f}
- 🎯 Konvergensi: {conv}
{lpm_section}
📈 INDIKATOR: RSI {latest['rsi']:.1f} | ATR {latest['atr']:.2f} | Inflow {latest['inflow_ratio']:.2f}x
EMA20 {latest['ema20']:.2f} | EMA50 {latest['ema50']:.2f} | EMA200 {latest['ema200']:.2f}

🎯 CONFLUENCE ({conf_score}/100 → {grade_signal(conf_score)}):
Trend {conf_bd.get('Trend',0)} | Struct {conf_bd.get('Structure',0)} | SmartMoney {conf_bd.get('SmartMoney',0)} | Mom {conf_bd.get('Momentum',0)} | PA {conf_bd.get('PriceAction',0)}

⏰ INTRADAY: BSJP {bs_score} ({grade_bsjp_bpjs(bs_score)}) | BPJS {bp_score} ({grade_bsjp_bpjs(bp_score)})

💰 PLAN: Entry {entry:.2f} | SL {sl:.2f} | TP1 {tp1:.2f} | TP2 {tp2:.2f} | RR 1:{rr}

INSTRUKSI:
1. VERDICT (BUY/WAIT/AVOID) + alasan data.
2. Highlight gelombang Aul Wave terkuat & terlemah.
3. Analisis LPM Smart Money: apakah ada akumulasi institusional, absorption, atau divergence?
4. Rekomendasi: Swing vs BSJP vs BPJS vs LPM Sniper (pilih skor tertinggi).
5. Max 250 kata, bahasa Indonesia, padat & actionable."""

# ──────────────────────────────────────────────────────────────────────────────
# 6. SCANNER
# ──────────────────────────────────────────────────────────────────────────────
def scan_ticker(ticker, timeframe, market, lpm_settings=None):
    try:
        symbol = f"{ticker}.JK" if market == "IHSG" else f"{ticker}-USD"
        df = fetch_data(symbol, timeframe)
        df = compute_technicals(df)
        if df is None or len(df) < 200: return None

        # Compute LPM if settings provided
        lpm_df = compute_lpm_metrics(df, **lpm_settings) if lpm_settings else None
        if lpm_df is not None:
            df = lpm_df

        latest = df.iloc[-1]
        conf_score, conf_bd = ultimate_confluence_score(df)
        bs_score, bs_bd = bsjp_score(df)
        bp_score, bp_bd = bpjs_score(df)
        pattern = detect_patterns(df)
        trade_plan = calc_trade_plan(latest)

        lpm_score, lpm_bd = (0, {}) if lpm_df is None else lpm_sniper_score(df)

        conv = "MAX BUY" if latest["max_buy"] else ("CROSS UP" if latest["cross_up"] else 
               ("MAX SELL" if latest["max_sell"] else ("CROSS DOWN" if latest["cross_down"] else "-")))

        result = {
            "Ticker": ticker, "Symbol": symbol,
            "Close": round(latest["Close"], 4),
            "RSI": round(latest["rsi"], 1),
            "🟡 Vol": round(latest["vol_wave"], 1),
            "🔵 Trend": round(latest["trend_wave"], 1),
            "🟣 Dom": round(latest["dom_wave"], 1),
            "⚪ Struct": round(latest["struct_wave"], 1),
            "Conv": conv,
            "Confluence": conf_score, "Grade": grade_signal(conf_score),
            "BSJP": bs_score, "BSJP Grade": grade_bsjp_bpjs(bs_score),
            "BPJS": bp_score, "BPJS Grade": grade_bsjp_bpjs(bp_score),
            "Pattern": pattern, "Inflow": round(latest["inflow_ratio"], 2),
            "_df": df, "_conf_bd": conf_bd, "_bs_bd": bs_bd, "_bp_bd": bp_bd,
            "_trade_plan": trade_plan,
        }

        if lpm_df is not None:
            dte_val = latest["dte"]
            result.update({
                "LPM Norm": round(latest["lpm_norm"], 1),
                "LPM Conf": round(latest["lpm_confidence"], 1),
                "LPM State": latest["lpm_state"],
                "LPM Trend": latest["lpm_trend_status"],
                "RelVol": round(latest["rel_vol"], 2),
                "BigMoney": "YES" if latest["is_big_money"] else "NO",
                "BuyAbs": "YES" if latest["buy_absorption"] else "NO",
                "SellAbs": "YES" if latest["sell_absorption"] else "NO",
                "BullDiv": "YES" if latest["bull_div"] else "NO",
                "BearDiv": "YES" if latest["bear_div"] else "NO",
                "DTE": round(dte_val, 1) if not pd.isna(dte_val) else "N/A",
                "VP Pos": latest["vp_position"],
                "LPM Score": lpm_score,
                "LPM Grade": grade_lpm(lpm_score),
                "_lpm_bd": lpm_bd,
            })

        return result
    except Exception:
        return None

def run_scan(tickers, timeframe, market, thresholds, aul_filters, mode, lpm_settings=None):
    results = []
    progress = st.progress(0)
    status = st.empty()
    total = len(tickers)

    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(scan_ticker, t, timeframe, market, lpm_settings): t for t in tickers}
        for i, f in enumerate(futures):
            try:
                r = f.result(timeout=30)
                if r:
                    if not check_aul_wave_filter(r["_df"], aul_filters):
                        progress.progress((i + 1) / total); continue
                    passed = False
                    if mode == "Confluence" and r["Confluence"] >= thresholds["conf"]: passed = True
                    elif mode == "BSJP" and r["BSJP"] >= thresholds["bsjp"]: passed = True
                    elif mode == "BPJS" and r["BPJS"] >= thresholds["bpjs"]: passed = True
                    elif mode == "ALL":
                        if (r["Confluence"] >= thresholds["conf"] or 
                            r["BSJP"] >= thresholds["bsjp"] or 
                            r["BPJS"] >= thresholds["bpjs"]): passed = True
                    elif mode == "Aul Wave Only": passed = True
                    elif mode == "LPM Smart Money":
                        if "LPM Score" in r and r["LPM Score"] >= thresholds.get("lpm", 60):
                            passed = True
                    if passed: results.append(r)
            except Exception: pass
            progress.progress((i + 1) / total)
            status.text(f"Scanning {i+1}/{total}...")

    progress.empty(); status.empty()
    return results

# ──────────────────────────────────────────────────────────────────────────────
# 7. CHART — 4 Subplots (Price, RSI, Aul Wave, LPM)
# ──────────────────────────────────────────────────────────────────────────────
def plot_chart(df, ticker, trade_plan):
    entry, sl, tp1, tp2, _ = trade_plan
    has_lpm = "lpm_norm" in df.columns

    rows = 4 if has_lpm else 3
    heights = [0.42, 0.14, 0.22, 0.22] if has_lpm else [0.5, 0.18, 0.32]
    titles = ["Price + EMA + VP", "RSI", "🌊 Aul Wave", "🧠 LPM Smart Money"] if has_lpm else ["Price + EMA", "RSI", "🌊 Aul Wave Predictive Trend Matrix"]

    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                        row_heights=heights,
                        subplot_titles=titles)

    # Row 1: Price
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"],
                                  low=df["Low"], close=df["Close"], name="Price"), row=1, col=1)
    for ema, color in [("ema20", "cyan"), ("ema50", "yellow"), ("ema200", "orange")]:
        fig.add_trace(go.Scatter(x=df.index, y=df[ema], name=ema.upper(),
                                  line=dict(color=color, width=1)), row=1, col=1)

    fig.add_hline(y=entry, line_dash="dash", line_color="white", row=1, col=1, annotation_text=f"Entry {entry:.2f}")
    fig.add_hline(y=sl, line_dash="dot", line_color="red", row=1, col=1, annotation_text=f"SL {sl:.2f}")
    fig.add_hline(y=tp1, line_dash="dot", line_color="lime", row=1, col=1, annotation_text=f"TP1 {tp1:.2f}")
    fig.add_hline(y=tp2, line_dash="dot", line_color="green", row=1, col=1, annotation_text=f"TP2 {tp2:.2f}")

    if has_lpm and "poc" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["poc"], name="POC", line=dict(color="white", width=1, dash="dash")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["vah"], name="VAH", line=dict(color="red", width=1, dash="dot")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["val"], name="VAL", line=dict(color="green", width=1, dash="dot")), row=1, col=1)

    # Row 2: RSI
    fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], name="RSI", line=dict(color="purple")), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    # Row 3: Aul Wave
    fig.add_trace(go.Scatter(x=df.index, y=df["vol_wave"], name="🟡 Vol",
                              line=dict(color="#FFD600", width=2)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["trend_wave"], name="🔵 Trend",
                              line=dict(color="#00BFFF", width=2)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["dom_wave"], name="🟣 Dom",
                              line=dict(color="#D500F9", width=2)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["struct_wave"], name="⚪ Struct",
                              line=dict(color="#FFFFFF", width=2)), row=3, col=1)
    fig.add_hline(y=80, line_color="rgba(0,100,0,0.5)", row=3, col=1, annotation_text="Super Bull")
    fig.add_hline(y=40, line_dash="dash", line_color="rgba(0,255,0,0.3)", row=3, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="gray", row=3, col=1)
    fig.add_hline(y=-40, line_dash="dash", line_color="rgba(255,0,0,0.3)", row=3, col=1)
    fig.add_hline(y=-80, line_color="rgba(139,0,0,0.5)", row=3, col=1, annotation_text="Super Bear")

    # Row 4: LPM Smart Money
    if has_lpm:
        lpm_color = "#00ff88" if df["lpm_momentum"].iloc[-1] >= 0 else "#ff3860"
        fig.add_trace(go.Scatter(x=df.index, y=df["lpm_norm"], name="LPM Norm",
                                  line=dict(color=lpm_color, width=2)), row=4, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["lpm_confidence"], name="Confidence",
                                  line=dict(color="rgba(255,255,255,0.6)", width=1)), row=4, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["lpm_smooth_trend"], name="LPM Trend",
                                  line=dict(color="rgba(255,255,0,0.3)", width=1)), row=4, col=1)

        # Absorption markers
        abs_buy_idx = df.index[df["buy_absorption"]]
        abs_sell_idx = df.index[df["sell_absorption"]]
        if len(abs_buy_idx) > 0:
            fig.add_trace(go.Scatter(x=abs_buy_idx, y=[5]*len(abs_buy_idx), mode="markers",
                                      marker=dict(color="aqua", size=8, symbol="circle"),
                                      name="Buy Absorb"), row=4, col=1)
        if len(abs_sell_idx) > 0:
            fig.add_trace(go.Scatter(x=abs_sell_idx, y=[95]*len(abs_sell_idx), mode="markers",
                                      marker=dict(color="orange", size=8, symbol="circle"),
                                      name="Sell Absorb"), row=4, col=1)

        # Divergence markers
        bull_idx = df.index[df["bull_div"]]
        bear_idx = df.index[df["bear_div"]]
        if len(bull_idx) > 0:
            fig.add_trace(go.Scatter(x=bull_idx, y=[10]*len(bull_idx), mode="markers",
                                      marker=dict(color="lime", size=10, symbol="triangle-up"),
                                      name="Bull Div"), row=4, col=1)
        if len(bear_idx) > 0:
            fig.add_trace(go.Scatter(x=bear_idx, y=[90]*len(bear_idx), mode="markers",
                                      marker=dict(color="red", size=10, symbol="triangle-down"),
                                      name="Bear Div"), row=4, col=1)

        # Zones
        fig.add_hline(y=0, line_color="rgba(128,128,128,0.5)", row=4, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="rgba(128,128,128,0.7)", row=4, col=1)
        fig.add_hline(y=75, line_dash="dash", line_color="rgba(0,255,0,0.5)", row=4, col=1, annotation_text="Strong Accum")
        fig.add_hline(y=90, line_dash="dash", line_color="rgba(255,165,0,0.5)", row=4, col=1, annotation_text="Exhausted")

    fig.update_layout(title=f"{ticker} — Aulsome Matrix Pro V8.0",
                       template="plotly_dark", height=1100 if has_lpm else 900,
                       xaxis_rangeslider_visible=False, showlegend=True,
                       paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a")
    return fig

# ──────────────────────────────────────────────────────────────────────────────
# 8. MAIN APP
# ──────────────────────────────────────────────────────────────────────────────
def main():
    init_state()
    st.title("🌊 Aulsome Matrix Pro V8.0")
    st.caption("Aul Wave Predictive Trend Matrix + LPM Smart Money Tracker PRO v6 + Confluence + BSJP/BPJS")

    with st.sidebar:
        st.header("⚙️ Configuration")
        market = st.selectbox("Market", ["IHSG", "Crypto"])
        timeframe = st.selectbox("Timeframe", ["1d", "4h", "1h", "15m"], index=0)
        mode = st.radio("Scan Mode", ["Confluence", "BSJP", "BPJS", "ALL", "Aul Wave Only", "LPM Smart Money"], index=0)

        st.markdown("---")
        st.subheader("🌊 Aul Wave Filter (4 Gelombang)")
        st.caption("Filter dengan range MIN-MAX sesuai Pine Script asli")

        with st.expander("🟡 Vol Wave - Kuning (Smart Money)", expanded=False):
            yellow_enabled = st.checkbox("Aktifkan 🟡", value=False, key="y_en")
            yellow_min, yellow_max = st.slider("Range Vol Wave", -100, 100, (0, 100), 5, key="y_range")
            yellow_rising = st.checkbox("Harus rising (naik)", value=False, key="y_ris")

        with st.expander("🔵 Trend Wave - Biru (TSI Velocity)", expanded=False):
            blue_enabled = st.checkbox("Aktifkan 🔵", value=False, key="b_en")
            blue_min, blue_max = st.slider("Range Trend Wave", -100, 100, (0, 100), 5, key="b_range")
            blue_rising = st.checkbox("Harus rising (naik)", value=False, key="b_ris")

        with st.expander("🟣 Dom Wave - Ungu (Dominance)", expanded=False):
            purple_enabled = st.checkbox("Aktifkan 🟣", value=False, key="p_en")
            purple_min, purple_max = st.slider("Range Dom Wave", -100, 100, (0, 100), 5, key="p_range")
            purple_rising = st.checkbox("Harus rising (naik)", value=False, key="p_ris")

        with st.expander("⚪ Struct Wave - Putih (Price Structure)", expanded=False):
            white_enabled = st.checkbox("Aktifkan ⚪", value=False, key="w_en")
            white_min, white_max = st.slider("Range Struct Wave", -100, 100, (-50, 50), 5, key="w_range")
            white_rising = st.checkbox("Harus rising (naik)", value=False, key="w_ris")

        with st.expander("🎯 Konvergensi (Pertemuan 4 Garis)", expanded=False):
            require_cross_up = st.checkbox("⬆️ Wajib All Cross Up (semua >0)", value=False, key="cu")
            require_max_buy = st.checkbox("🔥 Wajib MAX BUY (semua >80)", value=False, key="mb")

        aul_filters = {
            "yellow_enabled": yellow_enabled, "yellow_min": yellow_min, "yellow_max": yellow_max, "yellow_rising": yellow_rising,
            "blue_enabled": blue_enabled, "blue_min": blue_min, "blue_max": blue_max, "blue_rising": blue_rising,
            "purple_enabled": purple_enabled, "purple_min": purple_min, "purple_max": purple_max, "purple_rising": purple_rising,
            "white_enabled": white_enabled, "white_min": white_min, "white_max": white_max, "white_rising": white_rising,
            "require_cross_up": require_cross_up, "require_max_buy": require_max_buy,
        }
        active = sum([yellow_enabled, blue_enabled, purple_enabled, white_enabled])
        if active > 0: st.success(f"🌊 {active}/4 gelombang aktif")
        if require_max_buy: st.warning("🔥 Mode MAX BUY aktif (sangat ketat)")

        st.markdown("---")
        st.subheader("🧠 LPM Smart Money Tracker")
        st.caption("Pine Script v6 @yucuppucuy — Liquidity Pressure Matrix")

        with st.expander("⚙️ LPM Settings", expanded=False):
            lpm_vol_len = st.number_input("Volume MA Length", 1, 100, 20, 1, key="lpm_vl")
            lpm_big_mult = st.number_input("Big Money Threshold", 0.1, 10.0, 1.5, 0.1, key="lpm_bm")
            lpm_smooth = st.number_input("LPM Smoothing EMA", 1, 50, 5, 1, key="lpm_sm")
            lpm_max_rel = st.number_input("Max Rel Volume Cap", 1.0, 20.0, 4.0, 0.25, key="lpm_mr")
            lpm_use_abs = st.checkbox("Use Absorption Boost", value=True, key="lpm_ua")
            lpm_spread = st.number_input("Spread ATR Mult", 0.1, 5.0, 0.8, 0.1, key="lpm_sp")
            lpm_abs_boost = st.number_input("Absorption Boost", 0.0, 1.0, 0.25, 0.05, key="lpm_ab")
            lpm_use_vp = st.checkbox("Use Volume Profile", value=True, key="lpm_uvp")
            lpm_vp_look = st.number_input("VP Lookback", 10, 500, 50, 10, key="lpm_vpl")
            lpm_vp_pct = st.number_input("Value Area %", 50.0, 100.0, 70.0, 5.0, key="lpm_vpp")
            lpm_lookback = st.number_input("Norm Lookback", 5, 200, 50, 5, key="lpm_lb")
            lpm_dte_len = st.number_input("DTE Slope Period", 2, 100, 14, 1, key="lpm_dl")
            lpm_exhaust = st.number_input("Exhaustion Level", 50.0, 100.0, 90.0, 1.0, key="lpm_ex")
            lpm_div_left = st.number_input("Div Pivot Left", 1, 20, 3, 1, key="lpm_dleft")
            lpm_div_right = st.number_input("Div Pivot Right", 1, 20, 3, 1, key="lpm_dright")
            lpm_div_vol = st.checkbox("Require Big Money at Pivot", value=False, key="lpm_dv")
            lpm_trend_pivot = st.number_input("Trend Pivot Length", 2, 50, 5, 1, key="lpm_tp")
            lpm_trend_smooth = st.number_input("Trendline Smoothing", 1, 50, 3, 1, key="lpm_ts")

        lpm_settings = {
            "vol_length": int(lpm_vol_len), "big_vol_mult": float(lpm_big_mult),
            "smooth_len": int(lpm_smooth), "max_rel_vol": float(lpm_max_rel),
            "use_absorption": lpm_use_abs, "atr_len": 14, "spread_limit": float(lpm_spread),
            "absorb_boost": float(lpm_abs_boost), "use_vp": lpm_use_vp,
            "vp_lookback": int(lpm_vp_look), "vp_value_area": float(lpm_vp_pct),
            "lookback": int(lpm_lookback), "dte_len": int(lpm_dte_len),
            "exhaust_level": float(lpm_exhaust), "div_left": int(lpm_div_left),
            "div_right": int(lpm_div_right), "require_vol_confirm": lpm_div_vol,
            "trend_pivot_len": int(lpm_trend_pivot), "trend_smooth": int(lpm_trend_smooth),
        }

        st.markdown("---")
        st.subheader("🎯 Score Thresholds")
        thresholds = {
            "conf": st.slider("Min Confluence", 0, 100, 65, 5),
            "bsjp": st.slider("Min BSJP", 0, 100, 60, 5),
            "bpjs": st.slider("Min BPJS", 0, 100, 60, 5),
        }
        if mode == "LPM Smart Money":
            thresholds["lpm"] = st.slider("Min LPM Score", 0, 100, 60, 5)

        st.markdown("---")
        universe_size = st.slider("Universe Size", 50, 800, 200, 50)

        if st.button("🚀 RUN SCAN", use_container_width=True, type="primary"):
            tickers_raw = IHSG_MEGA if market == "IHSG" else CRYPTO_MEGA
            tickers = tickers_raw.split()[:universe_size]
            lpm_s = lpm_settings if mode == "LPM Smart Money" else None
            with st.spinner(f"Scanning {len(tickers)} tickers..."):
                st.session_state["results"] = run_scan(tickers, timeframe, market, thresholds, aul_filters, mode, lpm_s)
                st.session_state["scan_triggered"] = True
                st.session_state["last_scan_time"] = datetime.now().strftime("%H:%M:%S")
                st.session_state["scan_mode"] = mode

    # ─── MAIN PANEL ───
    if st.session_state["scan_triggered"]:
        results = st.session_state["results"]
        if not results:
            st.warning("❌ Tidak ada ticker yang lolos. Longgarkan range filter Aul Wave, threshold, atau LPM settings.")
            return

        sort_map = {"Confluence": "Confluence", "BSJP": "BSJP", "BPJS": "BPJS",
                    "ALL": "Confluence", "Aul Wave Only": "🟡 Vol", "LPM Smart Money": "LPM Score"}
        sort_key = sort_map.get(st.session_state["scan_mode"], "Confluence")
        results = sorted(results, key=lambda x: x.get(sort_key, 0), reverse=True)

        st.success(f"✅ {len(results)} lolos | Mode: **{st.session_state['scan_mode']}** | Scan: {st.session_state['last_scan_time']}")

        df_display = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in results])

        has_lpm = any("LPM Score" in r for r in results)
        if has_lpm:
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Total", len(results))
            c2.metric("🔥 Sniper", sum(1 for r in results if r.get("Confluence", 0) >= 85))
            c3.metric("🌅 BSJP Prime", sum(1 for r in results if r.get("BSJP", 0) >= 80))
            c4.metric("🌇 BPJS Prime", sum(1 for r in results if r.get("BPJS", 0) >= 80))
            c5.metric("🎯 MAX BUY", sum(1 for r in results if r.get("Conv") == "MAX BUY"))
            c6.metric("🧠 LPM SNIPER", sum(1 for r in results if r.get("LPM Score", 0) >= 90))
        else:
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Total", len(results))
            c2.metric("🔥 Sniper", sum(1 for r in results if r.get("Confluence", 0) >= 85))
            c3.metric("🌅 BSJP Prime", sum(1 for r in results if r.get("BSJP", 0) >= 80))
            c4.metric("🌇 BPJS Prime", sum(1 for r in results if r.get("BPJS", 0) >= 80))
            c5.metric("🎯 MAX BUY", sum(1 for r in results if r.get("Conv") == "MAX BUY"))

        st.dataframe(df_display, use_container_width=True, height=400)
        st.download_button("📥 Download CSV", df_display.to_csv(index=False),
                           f"aulsome_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")

        st.markdown("---")
        st.subheader("🔬 Deep Analysis")
        selected = st.selectbox("Pilih Ticker", [r["Ticker"] for r in results])
        sel = next(r for r in results if r["Ticker"] == selected)

        st.markdown("#### 🌊 Aul Wave Status (4 Gelombang Asli)")
        w1, w2, w3, w4, w5 = st.columns(5)
        w1.metric("🟡 Vol (Kuning)", f"{sel['🟡 Vol']}")
        w2.metric("🔵 Trend (Biru)", f"{sel['🔵 Trend']}")
        w3.metric("🟣 Dom (Ungu)", f"{sel['🟣 Dom']}")
        w4.metric("⚪ Struct (Putih)", f"{sel['⚪ Struct']}")
        w5.metric("🎯 Konvergensi", sel["Conv"])

        st.markdown("#### 📊 Strategy Scores")
        cA, cB, cC = st.columns(3)
        cA.metric("Confluence", f"{sel['Confluence']}/100", sel["Grade"])
        cB.metric("🌅 BSJP", f"{sel['BSJP']}/100", sel["BSJP Grade"])
        cC.metric("🌇 BPJS", f"{sel['BPJS']}/100", sel["BPJS Grade"])

        if has_lpm and "LPM Score" in sel:
            st.markdown("#### 🧠 LPM Smart Money Status")
            lpm_cols = st.columns(6)
            lpm_cols[0].metric("LPM Norm", f"{sel.get('LPM Norm', 'N/A')}")
            lpm_cols[1].metric("Confidence", f"{sel.get('LPM Conf', 'N/A')}%")
            lpm_cols[2].metric("LPM State", sel.get("LPM State", "N/A"))
            lpm_cols[3].metric("LPM Score", f"{sel.get('LPM Score', 0)}/100", sel.get("LPM Grade", "N/A"))
            lpm_cols[4].metric("Big Money", sel.get("BigMoney", "NO"))
            lpm_cols[5].metric("Buy Abs", sel.get("BuyAbs", "NO"))

            lpm2 = st.columns(6)
            lpm2[0].metric("Sell Abs", sel.get("SellAbs", "NO"))
            lpm2[1].metric("Bull Div", sel.get("BullDiv", "NO"))
            lpm2[2].metric("Bear Div", sel.get("BearDiv", "NO"))
            lpm2[3].metric("DTE", sel.get("DTE", "N/A"))
            lpm2[4].metric("VP Pos", sel.get("VP Pos", "N/A"))
            lpm2[5].metric("RelVol", sel.get("RelVol", "N/A"))

            with st.expander("🧠 LPM Breakdown"): st.json(sel.get("_lpm_bd", {}))

        with st.expander("📊 Confluence Breakdown"): st.json(sel["_conf_bd"])
        with st.expander("🌅 BSJP Breakdown"): st.json(sel["_bs_bd"])
        with st.expander("🌇 BPJS Breakdown"): st.json(sel["_bp_bd"])

        entry, sl, tp1, tp2, rr = sel["_trade_plan"]
        st.info(f"💰 **Trade Plan** — Entry `{entry:.4f}` | SL `{sl:.4f}` | TP1 `{tp1:.4f}` | TP2 `{tp2:.4f}` | RR 1:{rr}")

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
                        lpm_data = None
                        if has_lpm and "LPM Score" in sel:
                            lpm_data = {"score": sel.get("LPM Score", 0), "grade": sel.get("LPM Grade", "N/A")}
                        prompt = build_ai_prompt(sel["Ticker"], sel["_df"], sel["Confluence"], sel["_conf_bd"],
                                                  sel["Pattern"], sel["_trade_plan"],
                                                  (sel["BSJP"], sel["_bs_bd"]), (sel["BPJS"], sel["_bp_bd"]),
                                                  lpm_data=lpm_data)
                        resp = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.3, max_tokens=700)
                        st.markdown(resp.choices[0].message.content)
                    except Exception as e:
                        st.error(f"AI error: {e}")
    else:
        st.info("👈 Atur range MIN-MAX gelombang Aul Wave & LPM Settings di sidebar, lalu klik **RUN SCAN**.")

if __name__ == "__main__":
    main()
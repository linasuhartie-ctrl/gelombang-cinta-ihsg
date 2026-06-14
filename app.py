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
import ccxt

# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIG & UNIVERSE
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Aulsome Matrix Pro V8.5", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")

IHSG_MEGA = """AALI ABBA ABDA ABMM ACES ACST ADCP ADES ADHI ADMF ADMG ADMR ADRO AGII AGRO AHAP AISA AKPI AKRA ALDO ALKA ALMI AMAG AMAN AMAR AMFG AMIN AMMN AMRT ANJT ANTM APEX APLN ARCI ARGO ARII ARNA ARTA ARTI ARTO ASBI ASGR ASII ASRI ASRM ASSA ATIC AUTO AVIA BABP BACA BAJA BALI BANK BAPA BATA BBCA BBHI BBKP BBLD BBMD BBNI BBRI BBRM BBTN BBYB BCAP BCIC BDMN BEKS BELL BESS BEST BFIN BGTG BINA BIPI BIPP BIRD BISI BJBR BJTM BKDP BKSL BLTA BMAS BMHS BMRI BMSR BMTR BNBA BNBR BNGA BNII BNLI BOBA BOLA BPFI BRIS BREN BRMS BRNA BRPT BSDE BSIM BSSR BSWD BTEK BTEL BTON BTPN BTPS BUDI BUKK BULL BUMI BVIC BWPT BYAN CAKK CAMP CARS CASH CASS CCSI CEKA CENT CFIN CINT CITA CITY CLEO CMNP CMPP CNKO CNTX COAL CPIN CPRO CSAP CSRA CTBN CTRA DART DAYA DCII DEAL DEWA DFAM DGIK DILD DIVA DKFT DLTA DMMX DMND DNAR DNET DOID DPNS DSFI DSNG DSSA DUTI DYAN EAST EKAD ELSA EMDE EMTK ENRG EPMT ERAA ESSA ETWA EXCL FAST FASW FILM FIRE FISH FMII FOOD FORU FORZ FPNI FREN GAMA GDST GDYR GEMA GEMS GGRM GIAA GJTL GLOB GLVA GMFI GMTD GOLD GOOD GOTO GPRA GSMF GTBO GWSA GZCO HADE HAIS HDFA HEAL HERO HEXA HITS HKMU HMSP HOKI HOME HRME HRTA HRUM IATA IBST ICBP ICON IDEA IGAR IIKP IKAI IMAS IMJS IMPC INAF INAI INCF INCI INCO INDF INDO INDR INDS INDY INPC INPS INRU INTA INTP IPCC IPCM IPOL IPTV IRRA ISAT ISSP ITIC ITMG JAKS JAST JAWA JAYA JECC JGLE JIHD JKON JMAS JSPT JTPE KAEF KBLI KBLM KBLV KDSI KEEN KEJU KIAS KICI KIJA KINO KIOS KKGI KLBF KOBX KOIN KONI KPIG KRYA LAMI LCGP LEAD LINK LION LMAS LMPI LMSH LPCK LPGI LPIN LPKR LPLI LPPF LSIP LTLS MAIN MAMI MAPA MAPB MAPI MARK MASA MAYA MBAP MBSS MBTO MCAS MCOR MDIA MDKA MDLN MDRN MEDC MEGA MERK META MFIN MICE MIDI MIKA MINA MIRA MITI MKPI MLBI MLIA MLPL MLPT MMLP MNCN MOLI MORA MPMX MPPA MSIN MSKY MTDL MTEL MTLA MTMH MTPS MTRA MTSM MYOH MYOR MYRX MYTX NANO NELY NFCX NIPS NIRO NISP NOBU NRCA NZIA OASA OBMD OMED OMRE ONIX PADI PALM PAMG PANI PANR PANS PBSA PCAR PEGE PEHA PGAS PGEO PGLI PICO PJAA PKPK PLAS PLIN PNBN PNBS PNIN PNLF PNSE POLA POLI POLL POLY POOL PORT PRAS PRDA PSAB PSDN PSGO PSKT PTBA PTPP PTPW PUDA PURA PWON PYFA PZZA RAJA RALS RANC RBMS RDTX REAL RELI RICY RIGS RIMO RMBA ROCK ROTI RSGK RUIS SAFE SAME SAMF SAPX SCCO SCMA SCNP SDMU SDPC SFAN SGER SGRO SHID SIDO SILO SIMA SIMP SINI SIPD SKBM SKLT SKYB SMAR SMBR SMCB SMDR SMGR SMIL SMKL SMMA SMMT SMRA SMRU SMSM SOBI SOHO SONA SOSS SOTO SPMA SQMI SRAJ SRIL SRSN SRTG SSIA SSMS SSTM STTP SUGI SULI SUPR SURE SWAT TAXI TAYS TBIG TBLA TBMS TCID TCPI TEBE TECH TELE TFCO TGKA TIFA TINS TIRA TIRT TKIM TLDN TLKM TMAS TMPO TNCA TOBA TOYS TPIA TPMA TRAM TRIL TRIM TRIN TRIS TRJA TRST TRUK TSPC TUGU TURI ULTJ UNIC UNIT UNSP UNTR UNVR URBN VCGG VICO VINS VIVA VKTR VOKS VRNA WAPO WEHA WEGE WIFI WIKA WINS WOMF WOOD WSBP WSKT WTON YELO YPAS ZATA ZBRA ZINC ZONE ZYRX"""

CRYPTO_MEGA = """
BTC ETH BNB SOL XRP ADA DOGE AVAX DOT MATIC LINK SHIB LTC NEAR UNI APT ARB OP TIA SUI FET RNDR STX
FIL ATOM IMX HBAR ETC ICP PEPE WIF BONK ORDI INJ THETA LDO VET BEAM SEI AAVE MKR RUNE GALA EGLD
ALGO FLOW DYDX CRV SNX PENDLE JUP PYTH STRK W ENA ROSE AGIX STG AXS SAND MANA CHZ MINA KAVA GRT
AGLD JASMY TRX KAS XLM XMR BCH BSV LUNC LUNA USTC JTO 1INCH MASK ENS BLUR GLM AKT NOS IO AEVO ZK
ZRO LISTA NOT BB PIXEL PORTAL XAI ACE SATS FLOKI MEME LADYS TURBO PEOPLE TRB GAS ARK WAVES ONT ONG
NEO QTUM DGB SC XVG HOT RVN CKB SLP GNS PERP GMX WOO ZRX KNC LRC SUSHI BAKE JOE CAKE PORK BRETT
BOME MEW MYRO WEN COQ KDA OSMO RETH LPT ALT MANTA ONDO RIF NTRN PAI SKL METIS SCRT CFX ACH TRU HOOK
MAGIC GAL CORE EDU ID COMBO RDNT HIFI MAV PUNDIX BEL FRONT C98 MTL REEF ATA ALICE PROM DAR CHR SXP
STEEM KMD STRAX ADX ICX OGN NKN DENT KEY MFT DATA VTHO STMX IQ UTK OXT ANKR CTSI COS TROY PIVX SYS
SCR GFT QKC IOTX CTXC DOCK MITH TFUEL GTC MLN BOND FOR LINA DEGO EPS AUTO TKO TVK QUICK ERN RAMP
PHA BAR CITY ASR JUV ATM OG PSG SANTOS LAZIO ALPINE MIR ANC ZEN RARE CLV ALPHA FIS SPELL CHESS QI
GHST VOXEL BNX NMR VIB AST OAX DUSK LSK ARDR LOOM REQ AKRO POLS HARD STPT OOKI UNFI WING MOB MOVR
SYN HIGH FTM ONE HNT CSPR CELO KLAY XDC ZIL XEM IOST VSYS ELA NULS WTC DCR ARRR ZEC DASH NANO BTM
HC CREAM CVX FXS LQTY AMP KEEP RSR BAL BAND UMA DODO RAY SRM OCEAN QNT STORJ XTZ YFII COMP ENJ ILV
YGG PYR UOS DG REVV SENATE APE TAO SNM AR MOG SPX POPCAT BILLY MICHI CFG POLYX RBN SD ETHFI EIGEN
OKB CRO KCS GT HT FTT TON POL SDAO FLUX KSM AURORA VRA TWT TOMO TLM DIA ORN DEXT SUKU TRAC TEL UBT
WAX WAN XEC XYO ZEST TNC TITAN SYLO SWFTC SWRV TCT TUBE TTV TTC TSHP TRYB UPP UQC UMK UMB TAI BNT
BZRX CEL DHT DVF FARM HEZ IDEX INDEX MCB MDX MTA NDX RARI REN REP RGT RLY SFI SHROOM STAKE SWAG
TRADE VSP WETH YAM CELR CQT CTX OMG MBOX UFO ATLAS AUDIO BABYDOGE BONE ELON KISHU LEASH SAMO VOLT
WOJAK API3 AUCTION BICO BOBA BRD BTT CND CVC DERC EFI FIDA HFT LIT LOOKS MBL MDT MERC NEXO ORBS
ORCA POLY POWR RAD ROOK SUPER TUSD VGX VITE WABI WAXP WNXM ZB ZCL AERGO AMB AOA APPC AXE BANCA BBN
BCD BCPT BCV BFT BIX BKX BLZ BMC BMX BNTY BOS BTG BTO CAN CBT CENNZ CHAT CMT CNN COFI COSM CPC CPX
CRPT CS CSM CTR DAG DAT DBC DCC DGD DLT DMT DNT DOR DPAY DRGN DTA DTH EDR EGT EKO ELEC ELF ENG
EOSDAC ETHOS EVN EVX EXRN FUEL FUN GAM GBC GCS GMB GNO GNT GSC GTO GVT GX HMC HMQ HSR IGNIS INCNT
INS INT ITC JNT KICK KIN LA LEND LET LRN LYM MCO MDA MDS MED MEETONE MNX MOF MTN MUE NAS NCASH NEBL
NGOT NXT OCN ODN OF OST OTN OX PAL PAR PAY PAX PBL PFR PHX PLR POA POE PPT PRO PRL QASH QLC QSP R
RFR RHOC RNTB RUFF RVT SALT SAN SBD SENT SHIFT SIB SKM SMART SMT SNC SNGLS SNT SOC SPANK SRN STQ
STRAT SUB SUR TAU THRT TIO TKN TNT UKG USDT VEN VERI VEE WINGS WPR XAS XBC XBN XBT XCN XCP XDN XES
XHV XIN XMY XNC XNS XSGD XST XWC YEE YOYOW ZAP ZCO ZLA ZPT WBTC STETH WSTETH WBETH LEO DAI HYPE
USDS RAIN CC BEST FIGURE ARC TEMPO AERO VIRTUAL WLFI HYPER MASS TAPZI STL RIPPLEX SOLU
"""

# ──────────────────────────────────────────────────────────────────────────────
# 2. CORE ENGINE
# ──────────────────────────────────────────────────────────────────────────────
def init_state():
    if "results" not in st.session_state: st.session_state["results"] = []
    if "scan_triggered" not in st.session_state: st.session_state["scan_triggered"] = False
    if "last_scan_time" not in st.session_state: st.session_state["last_scan_time"] = None
    if "scan_mode" not in st.session_state: st.session_state["scan_mode"] = None
    if "fetch_stats" not in st.session_state: st.session_state["fetch_stats"] = (0, 0)

def get_client():
    try: return Groq(api_key=st.secrets.get("GROQ_KEY", ""))
    except: return None

def pandas_wma(series, window):
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

# ─── Improved CCXT data fetcher with valid symbol check ───
@st.cache_data(ttl=120, show_spinner=False)
def get_valid_crypto_tickers(universe_tickers):
    """Preload Binance markets and filter only those that exist + USDT pairs."""
    try:
        exchange = ccxt.binance()
        markets = exchange.load_markets()
        valid = set()
        for t in universe_tickers:
            symbol = f"{t}/USDT"
            if symbol in markets and markets[symbol].get("active", False):
                valid.add(t)
        return list(valid)
    except Exception:
        # fallback: return all tickers (will be filtered later by fetch error)
        return universe_tickers

@st.cache_data(ttl=600, show_spinner=False)
def fetch_data(ticker, timeframe, market):
    try:
        if market == "Crypto":
            return _fetch_ccxt(ticker, timeframe)
        else:
            return _fetch_yf(ticker, timeframe)
    except Exception:
        return None

def _fetch_yf(ticker, timeframe):
    mapping = {"15m": ("5d", "15m"), "1h": ("1mo", "1h"), "4h": ("2mo", "4h"), "1d": ("2y", "1d")}
    period, interval = mapping.get(timeframe, ("2y", "1d"))
    df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
    if df.empty or len(df) < 100: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df.dropna()

def _fetch_ccxt(ticker, timeframe):
    exchange = ccxt.binance({'enableRateLimit': True, 'timeout': 20000})
    tf_map = {"15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"}
    ccxt_tf = tf_map.get(timeframe, "1d")
    limits = {"15m": 200, "1h": 200, "4h": 300, "1d": 500}
    limit = limits.get(timeframe, 500)
    symbol = f"{ticker}/USDT"

    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=ccxt_tf, limit=limit)
    except Exception:
        return None

    if len(ohlcv) < 100:
        return None

    df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    return df.dropna()

# ─── Technicals ───
def compute_technicals(df):
    if df is None or len(df) < 100: return None
    try:
        df = df.copy()
        df["close_position"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"] + 1e-9)
        df["ema20"] = ta.trend.ema_indicator(df["Close"], window=20)
        df["ema50"] = ta.trend.ema_indicator(df["Close"], window=50)
        df["ema200"] = ta.trend.ema_indicator(df["Close"], window=200)
        df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
        df["atr"] = ta.volatility.AverageTrueRange(df["High"], df["Low"], df["Close"], window=14).average_true_range()

        hl = (df["High"] - df["Low"]).replace(0, 1e-9)
        mf_mult = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / hl
        mf_vol = mf_mult * df["Volume"]
        vol_raw = (mf_vol.rolling(20).mean() / df["Volume"].rolling(20).mean().replace(0, 1e-9)) * 100
        df["vol_wave"] = vol_raw.ewm(span=5, adjust=False).mean()

        pc = df["Close"].diff()
        ds_pc = pc.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
        ds_abs_pc = pc.abs().ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
        df["trend_wave"] = 100 * (ds_pc / ds_abs_pc.replace(0, 1e-9))

        df["dom_wave"] = ((df["rsi"] - 50) * 2).ewm(span=3, adjust=False).mean()

        hh = df["High"].rolling(20).max()
        ll = df["Low"].rolling(20).min()
        struct_raw = ((df["Close"] - ll) / (hh - ll).replace(0, 1e-9)) * 200 - 100
        df["struct_wave"] = pandas_wma(struct_raw, 8)

        df["max_buy"] = ((df["vol_wave"] > 80) & (df["trend_wave"] > 80) & (df["dom_wave"] > 80) & (df["struct_wave"] > 80))
        df["max_sell"] = ((df["vol_wave"] < -80) & (df["trend_wave"] < -80) & (df["dom_wave"] < -80) & (df["struct_wave"] < -80))
        df["cross_up"] = ((df["vol_wave"] > 0) & (df["trend_wave"] > 0) & (df["dom_wave"] > 0) & (df["struct_wave"] > 0))
        df["cross_down"] = ((df["vol_wave"] < 0) & (df["trend_wave"] < 0) & (df["dom_wave"] < 0) & (df["struct_wave"] < 0))

        df["value_now_m"] = (df["Close"] * df["Volume"]) / 1e6
        df["value_ma20"] = df["value_now_m"].rolling(20).mean()
        df["inflow_ratio"] = df["value_now_m"] / df["value_ma20"].replace(0, 1e-9)

        df["bull_score"] = (
            df["vol_wave"].clip(-100, 100) / 100 * 25 +
            df["trend_wave"].clip(-100, 100) / 100 * 25 +
            df["dom_wave"].clip(-100, 100) / 100 * 25 +
            df["struct_wave"].clip(-100, 100) / 100 * 25
        ).clip(-100, 100)

        return df.dropna()
    except Exception:
        return None

# ─── LPM ───
def compute_lpm_metrics(df, big_vol_mult=1.5, exhaust_level=90.0):
    if df is None or len(df) < 100: return None
    df = df.copy()
    vol_length, smooth_len, max_rel_vol = 20, 5, 4.0
    atr_len, spread_limit, absorb_boost = 14, 0.8, 0.25
    vp_lookback, vp_value_area = 50, 70.0
    lookback, dte_len = 50, 14
    div_left, div_right = 3, 3
    trend_pivot_len, trend_smooth = 5, 3

    avg_vol = df["Volume"].rolling(vol_length).mean()
    rel_vol_raw = (df["Volume"] / avg_vol.replace(0, np.nan)).fillna(0)
    rel_vol = rel_vol_raw.clip(upper=max_rel_vol)
    is_big_money = rel_vol_raw >= big_vol_mult
    vol_weight = (rel_vol - 1.0).clip(lower=0.0)

    vol_sum = df["Volume"].rolling(vp_lookback).sum().replace(0, np.nan)
    poc = (df["Close"] * df["Volume"]).rolling(vp_lookback).sum() / vol_sum
    vp_std = df["Close"].rolling(vp_lookback).std()
    vp_mult = 1.036 if vp_value_area >= 70 else (1.282 if vp_value_area >= 80 else 1.645)
    vah = poc + vp_std * vp_mult
    val = poc - vp_std * vp_mult
    in_va = (df["Close"] >= val) & (df["Close"] <= vah)
    above_vah = df["Close"] > vah
    below_val = df["Close"] < val

    rng = df["High"] - df["Low"]
    rng_safe = rng.replace(0, np.nan)
    intra_pressure = (((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / rng_safe).fillna(0)

    atr_val = df["atr"] if "atr" in df.columns else ta.volatility.AverageTrueRange(
        df["High"], df["Low"], df["Close"], window=atr_len).average_true_range()
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

    lpm_high = lpm_smooth.rolling(lookback).max()
    lpm_low = lpm_smooth.rolling(lookback).min()
    denom = lpm_high - lpm_low
    lpm_norm = pd.Series(50.0, index=df.index)
    valid = (denom > 0) & denom.notna()
    lpm_norm[valid] = ((lpm_smooth[valid] - lpm_low[valid]) / denom[valid]) * 100.0
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
            if (df.loc[c_idx, "Low"] < df.loc[p_idx, "Low"]) and (lpm_smooth.loc[c_idx] > lpm_smooth.loc[p_idx]):
                bull_div.loc[c_idx] = True
    if len(high_idx) >= 2:
        for i in range(1, len(high_idx)):
            c_idx, p_idx = high_idx[i], high_idx[i-1]
            if (df.loc[c_idx, "High"] > df.loc[p_idx, "High"]) and (lpm_smooth.loc[c_idx] < lpm_smooth.loc[p_idx]):
                bear_div.loc[c_idx] = True

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

    strong_accum = (confidence >= 75) & (lpm_momentum > 0) & (~is_exhausted)
    accumulation = bull_div | buy_absorption | ((confidence >= 60) & (lpm_momentum > 0) & is_big_money)
    distribution = bear_div | sell_absorption | ((confidence <= 25) & (lpm_momentum < 0))

    lpm_state = pd.Series("NEUTRAL", index=df.index)
    lpm_state[is_exhausted] = "EXHAUSTED"
    lpm_state[strong_accum] = "STRONG ACCUM"
    lpm_state[accumulation & ~strong_accum & ~is_exhausted] = "ACCUMULATION"
    lpm_state[distribution & ~is_exhausted] = "DISTRIBUTION"
    lpm_state[no_buildup & ~is_exhausted] = "NO BUILDUP"

    vp_pos = pd.Series("NEUTRAL", index=df.index)
    vp_pos[above_vah] = "ABOVE VAH"
    vp_pos[below_val] = "BELOW VAL"
    vp_pos[in_va & ~above_vah & ~below_val] = "IN VALUE AREA"

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
    if df is None or len(df) < 50: return 0, {}
    latest = df.iloc[-1]
    bd = {}
    score = 0
    state_map = {"STRONG ACCUM": 40, "ACCUMULATION": 25, "DISTRIBUTION": -20, "EXHAUSTED": -10, "NO BUILDUP": -5, "NEUTRAL": 0}
    state_pts = state_map.get(latest["lpm_state"], 0)
    bd["LPM State"] = state_pts; score += state_pts
    abs_pts = 25 if latest["buy_absorption"] else 0
    bd["Buy Absorption"] = abs_pts; score += abs_pts
    div_pts = 20 if latest["bull_div"] else 0
    bd["Bull Divergence"] = div_pts; score += div_pts
    bm_pts = 10 if latest["is_big_money"] else 0
    bd["Big Money"] = bm_pts; score += bm_pts
    vp_pts = 5 if latest["vp_position"] == "BELOW VAL" else (3 if latest["vp_position"] == "IN VALUE AREA" else 0)
    bd["VP Position"] = vp_pts; score += vp_pts
    mom_pts = 5 if latest["lpm_momentum"] > 0 else 0
    bd["LPM Momentum"] = mom_pts; score += mom_pts
    exh_pts = 5 if not latest["is_exhausted"] else 0
    bd["Not Exhausted"] = exh_pts; score += exh_pts
    return max(0, min(100, score)), bd

def grade_lpm(score):
    if score >= 90: return "🔥 SNIPER"
    elif score >= 80: return "💎 PRIME"
    elif score >= 70: return "✅ STRONG"
    elif score >= 60: return "⚠️ WATCH"
    return "❌ SKIP"

# ─── Confluence ───
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

    total = trend_pts + struct_pts + flow_pts + mom_pts
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

# ─── AI Prompt ───
def build_ai_prompt(ticker, df, conf_score, conf_bd, trade_plan, lpm_data=None):
    latest = df.iloc[-1]
    entry, sl, tp1, tp2, rr = trade_plan
    conv = "🔥 MAX BUY" if latest["max_buy"] else ("🌅 CROSS UP" if latest["cross_up"] else 
           ("🔻 MAX SELL" if latest["max_sell"] else ("🌇 CROSS DOWN" if latest["cross_down"] else "—")))
    lpm_section = ""
    if lpm_data and "lpm_norm" in latest:
        dte_val = latest["dte"]
        dte_str = f"{dte_val:.1f}" if not pd.isna(dte_val) else "N/A"
        lpm_section = f"""
🧠 LPM SMART MONEY (Pine Script v6):
- LPM Norm: {latest['lpm_norm']:.1f} | Confidence: {latest['lpm_confidence']:.1f}%
- State: {latest['lpm_state']} | Trend: {latest['lpm_trend_status']}
- Rel Volume: {latest['rel_vol']:.2f}x | Big Money: {'YES' if latest['is_big_money'] else 'NO'}
- Buy Absorption: {'YES' if latest['buy_absorption'] else 'NO'} | Sell Absorption: {'YES' if latest['sell_absorption'] else 'NO'}
- VP Position: {latest['vp_position']} | DTE: {dte_str} bars
- LPM Score: {lpm_data.get('score',0)}/100 ({lpm_data.get('grade','N/A')})
"""
    return f"""Anda trader profesional. Analisis {ticker} berdasarkan data:

📊 PRICE: Close {latest['Close']:.2f} | Close Pos: {latest['close_position']*100:.1f}%
🌊 AUL WAVE: 🟡Vol {latest['vol_wave']:.1f} 🔵Trend {latest['trend_wave']:.1f} 🟣Dom {latest['dom_wave']:.1f} ⚪Struct {latest['struct_wave']:.1f} → {conv}
{lpm_section}
📈 RSI {latest['rsi']:.1f} | ATR {latest['atr']:.2f} | Inflow {latest['inflow_ratio']:.2f}x
EMA20 {latest['ema20']:.2f} | EMA50 {latest['ema50']:.2f} | EMA200 {latest['ema200']:.2f}

🎯 CONFLUENCE ({conf_score}/100 → {grade_signal(conf_score)}):
Trend {conf_bd.get('Trend',0)} | Struct {conf_bd.get('Structure',0)} | SmartMoney {conf_bd.get('SmartMoney',0)} | Mom {conf_bd.get('Momentum',0)}

💰 PLAN: Entry {entry:.2f} | SL {sl:.2f} | TP1 {tp1:.2f} | TP2 {tp2:.2f} | RR 1:{rr}

INSTRUKSI:
1. VERDICT (BUY/WAIT/AVOID) + alasan data.
2. Highlight gelombang Aul Wave terkuat & terlemah.
3. Analisis LPM Smart Money jika ada.
4. Rekomendasi strategi terbaik.
5. Max 200 kata, bahasa Indonesia, padat & actionable."""

# ─── Scanner (simple, with feedback) ───
def scan_ticker(ticker, timeframe, market, use_lpm=False, lpm_params=None):
    try:
        df = fetch_data(ticker, timeframe, market)
        df = compute_technicals(df)
        if df is None or len(df) < 200: return None, False
        if use_lpm:
            df = compute_lpm_metrics(df, **lpm_params)
            if df is None: return None, False
        latest = df.iloc[-1]
        conf_score, conf_bd = ultimate_confluence_score(df)
        trade_plan = calc_trade_plan(latest)
        lpm_score, lpm_bd = (0, {}) if not use_lpm else lpm_sniper_score(df)
        conv = "MAX BUY" if latest["max_buy"] else ("CROSS UP" if latest["cross_up"] else 
               ("MAX SELL" if latest["max_sell"] else ("CROSS DOWN" if latest["cross_down"] else "-")))
        result = {
            "Ticker": ticker,
            "Close": round(latest["Close"], 4),
            "Confluence": conf_score, "Grade": grade_signal(conf_score),
            "Conv": conv,
            "🟡 Vol": round(latest["vol_wave"], 1),
            "🔵 Trend": round(latest["trend_wave"], 1),
            "🟣 Dom": round(latest["dom_wave"], 1),
            "⚪ Struct": round(latest["struct_wave"], 1),
            "RSI": round(latest["rsi"], 1),
            "Inflow": round(latest["inflow_ratio"], 2),
            "_df": df, "_conf_bd": conf_bd,
            "_trade_plan": trade_plan,
        }
        if use_lpm:
            dte_val = latest["dte"]
            result.update({
                "LPM Score": lpm_score, "LPM Grade": grade_lpm(lpm_score),
                "LPM State": latest["lpm_state"],
                "BuyAbs": "YES" if latest["buy_absorption"] else "NO",
                "BullDiv": "YES" if latest["bull_div"] else "NO",
                "_lpm_bd": lpm_bd,
            })
        return result, True
    except Exception:
        return None, False

def run_scan(tickers, timeframe, market, mode, lpm_params=None, min_conf=0, min_lpm=0):
    results = []
    progress = st.progress(0)
    status = st.empty()
    total = len(tickers)
    success_count = 0
    fail_count = 0

    use_lpm = (mode == "LPM Smart Money")
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(scan_ticker, t, timeframe, market, use_lpm, lpm_params): t for t in tickers}
        for i, f in enumerate(futures):
            try:
                r, ok = f.result(timeout=60)
                if ok:
                    success_count += 1
                    if mode == "Confluence" and r["Confluence"] >= min_conf:
                        results.append(r)
                    elif mode == "LPM Smart Money" and r.get("LPM Score", 0) >= min_lpm:
                        results.append(r)
                else:
                    fail_count += 1
            except Exception:
                fail_count += 1
            progress.progress((i + 1) / total)
            status.text(f"Fetch {i+1}/{total} | ✅ {success_count} | ❌ {fail_count}")
    progress.empty()
    status.empty()
    # Store stats in session
    st.session_state["fetch_stats"] = (success_count, fail_count)
    return results

# ─── Chart (unchanged) ───
def plot_chart(df, ticker, trade_plan):
    entry, sl, tp1, tp2, _ = trade_plan
    has_lpm = "lpm_norm" in df.columns
    rows = 3 if has_lpm else 2
    heights = [0.5, 0.25, 0.25] if has_lpm else [0.6, 0.4]
    titles = (["Price + EMA + VP", "🌊 Aul Wave", "🧠 LPM Smart Money"]
              if has_lpm else ["Price + EMA", "🌊 Aul Wave Predictive Trend Matrix"])
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                        row_heights=heights, subplot_titles=titles)
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
    fig.add_trace(go.Scatter(x=df.index, y=df["vol_wave"], name="🟡 Vol", line=dict(color="#FFD600", width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["trend_wave"], name="🔵 Trend", line=dict(color="#00BFFF", width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["dom_wave"], name="🟣 Dom", line=dict(color="#D500F9", width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["struct_wave"], name="⚪ Struct", line=dict(color="#FFFFFF", width=2)), row=2, col=1)
    fig.add_hline(y=80, line_color="rgba(0,100,0,0.5)", row=2, col=1, annotation_text="Super Bull")
    fig.add_hline(y=40, line_dash="dash", line_color="rgba(0,255,0,0.3)", row=2, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="gray", row=2, col=1)
    fig.add_hline(y=-40, line_dash="dash", line_color="rgba(255,0,0,0.3)", row=2, col=1)
    fig.add_hline(y=-80, line_color="rgba(139,0,0,0.5)", row=2, col=1, annotation_text="Super Bear")
    if has_lpm:
        lpm_color = "#00ff88" if df["lpm_momentum"].iloc[-1] >= 0 else "#ff3860"
        fig.add_trace(go.Scatter(x=df.index, y=df["lpm_norm"], name="LPM Norm", line=dict(color=lpm_color, width=2)), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["lpm_confidence"], name="Confidence", line=dict(color="rgba(255,255,255,0.6)", width=1)), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["lpm_smooth_trend"], name="LPM Trend", line=dict(color="rgba(255,255,0,0.3)", width=1)), row=3, col=1)
        abs_buy = df.index[df["buy_absorption"]]
        abs_sell = df.index[df["sell_absorption"]]
        if len(abs_buy): fig.add_trace(go.Scatter(x=abs_buy, y=[5]*len(abs_buy), mode="markers", marker=dict(color="aqua", size=8), name="Buy Absorb"), row=3, col=1)
        if len(abs_sell): fig.add_trace(go.Scatter(x=abs_sell, y=[95]*len(abs_sell), mode="markers", marker=dict(color="orange", size=8), name="Sell Absorb"), row=3, col=1)
        bull = df.index[df["bull_div"]]
        bear = df.index[df["bear_div"]]
        if len(bull): fig.add_trace(go.Scatter(x=bull, y=[10]*len(bull), mode="markers", marker=dict(color="lime", size=10, symbol="triangle-up"), name="Bull Div"), row=3, col=1)
        if len(bear): fig.add_trace(go.Scatter(x=bear, y=[90]*len(bear), mode="markers", marker=dict(color="red", size=10, symbol="triangle-down"), name="Bear Div"), row=3, col=1)
        fig.add_hline(y=0, line_color="rgba(128,128,128,0.5)", row=3, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="rgba(128,128,128,0.7)", row=3, col=1)
        fig.add_hline(y=75, line_dash="dash", line_color="rgba(0,255,0,0.5)", row=3, col=1, annotation_text="Strong Accum")
        fig.add_hline(y=90, line_dash="dash", line_color="rgba(255,165,0,0.5)", row=3, col=1, annotation_text="Exhausted")
    fig.update_layout(title=f"{ticker} — Aulsome Matrix Pro V8.5",
                      template="plotly_dark", height=1000 if has_lpm else 800,
                      xaxis_rangeslider_visible=False, showlegend=True,
                      paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a")
    return fig

# ──────────────────────────────────────────────────────────────────────────────
# 9. MAIN APP – Sederhana & Fokus
# ──────────────────────────────────────────────────────────────────────────────
def main():
    init_state()
    st.title("🌊 Aulsome Matrix Pro V8.5")
    st.caption("Confluence + LPM Smart Money | Hybrid Data (CCXT & Yahoo)")

    with st.sidebar:
        st.header("⚙️ Configuration")
        market = st.selectbox("Market", ["Crypto", "IHSG"], index=0)  # default Crypto
        timeframe = st.selectbox("Timeframe", ["1d", "4h", "1h"], index=0)
        mode = st.radio("Scan Mode", ["Confluence", "LPM Smart Money"], index=0)
        st.markdown("---")
        st.subheader("🎯 Filter")
        if mode == "Confluence":
            min_score = st.slider("Min Confluence Score", 0, 100, 50, 5)
        else:
            min_score = st.slider("Min LPM Score", 0, 100, 50, 5)
        st.markdown("---")
        st.subheader("🧠 LPM Settings (only for LPM mode)")
        lpm_big = st.slider("Big Money Threshold", 0.5, 5.0, 1.5, 0.1, key="lpm_big")
        lpm_exhaust = st.slider("Exhaustion Level", 50, 100, 90, 1, key="lpm_ex")
        lpm_params = {"big_vol_mult": float(lpm_big), "exhaust_level": float(lpm_exhaust)}
        st.markdown("---")
        st.subheader("📝 Custom Tickers (Optional)")
        custom_tickers = st.text_area("Paste tickers", placeholder="BTC\nETH\nSOL", height=80, key="custom")
        use_custom = st.checkbox("Use Custom Tickers", value=False, key="use_custom")
        st.markdown("---")
        universe_size = st.slider("Universe Size", 5, 300, 50, 25)

        if st.button("🚀 RUN SCAN", use_container_width=True, type="primary"):
            # Determine ticker list
            if use_custom and custom_tickers.strip():
                tickers = [t.strip().upper() for t in custom_tickers.replace(",", " ").split() if t.strip()]
                st.info(f"📋 {len(tickers)} custom tickers")
            else:
                if market == "IHSG":
                    tickers = IHSG_MEGA.split()[:universe_size]
                else:
                    base_tickers = CRYPTO_MEGA.split()
                    # Filter valid crypto tickers only
                    valid = get_valid_crypto_tickers(base_tickers[:universe_size])
                    if not valid:
                        st.warning("⚠️ Tidak bisa mengambil daftar pasar Binance. Menggunakan universe mentah.")
                        tickers = base_tickers[:universe_size]
                    else:
                        tickers = valid[:universe_size]
                        st.info(f"🔍 {len(tickers)} ticker crypto valid dari Binance")

            with st.spinner(f"Scanning {len(tickers)} tickers..."):
                st.session_state["results"] = run_scan(
                    tickers, timeframe, market, mode,
                    lpm_params=lpm_params if mode == "LPM Smart Money" else None,
                    min_conf=min_score if mode == "Confluence" else 0,
                    min_lpm=min_score if mode == "LPM Smart Money" else 0
                )
                st.session_state["scan_triggered"] = True
                st.session_state["last_scan_time"] = datetime.now().strftime("%H:%M:%S")
                st.session_state["scan_mode"] = mode

    # ─── MAIN PANEL ───
    if st.session_state["scan_triggered"]:
        results = st.session_state["results"]
        if not results:
            succ, fail = st.session_state.get("fetch_stats", (0, 0))
            st.warning(f"❌ Tidak ada ticker yang lolos. Data berhasil: {succ}, gagal: {fail}. Coba longgarkan threshold atau periksa koneksi.")
            return

        sort_key = "Confluence" if st.session_state["scan_mode"] == "Confluence" else "LPM Score"
        results = sorted(results, key=lambda x: x.get(sort_key, 0), reverse=True)

        succ, fail = st.session_state.get("fetch_stats", (0, 0))
        st.success(f"✅ {len(results)} lolos | Data ✅ {succ} ❌ {fail} | Mode: {st.session_state['scan_mode']} | {st.session_state['last_scan_time']}")

        df_display = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in results])

        has_lpm = any("LPM Score" in r for r in results)
        if has_lpm:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total", len(results))
            c2.metric("🔥 Sniper (Conf)", sum(1 for r in results if r.get("Confluence", 0) >= 85))
            c3.metric("🧠 LPM Sniper", sum(1 for r in results if r.get("LPM Score", 0) >= 90))
            c4.metric("🎯 MAX BUY", sum(1 for r in results if r.get("Conv") == "MAX BUY"))
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total", len(results))
            c2.metric("🔥 Sniper", sum(1 for r in results if r.get("Confluence", 0) >= 85))
            c3.metric("🎯 MAX BUY", sum(1 for r in results if r.get("Conv") == "MAX BUY"))

        st.dataframe(df_display, use_container_width=True, height=400)
        st.download_button("📥 Download CSV", df_display.to_csv(index=False),
                           f"aul_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")

        st.markdown("---")
        st.subheader("🔬 Deep Analysis")
        selected = st.selectbox("Pilih Ticker", [r["Ticker"] for r in results])
        sel = next(r for r in results if r["Ticker"] == selected)

        st.markdown("#### 🌊 Aul Wave")
        w1, w2, w3, w4, w5 = st.columns(5)
        w1.metric("🟡 Vol", f"{sel['🟡 Vol']}")
        w2.metric("🔵 Trend", f"{sel['🔵 Trend']}")
        w3.metric("🟣 Dom", f"{sel['🟣 Dom']}")
        w4.metric("⚪ Struct", f"{sel['⚪ Struct']}")
        w5.metric("Conv", sel["Conv"])

        cA, cB = st.columns(2)
        cA.metric("Confluence", f"{sel['Confluence']}/100", sel["Grade"])
        if has_lpm and "LPM Score" in sel:
            cB.metric("LPM Score", f"{sel['LPM Score']}/100", sel.get("LPM Grade", ""))

        if has_lpm and "LPM Score" in sel:
            with st.expander("🧠 LPM Details"):
                lpm_cols = st.columns(4)
                lpm_cols[0].metric("State", sel.get("LPM State", "N/A"))
                lpm_cols[1].metric("BuyAbs", sel.get("BuyAbs", "NO"))
                lpm_cols[2].metric("BullDiv", sel.get("BullDiv", "NO"))
                st.json(sel.get("_lpm_bd", {}))

        with st.expander("📊 Confluence Breakdown"):
            st.json(sel["_conf_bd"])

        entry, sl, tp1, tp2, rr = sel["_trade_plan"]
        st.info(f"💰 Entry `{entry:.4f}` | SL `{sl:.4f}` | TP1 `{tp1:.4f}` | TP2 `{tp2:.4f}` | RR 1:{rr}")

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
                                                  sel["_trade_plan"], lpm_data=lpm_data)
                        resp = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.3, max_tokens=600)
                        st.markdown(resp.choices[0].message.content)
                    except Exception as e:
                        st.error(f"AI error: {e}")
    else:
        st.info("👈 Atur mode & threshold di sidebar, lalu klik **RUN SCAN**.")

if __name__ == "__main__":
    main()
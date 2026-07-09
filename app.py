import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from concurrent.futures import ThreadPoolExecutor, as_completed
from groq import Groq
from datetime import datetime
import time

# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIG & UNIVERSE
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Aulsome Matrix Pro V8.6", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")

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

# ─── BATCH FETCH (yfinance multi-ticker) ───
@st.cache_data(ttl=600, show_spinner=False)
def fetch_batch(tickers, timeframe, market):
    """Download banyak ticker sekaligus, resample ke 4h secara dinamis jika diminta."""
    # Untuk 4h, kita ambil data 1h sejauh 3 bulan agar saat digabung (dibagi 4) tetap sisa >100 candle
    tf_map = {
        "15m": ("5d", "15m"), 
        "1h": ("1mo", "1h"), 
        "4h": ("3mo", "1h"), 
        "1d": ("2y", "1d")
    }
    period, interval = tf_map.get(timeframe, ("2y", "1d"))

    data = {}

    def resample_if_needed(df, tf):
        """Fungsi pembantu Pandas untuk menjahit candle jadi 4 jam"""
        if tf == "4h" and len(df) > 0:
            resampled = df.resample('4h').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            return resampled
        return df

    if market == "Crypto":
        symbols = " ".join([f"{t}-USD" for t in tickers])
        for attempt in range(3):
            try:
                df_all = yf.download(symbols, period=period, interval=interval, progress=False, auto_adjust=True, group_by='ticker')
                
                if df_all.empty:
                    time.sleep(2)
                    continue
                
                if len(tickers) == 1:
                    t = tickers[0]
                    df = df_all.copy()
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(df.columns.names.index('Price') if 'Price' in df.columns.names else 0)
                    
                    df = resample_if_needed(df, timeframe)
                    if len(df) >= 100:
                        data[t] = df.dropna()
                else:
                    for t in tickers:
                        try:
                            symbol = f"{t}-USD"
                            if isinstance(df_all.columns, pd.MultiIndex):
                                df = df_all[symbol].copy()
                            else:
                                df = df_all.copy()
                            
                            df = resample_if_needed(df, timeframe)
                            if len(df) >= 100:
                                data[t] = df.dropna()
                        except KeyError:
                            continue
                break
            except Exception:
                time.sleep(5)
        return data

    else:  # IHSG
        for t in tickers:
            symbol = f"{t}.JK"
            for attempt in range(2):
                try:
                    df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
                    if not df.empty:
                        if isinstance(df.columns, pd.MultiIndex):
                            df.columns = df.columns.get_level_values(0)
                        
                        df = resample_if_needed(df, timeframe)
                        if len(df) >= 100:
                            data[t] = df.dropna()
                    break
                except Exception:
                    time.sleep(2)
            time.sleep(0.1)
        return data

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

# ─── SCANNER ───
def scan_ticker(ticker, df_dict, use_lpm=False, lpm_params=None):
    df = df_dict.get(ticker)
    if df is None: return None, False
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

def run_scan(tickers, timeframe, market, mode, lpm_params=None, min_score=0):
    results = []
    progress = st.progress(0)
    status = st.empty()

    with st.spinner("📡 Mengunduh data..."):
        df_dict = fetch_batch(tickers, timeframe, market)

    total = len(tickers)
    success = 0
    fail = 0

    use_lpm = (mode == "LPM Smart Money")
    for i, t in enumerate(tickers):
        r, ok = scan_ticker(t, df_dict, use_lpm=use_lpm, lpm_params=lpm_params)
        if ok:
            success += 1
            if mode == "Confluence" and r["Confluence"] >= min_score:
                results.append(r)
            elif mode == "LPM Smart Money" and r.get("LPM Score", 0) >= min_score:
                results.append(r)
        else:
            fail += 1
        progress.progress((i + 1) / total)
        status.text(f"Analisis {i+1}/{total} | ✅ {success} | ❌ {fail}")
    progress.empty()
    status.empty()
    st.session_state["fetch_stats"] = (success, fail)
    return results

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
    fig.update_layout(title=f"{ticker} — Aulsome Matrix Pro V8.6",
                      template="plotly_dark", height=1000 if has_lpm else 800,
                      xaxis_rangeslider_visible=False, showlegend=True,
                      paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a")
    return fig

# ─── MAIN ───
def main():
    init_state()
    st.title("🌊 Aulsome Matrix Pro V8.6")
    st.caption("Full yfinance | Batch Download | Universe s/d 700 | Anti‑Rate‑Limit")

    with st.sidebar:
        st.header("⚙️ Configuration")
        market = st.selectbox("Market", ["Crypto", "IHSG"], index=0)
        timeframe = st.selectbox("Timeframe", ["1d", "4h", "1h"], index=0)
        mode = st.radio("Scan Mode", ["Confluence", "LPM Smart Money"], index=0)
        st.markdown("---")
        min_score = st.slider("Min Score", 0, 100, 50, 5)
        st.markdown("---")
        universe_size = st.slider("Universe Size", 10, 700, 100, 25)

        if st.button("🚀 RUN SCAN", use_container_width=True, type="primary"):
            if market == "IHSG":
                tickers = IHSG_MEGA.split()[:universe_size]
            else:
                tickers = CRYPTO_MEGA.split()[:universe_size]

            use_lpm = (mode == "LPM Smart Money")
            with st.spinner(f"Scanning {len(tickers)} tickers..."):
                st.session_state["results"] = run_scan(
                    tickers, timeframe, market, mode,
                    lpm_params={"big_vol_mult": 1.5, "exhaust_level": 90.0} if use_lpm else None,
                    min_score=min_score
                )
                st.session_state["scan_triggered"] = True
                st.session_state["last_scan_time"] = datetime.now().strftime("%H:%M:%S")
                st.session_state["scan_mode"] = mode

    if st.session_state["scan_triggered"]:
        results = st.session_state["results"]
        if not results:
            succ, fail = st.session_state.get("fetch_stats", (0, 0))
            st.warning(f"❌ Tidak ada yang lolos. Data OK: {succ}, Gagal: {fail}. Longgarkan skor atau cek koneksi.")
            return

        sort_key = "Confluence" if st.session_state["scan_mode"] == "Confluence" else "LPM Score"
        results = sorted(results, key=lambda x: x.get(sort_key, 0), reverse=True)
        succ, fail = st.session_state.get("fetch_stats", (0, 0))
        st.success(f"✅ {len(results)} lolos | Data OK: {succ} | Gagal: {fail} | {st.session_state['last_scan_time']}")

        df_display = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in results])
        has_lpm = any("LPM Score" in r for r in results)

        c1, c2, c3 = st.columns(3)
        c1.metric("Total", len(results))
        c2.metric("🔥 Sniper", sum(1 for r in results if r.get("Confluence", 0) >= 85))
        c3.metric("🎯 MAX BUY", sum(1 for r in results if r.get("Conv") == "MAX BUY"))
        if has_lpm:
            st.metric("🧠 LPM Sniper (≥90)", sum(1 for r in results if r.get("LPM Score", 0) >= 90))

        st.dataframe(df_display, use_container_width=True, height=400)
        st.download_button("📥 CSV", df_display.to_csv(index=False),
                           f"aul_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")

        st.markdown("---")
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
                lpm_cols = st.columns(3)
                lpm_cols[0].metric("State", sel.get("LPM State", ""))
                lpm_cols[1].metric("BuyAbs", sel.get("BuyAbs", ""))
                lpm_cols[2].metric("BullDiv", sel.get("BullDiv", ""))
                if "_lpm_bd" in sel: st.json(sel["_lpm_bd"])

        with st.expander("📊 Confluence Breakdown"):
            st.json(sel["_conf_bd"])

        entry, sl, tp1, tp2, rr = sel["_trade_plan"]
        st.info(f"💰 Entry `{entry:.4f}` | SL `{sl:.4f}` | TP1 `{tp1:.4f}` | TP2 `{tp2:.4f}` | RR 1:{rr}")

        st.plotly_chart(plot_chart(sel["_df"], sel["Ticker"], sel["_trade_plan"]), use_container_width=True)

        st.markdown("---")
        if st.button("🧠 AI Analysis (Groq)"):
            client = get_client()
            if not client:
                st.error("Groq API key tidak ditemukan.")
            else:
                with st.spinner("AI menganalisis..."):
                    try:
                        lpm_data = None
                        if has_lpm and "LPM Score" in sel:
                            lpm_data = {"score": sel.get("LPM Score", 0), "grade": sel.get("LPM Grade", "")}
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
        st.info("👈 Atur parameter di sidebar, lalu klik RUN SCAN.")
        
        # ============================================================
# FINAL COPY-PASTE PATCH — MATRIX SCREENER FULL
# Paste di bagian paling bawah app.py, menggantikan:
# if __name__ == "__main__":
#     main()
# ============================================================

def pandas_wma(series, window):
    weights = np.arange(1, window + 1)
    return series.rolling(window, min_periods=max(2, window // 2)).apply(
        lambda x: np.dot(x, weights[-len(x):]) / weights[-len(x):].sum(),
        raw=True
    )


def rolling_percent_rank(series, window=200):
    min_periods = min(80, max(30, window // 3))

    def _rank(x):
        x = x[~np.isnan(x)]
        if len(x) == 0:
            return np.nan
        return (np.sum(x <= x[-1]) / len(x)) * 200.0 - 100.0

    return series.rolling(window, min_periods=min_periods).apply(_rank, raw=True)


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

    def clean_columns(df, symbol=None):
        if df is None or df.empty:
            return df

        if isinstance(df.columns, pd.MultiIndex):
            if symbol is not None:
                lv0 = df.columns.get_level_values(0)
                lv1 = df.columns.get_level_values(1)

                if symbol in lv0:
                    df = df[symbol].copy()
                elif symbol in lv1:
                    df = df.xs(symbol, axis=1, level=1).copy()

            if isinstance(df.columns, pd.MultiIndex):
                for lvl in range(df.columns.nlevels):
                    vals = set(df.columns.get_level_values(lvl))
                    if {"Open", "High", "Low", "Close"}.issubset(vals):
                        df.columns = df.columns.get_level_values(lvl)
                        break

        return df

    def resample_if_needed(df, tf):
        if df is None or df.empty:
            return df

        if tf == "4h":
            df = df.resample("4H").agg({
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum",
            }).dropna()

        return df

    if market == "Crypto":
        symbols = " ".join([f"{t}-USD" for t in tickers])

        for attempt in range(3):
            try:
                df_all = yf.download(
                    symbols,
                    period=period,
                    interval=interval,
                    progress=False,
                    auto_adjust=True,
                    group_by="ticker",
                    threads=True,
                )

                if df_all.empty:
                    time.sleep(2)
                    continue

                for t in tickers:
                    symbol = f"{t}-USD"
                    try:
                        df = clean_columns(df_all.copy(), symbol=symbol)
                        df = resample_if_needed(df, timeframe)

                        needed = {"Open", "High", "Low", "Close", "Volume"}
                        if df is not None and not df.empty and needed.issubset(df.columns):
                            df = df[list(needed)].copy()
                            df = df.dropna()
                            if len(df) >= 80:
                                data[t] = df
                    except Exception:
                        continue

                break

            except Exception:
                time.sleep(3)

        return data

    for t in tickers:
        symbol = f"{t}.JK"

        for attempt in range(2):
            try:
                df = yf.download(
                    symbol,
                    period=period,
                    interval=interval,
                    progress=False,
                    auto_adjust=True,
                    threads=False,
                )

                df = clean_columns(df, symbol=symbol)
                df = resample_if_needed(df, timeframe)

                needed = {"Open", "High", "Low", "Close", "Volume"}
                if df is not None and not df.empty and needed.issubset(df.columns):
                    df = df[list(needed)].copy()
                    df = df.dropna()
                    if len(df) >= 80:
                        data[t] = df

                break

            except Exception:
                time.sleep(1)

        time.sleep(0.05)

    return data


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
            df["High"], df["Low"], df["Close"], window=14
        ).average_true_range()

        hl = (df["High"] - df["Low"]).replace(0, np.nan)
        mf_mult = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / hl
        mf_vol = mf_mult * df["Volume"]
        vol_raw = (
            mf_vol.rolling(20, min_periods=10).mean()
            / df["Volume"].rolling(20, min_periods=10).mean().replace(0, np.nan)
        ) * 100
        df["vol_wave"] = vol_raw.ewm(span=5, adjust=False).mean()

        pc = df["Close"].diff()
        ds_pc = pc.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
        ds_abs_pc = pc.abs().ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
        df["trend_wave"] = 100 * (ds_pc / ds_abs_pc.replace(0, np.nan))

        df["dom_wave"] = ((df["rsi"] - 50) * 2).ewm(span=3, adjust=False).mean()

        hh = df["High"].rolling(20, min_periods=10).max()
        ll = df["Low"].rolling(20, min_periods=10).min()
        struct_raw = ((df["Close"] - ll) / (hh - ll).replace(0, np.nan)) * 200 - 100
        df["struct_wave"] = pandas_wma(struct_raw, 8)

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

        df["value_now_m"] = (df["Close"] * df["Volume"]) / 1e6
        df["value_ma20"] = df["value_now_m"].rolling(20, min_periods=10).mean()
        df["inflow_ratio"] = df["value_now_m"] / df["value_ma20"].replace(0, np.nan)
        df["valid_market"] = (df["Volume"].rolling(20, min_periods=10).mean() > 0) & df["Close"].notna()

        norm_len = 200
        df["vol_n"] = rolling_percent_rank(df["vol_wave"], norm_len).fillna(df["vol_wave"].clip(-100, 100))
        df["trend_n"] = rolling_percent_rank(df["trend_wave"], norm_len).fillna(df["trend_wave"].clip(-100, 100))
        df["dom_n"] = rolling_percent_rank(df["dom_wave"], norm_len).fillna(df["dom_wave"].clip(-100, 100))
        df["struct_n"] = rolling_percent_rank(df["struct_wave"], norm_len).fillna(df["struct_wave"].clip(-100, 100))

        df["matrix_score"] = (
            df["vol_n"] * 0.30
            + df["trend_n"] * 0.25
            + df["dom_n"] * 0.20
            + df["struct_n"] * 0.25
        ).clip(-100, 100)

        df["matrix_slope"] = df["matrix_score"].diff().fillna(0)
        df["matrix_accel"] = df["matrix_slope"].diff().fillna(0)

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

        adx_ind = ta.trend.ADXIndicator(df["High"], df["Low"], df["Close"], window=14)
        df["adx"] = adx_ind.adx()
        df["trending"] = df["adx"] >= 20

        bb_basis = df["Close"].rolling(20, min_periods=10).mean()
        bb_dev = df["Close"].rolling(20, min_periods=10).std() * 2.0
        bb_width = ((bb_basis + bb_dev) - (bb_basis - bb_dev)).abs() / bb_basis.abs().replace(0, np.nan) * 100
        df["bb_width"] = bb_width
        df["bb_width_avg"] = bb_width.rolling(100, min_periods=20).mean()
        df["compression"] = df["bb_width"] < df["bb_width_avg"]

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
            "Close", "ema20", "ema50", "ema200", "rsi", "atr",
            "vol_n", "trend_n", "dom_n", "struct_n",
            "matrix_score", "matrix_slope", "adx",
        ]

        return df.dropna(subset=needed_cols)

    except Exception:
        return None


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
    warnings_list = []

    if bool(latest.get("bear_div_matrix", False)):
        warnings_list.append("Bear Div")
    if bool(latest.get("bull_div_matrix", False)):
        warnings_list.append("Bull Div")
    if bool(latest.get("bull_exhaustion", False)):
        warnings_list.append("Bull Exhaust")
    if bool(latest.get("bear_exhaustion", False)):
        warnings_list.append("Bear Exhaust")
    if bool(latest.get("distribution", False)):
        warnings_list.append("Distribution")
    if bool(latest.get("accumulation", False)):
        warnings_list.append("Accumulation")
    if bool(latest.get("pre_breakout_bull", False)):
        warnings_list.append("Pre-Breakout Bull")
    if bool(latest.get("pre_breakout_bear", False)):
        warnings_list.append("Pre-Breakout Bear")

    return " | ".join(warnings_list[:3]) if warnings_list else "Clear"


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

    regime_score = 80 if regime == "TRENDING" else 75 if regime == "COMPRESSION" else 55 if regime == "TRANSITION" else 35
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

    if bool(latest.get("pre_breakout_bull", False)):
        long_bonus += 8
    if bool(latest.get("accumulation", False)):
        long_bonus += 8
    if bool(latest.get("bull_div_matrix", False)):
        long_bonus += 5

    if bool(latest.get("pre_breakout_bear", False)):
        short_bonus += 8
    if bool(latest.get("distribution", False)):
        short_bonus += 8
    if bool(latest.get("bear_div_matrix", False)):
        short_bonus += 5

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
        elif long_rank >= 85 and matrix > 20 and slope > 0 and bull_count >= 3 and htf_score >= -10 and not bool(latest.get("bear_div_matrix", False)):
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
        elif short_rank >= 85 and matrix < -20 and slope < 0 and bear_count >= 3 and htf_score <= 10 and not bool(latest.get("bull_div_matrix", False)):
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
- Buy Absorption: {'YES' if latest.get('buy_absorption', False) else 'NO'} | Sell Absorption: {'YES' if latest.get('sell_absorption', False) else 'NO'}
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


def scan_ticker(ticker, df_dict, htf_dict=None, use_lpm=False, lpm_params=None):
    df_raw = df_dict.get(ticker)

    if df_raw is None:
        return None, False

    df = compute_technicals(df_raw)

    if df is None or len(df) < 50:
        return None, False

    if use_lpm:
        try:
            df = compute_lpm_metrics(df, **(lpm_params or {"big_vol_mult": 1.5, "exhaust_level": 90.0}))
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

    metrics = matrix_screener_metrics(df, htf_df=htf_df, use_lpm=use_lpm)

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

    for i, t in enumerate(tickers):
        r, ok = scan_ticker(
            t,
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
        status.text(f"Analisis {i + 1}/{total}{htf_txt} | ✅ {success} | ❌ {fail} | Lolos {len(results)}")

    progress.empty()
    status.empty()

    st.session_state["fetch_stats"] = (success, fail)
    st.session_state["htf_tf"] = htf_tf if use_htf else "OFF"

    return results


def plot_chart(df, ticker, trade_plan, metrics=None):
    has_lpm = "lpm_norm" in df.columns

    rows = 3 if has_lpm else 2
    heights = [0.48, 0.27, 0.25] if has_lpm else [0.58, 0.42]

    titles = ["Price + EMA + Trade Plan", "🌊 Matrix Score + Normalized Waves"]

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

    for ema, color in [("ema20", "cyan"), ("ema50", "yellow"), ("ema200", "orange")]:
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

    fig.add_hline(y=entry, line_dash="dash", line_color="white", row=1, col=1, annotation_text=f"{side} Entry {entry:.4f}")
    fig.add_hline(y=sl, line_dash="dot", line_color="red", row=1, col=1, annotation_text=f"SL {sl:.4f}")
    fig.add_hline(y=tp1, line_dash="dot", line_color="lime", row=1, col=1, annotation_text=f"TP1 {tp1:.4f}")
    fig.add_hline(y=tp2, line_dash="dot", line_color="green", row=1, col=1, annotation_text=f"TP2 {tp2:.4f}")

    if has_lpm and "poc" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["poc"], name="POC", line=dict(color="white", width=1, dash="dash")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["vah"], name="VAH", line=dict(color="red", width=1, dash="dot")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["val"], name="VAL", line=dict(color="green", width=1, dash="dot")), row=1, col=1)

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

    for y, color, text in [
        (75, "rgba(0,255,0,0.45)", "Bull Extreme"),
        (20, "rgba(0,255,0,0.25)", None),
        (0, "gray", None),
        (-20, "rgba(255,0,0,0.25)", None),
        (-75, "rgba(255,0,0,0.45)", "Bear Extreme"),
    ]:
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

        fig.add_trace(go.Scatter(x=df.index, y=df["lpm_norm"], name="LPM Norm", line=dict(color=lpm_color, width=2)), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["lpm_confidence"], name="Confidence", line=dict(color="rgba(255,255,255,0.65)", width=1)), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["lpm_smooth_trend"], name="LPM Trend", line=dict(color="rgba(255,255,0,0.45)", width=1)), row=3, col=1)

        if "buy_absorption" in df.columns:
            idx = df.index[df["buy_absorption"]]
            if len(idx):
                fig.add_trace(go.Scatter(x=idx, y=[8] * len(idx), mode="markers", marker=dict(color="aqua", size=8), name="Buy Absorb"), row=3, col=1)

        if "sell_absorption" in df.columns:
            idx = df.index[df["sell_absorption"]]
            if len(idx):
                fig.add_trace(go.Scatter(x=idx, y=[92] * len(idx), mode="markers", marker=dict(color="orange", size=8), name="Sell Absorb"), row=3, col=1)

        fig.add_hline(y=50, line_dash="dot", line_color="gray", row=3, col=1)
        fig.add_hline(y=75, line_dash="dash", line_color="rgba(0,255,0,0.5)", row=3, col=1, annotation_text="Accum")
        fig.add_hline(y=90, line_dash="dash", line_color="rgba(255,165,0,0.5)", row=3, col=1, annotation_text="Exhaust")

    subtitle = ""

    if metrics:
        subtitle = f" | {metrics.get('State')} | {metrics.get('Side')} | Rank {metrics.get('Rank')} | Warning: {metrics.get('Warning')}"

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


def main():
    init_state()

    st.title("🌊 Aulsome Matrix Pro V8.7")
    st.caption("State-Based Matrix Screener | Long/Short Rank | HTF Confirmation | LPM Smart Money")

    with st.sidebar:
        st.header("⚙️ Configuration")

        market = st.selectbox("Market", ["Crypto", "IHSG"], index=0)
        timeframe = st.selectbox("Timeframe", ["15m", "1h", "4h", "1d", "1wk"], index=3)
        mode = st.radio("Scan Mode", ["Matrix Screener", "Long Only", "Short Only", "LPM + Matrix"], index=0)

        use_htf = st.checkbox("Use Auto HTF Confirmation", value=True)

        if use_htf:
            st.caption(f"Auto HTF: `{get_auto_htf(timeframe)}`")
        else:
            st.caption("Auto HTF: `OFF`")

        min_score = st.slider("Min Rank", 0, 100, 60, 5)
        universe_size = st.slider("Universe Size", 10, 700, 100, 25)

        custom_symbols = st.text_area(
            "Custom symbols optional",
            placeholder="BTC ETH SOL atau BBCA BBRI BMRI",
            height=80,
        )

        lpm_params = {"big_vol_mult": 1.5, "exhaust_level": 90.0}

        if mode == "LPM + Matrix":
            with st.expander("🧠 LPM Settings", expanded=False):
                lpm_params["big_vol_mult"] = st.slider("Big Volume Multiplier", 1.0, 3.0, 1.5, 0.1)
                lpm_params["exhaust_level"] = st.slider("Exhaustion Level", 70.0, 98.0, 90.0, 1.0)

        if st.button("🚀 RUN MATRIX SCAN", use_container_width=True, type="primary"):
            if custom_symbols.strip():
                tickers = [
                    x.strip().upper()
                    for x in custom_symbols.replace(",", " ").split()
                    if x.strip()
                ]
            elif market == "IHSG":
                tickers = IHSG_MEGA.split()[:universe_size]
            else:
                tickers = CRYPTO_MEGA.split()[:universe_size]

            with st.spinner(f"Scanning {len(tickers)} tickers..."):
                st.session_state["results"] = run_scan(
                    tickers,
                    timeframe,
                    market,
                    mode,
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

    results = sorted(results, key=lambda x: x.get(sort_key, 0), reverse=True)

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

    state_filter = st.selectbox(
        "Filter State",
        ["ALL"] + sorted(df_display["State"].dropna().unique().tolist()),
        index=0,
    )

    view_df = df_display if state_filter == "ALL" else df_display[df_display["State"] == state_filter]

    st.dataframe(view_df[ordered_cols], use_container_width=True, height=430)

    st.download_button(
        "📥 Download CSV",
        view_df[ordered_cols].to_csv(index=False),
        f"matrix_scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv",
    )

    st.markdown("#### 🔎 Detail Ticker")

    selected = st.selectbox("Pilih Ticker", [r["Ticker"] for r in results])
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

        l1.metric("LPM Score", f"{sel.get('LPM Score', 0)}", sel.get("LPM Grade", ""))
        l2.metric("LPM State", sel.get("LPM State", ""))
        l3.metric("BuyAbs / SellAbs", f"{sel.get('BuyAbs', 'NO')} / {sel.get('SellAbs', 'NO')}")
        l4.metric("BullDiv / BearDiv", f"{sel.get('BullDiv', 'NO')} / {sel.get('BearDiv', 'NO')}")

    with st.expander("📊 Rank Breakdown"):
        st.json(metrics.get("Breakdown", {}))

    if "_lpm_bd" in sel:
        with st.expander("🧠 LPM Breakdown"):
            st.json(sel.get("_lpm_bd", {}))

    st.plotly_chart(
        plot_chart(sel["_df"], sel["Ticker"], plan, metrics=metrics),
        use_container_width=True,
    )

    st.markdown("#### 🧠 AI Analysis")

    if st.button("Generate AI Analysis", use_container_width=True):
        client = get_client()

        if not client:
            st.error("Groq API key tidak ditemukan di Streamlit secrets.")
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
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3,
                        max_tokens=700,
                    )

                    st.markdown(resp.choices[0].message.content)

                except Exception as e:
                    st.error(f"AI error: {e}")


if __name__ == "__main__":
    main()



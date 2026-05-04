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

# --- CONFIG ---
st.set_page_config(
    page_title="Aulsome Matrix Pro V4.4",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UNIVERSE ---
IHSG_MEGA = """AALI ABBA ABDA ABMM ACES ACST ADCP ADES ADHI ADMF ADMG ADMR ADRO AGII AGRO AHAP AISA AKPI AKRA ALDO ALKA ALMI AMAG AMAN AMAR AMFG AMIN AMMN AMRT ANJT ANTM APEX APLN ARCI ARGO ARII ARNA ARTA ARTI ARTO ASBI ASGR ASII ASRI ASRM ASSA ATIC AUTO AVIA BABP BACA BAJA BALI BANK BAPA BATA BBCA BBHI BBKP BBLD BBMD BBNI BBRI BBRM BBTN BBYB BCAP BCIC BDMN BEKS BELL BESS BEST BFIN BGTG BINA BIPI BIPP BIRD BISI BJBR BJTM BKDP BKSL BLTA BMAS BMHS BMRI BMSR BMTR BNBA BNBR BNGA BNII BNLI BOBA BOLA BPFI BRIS BREN BRMS BRNA BRPT BSDE BSIM BSSR BSWD BTEK BTEL BTON BTPN BTPS BUDI BUKK BULL BUMI BVIC BWPT BYAN CAKK CAMP CARS CASH CASS CCSI CEKA CENT CFIN CINT CITA CITY CLEO CMNP CMPP CNKO CNTX COAL CPIN CPRO CSAP CSRA CTBN CTRA DART DAYA DCII DEAL DEWA DFAM DGIK DILD DIVA DKFT DLTA DMMX DMND DNAR DNET DOID DPNS DSFI DSNG DSSA DUTI DYAN EAST EKAD ELSA EMDE EMTK ENRG EPMT ERAA ESSA ETWA EXCL FAST FASW FILM FIRE FISH FMII FOOD FORU FORZ FPNI FREN GAMA GDST GDYR GEMA GEMS GGRM GIAA GJTL GLOB GLVA GMFI GMTD GOLD GOOD GOTO GPRA GSMF GTBO GWSA GZCO HADE HAIS HDFA HEAL HERO HEXA HITS HKMU HMSP HOKI HOME HRME HRTA HRUM IATA IBST ICBP ICON IDEA IGAR IIKP IKAI IMAS IMJS IMPC INAF INAI INCF INCI INCO INDF INDO INDR INDS INDY INPC INPS INRU INTA INTP IPCC IPCM IPOL IPTV IRRA ISAT ISSP ITIC ITMG JAKS JAST JAWA JAYA JECC JGLE JIHD JKON JMAS JSPT JTPE KAEF KBLI KBLM KBLV KDSI KEEN KEJU KIAS KICI KIJA KINO KIOS KKGI KLBF KOBX KOIN KONI MAXI KPIG KRYA LAMI LCGP LEAD LINK LION LMAS LMPI LMSH LPCK LPGI LPIN LPKR LPLI LPPF LSIP LTLS MAIN MAMI MAPA MAPB MAPI MARK MASA MAYA MBAP MBSS MBTO MCAS MCOR MDIA MDKA MDLN MDRN MEDC MEGA MERK META MFIN MICE MIDI MIKA MINA MIRA MITI MKPI MLBI MLIA MLPL MLPT MMLP MNCN MOLI MORA MPMX MPPA MSIN MSKY MTDL MTEL MTLA MTMH MTPS MTRA MTSM MYOH MYOR MYRX MYTX NANO NELY NFCX NIPS NIRO NISP NOBU NRCA NZIA OASA OBMD OMED OMRE ONIX PADI PALM PAMG PANI PANR PANS PBSA PCAR PEGE PEHA PGAS PGEO PGLI PICO PJAA PKPK PLAS PLIN PNBN PNBS PNIN PNLF PNSE POLA POLI POLL POLY POOL PORT PRAS PRDA PSAB PSDN PSGO PSKT PTBA PTPP PTPW PUDA PURA PWON PYFA PZZA RAJA RALS RANC RBMS RDTX REAL RELI RICY RIGS RIMO RMBA ROCK ROTI RSGK RUIS SAFE SAME SAMF SAPX SCCO SCMA SCNP SDMU SDPC SFAN SGER SGRO SHID SIDO SILO SIMA SIMP SINI SIPD SKBM SKLT SKYB SMAR SMBR SMCB SMDR SMGR SMIL SMKL SMMA SMMT SMRA SMRU SMSM SOBI SOHO SONA SOSS SOTO SPMA SQMI SRAJ SRIL SRSN SRTG SSIA SSMS SSTM STTP SUGI SULI SUPR SURE SWAT TAXI TAYS TBIG TBLA TBMS TCID TCPI TEBE TECH TELE TFCO TGKA TIFA TINS TIRA TIRT TKIM TLDN TLKM TMAS TMPO TNCA TOBA TOYS TPIA TPMA TRAM TRIL TRIM TRIN TRIS TRJA TRST TRUK TSPC TUGU TURI ULTJ UNIC UNIT UNSP UNTR UNVR URBN VCGG VICO VINS VIVA VKTR VOKS VRNA WAPO WEHA WEGE WIFI WIKA WINS WOMF WOOD WSBP WSKT WTON YELO YPAS ZATA ZBRA ZINC ZONE ZYRX"""
CRYPTO_MEGA = """BTC ETH BNB SOL XRP ADA DOGE AVAX DOT MATIC LINK SHIB LTC NEAR UNI APT ARB OP TIA SUI FET RNDR STX FIL ATOM IMX HBAR ETC ICP PEPE WIF BONK ORDI INJ THETA LDO VET BEAM SEI AAVE MKR RUNE GALA EGLD ALGO FLOW DYDX CRV SNX PENDLE JUP PYTH STRK W ENA ROSE AGIX STG AXS SAND MANA CHZ MINA KAVA GRT AGLD JASMY TRX KAS XLM XMR BCH BSV LUNC LUNA USTC JTO 1INCH MASK ENS BLUR T GLM AKT NOS IO AEVO ZK ZRO LISTA NOT BB PIXEL PORTAL XAI ACE SATS FLOKI MEME LADYS TURBO PEOPLE TRB GAS ARK WAVES ONT ONG NEO QTUM DGB SC XVG HOT RVN CKB SLP GNS PERP GMX WOO ZRX KNC LRC SUSHI BAKE JOE CAKE PORK BRETT BOME MEW MYRO WEN COQ KDA OSMO RETH LPT ALT MANTA ONDO RIF NTRN PAI SKL METIS SCRT CFX ACH TRU HOOK MAGIC GAL CORE EDU ID COMBO RDNT HIFI MAV PUNDIX BEL FRONT C98 MTL REEF ATA ALICE PROM DAR CHR SXP STEEM KMD STRAX ADX ICX OGN NKN DENT KEY MFT DATA VTHO STMX IQ UTK OXT ANKR CTSI COS TROY PIVX SYS SCR GFT QKC IOTX CTXC DOCK MITH TFUEL GTC MLN BOND FOR LINA DEGO EPS AUTO TKO TVK QUICK ERN RAMP PHA BAR CITY ASR JUV ATM OG PSG SANTOS LAZIO ALPINE FLOW MIR ANC ZEN RARE CLV ALPHA FIS SPELL CHESS QI GHST VOXEL BNX NMR VIB AST OAX DUSK LSK ARDR LOOM REQ AKRO POLS HARD STPT OOKI UNFI WING FOR BOND MOB MOVR SYN HIGH KP3R SNT MULTI VANRY"""

# --- HELPERS ---
def init_state():
    if "results" not in st.session_state: st.session_state["results"] = []
    if "insight_cache" not in st.session_state: st.session_state["insight_cache"] = {}

def get_client():
    try: return Groq(api_key=st.secrets["GROQ_KEY"])
    except: return None

def pandas_wma(series, window):
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

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
    df["ema50"] = ta.trend.ema_indicator(df["Close"], window=50)
    df["ema200"] = ta.trend.ema_indicator(df["Close"], window=200)
    df["vol_sma20"] = df["Volume"].rolling(20).mean()
    df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
    
    # Matrix Waves
    hl = (df["High"] - df["Low"]).replace(0, 0.001)
    mf_vol = (((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / hl) * df["Volume"]
    df["vol_wave"] = (mf_vol.rolling(20).mean() / df["Volume"].rolling(20).mean().replace(0, 0.001) * 100).ewm(span=5).mean()
    pc = df["Close"].diff()
    df["trend_wave"] = 100 * (pc.ewm(span=25).mean().ewm(span=13).mean() / pc.abs().ewm(span=25).mean().ewm(span=13).mean().replace(0, 0.001))
    df["dom_wave"] = ((ta.momentum.rsi(df["Close"]) - 50) * 2).ewm(span=3).mean()
    hh, ll = df["High"].rolling(20).max(), df["Low"].rolling(20).min()
    df["struct_wave"] = pandas_wma(((df["Close"] - ll) / (hh - ll).replace(0, 0.001)) * 200 - 100, 8)
    
    # Inflow Metrics
    df["value_now_m"] = (df["Close"] * df["Volume"]) / 1e6
    df["value_ma20"] = df["value_now_m"].rolling(20).mean()
    df["inflow_ratio"] = df["value_now_m"] / df["value_ma20"].replace(0, 0.001)
    
    # Bull Score
    scores = []
    for i in range(len(df)):
        if i < 30: scores.append(0); continue
        r = df.iloc[i]
        s = 0
        if r["Close"] > r["Open"]: s += 10
        if r["vol_wave"] > 0: s += 15
        if r["trend_wave"] > 0: s += 15
        if r["inflow_ratio"] > 1.2: s += 20
        if r["struct_wave"] > -50: s += 30
        if r["rsi"] > 50: s += 10
        scores.append(min(s, 100))
    df["bull_score"] = scores
    return df.dropna()

# --- ENGINE SNIPER ---
def check_sniper_entry(df, swing_len=5, zone_pct=1.5):
    if len(df) < 30: return False
    latest = df.iloc[-1]
    is_uptrend = latest["Close"] > latest["ema200"]
    is_vol_spike = latest["Volume"] > (latest["vol_sma20"] * 1.2)
    
    # Pivot Logic
    pivot_lows = []
    for i in range(swing_len, len(df) - swing_len):
        if all(df.iloc[i]["Low"] <= df.iloc[i-j]["Low"] for j in range(1, swing_len+1)) and \
           all(df.iloc[i]["Low"] <= df.iloc[i+j]["Low"] for j in range(1, swing_len+1)):
            pivot_lows.append(df.iloc[i]["Low"])
    
    in_support = False
    if pivot_lows:
        lp = pivot_lows[-1]
        if latest["Low"] <= (lp * (1 + zone_pct/100)) and latest["Close"] >= lp: in_support = True
            
    bullish_candle = latest["Close"] > latest["Open"] and (latest["Close"]-latest["Open"]) > ((latest["High"]-latest["Low"]) * 0.4)
    return is_uptrend and in_support and is_vol_spike and bullish_candle

# --- PATTERN DETECTION ---
def detect_patterns(df):
    if df is None or len(df) < 5: return "Neutral"
    c = [df.iloc[-i] for i in range(5, 0, -1)]
    def body(n): return abs(n["Close"] - n["Open"])
    def is_bull(n): return n["Close"] > n["Open"]
    def is_bear(n): return n["Open"] > n["Close"]
    
    if (min(c[4]["Open"], c[4]["Close"]) - c[4]["Low"]) > 2 * body(c[4]): return "Hammer/Pin Bar"
    if is_bear(c[3]) and is_bull(c[4]) and c[4]["Close"] >= c[3]["Open"]: return "Bullish Engulfing"
    if all(is_bull(c[i]) for i in [2,3,4]) and c[4]["Close"] > c[3]["Close"]: return "Three White Soldiers"
    return "Neutral"

# --- MAIN APP ---
def main():
    init_state()
    st.title("🔮 Aulsome Matrix Pro V4.4")
    
    with st.sidebar:
        st.header("⚙️ Filter Engine")
        market = st.radio("Universe", ["IHSG", "Crypto"], horizontal=True)
        timeframe = st.selectbox("Timeframe", ["15m","1h","4h","1d"], index=3)
        mode = st.selectbox("Metode Screening", ["Sniper Filter 🎯", "Inflow Detector 💰", "Wave Matrix 🌊", "Candlestick Pattern 🕯️"])
        
        strategy = None
        struct_range = (-100, 100)
        
        if mode == "Sniper Filter 🎯":
            st.info("🎯 Sniper: Uptrend + Support + Vol Spike + Reversal.")
        
        elif mode == "Inflow Detector 💰":
            strategy = st.selectbox("Signal Inflow", ["High Inflow (≥1.5x)", "Inflow + Bandar Akumulasi", "Strong Value Only"])
        
        elif mode == "Wave Matrix 🌊":
            strategy = st.selectbox("Wave Signal", ["Garis Putih (Oversold)","Golden Cross (Struct>Dom)","Bandar Power"])
            if "Putih" in strategy: struct_range = st.slider("Range Putih", -100, 100, (-100, -50))
        
        elif mode == "Candlestick Pattern 🕯️":
            strategy = st.selectbox("Pola Candle", ["Hammer/Pin Bar", "Bullish Engulfing", "Three White Soldiers"])

        st.markdown("---")
        min_turnover = st.number_input("Min Turnover (Mln)", 0.0, 5000.0, 10.0)
        run_scan = st.button("🚀 MULAI SCANNING", use_container_width=True)

    suffix = ".JK" if market == "IHSG" else "-USD"
    tickers = sorted([f"{t.strip()}{suffix}" for t in (IHSG_MEGA if market == "IHSG" else CRYPTO_MEGA).split() if t.strip()])

    tab_res, tab_deep = st.tabs(["📊 Hasil Screening", "🧠 Deep Journey"])

    with tab_res:
        if run_scan:
            results = []
            prog = st.progress(0)
            def process(t):
                df = fetch_data(t, timeframe)
                df = compute_technicals(df)
                if df is None or len(df) < 40: return None
                
                latest, prev = df.iloc[-1], df.iloc[-2]
                if latest["value_now_m"] < min_turnover: return None
                
                matched = False
                trigger = "Manual"
                
                if mode == "Sniper Filter 🎯":
                    if check_sniper_entry(df): matched = True; trigger = "SNIPER BUY"
                
                elif mode == "Inflow Detector 💰":
                    if "High" in strategy: matched = latest["inflow_ratio"] >= 1.5
                    elif "Akumulasi" in strategy: matched = latest["inflow_ratio"] > 1.2 and latest["vol_wave"] > 0
                    elif "Strong" in strategy: matched = latest["value_now_m"] > 500
                    trigger = "INFLOW"
                
                elif mode == "Wave Matrix 🌊":
                    if "Putih" in strategy: matched = struct_range[0] <= latest["struct_wave"] <= struct_range[1]
                    elif "Golden" in strategy: matched = prev["struct_wave"] < prev["dom_wave"] and latest["struct_wave"] > latest["dom_wave"]
                    elif "Power" in strategy: matched = latest["vol_wave"] > 30
                    trigger = "WAVE"
                
                elif mode == "Candlestick Pattern 🕯️":
                    if detect_patterns(df) == strategy: matched = True; trigger = strategy
                
                if matched:
                    return {
                        "Asset": t.replace(suffix,""), "Price": round(latest["Close"], 2),
                        "Signal": trigger, "Score": int(latest["bull_score"]),
                        "Inflow": round(latest["inflow_ratio"],2), "Bandar": round(latest["vol_wave"],1),
                        "Trend": "UP" if latest["Close"] > latest["ema200"] else "DOWN"
                    }
                return None

            with ThreadPoolExecutor(max_workers=20) as exe:
                for i, res in enumerate(exe.map(process, tickers)):
                    if res: results.append(res)
                    prog.progress((i+1)/len(tickers))
            st.session_state["results"] = sorted(results, key=lambda x: x["Score"], reverse=True)
            st.rerun()

        if st.session_state["results"]:
            st.dataframe(pd.DataFrame(st.session_state["results"]), use_container_width=True, hide_index=True)
        else: st.info("Tekan RUN SCAN untuk memulai.")

    with tab_deep:
        if st.session_state["results"]:
            selected = st.selectbox("Analisis Saham:", [r["Asset"] for r in st.session_state["results"]])
            df_p = compute_technicals(fetch_data(selected + suffix, timeframe))
            if df_p is not None:
                fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.5, 0.25, 0.25])
                fig.add_trace(go.Candlestick(x=df_p.index, open=df_p["Open"], high=df_p["High"], low=df_p["Low"], close=df_p["Close"], name="Price"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p["ema200"], name="EMA 200", line=dict(color="white")), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p["vol_wave"], name="Bandar", line=dict(color="yellow")), row=2, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p["struct_wave"], name="Struktur", line=dict(color="cyan")), row=2, col=1)
                fig.add_trace(go.Bar(x=df_p.index, y=df_p["inflow_ratio"], name="Inflow Ratio"), row=3, col=1)
                fig.update_layout(template="plotly_dark", height=800, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
                
                if st.button("🪄 Sniper AI Insight"):
                    client = get_client()
                    if client:
                        prompt = f"Saham {selected} harga {df_p.iloc[-1]['Close']}. Berikan analisis Entry, SL, dan TP."
                        resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile")
                        st.markdown(resp.choices[0].message.content)
        else: st.warning("Scan market dulu.")

if __name__ == "__main__":
    main()

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
    page_title="Aulsome Matrix Pro",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UNIVERSE ---
IHSG_MEGA = """AALI ABBA ABDA ABMM ACES ACST ADCP ADES ADHI ADMF ADMG ADMR ADRO AGII AGRO AHAP AISA AKPI AKRA ALDO ALKA ALMI AMAG AMAN AMAR AMFG AMIN AMMN AMRT ANJT ANTM APEX APLN ARCI ARGO ARII ARNA ARTA ARTI ARTO ASBI ASGR ASII ASRI ASRM ASSA ATIC AUTO AVIA BABP BACA BAJA BALI BANK BAPA BATA BBCA BBHI BBKP BBLD BBMD BBNI BBRI BBRM BBTN BBYB BCAP BCIC BDMN BEKS BELL BESS BEST BFIN BGTG BINA BIPI BIPP BIRD BISI BJBR BJTM BKDP BKSL BLTA BMAS BMHS BMRI BMSR BMTR BNBA BNBR BNGA BNII BNLI BOBA BOLA BPFI BRIS BREN BRMS BRNA BRPT BSDE BSIM BSSR BSWD BTEK BTEL BTON BTPN BTPS BUDI BUKK BULL BUMI BVIC BWPT BYAN CAKK CAMP CARS CASH CASS CCSI CEKA CENT CFIN CINT CITA CITY CLEO CMNP CMPP CNKO CNTX COAL CPIN CPRO CSAP CSRA CTBN CTRA DART DAYA DCII DEAL DEWA DFAM DGIK DILD DIVA DKFT DLTA DMMX DMND DNAR DNET DOID DPNS DSFI DSNG DSSA DUTI DYAN EAST EKAD ELSA EMDE EMTK ENRG EPMT ERAA ESSA ESTI ETWA EXCL FAST FASW FILM FIRE FISH FMII FOOD FORU FORZ FPNI FREN GAMA GDST GDYR GEMA GEMS GGRM GIAA GJTL GLOB GLVA GMFI GMTD GOLD GOOD GOTO GPRA GSMF GTBO GWSA GZCO HADE HAIS HDFA HEAL HERO HEXA HITS HKMU HMSP HOKI HOME HRME HRTA HRUM IATA IBST ICBP ICON IDEA IGAR IIKP IKAI IMAS IMJS IMPC INAF INAI INCF INCI INCO INDF INDO INDR INDS INDY INPC INPS INRU INTA INTP IPCC IPCM IPOL IPTV IRRA ISAT ISSP ITIC ITMG JAKS JAST JAWA JAYA JECC JGLE JIHD JKON JMAS JSPT JTPE KAEF KBLI KBLM KBLV KDSI KEEN KEJU KIAS KICI KIJA KINO KIOS KKGI KLBF KOBX KOIN KONI KPIG KRYA LAMI LCGP LEAD LINK LION LMAS LMPI LMSH LPCK LPGI LPIN LPKR LPLI LPPF LSIP LTLS MAIN MAMI MAPA MAPB MAPI MARK MASA MAYA MBAP MBSS MBTO MCAS MCOR MDIA MDKA MDLN MDRN MEDC MEGA MERK META MFIN MICE MIDI MIKA MINA MIRA MITI MKPI MLBI MLIA MLPL MLPT MMLP MNCN MOLI MORA MPMX MPPA MSIN MSKY MTDL MTEL MTLA MTMH MTPS MTRA MTSM MYOH MYOR MYRX MYTX NANO NELY NFCX NIPS NIRO NISP NOBU NRCA NZIA OASA OBMD OMED OMRE ONIX PADI PALM PAMG PANI PANR PANS PBSA PCAR PEGE PEHA PGAS PGEO PGLI PICO PJAA PKPK PLAS PLIN PNBN PNBS PNIN PNLF PNSE POLA POLI POLL POLY POOL PORT PRAS PRDA PSAB PSDN PSGO PSKT PTBA PTPP PTPW PUDA PURA PWON PYFA PZZA RAJA RALS RANC RBMS RDTX REAL RELI RICY RIGS RIMO RMBA ROCK ROTI RSGK RUIS SAFE SAME SAMF SAPX SCCO SCMA SCNP SDMU SDPC SFAN SGER SGRO SHID SIDO SILO SIMA SIMP SINI SIPD SKBM SKLT SKYB SMAR SMBR SMCB SMDR SMGR SMIL SMKL SMMA SMMT SMRA SMRU SMSM SOBI SOHO SONA SOSS SOTO SPMA SQMI SRAJ SRIL SRSN SRTG SSIA SSMS SSTM STTP SUGI SULI SUPR SURE SWAT TAXI TAYS TBIG TBLA TBMS TCID TCPI TEBE TECH TELE TFCO TGKA TIFA TINS TIRA TIRT TKIM TLDN TLKM TMAS TMPO TNCA TOBA TOYS TPIA TPMA TRAM TRIL TRIM TRIN TRIS TRJA TRST TRUK TSPC TUGU TURI ULTJ UNIC UNIT UNSP UNTR UNVR URBN VCGG VICO VINS VIVA VKTR VOKS VRNA WAPO WEHA WEGE WIFI WIKA WINS WOMF WOOD WSBP WSKT WTON YELO YPAS ZATA ZBRA ZINC ZONE ZYRX"""
CRYPTO_MEGA = """BTC ETH BNB SOL XRP ADA DOGE AVAX DOT MATIC LINK SHIB LTC NEAR UNI APT ARB OP TIA SUI FET RNDR STX FIL ATOM IMX HBAR ETC ICP PEPE WIF BONK ORDI INJ THETA LDO VET BEAM SEI AAVE MKR RUNE GALA EGLD ALGO FLOW DYDX CRV SNX PENDLE JUP PYTH STRK W ENA ROSE AGIX STG AXS SAND MANA CHZ MINA KAVA GRT AGLD JASMY TRX KAS XLM XMR BCH BSV LUNC LUNA USTC JTO 1INCH MASK ENS BLUR T GLM AKT NOS IO AEVO ZK ZRO LISTA NOT BB PIXEL PORTAL XAI ACE SATS FLOKI MEME LADYS TURBO PEOPLE TRB GAS ARK WAVES ONT ONG NEO QTUM DGB SC XVG HOT RVN CKB SLP GNS PERP GMX WOO ZRX KNC LRC SUSHI BAKE JOE CAKE PORK BRETT BOME MEW MYRO WEN COQ KDA OSMO RETH LPT ALT MANTA ONDO RIF NTRN PAI SKL METIS SCRT CFX ACH TRU HOOK MAGIC GAL CORE EDU ID COMBO RDNT HIFI MAV PUNDIX BEL FRONT C98 MTL REEF ATA ALICE PROM DAR CHR SXP STEEM KMD STRAX ADX ICX OGN NKN DENT KEY MFT DATA VTHO STMX IQ UTK OXT ANKR CTSI COS TROY PIVX SYS SCR GFT QKC IOTX CTXC DOCK MITH TFUEL GTC MLN BOND FOR LINA DEGO EPS AUTO TKO TVK QUICK ERN RAMP PHA BAR CITY ASR JUV ATM OG PSG SANTOS LAZIO ALPINE FLOW MIR ANC ZEN RARE CLV ALPHA FIS SPELL CHESS QI GHST VOXEL BNX NMR VIB AST OAX DUSK LSK ARDR LOOM REQ AKRO POLS HARD STPT OOKI UNFI WING FOR BOND MOB MOVR SYN HIGH KP3R SNT MULTI VANRY"""

# --- HELPERS ---
def init_state():
    if "results" not in st.session_state: st.session_state["results"] = []
    if "insight_cache" not in st.session_state: st.session_state["insight_cache"] = {}

def get_client():
    try:
        return Groq(api_key=st.secrets["GROQ_KEY"])
    except:
        return None

def parse_universe(text, suffix):
    return sorted([f"{t.strip()}{suffix}" for t in text.split() if t.strip()])

def pandas_wma(series, window):
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

# --- FETCH & COMPUTE ---
@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(ticker, timeframe):
    try:
        mapping = {"15m": ("5d","15m"), "1h": ("1mo","1h"), "4h": ("2mo","1h"), "1d": ("1y","1d")}
        period, interval = mapping.get(timeframe, ("1y","1d"))
        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        
        if df.empty: return None
        
        # Handle yfinance Multi-Index columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        if timeframe == "4h":
            df = df.resample("4H").agg({"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna()
        return df.dropna()
    except:
        return None

def compute_matrix_waves(df):
    if df is None or len(df) < 50: return None
    df = df.copy().dropna()
    
    # Standard Indicators
    macd_obj = ta.trend.MACD(df["Close"])
    df["macd_hist"] = macd_obj.macd_diff()
    stoch_obj = ta.momentum.StochasticOscillator(df["High"], df["Low"], df["Close"], window=14, smooth_window=3)
    df["stoch_k"] = stoch_obj.stoch()
    df["rsi"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()
    df["ema20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["Close"].ewm(span=50, adjust=False).mean()

    # 1. Bandar (Yellow)
    hl = (df["High"] - df["Low"]).replace(0, 0.001)
    mf_mult = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / hl
    mf_vol = mf_mult * df["Volume"]
    df["vol_wave"] = (mf_vol.rolling(20).mean() / df["Volume"].rolling(20).mean().replace(0, 0.001) * 100).ewm(span=5, adjust=False).mean()

    # 2. Trend (Blue)
    pc = df["Close"].diff()
    dsp = pc.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    dsp_abs = pc.abs().ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    df["trend_wave"] = 100 * (dsp / dsp_abs.replace(0, 0.001))

    # 3. Dominasi (Purple)
    df["dom_wave"] = ((ta.momentum.rsi(df["Close"], window=14) - 50) * 2).ewm(span=3, adjust=False).mean()

    # 4. Struktur (White)
    hh, ll = df["High"].rolling(20).max(), df["Low"].rolling(20).min()
    df["struct_wave"] = pandas_wma(((df["Close"] - ll) / (hh - ll).replace(0, 0.001)) * 200 - 100, 8)
    
    return df.dropna()

def add_inflow_metrics(df):
    if df is None: return None
    df = df.copy()
    df["value_now"] = df["Close"] * df["Volume"]
    df["value_ma20"] = df["value_now"].rolling(20).mean()
    df["inflow_ratio"] = df["value_now"] / df["value_ma20"].replace(0, 0.001)
    df["value_now_m"] = df["value_now"] / 1e6
    df["value_ma20_m"] = df["value_ma20"] / 1e6
    return df

def compute_bull_score_series(df):
    scores = []
    for i in range(len(df)):
        if i < 30:
            scores.append(0)
            continue
        row, prev = df.iloc[i], df.iloc[i - 1]
        s = 0
        if row["Close"] > row["Open"]: s += 10
        if row["Close"] > prev["Close"]: s += 10
        if row["vol_wave"] > 0: s += 10
        if row["trend_wave"] > 0: s += 10
        if row["dom_wave"] > 0: s += 10
        if row["struct_wave"] > -20: s += 10
        if row["inflow_ratio"] > 1: s += 15
        if row["macd_hist"] > 0: s += 10
        if row["rsi"] > 50: s += 10
        if row["Close"] > row["ema20"]: s += 5
        scores.append(min(s, 100))
    df = df.copy()
    df["bull_score"] = scores
    return df

def bullish_level(score):
    if score >= 80: return "🔥 SUPER YAHUD"
    if score >= 60: return "✅ YAHUD"
    if score >= 40: return "👀 WATCHLIST"
    if score >= 20: return "⚠️ WEAK"
    return "❌ SKIP"

def detect_patterns(df):
    if df is None or len(df) < 5: return "Neutral"
    c1, c2, c3, c4, c5 = [df.iloc[-i] for i in range(5, 0, -1)]
    body5 = abs(c5["Close"] - c5["Open"])
    l_shadow5 = min(c5["Close"], c5["Open"]) - c5["Low"]
    u_shadow5 = c5["High"] - max(c5["Close"], c5["Open"])
    
    if (c4["Close"] < c4["Open"]) and (c5["Close"] > c5["Open"]) and (c5["Open"] <= c4["Close"]) and (c5["Close"] >= c4["Open"]):
        return "Bullish Engulfing"
    if (c3["Close"] < c3["Open"]) and (abs(c4["Close"] - c4["Open"]) < abs(c3["Close"] - c3["Open"]) * 0.3) and (c5["Close"] > c5["Open"]):
        return "Morning Star"
    if (l_shadow5 >= 2 * body5) and (u_shadow5 <= 0.2 * body5) and body5 > 0:
        return "Hammer"
    return "Neutral"

# --- AI & CHART ---
def get_ai_insight(client_obj, asset, df):
    lookback = df.tail(20)
    pattern = detect_patterns(df)
    latest = df.iloc[-1]
    
    rows = []
    for i, (_, row) in enumerate(lookback.iterrows(), start=1):
        rows.append(f"C{i}: Cl={row['Close']:.2f} | Bndr={row['vol_wave']:.1f} | Trnd={row['trend_wave']:.1f} | Inf={row['inflow_ratio']:.1f} | Score={int(row['bull_score'])}")

    sys_p = "Anda Senior Trader Elliott Wave. Gaya bicara mentor tajam & berbasis data. Berikan Trading Plan konkret (Entry, TP, SL)."
    user_p = f"Analisis {asset}. Pattern: {pattern}. Data 20 candle:\n" + "\n".join(rows) + f"\n\nBerikan verdict final: SUPER YAHUD / YAHUD / WATCHLIST / SKIP."

    try:
        resp = client_obj.chat.completions.create(
            messages=[{"role":"system","content":sys_p}, {"role":"user","content":user_p}],
            model="llama-3.3-70b-versatile", temperature=0.4
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Error AI: {str(e)}"

def build_chart(df):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.5, 0.25, 0.25])
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"), row=1, col=1)
    
    colors = {"vol_wave":"#FFD600", "trend_wave":"#00BFFF", "dom_wave":"#D500F9", "struct_wave":"#FFFFFF"}
    for col, color in colors.items():
        fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col, line=dict(color=color)), row=2, col=1)
    
    fig.add_trace(go.Bar(x=df.index, y=df["inflow_ratio"], name="Inflow", marker_color="#4ADE80"), row=3, col=1)
    fig.update_layout(template="plotly_dark", height=800, xaxis_rangeslider_visible=False)
    return fig

# --- MAIN APP ---
def main():
    init_state()
    client = get_client()
    st.title("🔮 Aulsome Matrix Pro V4.1")
    
    with st.sidebar:
        st.header("⚙️ Control Panel")
        market = st.radio("Universe", ["IHSG", "Crypto"], horizontal=True)
        timeframe = st.selectbox("Timeframe", ["15m","1h","4h","1d"], index=3)
        mode = st.selectbox("Mode Analysis", ["Wave Matrix","Candlestick Pattern","Inflow Detector"])
        
        min_turnover = st.number_input("Min Turnover (Mln)", 0.0, 5000.0, 10.0)
        min_inflow = st.slider("Min Inflow Ratio", 0.5, 5.0, 1.0)
        run_scan = st.button("🚀 RUN SCAN", use_container_width=True)

    suffix = ".JK" if market == "IHSG" else "-USD"
    tickers = parse_universe(IHSG_MEGA if market == "IHSG" else CRYPTO_MEGA, suffix)

    tab1, tab2 = st.tabs(["📊 Scan Market", "🧠 Deep Journey"])

    with tab1:
        if run_scan:
            results = []
            prog = st.progress(0)
            def process(t):
                df = fetch_data(t, timeframe)
                df = compute_matrix_waves(df)
                df = add_inflow_metrics(df)
                if df is None or len(df) < 30: return None
                df = compute_bull_score_series(df)
                
                latest = df.iloc[-1]
                turnover = (latest["Close"] * latest["Volume"]) / 1e6
                if turnover < min_turnover or latest["inflow_ratio"] < min_inflow: return None
                
                return {
                    "Asset": t.replace(suffix,""), "Price": round(latest["Close"], 4),
                    "Bandar": round(latest["vol_wave"],1), "Trend": round(latest["trend_wave"],1),
                    "Inflow": round(latest["inflow_ratio"],2), "BullScore": int(latest["bull_score"]),
                    "Level": bullish_level(latest["bull_score"]), "Pattern": detect_patterns(df)
                }

            with ThreadPoolExecutor(max_workers=20) as exe:
                for i, res in enumerate(exe.map(process, tickers)):
                    if res: results.append(res)
                    prog.progress((i+1)/len(tickers))
            
            st.session_state["results"] = sorted(results, key=lambda x: x["BullScore"], reverse=True)
            st.rerun()

        if st.session_state["results"]:
            st.dataframe(pd.DataFrame(st.session_state["results"]), use_container_width=True, hide_index=True)
        else:
            st.info("Gunakan sidebar untuk Scan.")

    with tab2:
        if st.session_state["results"]:
            selected = st.selectbox("Pilih Aset:", [r["Asset"] for r in st.session_state["results"]])
            t_full = selected + suffix
            df_p = add_inflow_metrics(compute_matrix_waves(fetch_data(t_full, timeframe)))
            if df_p is not None:
                df_p = compute_bull_score_series(df_p)
                st.plotly_chart(build_chart(df_p), use_container_width=True)
                if st.button("🪄 Get AI Insight"):
                    st.markdown(get_ai_insight(client, selected, df_p))
        else:
            st.warning("Scan market dulu Pak Aul!")

if __name__ == "__main__":
    main()

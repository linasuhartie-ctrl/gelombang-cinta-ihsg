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

# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIG & UNIVERSE
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Aulsome Matrix Pro V5.8",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

IHSG_MEGA = """AALI ABBA ABDA ABMM ACES ACST ADCP ADES ADHI ADMF ADMG ADMR ADRO AGII AGRO AHAP AISA AKPI AKRA ALDO ALKA ALMI AMAG AMAN AMAR AMFG AMIN AMMN AMRT ANJT ANTM APEX APLN ARCI ARGO ARII ARNA ARTA ARTI ARTO ASBI ASGR ASII ASRI ASRM ASSA ATIC AUTO AVIA BABP BACA BAJA BALI BANK BAPA BATA BBCA BBHI BBKP BBLD BBMD BBNI BBRI BBRM BBTN BBYB BCAP BCIC BDMN BEKS BELL BESS BEST BFIN BGTG BINA BIPI BIPP BIRD BISI BJBR BJTM BKDP BKSL BLTA BMAS BMHS BMRI BMSR BMTR BNBA BNBR BNGA BNII BNLI BOBA BOLA BPFI BRIS BREN BRMS BRNA BRPT BSDE BSIM BSSR BSWD BTEK BTEL BTON BTPN BTPS BUDI BUKK BULL BUMI BVIC BWPT BYAN CAKK CAMP CARS CASH CASS CCSI CEKA CENT CFIN CINT CITA CITY CLEO CMNP CMPP CNKO CNTX COAL CPIN CPRO CSAP CSRA CTBN CTRA DART DAYA DCII DEAL DEWA DFAM DGIK DILD DIVA DKFT DLTA DMMX DMND DNAR DNET DOID DPNS DSFI DSNG DSSA DUTI DYAN EAST EKAD ELSA EMDE EMTK ENRG EPMT ERAA ESSA ETWA EXCL FAST FASW FILM FIRE FISH FMII FOOD FORU FORZ FPNI FREN GAMA GDST GDYR GEMA GEMS GGRM GIAA GJTL GLOB GLVA GMFI GMTD GOLD GOOD GOTO GPRA GSMF GTBO GWSA GZCO HADE HAIS HDFA HEAL HERO HEXA HITS HKMU HMSP HOKI HOME HRME HRTA HRUM IATA IBST ICBP ICON IDEA IGAR IIKP IKAI IMAS IMJS IMPC INAF INAI INCF INCI INCO INDF INDO INDR INDS INDY INPC INPS INRU INTA INTP IPCC IPCM IPOL IPTV IRRA ISAT ISSP ITIC ITMG JAKS JAST JAWA JAYA JECC JGLE JIHD JKON JMAS JSPT JTPE KAEF KBLI KBLM KBLV KDSI KEEN KEJU KIAS KICI KIJA KINO KIOS KKGI KLBF KOBX KOIN KONI KPIG KRYA LAMI LCGP LEAD LINK LION LMAS LMPI LMSH LPCK LPGI LPIN LPKR LPLI LPPF LSIP LTLS MAIN MAMI MAPA MAPB MAPI MARK MASA MAYA MBAP MBSS MBTO MCAS MCOR MDIA MDKA MDLN MDRN MEDC MEGA MERK META MFIN MICE MIDI MIKA MINA MIRA MITI MKPI MLBI MLIA MLPL MLPT MMLP MNCN MOLI MORA MPMX MPPA MSIN MSKY MTDL MTEL MTLA MTMH MTPS MTRA MTSM MYOH MYOR MYRX MYTX NANO NELY NFCX NIPS NIRO NISP NOBU NRCA NZIA OASA OBMD OMED OMRE ONIX PADI PALM PAMG PANI PANR PANS PBSA PCAR PEGE PEHA PGAS PGEO PGLI PICO PJAA PKPK PLAS PLIN PNBN PNBS PNIN PNLF PNSE POLA POLI POLL POLY POOL PORT PRAS PRDA PSAB PSDN PSGO PSKT PTBA PTPP PTPW PUDA PURA PWON PYFA PZZA RAJA RALS RANC RBMS RDTX REAL RELI RICY RIGS RIMO RMBA ROCK ROTI RSGK RUIS SAFE SAME SAMF SAPX SCCO SCMA SCNP SDMU SDPC SFAN SGER SGRO SHID SIDO SILO SIMA SIMP SINI SIPD SKBM SKLT SKYB SMAR SMBR SMCB SMDR SMGR SMIL SMKL SMMA SMMT SMRA SMRU SMSM SOBI SOHO SONA SOSS SOTO SPMA SQMI SRAJ SRIL SRSN SRTG SSIA SSMS SSTM STTP SUGI SULI SUPR SURE SWAT TAXI TAYS TBIG TBLA TBMS TCID TCPI TEBE TECH TELE TFCO TGKA TIFA TINS TIRA TIRT TKIM TLDN TLKM TMAS TMPO TNCA TOBA TOYS TPIA TPMA TRAM TRIL TRIM TRIN TRIS TRJA TRST TRUK TSPC TUGU TURI ULTJ UNIC UNIT UNSP UNTR UNVR URBN VCGG VICO VINS VIVA VKTR VOKS VRNA WAPO WEHA WEGE WIFI WIKA WINS WOMF WOOD WSBP WSKT WTON YELO YPAS ZATA ZBRA ZINC ZONE ZYRX"""
CRYPTO_MEGA = """BTC ETH BNB SOL XRP ADA DOGE AVAX DOT MATIC LINK SHIB LTC NEAR UNI APT ARB OP TIA SUI FET RNDR STX FIL ATOM IMX HBAR ETC ICP PEPE WIF BONK ORDI INJ THETA LDO VET BEAM SEI AAVE MKR RUNE GALA EGLD ALGO FLOW DYDX CRV SNX PENDLE JUP PYTH STRK W ENA ROSE AGIX STG AXS SAND MANA CHZ MINA KAVA GRT AGLD JASMY TRX KAS XLM XMR BCH BSV LUNC LUNA USTC JTO 1INCH MASK ENS BLUR T GLM AKT NOS IO AEVO ZK ZRO LISTA NOT BB PIXEL PORTAL XAI ACE SATS FLOKI MEME LADYS TURBO PEOPLE TRB GAS ARK WAVES ONT ONG NEO QTUM DGB SC XVG HOT RVN CKB SLP GNS PERP GMX WOO ZRX KNC LRC SUSHI BAKE JOE CAKE PORK BRETT BOME MEW MYRO WEN COQ KDA OSMO RETH LPT ALT MANTA ONDO RIF NTRN PAI SKL METIS SCRT CFX ACH TRU HOOK MAGIC GAL CORE EDU ID COMBO RDNT HIFI MAV PUNDIX BEL FRONT C98 MTL REEF ATA ALICE PROM DAR CHR SXP STEEM KMD STRAX ADX ICX OGN NKN DENT KEY MFT DATA VTHO STMX IQ UTK OXT ANKR CTSI COS TROY PIVX SYS SCR GFT QKC IOTX CTXC DOCK MITH TFUEL GTC MLN BOND FOR LINA DEGO EPS AUTO TKO TVK QUICK ERN RAMP PHA BAR CITY ASR JUV ATM OG PSG SANTOS LAZIO ALPINE FLOW MIR ANC ZEN RARE CLV ALPHA FIS SPELL CHESS QI GHST VOXEL BNX NMR VIB AST OAX DUSK LSK ARDR LOOM REQ AKRO POLS HARD STPT OOKI UNFI WING FOR BOND MOB MOVR SYN HIGH"""

# ──────────────────────────────────────────────────────────────────────────────
# 2. CORE ENGINE
# ──────────────────────────────────────────────────────────────────────────────
def init_state():
    if "results" not in st.session_state: st.session_state["results"] = []
    if "last_filters" not in st.session_state: st.session_state["last_filters"] = {}

def get_client():
    try: return Groq(api_key=st.secrets["GROQ_KEY"])
    except: return None

def pandas_wma(series, window):
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(ticker, timeframe):
    try:
        mapping = {"15m": ("5d","15m"), "1h": ("1mo","1h"), "4h": ("2mo","1h"), "1d": ("1y","1d")}
        p, i = mapping.get(timeframe, ("1y","1d"))
        df = yf.download(ticker, period=p, interval=i, progress=False, auto_adjust=True)
        if df is None or df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df.dropna()
    except: return None

def compute_technicals(df):
    if df is None or len(df) < 200: return None
    df = df.copy()
    try:
        df["ma20"] = ta.trend.sma_indicator(df["Close"], window=20)
        df["ema20"] = ta.trend.ema_indicator(df["Close"], window=20)
        df["ema50"] = ta.trend.ema_indicator(df["Close"], window=50)
        df["ema200"] = ta.trend.ema_indicator(df["Close"], window=200)
        df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
        df["macd_hist"] = ta.trend.MACD(df["Close"]).macd_diff()
        df["stoch_k"] = ta.momentum.StochasticOscillator(df["High"], df["Low"], df["Close"]).stoch()
        df["vol_sma20"] = df["Volume"].rolling(20).mean()
        
        hl = (df["High"] - df["Low"]).replace(0, 0.001)
        mf_vol = (((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / hl) * df["Volume"]
        df["vol_wave"] = (mf_vol.rolling(20).mean() / df["Volume"].rolling(20).mean().replace(0, 0.001) * 100).ewm(span=5).mean()
        pc = df["Close"].diff()
        df["trend_wave"] = 100 * (pc.ewm(span=25).mean().ewm(span=13).mean() / pc.abs().ewm(span=25).mean().ewm(span=13).mean().replace(0, 0.001))
        df["dom_wave"] = ((ta.momentum.rsi(df["Close"]) - 50) * 2).ewm(span=3).mean()
        hh, ll = df["High"].rolling(20).max(), df["Low"].rolling(20).min()
        df["struct_wave"] = pandas_wma(((df["Close"] - ll) / (hh - ll).replace(0, 0.001)) * 200 - 100, 8)
        
        df["value_now_m"] = (df["Close"] * df["Volume"]) / 1e6
        df["value_ma20"] = df["value_now_m"].rolling(20).mean()
        df["inflow_ratio"] = df["value_now_m"] / df["value_ma20"].replace(0, 0.001)
        
        scores = []
        for i in range(len(df)):
            if i < 30: scores.append(0); continue
            r = df.iloc[i]
            s = 0
            if r["Close"] > r["Open"]: s += 10
            if r["vol_wave"] > 0: s += 15
            if r["trend_wave"] > 0: s += 15
            if r["inflow_ratio"] > 1.1: s += 20
            if r["struct_wave"] > -50: s += 30
            if r["rsi"] > 50: s += 10
            scores.append(min(s, 100))
        df["bull_score"] = scores
        return df.dropna()
    except: return None

# ──────────────────────────────────────────────────────────────────────────────
# 3. PATTERN ENGINE & REPORT
# ──────────────────────────────────────────────────────────────────────────────
def detect_patterns(df, use_trend, use_vol, use_inflow):
    if df is None or len(df) < 15: return "Neutral"
    try:
        c, p, p2, p3, p4 = df.iloc[-1], df.iloc[-2], df.iloc[-3], df.iloc[-4], df.iloc[-5]
    except IndexError: return "Neutral"
    
    uptrend = (c["Close"] > c["ema200"]) if use_trend else True
    vol_valid = (c["Volume"] > c["vol_sma20"]) if use_vol else True
    inflow_valid = (c["inflow_ratio"] > 1.0) if use_inflow else True
    
    if not (uptrend and inflow_valid and vol_valid): return "Neutral"

    def b(n): return abs(n["Close"] - n["Open"])
    def is_bull(n): return n["Close"] > n["Open"]
    def is_bear(n): return n["Open"] > n["Close"]
    def tr(n): return n["High"] - n["Low"]

    if (min(c["Open"], c["Close"]) - c["Low"]) > 1.8 * b(c) and (c["High"] - max(c["Open"], c["Close"])) < 0.2 * b(c): return "Hammer"
    if is_bear(p) and is_bull(c) and c["Open"] <= p["Close"] and c["Close"] >= p["Open"]: return "Bullish Engulfing"
    if (c["High"] - max(c["Open"], c["Close"])) > 1.8 * b(c) and (min(c["Open"], c["Close"]) - c["Low"]) < 0.2 * b(c): return "Inverted Hammer"
    if is_bear(p) and is_bull(c) and c["Open"] > p["Close"] and c["Close"] < p["Open"]: return "Bullish Harami"
    if b(c) < (tr(c) * 0.1) and (c["High"] - max(c["Open"], c["Close"])) < (tr(c) * 0.1): return "Dragonfly Doji"
    if is_bear(p) and is_bull(c) and c["Open"] < p["Low"] and c["Close"] > (p["Open"] + p["Close"])/2: return "Piercing Pattern"
    if is_bull(c) and b(c) > tr(c) * 0.9: return "Bullish Marubozu"
    if abs(c["Low"] - p["Low"]) < (c["Low"] * 0.002) and is_bear(p) and is_bull(c): return "Tweezer Bottom"
    if b(c) < tr(c) * 0.3 and (c["High"]-max(c["Open"],c["Close"])) > b(c) and (min(c["Open"],c["Close"])-c["Low"]) > b(c): return "Bullish Spinning Top"
    if is_bull(p4) and all(is_bear(x) for x in [p3, p2, p]) and is_bull(c) and c["Close"] > p4["High"]: return "Rising Three Method"
    if b(c) < tr(c)*0.1 and (c["High"]-c["Close"]) > tr(c)*0.3: return "Bullish Long Legged Doji"
    if all(is_bull(x) for x in [p2, p, c]) and c["Close"] > p["Close"] > p2["Close"]: return "Three White Soldiers"
    if is_bear(p2) and is_bull(p) and p["Close"] < p2["Open"] and is_bull(c) and c["Close"] > p2["Open"]: return "Three Inside Up"
    if is_bear(p2) and b(p) < b(p2)*0.3 and is_bull(c) and c["Close"] > (p2["Open"]+p2["Close"])/2: return "Morning Star"
    if is_bear(p2) and is_bull(p) and p["Close"] > p2["Open"] and is_bull(c) and c["Close"] > p["Close"]: return "Three Outside Up"

    return "Neutral"

def prepare_download_file(df, filters):
    meta = f"--- Aulsome Matrix Pro Report ---\nDate: {time.strftime('%Y-%m-%d %H:%M:%S')}\nFilters:\n"
    for k, v in filters.items(): meta += f"- {k}: {v}\n"
    meta += "---------------------------------\n\n"
    return meta + df.to_csv(index=False)

# ──────────────────────────────────────────────────────────────────────────────
# 4. MAIN APP
# ──────────────────────────────────────────────────────────────────────────────
def main():
    init_state()
    st.title("🔮 Aulsome Matrix Pro V5.8")
    
    with st.sidebar:
        st.header("⚙️ Panel Kontrol")
        market = st.radio("Universe", ["IHSG", "Crypto"], horizontal=True)
        timeframe = st.selectbox("Timeframe", ["1h","4h","1d"], index=2)
        
        st.markdown("---")
        st.subheader("🛠️ Strictness Level")
        use_trend = st.checkbox("Wajib Uptrend (EMA 200)", value=True)
        use_vol = st.checkbox("Wajib Volume Spike", value=True)
        use_inflow = st.checkbox("Wajib Inflow > 1.0", value=True)
        
        st.markdown("---")
        mode = st.selectbox("Metode Screening", ["Wave Matrix 🌊", "Candlestick Pattern 🕯️", "Sniper Filter 🎯", "Inflow Detector 💰"])
        
        # LOGIC BARU: WAVE METERAN
        strategy = None
        wave_threshold = -60
        if mode == "Wave Matrix 🌊":
            strategy = st.selectbox("Signal", ["Garis Putih (Oversold)", "Golden Cross"])
            if strategy == "Garis Putih (Oversold)":
                wave_threshold = st.slider("Min Threshold Putih", -100, 100, -60, help="Semakin rendah semakin oversold")
        elif mode == "Candlestick Pattern 🕯️":
            strategy = st.selectbox("Pilih Pola", [
                "Hammer", "Bullish Engulfing", "Morning Star", "Three White Soldiers", "Three Outside Up"
            ])
        elif mode == "Inflow Detector 💰":
            strategy = st.selectbox("Signal", ["High Inflow (≥1.5x)", "Inflow + Bandar Akumulasi"])

        min_turnover = st.number_input("Min Turnover (Mln)", 0.0, 5000.0, 10.0)
        run_scan = st.button("🚀 EXECUTE SCAN", use_container_width=True)

    suffix = ".JK" if market == "IHSG" else "-USD"
    tickers_raw = (IHSG_MEGA if market == "IHSG" else CRYPTO_MEGA).split()
    tickers = [f"{t.strip()}{suffix}" for t in tickers_raw if t.strip()]

    tab1, tab2 = st.tabs(["📊 Hasil Screening", "🧠 Deep Journey"])

    with tab1:
        if run_scan:
            results = []
            prog = st.progress(0)
            def process(t):
                try:
                    df_raw = fetch_data(t, timeframe)
                    df = compute_technicals(df_raw)
                    if df is None: return None
                    
                    latest = df.iloc[-1]
                    if latest["value_now_m"] < min_turnover: return None
                    if use_inflow and latest["inflow_ratio"] < 1.0: return None
                    
                    matched = False
                    pat = detect_patterns(df, use_trend, use_vol, use_inflow)
                    
                    if mode == "Wave Matrix 🌊":
                        if "Putih" in strategy: 
                            matched = latest["struct_wave"] <= wave_threshold
                        else: # Golden Cross
                            matched = df.iloc[-2]["struct_wave"] < df.iloc[-2]["dom_wave"] and latest["struct_wave"] > latest["dom_wave"]
                    elif mode == "Candlestick Pattern 🕯️": matched = (pat == strategy)
                    elif mode == "Sniper Filter 🎯":
                        vol_ok = (latest["Volume"] > df["Volume"].rolling(20).mean().iloc[-1]) if use_vol else True
                        trend_ok = (latest["Close"] > latest["ema200"]) if use_trend else True
                        matched = trend_ok and vol_ok and pat != "Neutral"
                    elif mode == "Inflow Detector 💰":
                        if "High" in strategy: matched = latest["inflow_ratio"] >= 1.5
                        else: matched = latest["inflow_ratio"] > 1.2 and latest["vol_wave"] > 0
                    
                    if matched:
                        return {"Asset": t.replace(suffix,""), "Price": round(latest["Close"], 2), "Inflow": round(latest["inflow_ratio"],2), "Score": int(latest["bull_score"]), "WhiteWave": round(latest["struct_wave"],1), "Bandar": round(latest["vol_wave"],1)}
                except: return None
                return None

            with ThreadPoolExecutor(max_workers=20) as exe:
                for i, res in enumerate(exe.map(process, tickers)):
                    if res: results.append(res)
                    prog.progress((i+1)/len(tickers))
            
            st.session_state["results"] = results
            st.session_state["last_filters"] = {
                "Market": market, "Mode": mode, "Strategy": strategy, 
                "WhiteThreshold": wave_threshold if mode == "Wave Matrix 🌊" else "N/A"
            }
            st.rerun()

        if st.session_state["results"]:
            df_res = pd.DataFrame(st.session_state["results"])
            st.dataframe(df_res, use_container_width=True, hide_index=True)
            
            # --- EXPORT FEATURE ---
            csv_data = prepare_download_file(df_res, st.session_state["last_filters"])
            st.download_button("📥 DOWNLOAD CSV REPORT", csv_data, f"Report_{time.strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)
        else: st.info("Gunakan sidebar untuk memulainya.")

    with tab2:
        if st.session_state["results"]:
            selected = st.selectbox("Pilih Saham:", [r["Asset"] for r in st.session_state["results"]])
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
                
                if st.button("🪄 AI Order Flow Analysis"):
                    client = get_client()
                    if client:
                        with st.spinner("AI sedang membaca Market Structure..."):
                            lookback = df_p.tail(30).copy()
                            cols = ['Open', 'High', 'Low', 'Close', 'vol_wave', 'struct_wave', 'inflow_ratio', 'bull_score']
                            data_str = lookback[cols].to_string()
                            prompt = f"Senior Technical Analyst. Analisis {selected} (30 periode):\n{data_str}\nBeri Verdict & Trading Plan."
                            resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile")
                            st.markdown(resp.choices[0].message.content)
        else: st.info("Scan market dulu.")

if __name__ == "__main__":
    main()

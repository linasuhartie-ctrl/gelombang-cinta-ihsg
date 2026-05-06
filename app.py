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
import random
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIG & UNIVERSE
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Aulsome Matrix Pro V6.0",
    page_icon="🔮",
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
        if df.empty or len(df) < 50: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df.dropna()
    except: return None

def compute_technicals(df):
    if df is None or len(df) < 100: return None
    try:
        df = df.copy()
        df["ema200"] = ta.trend.ema_indicator(df["Close"], window=200)
        df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
        
        # Wave Matrix
        hl = (df["High"] - df["Low"]).replace(0, 0.001)
        mf_vol = (((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / hl) * df["Volume"]
        df["vol_wave"] = (mf_vol.rolling(20).mean() / df["Volume"].rolling(20).mean().replace(0, 0.001) * 100).ewm(span=5).mean()
        df["dom_wave"] = ((df["rsi"] - 50) * 2).ewm(span=3).mean()
        hh, ll = df["High"].rolling(20).max(), df["Low"].rolling(20).min()
        df["struct_wave"] = pandas_wma(((df["Close"] - ll) / (hh - ll).replace(0, 0.001)) * 200 - 100, 8)
        
        # Inflow
        df["value_now_m"] = (df["Close"] * df["Volume"]) / 1e6
        df["value_ma20"] = df["value_now_m"].rolling(20).mean()
        df["inflow_ratio"] = df["value_now_m"] / df["value_ma20"].replace(0, 0.001)
        
        # Bull Score
        scores = []
        for i in range(len(df)):
            if i < 50: scores.append(0); continue
            r = df.iloc[i]
            s = 0
            if r["vol_wave"] > 0: s += 25
            if r["dom_wave"] > 0: s += 20
            if r["inflow_ratio"] > 1.1: s += 25
            if r["struct_wave"] > -50: s += 30
            scores.append(min(s, 100))
        df["bull_score"] = scores
        return df.dropna()
    except: return None

def detect_patterns(df):
    if df is None or len(df) < 5: return "Neutral"
    c, p = df.iloc[-1], df.iloc[-2]
    body_c = abs(c["Close"] - c["Open"])
    if (min(c["Open"], c["Close"]) - c["Low"]) > 2 * body_c and c["rsi"] < 40: return "Hammer"
    if p["Close"] < p["Open"] and c["Close"] > c["Open"] and c["Open"] < p["Close"] and c["Close"] > p["Open"]: return "Bullish Engulfing"
    return "Neutral"

# ──────────────────────────────────────────────────────────────────────────────
# 3. MAIN APP
# ──────────────────────────────────────────────────────────────────────────────
def main():
    init_state()
    st.title("🔮 Aulsome Matrix Pro V6.0")
    
    with st.sidebar:
        st.header("🎯 Strategy Panel")
        market = st.radio("Universe", ["IHSG", "Crypto"], horizontal=True)
        timeframe = st.selectbox("Timeframe", ["1h","4h","1d"], index=2)
        
        st.markdown("---")
        mode = st.selectbox("Metode Screening", ["Wave Matrix 🌊", "Candlestick Pattern 🕯️", "Inflow Detector 💰", "Sniper Filter 🎯"])
        
        strategy, wave_threshold = None, -80
        if mode == "Wave Matrix 🌊":
            strategy = st.selectbox("Signal", ["Bullish Reversal (Bottoming)", "Bearish Reversal (Topping)", "Bullish Continuation", "Bearish Continuation"])
            wave_threshold = st.slider("White Threshold", -100, 100, -80 if "Bullish" in strategy else 80)
        elif mode == "Candlestick Pattern 🕯️":
            strategy = st.selectbox("Pattern", ["Hammer", "Bullish Engulfing"])
        elif mode == "Inflow Detector 💰":
            strategy = st.selectbox("Level", ["High Inflow (≥1.5x)", "Accumulation (≥1.2x + Vol↑)"])
        
        st.markdown("---")
        use_trend = st.checkbox("📈 Uptrend Only (EMA200)", value=True)
        min_turnover = st.number_input("💰 Min Turnover (Mln)", 1.0, 5000.0, 10.0)
        max_workers = st.slider("🔧 Concurrency", 5, 30, 15)
        
        if st.button("🚀 EXECUTE FULL SCAN", type="primary", use_container_width=True):
            st.session_state["scan_triggered"] = True
            st.rerun()

    # --- SCANNING LOGIC ---
    if st.session_state["scan_triggered"]:
        st.session_state["scan_triggered"] = False
        suffix = ".JK" if market == "IHSG" else "-USD"
        tickers_raw = (IHSG_MEGA if market == "IHSG" else CRYPTO_MEGA).split()
        tickers = [f"{t.strip()}{suffix}" for t in tickers_raw if t.strip()]
        
        results = []
        prog = st.progress(0)
        
        def process_ticker(t):
            df = compute_technicals(fetch_data(t, timeframe))
            if df is None: return None
            latest, prev = df.iloc[-1], df.iloc[-2]
            if latest["value_now_m"] < min_turnover: return None
            
            matched = False
            if mode == "Wave Matrix 🌊":
                if strategy == "Bullish Reversal (Bottoming)":
                    matched = latest["struct_wave"] <= wave_threshold and (latest["dom_wave"] > prev["dom_wave"] or latest["vol_wave"] > prev["vol_wave"])
                elif strategy == "Bearish Reversal (Topping)":
                    matched = latest["struct_wave"] >= wave_threshold and latest["vol_wave"] < prev["vol_wave"]
                elif "Bullish Continuation" in strategy:
                    matched = latest["vol_wave"] > 0 and latest["vol_wave"] > latest["dom_wave"] > latest["struct_wave"]
                elif "Bearish Continuation" in strategy:
                    matched = latest["vol_wave"] < 0 and latest["vol_wave"] < latest["dom_wave"] < latest["struct_wave"]
            elif mode == "Candlestick Pattern 🕯️":
                matched = detect_patterns(df) == strategy
            elif mode == "Inflow Detector 💰":
                matched = latest["inflow_ratio"] >= 1.5 if "High" in strategy else (latest["inflow_ratio"] > 1.2 and latest["vol_wave"] > 0)
            elif mode == "Sniper Filter 🎯":
                matched = latest["Volume"] > (df["Volume"].rolling(20).mean().iloc[-1] * 1.3) and detect_patterns(df) != "Neutral"
            
            if use_trend and latest["Close"] < latest["ema200"]: matched = False
            
            if matched:
                return {"Asset": t.replace(suffix,""), "Price": round(latest["Close"], 4), "Score": int(latest["bull_score"]), "Inflow": round(latest["inflow_ratio"], 2), "White": round(latest["struct_wave"], 1), "Yellow": round(latest["vol_wave"], 1), "Purple": round(latest["dom_wave"], 1), "Pattern": detect_patterns(df)}
            return None

        with ThreadPoolExecutor(max_workers=max_workers) as exe:
            for i, res in enumerate(exe.map(process_ticker, tickers)):
                if res: results.append(res)
                prog.progress((i+1)/len(tickers))
        
        st.session_state["results"] = sorted(results, key=lambda x: x["Score"], reverse=True)
        st.session_state["last_scan_time"] = datetime.now().strftime("%H:%M:%S")
        st.rerun()

    # --- UI DISPLAY ---
    tab_res, tab_deep = st.tabs(["📊 Screening Results", "📈 Deep Analysis"])
    
    with tab_res:
        if st.session_state["last_scan_time"]:
            st.success(f"✅ Last scan completed at {st.session_state['last_scan_time']}")
        if st.session_state["results"]:
            df_res = pd.DataFrame(st.session_state["results"])
            st.dataframe(df_res, use_container_width=True, hide_index=True)
            st.download_button("📥 Download CSV", df_res.to_csv(index=False), "results.csv", "text/csv", use_container_width=True)
        else: st.info("Gunakan sidebar untuk memulainya.")

    with tab_deep:
        if st.session_state["results"]:
            selected = st.selectbox("🎯 Select Asset", [r["Asset"] for r in st.session_state["results"]])
            suffix = ".JK" if market == "IHSG" else "-USD"
            df_p = compute_technicals(fetch_data(selected + suffix, timeframe))
            if df_p is not None:
                fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.5, 0.3, 0.2])
                fig.add_trace(go.Candlestick(x=df_p.index, open=df_p["Open"], high=df_p["High"], low=df_p["Low"], close=df_p["Close"], name="Price"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p["ema200"], name="EMA200", line=dict(color="orange")), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p["vol_wave"], name="Yellow", line=dict(color="yellow")), row=2, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p["dom_wave"], name="Purple", line=dict(color="purple")), row=2, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p["struct_wave"], name="White", line=dict(color="white")), row=2, col=1)
                fig.add_trace(go.Bar(x=df_p.index, y=df_p["inflow_ratio"], name="Inflow"), row=3, col=1)
                fig.update_layout(template="plotly_dark", height=800, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
                
                if st.button("🧠 AI Signal Analysis"):
                    client = get_client()
                    if client:
                        with st.spinner("Analyzing..."):
                            latest = df_p.iloc[-1]
                            prompt = f"Analisis {selected}: White:{latest['struct_wave']:.1f}, Yellow:{latest['vol_wave']:.1f}, Inflow:{latest['inflow_ratio']:.2f}x. Beri Verdict BUY/HOLD/SELL."
                            resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}])
                            st.write(resp.choices[0].message.content)
        else: st.info("Scan market dulu.")

if __name__ == "__main__":
    main()

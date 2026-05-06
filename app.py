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
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIG & UNIVERSE (Sama seperti V6.1)
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Aulsome Matrix Pro V6.2", page_icon="🔮", layout="wide")

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

@st.cache_data(ttl=600)
def fetch_data(ticker, timeframe):
    try:
        mapping = {"15m": ("5d", "15m"), "1h": ("1mo", "1h"), "4h": ("2mo", "4h"), "1d": ("2y", "1d")}
        p, i = mapping.get(timeframe, ("2y", "1d"))
        df = yf.download(ticker.upper(), period=p, interval=i, progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df.dropna()
    except: return None

def compute_technicals(df):
    if df is None or len(df) < 100: return None
    try:
        df = df.copy()
        df["EMA20"] = ta.trend.ema_indicator(df["Close"], window=20)
        df["EMA50"] = ta.trend.ema_indicator(df["Close"], window=50)
        df["EMA200"] = ta.trend.ema_indicator(df["Close"], window=200)
        df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
        
        # Wave Matrix
        hl = (df["High"] - df["Low"]).replace(0, 0.001)
        mf_vol = (((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / hl) * df["Volume"]
        df["Vol_Wave"] = (mf_vol.rolling(20).mean() / df["Volume"].rolling(20).mean().replace(0, 0.001) * 100).ewm(span=5).mean()
        df["Dom_Wave"] = ((df["RSI"] - 50) * 2).ewm(span=3).mean()
        hh, ll = df["High"].rolling(20).max(), df["Low"].rolling(20).min()
        df["Struct_Wave"] = pandas_wma(((df["Close"] - ll) / (hh - ll).replace(0, 0.001)) * 200 - 100, 8)
        
        # Inflow
        df["value_now_m"] = (df["Close"] * df["Volume"]) / 1e6
        df["value_ma20"] = df["value_now_m"].rolling(20).mean()
        df["Inflow_Ratio"] = df["value_now_m"] / df["value_ma20"].replace(0, 0.001)
        
        return df.dropna()
    except: return None

# ──────────────────────────────────────────────────────────────────────────────
# 3. PROMPT BUILDER
# ──────────────────────────────────────────────────────────────────────────────
def build_ai_prompt(asset, df):
    lookback = df.tail(30).copy()
    # Memilih kolom penting agar prompt tidak kepanjangan (Token limit)
    cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'EMA200', 'Vol_Wave', 'Struct_Wave', 'Inflow_Ratio', 'RSI']
    data_str = lookback[cols].to_string()

    return f"""
Anda adalah Senior Technical Analyst dengan spesialisasi dalam *Market Structure* dan *Order Flow*. 
Tugas Anda adalah memberikan analisis objektif untuk aset {asset} berdasarkan data teknikal berikut.

DATA MARKET (Last 30 Periods):
{data_str}

INSTRUKSI ANALISIS (WAJIB DIIKUTI):
1. MARKET STRUCTURE: Identifikasi apakah harga dalam fase uptrend, downtrend, atau sideways berdasarkan EMA20/50/200. Apakah ada konfirmasi Higher High (HH) atau Lower Low (LL)?
2. MOMENTUM & FLOW: Analisis interaksi antara Vol_Wave (akumulasi bandar) dan Inflow_Ratio. Jika vol_wave positif namun harga stagnan, apa artinya?
3. SENSITIVITY: Apakah RSI menunjukkan divergensi atau konfirmasi tren?
4. ELLIOTT WAVE: Berikan hipotesis sederhana mengenai fase Elliott Wave saat ini (Impulsive vs Corrective).
5. VERDICT: Berikan label tegas: [SUPER YAHUD / YAHUD / WATCHLIST / WEAK / SKIP].
6. TRADING PLAN: Sertakan rasio Risk/Reward. Tentukan Entry, Stop Loss, dan Target Price yang realistis berdasarkan support/resistance terdekat.

FORMAT OUTPUT:
Gunakan format Markdown yang profesional dengan sub-header yang jelas. Hindari bahasa yang terlalu umum. Fokus pada "Evidence-based analysis".
"""

# ──────────────────────────────────────────────────────────────────────────────
# 4. MAIN UI & SCANNER (Ringkas)
# ──────────────────────────────────────────────────────────────────────────────
def main():
    init_state()
    st.sidebar.title("🎯 Control Panel")
    market = st.sidebar.radio("Universe", ["IHSG", "Crypto"], horizontal=True)
    timeframe = st.sidebar.selectbox("Timeframe", ["1h","4h","1d"], index=2)
    min_turnover = st.sidebar.number_input("Min Turnover (Mln)", 1.0, 5000.0, 10.0)
    
    if st.sidebar.button("🚀 START SCAN", type="primary", use_container_width=True):
        st.session_state["scan_triggered"] = True
        st.rerun()

    if st.session_state["scan_triggered"]:
        st.session_state["scan_triggered"] = False
        suffix = ".JK" if market == "IHSG" else "-USD"
        tickers = [f"{t.strip()}{suffix}" for t in (IHSG_MEGA if market == "IHSG" else CRYPTO_MEGA).split()]
        
        results = []
        prog = st.progress(0)
        
        def process_ticker(t):
            df = compute_technicals(fetch_data(t, timeframe))
            if df is None: return None
            latest = df.iloc[-1]
            if latest["value_now_m"] < min_turnover: return None
            
            # Sinyal Reversal Otomatis (Garis Putih <= -80)
            if latest["Struct_Wave"] <= -80:
                return {"Asset": t.replace(suffix,""), "Price": round(latest["Close"], 2), "Inflow": round(latest["Inflow_Ratio"], 2), "White": round(latest["Struct_Wave"], 1), "Yellow": round(latest["Vol_Wave"], 1)}
            return None

        with ThreadPoolExecutor(max_workers=20) as exe:
            for i, res in enumerate(exe.map(process_ticker, tickers)):
                if res: results.append(res)
                prog.progress((i+1)/len(tickers))
        
        st.session_state["results"] = results
        st.session_state["last_scan_time"] = datetime.now().strftime("%H:%M:%S")
        st.rerun()

    tab1, tab2 = st.tabs(["📋 Watchlist", "🔍 Deep Analysis"])
    
    with tab1:
        if st.session_state["results"]:
            st.dataframe(pd.DataFrame(st.session_state["results"]), use_container_width=True, hide_index=True)
        else: st.info("Scan market untuk mencari aset di area Reversal.")

    with tab2:
        if st.session_state["results"]:
            selected = st.selectbox("Pilih Aset", [r["Asset"] for r in st.session_state["results"]])
            suffix = ".JK" if market == "IHSG" else "-USD"
            df_p = compute_technicals(fetch_data(selected + suffix, timeframe))
            
            if df_p is not None:
                # Chart logic
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)
                fig.add_trace(go.Candlestick(x=df_p.index, open=df_p["Open"], high=df_p["High"], low=df_p["Low"], close=df_p["Close"], name="Price"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p["Vol_Wave"], name="Yellow", line=dict(color="yellow")), row=2, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p["Struct_Wave"], name="White", line=dict(color="white")), row=2, col=1)
                fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
                
                if st.button("🪄 RUN SENIOR AI ANALYSIS"):
                    client = get_client()
                    if client:
                        with st.spinner("Analyzing Market Structure..."):
                            prompt = build_ai_prompt(selected, df_p)
                            resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}])
                            st.markdown(resp.choices[0].message.content)
        else: st.info("Pilih aset dari tab Watchlist.")

if __name__ == "__main__":
    main()

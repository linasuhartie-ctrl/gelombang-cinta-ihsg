import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import time
from concurrent.futures import ThreadPoolExecutor
from groq import Groq

# Membersihkan peringatan agar UI tetap elegan
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# 0. API & CONFIG
# ──────────────────────────────────────────────────────────────────────────────
try:
    # Mengambil kunci dari Secrets
    client = Groq(api_key=st.secrets["GROQ_KEY"])
except Exception:
    st.error("⚠️ GROQ_KEY tidak ditemukan! Tambahkan di Secrets Dashboard Streamlit.")

st.set_page_config(page_title="Aulsome Matrix V4.1", page_icon="🔮", layout="wide")

# (Daftar Ticker tetap sama - IHSG & Crypto)
IHSG_MEGA = """ AALI ABBA ABDA ABMM ACES ACST ADCP ADES ADHI ADMF ADMG ADMR ADRO AGII AGRO AHAP AISA AKPI AKRA ALDO ALKA ALMI AMAG AMAN AMAR AMFG AMIN AMMN AMRT ANJT ANTM APEX APLN ARCI ARGO ARII ARNA ARTA ARTI ARTO ASBI ASGR ASII ASRI ASRM ASSA ATIC AUTO AVIA BABP BACA BAJA BALI BANK BAPA BATA BBCA BBHI BBKP BBLD BBMD BBNI BBRI BBRM BBTN BBYB BCAP BCIC BDMN BEKS BELL BESS BEST BFIN BGTG BINA BIPI BIPP BIRD BISI BJBR BJTM BKDP BKSL BLTA BMAS BMHS BMRI BMSR BMTR BNBA BNBR BNGA BNII BNLI BOBA BOLA BPFI BRIS BREN BRMS BRNA BRPT BSDE BSIM BSSR BSWD BTEK BTEL BTON BTPN BTPS BUDI BUKK BULL BUMI BVIC BWPT BYAN CAKK CAMP CARS CASH CASS CCSI CEKA CENT CFIN CINT CITA CITY CLEO CMNP CMPP CNKO CNTX COAL CPIN CPRO CSAP CSRA CTBN CTRA DART DAYA DCII DEAL DEWA DFAM DGIK DILD DIVA DKFT DLTA DMMX DMND DNAR DNET DOID DPNS DSFI DSNG DSSA DUTI DYAN EAST EKAD ELSA EMDE EMTK ENRG EPMT ERAA ESSA ESTI ETWA EXCL FAST FASW FILM FIRE FISH FMII FOOD FORU FORZ FPNI FREN GAMA GDST GDYR GEMA GEMS GGRM GIAA GJTL GLOB GLVA GMFI GMTD GOLD GOOD GOTO GPRA GSMF GTBO GWSA GZCO HADE HAIS HDFA HEAL HERO HEXA HITS HKMU HMSP HOKI HOME HRME HRTA HRUM IATA IBST ICBP ICON IDEA IGAR IIKP IKAI IMAS IMJS IMPC INAF INAI INCF INCI INCO INDF INDO INDR INDS INDY INPC INPS INRU INTA INTP IPCC IPCM IPOL IPTV IRRA ISAT ISSP ITIC ITMG JAKS JAST JAWA JAYA JECC JGLE JIHD JKON JMAS JSPT JTPE KAEF KBLI KBLM KBLV KDSI KEEN KEJU KIAS KICI KIJA KINO KIOS KKGI KLBF KOBX KOIN KONI KPIG KRYA LAMI LCGP LEAD LINK LION LMAS LMPI LMSH LPCK LPGI LPIN LPKR LPLI LPPF LSIP LTLS MAIN MAMI MAPA MAPB MAPI MARK MASA MAYA MBAP MBSS MBTO MCAS MCOR MDIA MDKA MDLN MDRN MEDC MEGA MERK META MFIN MICE MIDI MIKA MINA MIRA MITI MKPI MLBI MLIA MLPL MLPT MMLP MNCN MOLI MORA MPMX MPPA MSIN MSKY MTDL MTEL MTLA MTMH MTPS MTRA MTSM MYOH MYOR MYRX MYTX NANO NELY NFCX NIPS NIRO NISP NOBU NRCA NZIA OASA OBMD OMED OMRE ONIX PADI PALM PAMG PANI PANR PANS PBSA PCAR PEGE PEHA PGAS PGEO PGLI PICO PJAA PKPK PLAS PLIN PNBN PNBS PNIN PNLF PNSE POLA POLI POLL POLY POOL PORT PRAS PRDA PSAB PSDN PSGO PSKT PTBA PTPP PTPW PUDA PURA PWON PYFA PZZA RAJA RALS RANC RBMS RDTX REAL RELI RICY RIGS RIMO RMBA ROCK ROTI RSGK RUIS SAFE SAME SAMF SAPX SCCO SCMA SCNP SDMU SDPC SFAN SGER SGRO SHID SIDO SILO SIMA SIMP SINI SIPD SKBM SKLT SKYB SMAR SMBR SMCB SMDR SMGR SMIL SMKL SMMA SMMT SMRA SMRU SMSM SOBI SOHO SONA SOSS SOTO SPMA SQMI SRAJ SRIL SRSN SRTG SSIA SSMS SSTM STTP SUGI SULI SUPR SURE SWAT TAXI TAYS TBIG TBLA TBMS TCID TCPI TEBE TECH TELE TFCO TGKA TIFA TINS TIRA TIRT TKIM TLDN TLKM TMAS TMPO TNCA TOBA TOYS TPIA TPMA TRAM TRIL TRIM TRIN TRIS TRJA TRST TRUK TSPC TUGU TURI ULTJ UNIC UNIT UNSP UNTR UNVR URBN VCGG VICO VINS VIVA VKTR VOKS VRNA WAPO WEHA WEGE WIFI WIKA WINS WOMF WOOD WSBP WSKT WTON YELO YPAS ZATA ZBRA ZINC ZONE ZYRX """
CRYPTO_MEGA = """ BTC ETH BNB SOL XRP ADA DOGE AVAX DOT MATIC LINK SHIB LTC NEAR UNI APT ARB OP TIA SUI FET RNDR STX FIL ATOM IMX HBAR ETC ICP PEPE WIF BONK ORDI INJ THETA LDO VET BEAM SEI AAVE MKR RUNE GALA EGLD ALGO FLOW DYDX CRV SNX PENDLE JUP PYTH STRK W ENA ROSE AGIX STG AXS SAND MANA CHZ MINA KAVA GRT AGLD JASMY TRX KAS XLM XMR BCH BSV LUNC LUNA USTC JTO 1INCH MASK ENS BLUR T GLM AKT NOS IO AEVO ZK ZRO LISTA NOT BB PIXEL PORTAL XAI ACE SATS FLOKI MEME LADYS TURBO PEOPLE TRB GAS ARK WAVES ONT ONG NEO QTUM DGB SC XVG HOT RVN CKB SLP GNS PERP GMX WOO ZRX KNC LRC SUSHI BAKE JOE CAKE PORK BRETT BOME MEW MYRO WEN COQ KDA OSMO RETH LPT ALT MANTA ONDO RIF NTRN PAI SKL METIS SCRT CFX ACH TRU HOOK MAGIC GAL CORE EDU ID COMBO RDNT HIFI MAV PUNDIX BEL FRONT C98 MTL REEF ATA ALICE PROM DAR CHR SXP STEEM KMD STRAX ADX ICX OGN NKN DENT KEY MFT DATA VTHO STMX IQ UTK OXT ANKR CTSI COS TROY PIVX SYS SCR GFT QKC IOTX CTXC DOCK MITH TFUEL GTC MLN BOND FOR LINA DEGO EPS AUTO TKO TVK QUICK ERN RAMP PHA BAR CITY ASR JUV ATM OG PSG SANTOS LAZIO ALPINE FLOW MIR ANC ZEN RARE CLV ALPHA FIS SPELL CHESS QI GHST VOXEL BNX NMR VIB AST OAX DUSK LSK ARDR LOOM REQ AKRO POLS HARD STPT OOKI UNFI WING FOR BOND MOB MOVR SYN HIGH KP3R SNT MULTI VANRY """

# ──────────────────────────────────────────────────────────────────────────────
# 1. CORE ENGINE (AULYEAH PREDICTIVE)
# ──────────────────────────────────────────────────────────────────────────────

def pandas_wma(series, window):
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def compute_matrix_waves(df):
    if df is None or len(df) < 50: return None
    df = df.copy()
    
    # Technical Indicators
    macd = ta.trend.MACD(df['Close'])
    df['macd_hist'] = macd.macd_diff()
    stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'], window=14, smooth_window=3)
    df['stoch_k'] = stoch.stoch()

    # Gelombang 1: Bandar (Kuning)
    mf_mult = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (df["High"] - df["Low"]).replace(0, 0.001)
    df["vol_wave"] = (mf_mult * df["Volume"]).rolling(20).mean() / df["Volume"].rolling(20).mean().replace(0, 0.001) * 100
    df["vol_wave"] = df["vol_wave"].ewm(span=5, adjust=False).mean()
    
    # Gelombang 2: Trend (Biru)
    pc = df["Close"].diff()
    dsp = pc.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    dsp_abs = pc.abs().ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    df["trend_wave"] = 100 * (dsp / dsp_abs.replace(0, 0.001))
    
    # Gelombang 3: Dominasi (Ungu)
    df["dom_wave"] = ((ta.momentum.rsi(df["Close"], window=14) - 50) * 2).ewm(span=3, adjust=False).mean()
    
    # Gelombang 4: Struktur (Putih)
    hh, ll = df["High"].rolling(20).max(), df["Low"].rolling(20).min()
    df["struct_wave"] = pandas_wma(((df["Close"] - ll) / (hh - ll).replace(0, 0.001)) * 200 - 100, 8)
    
    return df

@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(ticker, timeframe):
    try:
        p, i = ("5d", "15m") if timeframe == "15m" else ("1mo", "1h") if timeframe == "1h" else ("2mo", "1h") if timeframe == "4h" else ("1y", "1d")
        df = yf.download(ticker, period=p, interval=i, progress=False, auto_adjust=True)
        if df.empty: return None
        if timeframe == "4h":
            df = df.resample("4H").agg({"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna()
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

# ──────────────────────────────────────────────────────────────────────────────
# 2. AI NARRATIVE ENGINE
# ──────────────────────────────────────────────────────────────────────────────

def get_ai_insight(asset, price, df):
    lookback = df.tail(20)
    latest, start = lookback.iloc[-1], lookback.iloc[0]
    
    prompt = f"""
    Analisis Naratif 'Aulyeah Matrix' untuk {asset}.
    
    PERBANDINGAN 20 CANDLE:
    - Harga: {start['Close']:.2f} -> {latest['Close']:.2f}
    - Bandar (Kuning): {start['vol_wave']:.1f} -> {latest['vol_wave']:.1f}
    - Trend (Biru): {start['trend_wave']:.1f} -> {latest['trend_wave']:.1f}
    - Dominasi (Ungu): {latest['dom_wave']:.1f}
    - Struktur (Putih): {latest['struct_wave']:.1f}
    
    DATA TAMBAHAN:
    - MACD Hist: {latest['macd_hist']:.4f} | Stoch K: {latest['stoch_k']:.1f}

    TUGAS:
    1. Ceritakan dinamika Bandar vs Harga dalam 20 candle terakhir.
    2. Bedah teknikal (Candle, Elliot Wave, Stoch).
    3. Trading Plan: Entry, TP1, TP2, SL (Angka konkret).
    4. Verdict: YAHUD atau SKIP.
    """
    try:
        resp = client.chat.completions.create(
            messages=[{"role": "system", "content": "Anda mentor trading Pak Aul. Gunakan bahasa tajam & edukatif."},
                      {"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", temperature=0.5
        )
        return resp.choices[0].message.content
    except Exception as e: return f"Error: {str(e)}"

# ──────────────────────────────────────────────────────────────────────────────
# 3. UI
# ──────────────────────────────────────────────────────────────────────────────

def main():
    st.sidebar.title("🔮 Matrix V4.1")
    market = st.sidebar.radio("Market:", ["IHSG", "Crypto"])
    timeframe = st.sidebar.selectbox("Timeframe:", ["15m", "1h", "4h", "1d"], index=3)
    min_vol = st.sidebar.number_input("Min Vol (Mln)", 0.1, 5000.0, 10.0)

    tickers = sorted([t.strip() + (".JK" if market == "IHSG" else "-USD") for t in (IHSG_MEGA if market == "IHSG" else CRYPTO_MEGA).split()])

    tab_scan, tab_ai = st.tabs(["📊 Scan", "🧠 Deep Analysis"])

    with tab_scan:
        if st.sidebar.button(f"🚀 RUN SCAN ({len(tickers)} ASSETS)"):
            results = []
            progress = st.progress(0)
            def process(t):
                df = compute_matrix_waves(fetch_data(t, timeframe))
                if df is not None:
                    latest = df.iloc[-1]
                    turnover = (latest['Close'] * latest['Volume']) / 1e6 if market == "Crypto" else latest['Volume'] / 1e6
                    if turnover >= min_vol and (latest['struct_wave'] < -50 or latest['vol_wave'] > 50):
                        return {"Asset": t.replace(".JK","").replace("-USD",""), "Price": round(latest['Close'],2), "Bandar🟡": round(latest['vol_wave'],1), "Quality": "🔥 SUPER" if latest['struct_wave'] < -80 else "✅ YAHUD"}
                return None

            with ThreadPoolExecutor(max_workers=20) as exe:
                scanned = 0
                for r in exe.map(process, tickers):
                    scanned += 1
                    if r: results.append(r)
                    progress.progress(scanned/len(tickers))
            st.session_state["results"] = results
        
        if "results" in st.session_state:
            st.dataframe(pd.DataFrame(st.session_state["results"]), use_container_width=True)

    with tab_ai:
        if "results" in st.session_state and st.session_state["results"]:
            selected = st.selectbox("Pilih Aset:", [r["Asset"] for r in st.session_state["results"]])
            df_p = compute_matrix_waves(fetch_data(selected + (".JK" if market == "IHSG" else "-USD"), timeframe))
            
            if df_p is not None:
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
                fig.add_trace(go.Candlestick(x=df_p.index, open=df_p["Open"], high=df_p["High"], low=df_p["Low"], close=df_p["Close"], name="Price"), row=1, col=1)
                for w, c in [('vol_wave','#FFD600'), ('trend_wave','#00BFFF'), ('dom_wave','#D500F9'), ('struct_wave','white')]:
                    fig.add_trace(go.Scatter(x=df_p.index, y=df_p[w], line=dict(color=c)), row=2, col=1)
                fig.update_layout(template="plotly_dark", height=700, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)

                if st.button("🪄 Get AI Narrative Insight"):
                    with st.spinner("Membaca sejarah..."):
                        st.markdown(get_ai_insight(selected, df_p.iloc[-1]['Close'], df_p))

if __name__ == "__main__":
    main()

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

# Membersihkan peringatan agar UI tetap rapi
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# 0. API & CONFIG
# ──────────────────────────────────────────────────────────────────────────────
try:
    # Mengambil kunci Groq dari Streamlit Secrets
    client = Groq(api_key=st.secrets["GROQ_KEY"])
except Exception:
    st.error("⚠️ GROQ_KEY tidak ditemukan di Secrets! Tambahkan di dashboard Streamlit.")

st.set_page_config(page_title="Aulsome Screener Matrix", page_icon="🔮", layout="wide")

IHSG_MEGA = """
AALI ABBA ABDA ABMM ACES ACST ADCP ADES ADHI ADMF ADMG ADMR ADRO AGII AGRO 
AHAP AISA AKPI AKRA ALDO ALKA ALMI AMAG AMAN AMAR AMFG AMIN AMMN AMRT ANJT 
ANTM APEX APLN ARCI ARGO ARII ARNA ARTA ARTI ARTO ASBI ASGR ASII ASRI ASRM 
ASSA ATIC AUTO AVIA BABP BACA BAJA BALI BANK BAPA BATA BBCA BBHI BBKP BBLD 
BBMD BBNI BBRI BBRM BBTN BBYB BCAP BCIC BDMN BEKS BELL BESS BEST BFIN BGTG 
BINA BIPI BIPP BIRD BISI BJBR BJTM BKDP BKSL BLTA BMAS BMHS BMRI BMSR BMTR 
BNBA BNBR BNGA BNII BNLI BOBA BOLA BPFI BRIS BREN BRMS BRNA BRPT BSDE BSIM 
BSSR BSWD BTEK BTEL BTON BTPN BTPS BUDI BUKK BULL BUMI BVIC BWPT BYAN CAKK 
CAMP CARS CASH CASS CCSI CEKA CENT CFIN CINT CITA CITY CLEO CMNP CMPP CNKO 
CNTX COAL CPIN CPRO CSAP CSRA CTBN CTRA DART DAYA DCII DEAL DEWA DFAM DGIK 
DILD DIVA DKFT DLTA DMMX DMND DNAR DNET DOID DPNS DSFI DSNG DSSA DUTI DYAN 
EAST EKAD ELSA EMDE EMTK ENRG EPMT ERAA ESSA ESTI ETWA EXCL FAST FASW FILM 
FIRE FISH FMII FOOD FORU FORZ FPNI FREN GAMA GDST GDYR GEMA GEMS GGRM GIAA 
GJTL GLOB GLVA GMFI GMTD GOLD GOOD GOTO GPRA GSMF GTBO GWSA GZCO HADE HAIS 
HDFA HEAL HERO HEXA HITS HKMU HMSP HOKI HOME HRME HRTA HRUM IATA IBST ICBP 
ICON IDEA IGAR IIKP IKAI IMAS IMJS IMPC INAF INAI INCF INCI INCO INDF INDO 
INDR INDS INDY INPC INPS INRU INTA INTP IPCC IPCM IPOL IPTV IRRA ISAT ISSP 
ITIC ITMG JAKS JAST JAWA JAYA JECC JGLE JIHD JKON JMAS JSPT JTPE KAEF KBLI 
KBLM KBLV KDSI KEEN KEJU KIAS KICI KIJA KINO KIOS KKGI KLBF KOBX KOIN KONI 
KPIG KRYA LAMI LCGP LEAD LINK LION LMAS LMPI LMSH LPCK LPGI LPIN LPKR LPLI 
LPPF LSIP LTLS MAIN MAMI MAPA MAPB MAPI MARK MASA MAYA MBAP MBSS MBTO MCAS 
MCOR MDIA MDKA MDLN MDRN MEDC MEGA MERK META MFIN MICE MIDI MIKA MINA MIRA 
MITI MKPI MLBI MLIA MLPL MLPT MMLP MNCN MOLI MORA MPMX MPPA MSIN MSKY MTDL 
MTEL MTLA MTMH MTPS MTRA MTSM MYOH MYOR MYRX MYTX NANO NELY NFCX NIPS NIRO 
NISP NOBU NRCA NZIA OASA OBMD OMED OMRE ONIX PADI PALM PAMG PANI PANR PANS 
PBSA PCAR PEGE PEHA PGAS PGEO PGLI PICO PJAA PKPK PLAS PLIN PNBN PNBS PNIN 
PNLF PNSE POLA POLI POLL POLY POOL PORT PRAS PRDA PSAB PSDN PSGO PSKT PTBA 
PTPP PTPW PUDA PURA PWON PYFA PZZA RAJA RALS RANC RBMS RDTX REAL RELI RICY 
RIGS RIMO RMBA ROCK ROTI RSGK RUIS SAFE SAME SAMF SAPX SCCO SCMA SCNP SDMU 
SDPC SFAN SGER SGRO SHID SIDO SILO SIMA SIMP SINI SIPD SKBM SKLT SKYB SMAR 
SMBR SMCB SMDR SMGR SMIL SMKL SMMA SMMT SMRA SMRU SMSM SOBI SOHO SONA SOSS 
SOTO SPMA SQMI SRAJ SRIL SRSN SRTG SSIA SSMS SSTM STTP SUGI SULI SUPR SURE 
SWAT TAXI TAYS TBIG TBLA TBMS TCID TCPI TEBE TECH TELE TFCO TGKA TIFA TINS 
TIRA TIRT TKIM TLDN TLKM TMAS TMPO TNCA TOBA TOYS TPIA TPMA TRAM TRIL TRIM 
TRIN TRIS TRJA TRST TRUK TSPC TUGU TURI ULTJ UNIC UNIT UNSP UNTR UNVR URBN 
VCGG VICO VINS VIVA VKTR VOKS VRNA WAPO WEHA WEGE WIFI WIKA WINS WOMF WOOD 
WSBP WSKT WTON YELO YPAS ZATA ZBRA ZINC ZONE ZYRX
"""

CRYPTO_MEGA = """
BTC ETH BNB SOL XRP ADA DOGE AVAX DOT MATIC LINK SHIB LTC NEAR UNI APT ARB OP 
TIA SUI FET RNDR STX FIL ATOM IMX HBAR ETC ICP PEPE WIF BONK ORDI INJ THETA 
LDO VET BEAM SEI AAVE MKR RUNE GALA EGLD ALGO FLOW DYDX CRV SNX PENDLE JUP 
PYTH STRK W ENA ROSE AGIX STG AXS SAND MANA CHZ MINA KAVA GRT AGLD JASMY 
TRX KAS XLM XMR BCH BSV LUNC LUNA USTC JTO 1INCH MASK ENS BLUR T GLM AKT 
NOS IO AEVO ZK ZRO LISTA NOT BB PIXEL PORTAL XAI ACE SATS FLOKI MEME LADYS 
TURBO PEOPLE TRB GAS ARK WAVES ONT ONG NEO QTUM DGB SC XVG HOT RVN CKB SLP 
GNS PERP GMX WOO ZRX KNC LRC SUSHI BAKE JOE CAKE PORK BRETT BOME MEW MYRO 
WEN COQ KDA OSMO RETH LPT ALT MANTA ONDO RIF NTRN PAI SKL METIS SCRT CFX 
ACH TRU HOOK MAGIC GAL CORE EDU ID COMBO RDNT HIFI MAV PUNDIX BEL FRONT 
C98 MTL REEF ATA ALICE PROM DAR CHR SXP STEEM KMD STRAX ADX ICX OGN NKN 
DENT KEY MFT DATA VTHO STMX IQ UTK OXT ANKR CTSI COS TROY PIVX SYS SCR 
GFT QKC IOTX CTXC DOCK MITH TFUEL GTC MLN BOND FOR LINA DEGO EPS AUTO TKO 
TVK QUICK ERN RAMP PHA BAR CITY ASR JUV ATM OG PSG SANTOS LAZIO ALPINE 
FLOW MIR ANC ZEN RARE CLV ALPHA FIS SPELL CHESS QI GHST VOXEL BNX NMR VIB 
AST OAX DUSK LSK ARDR LOOM REQ AKRO POLS HARD STPT OOKI UNFI WING FOR 
BOND MOB MOVR SYN HIGH KP3R SNT MULTI VANRY
"""

# ──────────────────────────────────────────────────────────────────────────────
# 1. DATA ENGINE
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(ticker, timeframe):
    try:
        if timeframe == "15m":  p, i = "5d",  "15m"
        elif timeframe == "1h": p, i = "1mo", "1h"
        elif timeframe == "4h": p, i = "2mo", "1h"
        else:                   p, i = "1y",  "1d"
        df = yf.download(ticker, period=p, interval=i, progress=False, auto_adjust=True, timeout=10)
        if df is None or df.empty: return None
        if timeframe == "4h":
            df = df.resample("4H").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}).dropna()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except: return None

def pandas_wma(series, window):
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def compute_matrix_waves(df):
    if df is None or len(df) < 50: return None
    df = df.copy()
    
    # 1. SMART MONEY FLOW (KUNING)
    mf_mult = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (df["High"] - df["Low"]).replace(0, 0.0001)
    mf_vol = mf_mult * df["Volume"]
    vol_raw = (mf_vol.rolling(20).mean() / df["Volume"].rolling(20).mean().replace(0, 0.0001)) * 100
    df["vol_wave"] = vol_raw.ewm(span=5, adjust=False).mean()

    # 2. TREND VELOCITY (BIRU)
    pc = df["Close"].diff()
    dsp = pc.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    dsp_abs = pc.abs().ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    df["trend_wave"] = 100 * (dsp / dsp_abs.replace(0, 0.0001))

    # 3. BULL/BEAR DOMINANCE (UNGU)
    rsi_raw = ta.momentum.rsi(df["Close"], window=14)
    df["dom_wave"] = ((rsi_raw - 50) * 2).ewm(span=3, adjust=False).mean()

    # 4. PRICE STRUCTURE (PUTIH)
    hh, ll = df["High"].rolling(20).max(), df["Low"].rolling(20).min()
    struct_raw = ((df["Close"] - ll) / (hh - ll).replace(0, 0.0001)) * 200 - 100
    df["struct_wave"] = pandas_wma(struct_raw, 8)

    return df

# ──────────────────────────────────────────────────────────────────────────────
# 2. LOGIC & SCORING
# ──────────────────────────────────────────────────────────────────────────────

def detect_divergence(latest):
    yellow, blue = latest["vol_wave"], latest["trend_wave"]
    if yellow > 20 and blue < -20: return ("⚡ BULLISH DIVERGENCE", "Bandar akumulasi (Kuning) saat tren masih turun.")
    if blue > 60 and yellow < -20: return ("☠️ BEARISH DIVERGENCE", "Tren tinggi (Biru) tapi Bandar jualan (Kuning).")
    if all(x > 80 for x in [yellow, blue, latest["dom_wave"], latest["struct_wave"]]): return ("🔥 FULL CONVERGENCE BUY", "Semua gelombang kompak di atas 80!")
    return ("➡️ MIXED / NEUTRAL", "Belum ada sinyal konvergensi ekstrem.")

def compute_wave_score(latest):
    return sum(1 for x in [latest["vol_wave"], latest["trend_wave"], latest["dom_wave"], latest["struct_wave"]] if x > 40)

# ──────────────────────────────────────────────────────────────────────────────
# 3. AI ENGINE (GROQ)
# ──────────────────────────────────────────────────────────────────────────────

def get_ai_insight(asset, price, df):
    latest = df.iloc[-1]
    div_label, div_desc = detect_divergence(latest)
    
    prompt = f"""
    ASET: {asset} | HARGA: {price}
    MATRIX VALUES:
    - Bandar (Kuning): {round(latest['vol_wave'], 1)}
    - Trend (Biru): {round(latest['trend_wave'], 1)}
    - Dominasi (Ungu): {round(latest['dom_wave'], 1)}
    - Struktur (Putih): {round(latest['struct_wave'], 1)}
    - Divergence Status: {div_label}

    Tugas: Bedah 4 gelombang ini menggunakan kacamata 'Aulyeah Predictive'.
    Berikan:
    1. Summary Teknis (Teknikal & Bandarmology).
    2. Support & Resistance (Angka numerik konkret).
    3. Trading Plan (Entry, TP1, TP2, SL) & R/R Ratio.
    4. Verdict (SUPER YAHUD / YAHUD / SKIP).
    """

    try:
        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Anda adalah Senior Technical Analyst Aulsome Screener. Wajib bicara angka spesifik dan percaya diri."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.4,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Gagal memanggil Groq: {str(e)}"

# ──────────────────────────────────────────────────────────────────────────────
# 4. UI & MAIN APP
# ──────────────────────────────────────────────────────────────────────────────

def main():
    st.sidebar.title("🔮 Aulsome Screener V3.9")
    market = st.sidebar.radio("Universe:", ["IHSG", "Crypto"])
    timeframe = st.sidebar.selectbox("Timeframe:", ["15m", "1h", "4h", "1d"], index=3)
    min_vol = st.sidebar.number_input("Min Vol (Mln)", 0.1, 5000.0, 10.0)
    
    tickers = sorted([t.strip() + (".JK" if market == "IHSG" else "-USD") for t in (IHSG_MEGA if market == "IHSG" else CRYPTO_MEGA).split()])

    st.title("🚀 Aulsome Screener — Predictive Matrix 🔮")
    tab_scan, tab_ai = st.tabs(["📊 Matrix Scan", "🧠 Deep Analysis AI"])

    if st.sidebar.button(f"🚀 RUN SCAN ({len(tickers)} ASSETS)", use_container_width=True):
        st.session_state["insight_cache"] = {}
        results = []
        progress = st.progress(0)
        
        def process_ticker(t):
            df_raw = fetch_data(t, timeframe)
            df = compute_matrix_waves(df_raw)
            if df is not None and len(df) >= 10:
                latest = df.iloc[-1]
                turnover = ((latest["Close"] * latest["Volume"]) / 1_000_000) if market == "Crypto" else (latest["Volume"] / 1_000_000)
                if turnover < min_vol: return None
                
                score = compute_wave_score(latest)
                div_label, _ = detect_divergence(latest)
                if score >= 2 or "DIVERGENCE" in div_label:
                    return {
                        "Asset": t.replace(".JK","").replace("-USD",""), "Price": round(float(latest["Close"]), 4),
                        "Bandar🟡": round(latest["vol_wave"], 1), "Trend🔵": round(latest["trend_wave"], 1),
                        "Dom🟣": round(latest["dom_wave"], 1), "Struct⚪": round(latest["struct_wave"], 1),
                        "Score": f"{score}/4", "Divergence": div_label
                    }
            return None

        with ThreadPoolExecutor(max_workers=20) as executor:
            scanned = 0
            for res in executor.map(process_ticker, tickers):
                scanned += 1
                if res: results.append(res)
                progress.progress(scanned / len(tickers))
        st.session_state["results"] = results

    with tab_scan:
        if st.session_state.get("results"):
            df_res = pd.DataFrame(st.session_state["results"])
            st.dataframe(df_res, use_container_width=True, hide_index=True)
        else: st.info("Scan market dulu di sidebar.")

    with tab_ai:
        if st.session_state.get("results"):
            res_data = st.session_state["results"]
            selected = st.selectbox("Pilih Aset:", [r["Asset"] for r in res_data])
            data = next(r for r in res_data if r["Asset"] == selected)
            
            col_chart, col_ai = st.columns([2, 1])
            with col_chart:
                df_raw = fetch_data(selected + (".JK" if market == "IHSG" else "-USD"), timeframe)
                df_p = compute_matrix_waves(df_raw)
                if df_p is not None:
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.5, 0.5])
                    fig.add_trace(go.Candlestick(x=df_p.index, open=df_p["Open"], high=df_p["High"], low=df_p["Low"], close=df_p["Close"], name="Price"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['vol_wave'], name="Bandar(Y)", line=dict(color='#FFD600')), row=2, col=1)
                    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['trend_wave'], name="Trend(B)", line=dict(color='#00BFFF')), row=2, col=1)
                    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['dom_wave'], name="Dom(P)", line=dict(color='#D500F9')), row=2, col=1)
                    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['struct_wave'], name="Struct(W)", line=dict(color='white')), row=2, col=1)
                    fig.update_layout(template="plotly_dark", height=700, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)

            with col_ai:
                st.subheader("🧠 Groq Convergence Analysis")
                if st.button("🪄 Get AI Insight", use_container_width=True):
                    with st.spinner("Analyzing..."):
                        insight = get_ai_insight(selected, data["Price"], df_p)
                        st.session_state["current_insight"] = insight
                        st.markdown(insight)
                
                if st.session_state.get("current_insight"):
                    st.download_button("📂 Download Notes", st.session_state["current_insight"], f"Analisis_{selected}.txt", use_container_width=True)
        else: st.warning("Scan market dulu.")

if __name__ == "__main__":
    main()

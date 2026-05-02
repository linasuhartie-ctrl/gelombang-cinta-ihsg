"""
================================================================================
 ULTRA MTF WAVE MATRIX (IHSG & CRYPTO)
 Logic   : White Line (Structure) & Purple Line (Dominance)
 Author  : Senior Quantitative Developer
 Features: Multi-Timeframe (15m, 1h, 4h, 1d), Golden/Death Cross
================================================================================
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# 0.  CONFIG & DATASET
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Ultra MTF Wave Matrix", page_icon="🔮", layout="wide")

IHSG_RAW = """
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

CRYPTO_RAW = """
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
FLOW MIR ANC ZEN RARE CLV ALPHA FIS CHESS QI GHST VOXEL BNX NMR VIB AST 
OAX DUSK LSK ARDR LOOM REQ AKRO POLS HARD STPT OOKI UNFI WING FOR 
BOND MOB MOVR SYN HIGH KP3R SNT MULTI GNS GMX WOO ZRX KNC LRC SUSHI 
BAKE JOE CAKE PORK BRETT BOME MEW MYRO WEN COQ
"""

# ──────────────────────────────────────────────────────────────────────────────
# 1.  CORE ENGINE (MTF SUPPORT)
# ──────────────────────────────────────────────────────────────────────────────

def pandas_wma(series, window):
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def compute_waves(df):
    if df is None or len(df) < 30: return None
    df = df.copy()
    rsi_raw = ta.momentum.rsi(df['Close'], window=14)
    df['purple_line'] = ((rsi_raw - 50) * 2).ewm(span=3, adjust=False).mean()
    hh, ll = df['High'].rolling(20).max(), df['Low'].rolling(20).min()
    diff = (hh - ll).replace(0, 0.001)
    df['white_line'] = pandas_wma(((df['Close'] - ll) / diff) * 200 - 100, 8)
    return df

@st.cache_data(ttl=300, show_spinner=False)
def fetch_mtf_data(ticker, timeframe):
    """Fetch and handle 4h resampling logic."""
    try:
        if timeframe == "15m":
            df = yf.download(ticker, period="7d", interval="15m", progress=False, auto_adjust=True)
        elif timeframe == "1h":
            df = yf.download(ticker, period="1mo", interval="1h", progress=False, auto_adjust=True)
        elif timeframe == "4h":
            # 4h requires resampling from 1h
            raw_1h = yf.download(ticker, period="2mo", interval="1h", progress=False, auto_adjust=True)
            if raw_1h.empty: return None
            df = raw_1h.resample('4H').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
            }).dropna()
        else: # 1d
            df = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
            
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

# ──────────────────────────────────────────────────────────────────────────────
# 2.  APP INTERFACE
# ──────────────────────────────────────────────────────────────────────────────

def main():
    st.sidebar.markdown("### 🗺️ Market Explorer")
    market = st.sidebar.radio("Universe:", ["IHSG", "Crypto Perps"])
    timeframe = st.sidebar.selectbox("Timeframe:", ["15m", "1h", "4h", "1d"], index=3)
    
    st.sidebar.divider()
    st.sidebar.header("⚙️ Strategy Filters")
    strategy = st.sidebar.selectbox(
        "Sinyal:", 
        ["Level Garis Putih", "Golden Cross (Putih ↗ Ungu)", "Death Cross (Putih ↘ Ungu)"]
    )
    
    if strategy == "Level Garis Putih":
        struct_range = st.sidebar.slider("Range White Line", -100, 100, (50, 100))
    
    vol_label = "Min Vol (Juta Unit)" if market == "IHSG" else "Min Daily Vol (Juta USD)"
    min_vol = st.sidebar.slider(vol_label, 1, 1000, 10 if market == "IHSG" else 50)

    # Ticker loading
    if market == "IHSG":
        tickers = sorted(list(set([t.strip() + ".JK" for t in IHSG_RAW.split()])))
    else:
        tickers = sorted(list(set([t.strip() + "-USD" for t in CRYPTO_RAW.split()])))

    if st.sidebar.button(f"🔍 Scan {len(tickers)} Assets ({timeframe})"):
        results = []
        progress = st.progress(0)
        
        with st.spinner(f"Analisis {timeframe} sedang berjalan..."):
            for i, t in enumerate(tickers):
                df_raw = fetch_mtf_data(t, timeframe)
                df = compute_waves(df_raw)
                
                if df is not None and len(df) >= 2:
                    latest, prev = df.iloc[-1], df.iloc[-2]
                    
                    # Volume Check
                    turnover = (latest['Close'] * latest['Volume']) / 1_000_000 if market == "Crypto Perps" else latest['Volume'] / 1_000_000
                    if turnover < min_vol: continue
                    
                    is_match = False
                    trigger_msg = ""
                    
                    if strategy == "Level Garis Putih":
                        if struct_range[0] <= latest['white_line'] <= struct_range[1]:
                            is_match = True
                            trigger_msg = f"Level: {latest['white_line']:.1f}"
                    elif strategy == "Golden Cross (Putih ↗ Ungu)":
                        if prev['white_line'] <= prev['purple_line'] and latest['white_line'] > latest['purple_line']:
                            is_match = True
                            trigger_msg = "Bullish Cross"
                    elif strategy == "Death Cross (Putih ↘ Ungu)":
                        if prev['white_line'] >= prev['purple_line'] and latest['white_line'] < latest['purple_line']:
                            is_match = True
                            trigger_msg = "Bearish Cross"
                    
                    if is_match:
                        results.append({
                            "Asset": t.replace(".JK", "").replace("-USD", ""),
                            "Price": f"{latest['Close']:,.2f}" if market == "IHSG" else f"${latest['Close']:,.4f}",
                            "White Wave": round(latest['white_line'], 2),
                            "Purple Wave": round(latest['purple_line'], 2),
                            "Signal": trigger_msg,
                            "Vol (M)": round(turnover, 2)
                        })
                progress.progress((i + 1) / len(tickers))

        if results:
            res_df = pd.DataFrame(results).sort_values("White Wave", ascending=False)
            st.success(f"🔥 {timeframe}: Ditemukan {len(res_df)} peluang!")
            
            def color_signal(val):
                if val == "Bullish Cross": return 'color: #26a69a; font-weight: bold'
                if val == "Bearish Cross": return 'color: #ef5350; font-weight: bold'
                return ''

            st.dataframe(res_df.style.map(color_signal, subset=['Signal']), use_container_width=True)
            
            st.divider()
            target = st.selectbox("Analisis Grafik MTF:", res_df['Asset'])
            if target:
                full_t = target + (".JK" if market == "IHSG" else "-USD")
                df_p = compute_waves(fetch_mtf_data(full_t, timeframe))
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4], vertical_spacing=0.05)
                fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Price"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p['white_line'], name="White Line", line=dict(color='white', width=2)), row=2, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p['purple_line'], name="Purple Line", line=dict(color='#D500F9', width=1.5)), row=2, col=1)
                for l, c in [(80, 'red'), (0, 'gray'), (-80, 'green')]: fig.add_hline(y=l, line_dash="dash", line_color=c, opacity=0.3, row=2, col=1)
                
                fig.update_layout(template="plotly_dark", height=800, xaxis_rangeslider_visible=False, title=f"{target} - {timeframe}")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"Belum ada aset {market} yang memenuhi kriteria di timeframe {timeframe}.")

if __name__ == "__main__":
    main()

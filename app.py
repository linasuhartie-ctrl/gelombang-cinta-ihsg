import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# 0. API & CONFIG
# ──────────────────────────────────────────────────────────────────────────────
# Menggunakan API Key dari screenshot Anda
GEMINI_API_KEY = st.secrets["GEMINI_KEY"]

genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="Aulsome Screener", page_icon="🔮", layout="wide")

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
# 1. CORE LOGIC
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
    struct_raw = ((df['Close'] - ll) / diff) * 200 - 100
    df['white_line'] = pandas_wma(struct_raw, 8)
    return df

def detect_patterns(df):
    if df is None or len(df) < 6: return "Neutral"
    c1, c2, c3, c4, c5 = [df.iloc[-i] for i in range(5, 0, -1)]
    body5 = abs(c5['Close'] - c5['Open'])
    l_shadow5 = min(c5['Close'], c5['Open']) - c5['Low']
    u_shadow5 = c5['High'] - max(c5['Close'], c5['Open'])

    # Bullish Mat Hold[span_0](start_span)[span_0](end_span)
    if (c1['Close'] > c1['Open']) and (c2['Open'] > c1['Close']) and \
       (c2['Close'] < c2['Open']) and (min(c2['Low'], c3['Low'], c4['Low']) > c1['Low']) and \
       (c5['Close'] > c5['Open']) and (c5['Close'] > c2['High']):
        return "Bullish Mat Hold"
    
    # Morning Star[span_1](start_span)[span_1](end_span)
    if (c3['Close'] < c3['Open']) and (abs(c4['Close'] - c4['Open']) < abs(c3['Close'] - c3['Open']) * 0.3) and \
       (c5['Close'] > c5['Open']) and (c5['Close'] > (c3['Open'] + c3['Close'])/2):
        return "Morning Star"
        
    # Bullish Engulfing[span_2](start_span)[span_2](end_span)
    if (c4['Close'] < c4['Open']) and (c5['Close'] > c5['Open']) and \
       (c5['Open'] <= c4['Close']) and (c5['Close'] >= c4['Open']):
        return "Bullish Engulfing"
        
    # Hammer[span_3](start_span)[span_3](end_span)
    if (l_shadow5 >= 2 * body5) and (u_shadow5 <= 0.2 * body5) and (body5 > 0):
        return "Hammer"

    return "Neutral"

@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(ticker, timeframe):
    try:
        if timeframe == "15m": p, i = "5d", "15m"
        elif timeframe == "1h": p, i = "1mo", "1h"
        elif timeframe == "4h": p, i = "2mo", "1h"
        else: p, i = "1y", "1d"
        df = yf.download(ticker, period=p, interval=i, progress=False, auto_adjust=True)
        if df.empty: return None
        if timeframe == "4h":
            df = df.resample('4H').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

def get_ai_insight(asset, pattern, white, vol, quality, price):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Analisis aset {asset}. 
        Harga: {price}, Pola: {pattern}, White Wave: {white}, Vol Spike: {vol}x, Quality: {quality}.
        Berikan insight teknikal singkat mengapa ini menarik atau berisiko.
        Gunakan gaya bahasa profesional 'Aulsome Screener'.
        """
        return model.generate_content(prompt).text
    except Exception as e: return f"Error AI: {str(e)}"

# ──────────────────────────────────────────────────────────────────────────────
# 2. UI & APP
# ──────────────────────────────────────────────────────────────────────────────

def main():
    st.sidebar.title("🔮 Aulsome Screener V3.1")
    market = st.sidebar.radio("Market:", ["IHSG", "Crypto"])
    timeframe = st.sidebar.selectbox("Timeframe:", ["15m", "1h", "4h", "1d"], index=3)
    mode = st.sidebar.selectbox("Mode:", ["Wave Matrix", "Candlestick Pattern"])
    
    if mode == "Wave Matrix":
        strategy = st.sidebar.selectbox("Signal:", ["Level Garis Putih", "Golden Cross", "Death Cross"])
    else:
        strategy = st.sidebar.selectbox("Pattern:", ["Bullish Mat Hold", "Morning Star", "Bullish Engulfing", "Hammer"])

    min_vol = st.sidebar.number_input("Min Volume (Mln)", 0.1, 5000.0, 10.0)
    
    tickers = sorted([t.strip() + (".JK" if market == "IHSG" else "-USD") for t in (IHSG_MEGA if market == "IHSG" else CRYPTO_MEGA).split()])

    st.title("🚀 Aulsome Screener — Machine Analytics")
    tab_scan, tab_ai = st.tabs(["📊 Scan Market", "🧠 Deep Analysis & AI"])

    if st.sidebar.button(f"RUN SCAN ({len(tickers)} ASSETS)", use_container_width=True):
        results = []
        progress = st.progress(0)
        
        def process_ticker(t):
            df = compute_waves(fetch_data(t, timeframe))
            if df is not None and len(df) >= 10:
                latest, prev = df.iloc[-1], df.iloc[-2]
                turnover = (latest['Close'] * latest['Volume']) / 1_000_000 if market == "Crypto" else latest['Volume'] / 1_000_000
                if turnover < min_vol: return None
                
                avg_vol = df['Volume'].iloc[-6:-1].mean()
                vol_ratio = latest['Volume'] / avg_vol if avg_vol > 0 else 1.0
                
                match = False
                p = detect_patterns(df)
                if mode == "Wave Matrix":
                    if strategy == "Level Garis Putih" and (50 <= latest['white_line'] <= 100): match = True
                    elif strategy == "Golden Cross" and prev['white_line'] <= prev['purple_line'] and latest['white_line'] > latest['purple_line']: match = True
                else:
                    if p == strategy: match = True
                
                if match:
                    quality = "✅ YAHUD"
                    if vol_ratio > 1.5 and latest['white_line'] < -60: quality = "🔥 SUPER YAHUD"
                    return {"Asset": t.split('.')[0] if market == "IHSG" else t.split('-')[0], "Price": round(latest['Close'], 2), "Pattern": p, "White": round(latest['white_line'], 1), "Vol Spike": round(vol_ratio, 2), "Quality": quality}
            return None

        with ThreadPoolExecutor(max_workers=20) as executor:
            scanned = 0
            for res in executor.map(process_ticker, tickers):
                scanned += 1
                if res: results.append(res)
                progress.progress(scanned / len(tickers))
        
        st.session_state['results'] = results

    with tab_scan:
        if 'results' in st.session_state and st.session_state['results']:
            st.dataframe(pd.DataFrame(st.session_state['results']), use_container_width=True, hide_index=True)
        else: st.info("Klik Run Scan di sidebar.")

    with tab_ai:
        if 'results' in st.session_state and st.session_state['results']:
            selected = st.selectbox("Pilih Aset:", [r['Asset'] for r in st.session_state['results']])
            data = next(i for i in st.session_state['results'] if i['Asset'] == selected)
            
            col_ch, col_ai = st.columns([2, 1])
            with col_ch:
                t_full = selected + (".JK" if market == "IHSG" else "-USD")
                df_p = compute_waves(fetch_data(t_full, timeframe))
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4])
                fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Price"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p['white_line'], name="White Wave", line=dict(color='white')), row=2, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p['purple_line'], name="Purple Wave", line=dict(color='purple')), row=2, col=1)
                fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_ai:
                if st.button("🪄 Get AI Insight"):
                    with st.spinner("Analyzing..."):
                        st.markdown(get_ai_insight(selected, data['Pattern'], data['White'], data['Vol Spike'], data['Quality'], data['Price']))
        else: st.warning("Scan market dulu.")

if __name__ == "__main__":
    main()

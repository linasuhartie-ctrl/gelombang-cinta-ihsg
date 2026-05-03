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
# 0. CONFIG & DATASET
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="MHALIK Mega Screener", page_icon="🔮", layout="wide")

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
# 1. ENGINES (MTF, WAVE, & CANDLESTICK)
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
    """Mendeteksi pola candlestick sesuai kriteria Kitab[span_3](start_span)[span_3](end_span)."""
    if df is None or len(df) < 6: return "Neutral"
    
    # Ambil 5 data terakhir untuk Mat Hold
    c1, c2, c3, c4, c5 = [df.iloc[-i] for i in range(5, 0, -1)]
    
    # Perhitungan Komponen Candle Terakhir
    body = abs(c5['Close'] - c5['Open'])
    lower_shadow = min(c5['Close'], c5['Open']) - c5['Low']
    upper_shadow = c5['High'] - max(c5['Close'], c5['Open'])
    
    # 1. BULLISH MAT HOLD (Probabilitas UP: 78%)[span_4](start_span)[span_4](end_span)
    # C1: Long White, C2: Gap Up, C2-C4: Small & Decline, C5: Closes above C2 high
    if (c1['Close'] > c1['Open']) and \
       (c2['Open'] > c1['Close']) and \
       (c2['Close'] < c2['Open']) and \
       (min(c2['Low'], c3['Low'], c4['Low']) > c1['Low']) and \
       (c5['Close'] > c5['Open']) and (c5['Close'] > c2['High']):
        return "Bullish Mat Hold"

    # 2. BULLISH ENGULFING[span_5](start_span)[span_5](end_span)
    if (c4['Close'] < c4['Open']) and (c5['Close'] > c5['Open']) and \
       (c5['Open'] <= c4['Close']) and (c5['Close'] >= c4['Open']):
        return "Bullish Engulfing"

    # 3. HAMMER[span_6](start_span)[span_6](end_span)
    if (lower_shadow >= 2 * body) and (upper_shadow <= 0.1 * body) and (body > 0):
        return "Hammer"

    # 4. MORNING STAR[span_7](start_span)[span_7](end_span)
    if (c3['Close'] < c3['Open']) and \
       (abs(c4['Close'] - c4['Open']) < abs(c3['Close'] - c3['Open']) * 0.3) and \
       (c5['Close'] > c5['Open']) and (c5['Close'] > (c3['Open'] + c3['Close'])/2):
        return "Morning Star"

    return "Neutral"

@st.cache_data(ttl=300, show_spinner=False)
def fetch_mtf_data(ticker, timeframe):
    try:
        if timeframe == "15m": df = yf.download(ticker, period="7d", interval="15m", progress=False, auto_adjust=True)
        elif timeframe == "1h": df = yf.download(ticker, period="1mo", interval="1h", progress=False, auto_adjust=True)
        elif timeframe == "4h":
            raw_1h = yf.download(ticker, period="2mo", interval="1h", progress=False, auto_adjust=True)
            df = raw_1h.resample('4H').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
        else: df = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
        
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

# ──────────────────────────────────────────────────────────────────────────────
# 2. APP UI & SCANNING LOGIC
# ──────────────────────────────────────────────────────────────────────────────

def main():
    st.sidebar.title("🔮 MHALIK MEGA")
    market = st.sidebar.radio("Market Universe:", ["IHSG (Mega List)", "Crypto Perps"])
    timeframe = st.sidebar.selectbox("Timeframe:", ["15m", "1h", "4h", "1d"], index=3)
    
    st.sidebar.divider()
    mode = st.sidebar.selectbox("Kategori Scan:", ["Wave Matrix", "Candlestick Pattern"])
    
    if mode == "Wave Matrix":
        strategy = st.sidebar.selectbox("Sinyal Wave:", ["Level Garis Putih", "Golden Cross", "Death Cross"])
        if strategy == "Level Garis Putih":
            struct_range = st.sidebar.slider("Range White Line", -100, 100, (50, 100))
    else:
        strategy = st.sidebar.selectbox("Pilih Pola:", ["Bullish Mat Hold", "Bullish Engulfing", "Hammer", "Morning Star"])

    min_vol = st.sidebar.slider("Min Vol (Mln)", 1, 1000, 10)

    # Ticker Prep
    if "IHSG" in market: tickers = sorted(list(set([t.strip() + ".JK" for t in IHSG_MEGA.split()])))
    else: tickers = sorted(list(set([t.strip() + "-USD" for t in CRYPTO_MEGA.split()])))

    if st.sidebar.button(f"🔍 SCAN {len(tickers)} ASSETS"):
        results = []
        progress_bar = st.progress(0)
        
        for i, t in enumerate(tickers):
            df_raw = fetch_mtf_data(t, timeframe)
            df = compute_waves(df_raw)
            
            if df is not None and len(df) >= 6:
                latest, prev = df.iloc[-1], df.iloc[-2]
                turnover = (latest['Close'] * latest['Volume']) / 1_000_000 if "Crypto" in market else latest['Volume'] / 1_000_000
                if turnover < min_vol: continue
                
                is_match = False
                if mode == "Wave Matrix":
                    if strategy == "Level Garis Putih":
                        if struct_range[0] <= latest['white_line'] <= struct_range[1]: is_match = True
                    elif strategy == "Golden Cross":
                        if prev['white_line'] <= prev['purple_line'] and latest['white_line'] > latest['purple_line']: is_match = True
                    elif strategy == "Death Cross":
                        if prev['white_line'] >= prev['purple_line'] and latest['white_line'] < latest['purple_line']: is_match = True
                else:
                    pattern = detect_patterns(df)
                    if pattern == strategy: is_match = True
                
                if is_match:
                    results.append({
                        "Asset": t.replace(".JK", "").replace("-USD", ""),
                        "Price": f"{latest['Close']:,.2f}",
                        "White Wave": round(latest['white_line'], 2),
                        "Signal": strategy if mode == "Wave Matrix" else detect_patterns(df),
                        "Vol (M)": round(turnover, 2)
                    })
            progress_bar.progress((i + 1) / len(tickers))

        if results:
            st.success(f"Ditemukan {len(results)} Sinyal!")
            st.dataframe(pd.DataFrame(results), use_container_width=True)
            
            # Detil Chart
            st.divider()
            target = st.selectbox("Analisis Detail:", [r['Asset'] for r in results])
            full_t = target + (".JK" if "IHSG" in market else "-USD")
            df_p = compute_waves(fetch_mtf_data(full_t, timeframe))
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4], vertical_spacing=0.05)
            fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Price"), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_p.index, y=df_p['white_line'], name="White (Structure)", line=dict(color='white', width=2)), row=2, col=1)
            fig.add_trace(go.Scatter(x=df_p.index, y=df_p['purple_line'], name="Purple (Dominance)", line=dict(color='#D500F9', width=1.5)), row=2, col=1)
            for l, c in [(80, 'red'), (0, 'gray'), (-80, 'green')]: fig.add_hline(y=l, line_dash="dash", line_color=c, opacity=0.3, row=2, col=1)
            fig.update_layout(template="plotly_dark", height=700, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Zonk! Tidak ada yang cocok kriteria.")

if __name__ == "__main__":
    main()

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings(“ignore”)

# ──────────────────────────────────────────────────────────────────────────────

# 0. CONFIG & DATASET

# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title=“MHALIK Mega Screener”, page_icon=“🔮”, layout=“wide”)

IHSG_MEGA = “””
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
“””

CRYPTO_MEGA = “””
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
“””

# ──────────────────────────────────────────────────────────────────────────────

# 1. HELPER CANDLE FUNCTIONS

# ──────────────────────────────────────────────────────────────────────────────

def body_size(c):
return abs(c[‘Close’] - c[‘Open’])

def upper_shadow(c):
return c[‘High’] - max(c[‘Close’], c[‘Open’])

def lower_shadow(c):
return min(c[‘Close’], c[‘Open’]) - c[‘Low’]

def candle_range(c):
return c[‘High’] - c[‘Low’]

def is_bullish(c):
return c[‘Close’] > c[‘Open’]

def is_bearish(c):
return c[‘Close’] < c[‘Open’]

# ──────────────────────────────────────────────────────────────────────────────

# 2. ENGINES (MTF, WAVE, & CANDLESTICK)

# ──────────────────────────────────────────────────────────────────────────────

def pandas_wma(series, window):
weights = np.arange(1, window + 1)
return series.rolling(window).apply(
lambda x: np.dot(x, weights) / weights.sum(), raw=True
)

def compute_waves(df):
if df is None or len(df) < 30:
return None
df = df.copy()
rsi_raw = ta.momentum.rsi(df[‘Close’], window=14)
df[‘purple_line’] = ((rsi_raw - 50) * 2).ewm(span=3, adjust=False).mean()
hh = df[‘High’].rolling(20).max()
ll = df[‘Low’].rolling(20).min()
diff = (hh - ll).replace(0, 0.001)
struct_raw = ((df[‘Close’] - ll) / diff) * 200 - 100
df[‘white_line’] = pandas_wma(struct_raw, 8)
return df

def detect_patterns(df):
“””
Deteksi pola candlestick dengan validasi teknikal yang lebih ketat.
Menggunakan 5 candle terakhir (c1=paling lama, c5=terbaru).
Urutan pengecekan: dari pola paling kompleks ke paling sederhana.
“””
if df is None or len(df) < 6:
return “Neutral”

```
# Ambil 5 candle terakhir: c1 paling lama, c5 paling baru
c1, c2, c3, c4, c5 = [df.iloc[-i] for i in range(5, 0, -1)]

# Komponen candle terakhir
body5  = body_size(c5)
upper5 = upper_shadow(c5)
lower5 = lower_shadow(c5)
range5 = candle_range(c5)

# Safeguard: hindari pembagian nol
if range5 == 0 or body5 == 0:
    return "Neutral"

# ──────────────────────────────────────────────────────────────
# 1. BULLISH MAT HOLD (Probabilitas UP: ~78%)
# Kriteria:
#   C1 : Bullish besar — body >= 60% range
#   C2 : Gap up dari C1.Close → bearish (reaksi jual)
#   C3,C4: Bearish kecil berurutan (retracement halus)
#          Low-nya tetap di atas Low C1 (struktur bullish terjaga)
#   C5 : Bullish kuat — close menembus di atas High C2
# ──────────────────────────────────────────────────────────────
if (
    is_bullish(c1) and body_size(c1) >= 0.6 * candle_range(c1)
    and c2['Open'] > c1['Close']                            # gap up
    and is_bearish(c2)
    and is_bearish(c3) and body_size(c3) < body_size(c1)
    and is_bearish(c4) and body_size(c4) < body_size(c1)
    and c3['Close'] < c2['Close']                           # C3 turun dari C2
    and c4['Close'] < c3['Close']                           # C4 turun dari C3
    and min(c2['Low'], c3['Low'], c4['Low']) > c1['Low']    # retracement di atas Low C1
    and is_bullish(c5)
    and c5['Close'] > c2['High']                            # breakout atas High C2
):
    return "Bullish Mat Hold"

# ──────────────────────────────────────────────────────────────
# 2. MORNING STAR (3-candle reversal paling reliable)
# Pakai C3, C4, C5:
#   C3 : Bearish besar — body >= 50% range (konfirmasi downtrend)
#   C4 : "Bintang" — body sangat kecil (<= 30% body C3), open < close C3
#   C5 : Bullish solid — close masuk di atas midpoint body C3
# ──────────────────────────────────────────────────────────────
mid_c3 = (c3['Open'] + c3['Close']) / 2
if (
    is_bearish(c3) and body_size(c3) >= 0.5 * candle_range(c3)
    and body_size(c4) <= 0.3 * body_size(c3)               # bintang kecil
    and c4['Open'] < c3['Close']                            # buka di area low C3
    and is_bullish(c5)
    and c5['Close'] > mid_c3                                # menembus 50% C3
    and body5 >= 0.5 * range5                               # C5 harus solid bullish
):
    return "Morning Star"

# ──────────────────────────────────────────────────────────────
# 3. BULLISH ENGULFING
# Kriteria:
#   C4 : Bearish (prior candle)
#   C5 : Bullish — open <= close C4, close >= open C4
#         Body C5 LEBIH BESAR dari body C4 (genuine engulfing)
# ──────────────────────────────────────────────────────────────
if (
    is_bearish(c4)
    and is_bullish(c5)
    and c5['Open'] <= c4['Close']
    and c5['Close'] >= c4['Open']
    and body5 > body_size(c4)                               # engulfing sejati
):
    return "Bullish Engulfing"

# ──────────────────────────────────────────────────────────────
# 4. BEARISH ENGULFING
# Kriteria:
#   C4 : Bullish (prior candle)
#   C5 : Bearish — open >= close C4, close <= open C4
#         Body C5 LEBIH BESAR dari body C4
# ──────────────────────────────────────────────────────────────
if (
    is_bullish(c4)
    and is_bearish(c5)
    and c5['Open'] >= c4['Close']
    and c5['Close'] <= c4['Open']
    and body5 > body_size(c4)
):
    return "Bearish Engulfing"

# ──────────────────────────────────────────────────────────────
# 5. HAMMER (reversal bullish setelah downtrend)
# Kriteria:
#   - Ekor bawah panjang  : lower shadow >= 2x body
#   - Ekor atas kecil     : upper shadow <= 0.3x body (longgar)
#   - Body kecil relatif  : body <= 40% range
#   - Konteks downtrend   : close C5 < close C3
# ──────────────────────────────────────────────────────────────
if (
    lower5 >= 2.0 * body5
    and upper5 <= 0.3 * body5
    and body5 <= 0.4 * range5
    and c5['Close'] < c3['Close']                           # konfirmasi downtrend
):
    return "Hammer"

# ──────────────────────────────────────────────────────────────
# 6. SHOOTING STAR (reversal bearish setelah uptrend)
# Kriteria:
#   - Ekor atas panjang   : upper shadow >= 2x body
#   - Ekor bawah kecil    : lower shadow <= 0.3x body
#   - Body kecil relatif  : body <= 40% range
#   - Konteks uptrend     : close C5 > close C3
# ──────────────────────────────────────────────────────────────
if (
    upper5 >= 2.0 * body5
    and lower5 <= 0.3 * body5
    and body5 <= 0.4 * range5
    and c5['Close'] > c3['Close']                           # konfirmasi uptrend
):
    return "Shooting Star"

# ──────────────────────────────────────────────────────────────
# 7. DOJI (ketidakpastian / konsolidasi)
# Kriteria: body sangat kecil <= 5% dari total range
# ──────────────────────────────────────────────────────────────
if body5 <= 0.05 * range5:
    return "Doji"

return "Neutral"
```

# Label arah sinyal untuk ditampilkan di kolom tabel

PATTERN_DIRECTION = {
“Bullish Mat Hold”  : “🟢 Bullish”,
“Morning Star”      : “🟢 Bullish”,
“Bullish Engulfing” : “🟢 Bullish”,
“Hammer”            : “🟢 Bullish”,
“Bearish Engulfing” : “🔴 Bearish”,
“Shooting Star”     : “🔴 Bearish”,
“Doji”              : “🟡 Neutral”,
“Neutral”           : “⚪ Neutral”,
}

ALL_PATTERNS = [
“Bullish Mat Hold”,
“Morning Star”,
“Bullish Engulfing”,
“Hammer”,
“Bearish Engulfing”,
“Shooting Star”,
“Doji”,
]

@st.cache_data(ttl=300, show_spinner=False)
def fetch_mtf_data(ticker, timeframe):
try:
if timeframe == “15m”:
df = yf.download(ticker, period=“7d”, interval=“15m”,
progress=False, auto_adjust=True)
elif timeframe == “1h”:
df = yf.download(ticker, period=“1mo”, interval=“1h”,
progress=False, auto_adjust=True)
elif timeframe == “4h”:
raw_1h = yf.download(ticker, period=“2mo”, interval=“1h”,
progress=False, auto_adjust=True)
df = raw_1h.resample(‘4h’).agg(
{‘Open’: ‘first’, ‘High’: ‘max’, ‘Low’: ‘min’,
‘Close’: ‘last’, ‘Volume’: ‘sum’}
).dropna()
else:
df = yf.download(ticker, period=“6mo”, interval=“1d”,
progress=False, auto_adjust=True)

```
    if df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df
except Exception:
    return None
```

# ──────────────────────────────────────────────────────────────────────────────

# 3. APP UI & SCANNING LOGIC

# ──────────────────────────────────────────────────────────────────────────────

def main():
st.sidebar.title(“🔮 MHALIK MEGA”)
market    = st.sidebar.radio(“Market Universe:”, [“IHSG (Mega List)”, “Crypto Perps”])
timeframe = st.sidebar.selectbox(“Timeframe:”, [“15m”, “1h”, “4h”, “1d”], index=3)

```
st.sidebar.divider()
mode = st.sidebar.selectbox("Kategori Scan:", ["Wave Matrix", "Candlestick Pattern"])

strategy      = None
struct_range  = None

if mode == "Wave Matrix":
    strategy = st.sidebar.selectbox(
        "Sinyal Wave:",
        ["Level Garis Putih", "Golden Cross", "Death Cross"]
    )
    if strategy == "Level Garis Putih":
        struct_range = st.sidebar.slider("Range White Line", -100, 100, (50, 100))
else:
    strategy = st.sidebar.selectbox("Pilih Pola:", ALL_PATTERNS)
    # Tampilkan keterangan pola yang dipilih
    direction = PATTERN_DIRECTION.get(strategy, "")
    st.sidebar.caption(f"Arah sinyal: **{direction}**")

min_vol = st.sidebar.slider("Min Vol (Mln)", 1, 1000, 10)

# ── Ticker preparation ──────────────────────────────────────────────────
if "IHSG" in market:
    tickers = sorted(list(set([t.strip() + ".JK"  for t in IHSG_MEGA.split()])))
    suffix  = ".JK"
    is_crypto = False
else:
    tickers = sorted(list(set([t.strip() + "-USD" for t in CRYPTO_MEGA.split()])))
    suffix  = "-USD"
    is_crypto = True

# ── Main header ─────────────────────────────────────────────────────────
st.title("🔮 MHALIK Mega Screener")
col1, col2, col3 = st.columns(3)
col1.metric("Universe", f"{len(tickers)} Assets")
col2.metric("Market", "IHSG" if not is_crypto else "Crypto")
col3.metric("Timeframe", timeframe)

if st.sidebar.button(f"🔍 SCAN {len(tickers)} ASSETS", use_container_width=True):
    results      = []
    progress_bar = st.progress(0)
    status_txt   = st.empty()

    for i, t in enumerate(tickers):
        status_txt.text(f"Scanning {t} ... ({i+1}/{len(tickers)})")
        df_raw = fetch_mtf_data(t, timeframe)
        df     = compute_waves(df_raw)

        if df is not None and len(df) >= 6:
            latest  = df.iloc[-1]
            prev    = df.iloc[-2]

            # Volume / turnover filter
            if is_crypto:
                turnover = (latest['Close'] * latest['Volume']) / 1_000_000
            else:
                turnover = latest['Volume'] / 1_000_000

            if turnover < min_vol:
                progress_bar.progress((i + 1) / len(tickers))
                continue

            is_match = False

            if mode == "Wave Matrix":
                if strategy == "Level Garis Putih":
                    if struct_range[0] <= latest['white_line'] <= struct_range[1]:
                        is_match = True
                elif strategy == "Golden Cross":
                    if (prev['white_line'] <= prev['purple_line'] and
                            latest['white_line'] > latest['purple_line']):
                        is_match = True
                elif strategy == "Death Cross":
                    if (prev['white_line'] >= prev['purple_line'] and
                            latest['white_line'] < latest['purple_line']):
                        is_match = True
            else:
                detected = detect_patterns(df)
                if detected == strategy:
                    is_match = True

            if is_match:
                clean_name = t.replace(".JK", "").replace("-USD", "")
                pattern    = strategy if mode == "Candlestick Pattern" else "-"
                direction  = PATTERN_DIRECTION.get(pattern, "-")

                results.append({
                    "Asset"       : clean_name,
                    "Price"       : f"{latest['Close']:,.4f}" if is_crypto else f"{latest['Close']:,.0f}",
                    "White Wave"  : round(latest['white_line'], 2),
                    "Purple Wave" : round(latest['purple_line'], 2),
                    "Signal"      : strategy,
                    "Arah"        : direction if mode == "Candlestick Pattern" else "-",
                    "Vol (M)"     : round(turnover, 2),
                })

        progress_bar.progress((i + 1) / len(tickers))

    status_txt.empty()
    progress_bar.empty()

    # ── Results ─────────────────────────────────────────────────────────
    if results:
        st.success(f"✅ Ditemukan **{len(results)}** sinyal untuk **{strategy}**!")
        df_result = pd.DataFrame(results)
        st.dataframe(df_result, use_container_width=True, hide_index=True)

        # Download CSV
        csv = df_result.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Hasil (.csv)",
            data=csv,
            file_name=f"mhalik_{strategy.replace(' ', '_').lower()}_{timeframe}.csv",
            mime="text/csv",
        )

        # ── Detail Chart ─────────────────────────────────────────────
        st.divider()
        st.subheader("📊 Analisis Detail")
        target = st.selectbox("Pilih Asset:", [r['Asset'] for r in results])
        full_t = target + suffix
        df_p   = compute_waves(fetch_mtf_data(full_t, timeframe))

        if df_p is not None and len(df_p) >= 6:
            detected_pattern = detect_patterns(df_p)

            info_col1, info_col2, info_col3, info_col4 = st.columns(4)
            info_col1.metric("Asset",       target)
            info_col2.metric("Pola Terdeteksi", detected_pattern)
            info_col3.metric("White Wave",  round(df_p.iloc[-1]['white_line'], 2))
            info_col4.metric("Purple Wave", round(df_p.iloc[-1]['purple_line'], 2))

            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                row_heights=[0.6, 0.4],
                vertical_spacing=0.05,
                subplot_titles=(f"{target} — Price Action", "Wave Oscillator")
            )

            # Candlestick
            fig.add_trace(go.Candlestick(
                x=df_p.index,
                open=df_p['Open'], high=df_p['High'],
                low=df_p['Low'],   close=df_p['Close'],
                name="Price",
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350',
            ), row=1, col=1)

            # Wave lines
            fig.add_trace(go.Scatter(
                x=df_p.index, y=df_p['white_line'],
                name="White (Structure)",
                line=dict(color='white', width=2)
            ), row=2, col=1)

            fig.add_trace(go.Scatter(
                x=df_p.index, y=df_p['purple_line'],
                name="Purple (Dominance)",
                line=dict(color='#D500F9', width=1.5)
            ), row=2, col=1)

            # Hlines
            for level, color in [(80, 'red'), (0, 'gray'), (-80, 'green')]:
                fig.add_hline(
                    y=level, line_dash="dash", line_color=color,
                    opacity=0.4, row=2, col=1
                )

            # Highlight candle terakhir
            last_idx = df_p.index[-1]
            fig.add_vline(
                x=last_idx, line_dash="dot",
                line_color="yellow", opacity=0.5
            )

            fig.update_layout(
                template="plotly_dark",
                height=720,
                xaxis_rangeslider_visible=False,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                margin=dict(l=10, r=10, t=40, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Candlestick explanation
            st.divider()
            st.subheader("📖 Penjelasan Pola")
            explanations = {
                "Bullish Mat Hold"  : "**Bullish Mat Hold** — Pola 5-candle continuation bullish. C1 candle putih besar, diikuti gap up lalu retracement kecil (C2–C4), kemudian C5 breakout kuat di atas High C2. Probabilitas kelanjutan naik sekitar 78%.",
                "Morning Star"      : "**Morning Star** — Pola reversal bullish 3-candle. C3 bearish besar, C4 bintang kecil (ketidakpastian), C5 bullish solid menembus lebih dari 50% body C3. Sinyal pembalikan arah dari downtrend.",
                "Bullish Engulfing" : "**Bullish Engulfing** — C4 bearish sepenuhnya ditelan oleh C5 bullish yang lebih besar. Body C5 harus lebih lebar dari body C4. Sinyal reversal atau akselerasi naik.",
                "Hammer"            : "**Hammer** — Candle dengan ekor bawah panjang (≥2× body) dan ekor atas minimal. Muncul setelah downtrend. Menunjukkan penolakan harga rendah dan potensi pembalikan naik.",
                "Bearish Engulfing" : "**Bearish Engulfing** — Kebalikan Bullish Engulfing. C5 bearish menelan seluruh body C4 bullish. Sinyal reversal atau akselerasi turun.",
                "Shooting Star"     : "**Shooting Star** — Candle dengan ekor atas panjang (≥2× body) dan ekor bawah minimal. Muncul setelah uptrend. Menunjukkan penolakan harga tinggi dan potensi pembalikan turun.",
                "Doji"              : "**Doji** — Open dan Close hampir sama (body ≤5% range). Mencerminkan keseimbangan kekuatan jual-beli. Sinyal konsolidasi atau potensi pembalikan arah tergantung konteks.",
            }
            st.info(explanations.get(detected_pattern, "Tidak ada pola signifikan pada candle terakhir."))
        else:
            st.warning("Data tidak cukup untuk menampilkan chart.")
    else:
        st.warning("⚠️ Zonk! Tidak ada aset yang cocok dengan kriteria yang dipilih.")
        st.info("💡 Tips: Coba longgarkan filter volume, ganti timeframe, atau pilih pola lain.")
```

if **name** == “**main**”:
main()
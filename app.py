"""
================================================================================
 UNIFIED PREDICTIVE WAVE MATRIX (IHSG & CRYPTO)
 Logic   : White Line (Structure) & Purple Line (Dominance)
 Author  : Senior Quantitative Developer
 Stack   : Streamlit · yfinance · ta · Plotly
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
st.set_page_config(page_title="Multi-Market Wave Matrix", page_icon="🔮", layout="wide")

IHSG_TICKERS = """
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

CRYPTO_TICKERS = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD", "DOGE-USD",
    "AVAX-USD", "DOT-USD", "MATIC-USD", "LINK-USD", "SHIB-USD", "LTC-USD", "NEAR-USD",
    "UNI-USD", "APT-USD", "ARB-USD", "OP-USD", "TIA-USD", "SUI-USD", "FET-USD"
]

# ──────────────────────────────────────────────────────────────────────────────
# 1.  HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def pandas_wma(series, window):
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def compute_waves(df):
    df = df.copy()
    # Purple Line (Dominance)
    rsi_raw = ta.momentum.rsi(df['Close'], window=14)
    df['purple_line'] = ((rsi_raw - 50) * 2).ewm(span=3, adjust=False).mean()
    # White Line (Structure)
    hh = df['High'].rolling(20).max()
    ll = df['Low'].rolling(20).min()
    diff = (hh - ll).replace(0, 0.001)
    df['white_line'] = pandas_wma(((df['Close'] - ll) / diff) * 200 - 100, 8)
    return df

@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 30: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

# ──────────────────────────────────────────────────────────────────────────────
# 2.  APP UI
# ──────────────────────────────────────────────────────────────────────────────

def main():
    st.sidebar.header("🗺️ Market Selection")
    market = st.sidebar.radio("Pilih Market:", ["IHSG", "Crypto"])
    
    st.sidebar.divider()
    st.sidebar.header("⚙️ Matrix Filters")
    strategy = st.sidebar.selectbox("Strategi:", ["Level Garis Putih", "Crossing (Putih ↗ Ungu)"])
    
    if strategy == "Level Garis Putih":
        struct_range = st.sidebar.slider("Range White Line", -100, 100, (50, 100))
    
    # Penyesuaian label volume berdasarkan market
    vol_label = "Min Vol (Juta Lembar)" if market == "IHSG" else "Min Daily Turnover (Juta USD)"
    min_vol = st.sidebar.slider(vol_label, 1, 1000, 50 if market == "Crypto" else 10)

    # Penentuan ticker list berdasarkan market
    if market == "IHSG":
        tickers = sorted(list(dict.fromkeys([t.strip() + ".JK" for t in IHSG_TICKERS.split()])))
    else:
        tickers = CRYPTO_TICKERS

    if st.sidebar.button(f"🚀 Scan {market}"):
        results = []
        progress = st.progress(0)
        
        with st.spinner(f"Menganalisis {market}..."):
            for i, t in enumerate(tickers):
                df = fetch_data(t)
                if df is not None:
                    df = compute_waves(df)
                    if len(df) < 2: continue
                    latest, prev = df.iloc[-1], df.iloc[-2]
                    
                    # Volume Check
                    turnover = (latest['Close'] * latest['Volume']) / 1_000_000 if market == "Crypto" else latest['Volume'] / 1_000_000
                    if turnover < min_vol: continue
                    
                    # Logic
                    is_match = False
                    if strategy == "Level Garis Putih":
                        if struct_range[0] <= latest['white_line'] <= struct_range[1]: is_match = True
                    else:
                        if prev['white_line'] <= prev['purple_line'] and latest['white_line'] > latest['purple_line']: is_match = True
                    
                    if is_match:
                        results.append({
                            "Asset": t.replace(".JK", "").replace("-USD", ""),
                            "Price": f"{latest['Close']:,.2f}",
                            "White Line": round(latest['white_line'], 2),
                            "Purple Line": round(latest['purple_line'], 2),
                            "Vol (M)": round(turnover, 2)
                        })
                progress.progress((i + 1) / len(tickers))

        if results:
            res_df = pd.DataFrame(results).sort_values("White Line", ascending=False)
            st.success(f"Ditemukan {len(res_df)} peluang di {market}!")
            st.dataframe(res_df, use_container_width=True)
            
            st.divider()
            target = st.selectbox("Visualisasi:", res_df['Asset'])
            if target:
                full_t = target + (".JK" if market == "IHSG" else "-USD")
                df_p = compute_waves(fetch_data(full_t))
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4], vertical_spacing=0.05)
                fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Price"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p['white_line'], name="White", line=dict(color='white', width=2)), row=2, col=1)
                fig.add_trace(go.Scatter(x=df_p.index, y=df_p['purple_line'], name="Purple", line=dict(color='#D500F9', width=1.5)), row=2, col=1)
                for l, c in [(80, 'red'), (0, 'gray'), (-80, 'green')]: fig.add_hline(y=l, line_dash="dash", line_color=c, opacity=0.3, row=2, col=1)
                fig.update_layout(template="plotly_dark", height=700, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Belum ada aset yang lolos filter.")

if __name__ == "__main__":
    main()

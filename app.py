"""
================================================================================
 IHSG PREDICTIVE STRUCTURE SCREENER
 Logic   : Gelombang 4 - Price Structure (White Wave)
 Author  : Senior Quantitative Developer
 Stack   : Streamlit · yfinance · ta · Plotly
 Market  : Indonesian Stock Exchange (IDX)
================================================================================
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime
import time
import numpy as np
import warnings

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# 0.  PAGE CONFIG & TICKERS
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="IHSG Structure Screener", page_icon="🔮", layout="wide")

RAW_TICKERS = """
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

TICKER_UNIVERSE = sorted(list(dict.fromkeys([t.strip() + ".JK" for t in RAW_TICKERS.split()])))

# ──────────────────────────────────────────────────────────────────────────────
# 1.  CORE ENGINE (Porting Pine Script Logic)
# ──────────────────────────────────────────────────────────────────────────────

def pandas_wma(series, window):
    """Fungsi pembantu WMA karena pandas tidak punya bawaan."""
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def compute_predictive_matrix(df):
    """
    Menghitung Gelombang 4: Price Structure dari Pine Script.
    Formula: ((close - ll) / (hh - ll)) * 200 - 100 -> Smoothed by WMA 8
    """
    df = df.copy()
    # Gelombang 4 Logic
    hh = df['High'].rolling(20).max()
    ll = df['Low'].rolling(20).min()
    
    # Menghindari pembagian nol
    diff = (hh - ll).replace(0, 0.0001)
    struct_raw = ((df['Close'] - ll) / diff) * 200 - 100
    
    # Smoothing dengan WMA 8
    df['struct_wave'] = pandas_wma(struct_raw, 8)
    
    # Tambahan Trend Filter (SMA)
    df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
    return df

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_fundamentals(ticker: str) -> dict:
    try:
        info   = yf.Ticker(ticker).info
        return {
            "PER": round(float(info.get("trailingPE", -1)), 2),
            "PBV": round(float(info.get("priceToBook", -1)), 2),
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
        }
    except:
        return {"PER": -1, "PBV": -1, "name": ticker, "sector": "N/A"}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 30: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

# ──────────────────────────────────────────────────────────────────────────────
# 2.  UI & SCREENER
# ──────────────────────────────────────────────────────────────────────────────

def main():
    st.title("🔮 IHSG Predictive Trend Matrix")
    
    # Sidebar
    st.sidebar.header("⚙️ Matrix Parameters")
    min_struct = st.sidebar.slider("Min Price Structure Level (White Line)", -100, 100, 50)
    min_vol_m  = st.sidebar.slider("Min Vol Rata2 20H (Juta)", 1, 100, 10)
    max_pbv    = st.sidebar.slider("Max PBV", 0.5, 5.0, 1.5)
    
    if st.sidebar.button("🚀 Jalankan Screener"):
        universe_data = {}
        progress = st.progress(0)
        
        # Load Data
        with st.spinner("Menganalisis 500+ saham..."):
            for i, ticker in enumerate(TICKER_UNIVERSE):
                df = fetch_data(ticker)
                if df is not None:
                    universe_data[ticker] = df
                progress.progress((i + 1) / len(TICKER_UNIVERSE))
        
        # Screening
        results = []
        for ticker, df in universe_data.items():
            df_ind = compute_predictive_matrix(df)
            latest = df_ind.iloc[-1]
            
            # Filter 1: Volume & Trend
            avg_vol = df['Volume'].iloc[-20:].mean()
            if avg_vol < (min_vol_m * 1_000_000): continue
            if latest['Close'] < latest['SMA_50']: continue
            
            # Filter 2: Price Structure (Logika Pine Script)
            current_struct = latest['struct_wave']
            if current_struct < min_struct: continue
            
            # Filter 3: Fundamental (Hanya jika lolos teknikal)
            fnd = fetch_fundamentals(ticker)
            if fnd['PBV'] > max_pbv or fnd['PBV'] <= 0: continue
            
            results.append({
                "Ticker": ticker,
                "Nama": fnd['name'],
                "Price": latest['Close'],
                "Structure": round(current_struct, 2),
                "Vol 20D (M)": round(avg_vol / 1_000_000, 2),
                "PER": fnd['PER'],
                "PBV": fnd['PBV']
            })
            
        if results:
            res_df = pd.DataFrame(results).sort_values("Structure", ascending=False)
            st.success(f"Ditemukan {len(res_df)} saham potensial!")
            
            # Style Table
            st.dataframe(res_df.style.background_gradient(subset=['Structure'], cmap='RdYlGn'), use_container_width=True)
            
            # Visualisasi Chart
            st.divider()
            target = st.selectbox("Pilih Saham untuk Analisis Visual:", res_df['Ticker'])
            if target:
                df_plot = compute_predictive_matrix(universe_data[target])
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                   vertical_spacing=0.1, row_heights=[0.7, 0.3],
                                   subplot_titles=("Price Action", "Price Structure Wave (White Line)"))
                
                # Candlestick
                fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'],
                                           low=df_plot['Low'], close=df_plot['Close'], name="Price"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_50'], name="SMA 50", line=dict(color='yellow')), row=1, col=1)
                
                # Structure Wave
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['struct_wave'], name="Wave", line=dict(color='white', width=2)), row=2, col=1)
                
                # Critical Levels
                for lvl, clr in [(80, 'red'), (0, 'gray'), (-80, 'green')]:
                    fig.add_hline(y=lvl, line_dash="dash", line_color=clr, row=2, col=1)
                
                fig.update_layout(template="plotly_dark", height=800, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Tidak ada saham yang lolos kriteria. Coba longgarkan parameter.")

if __name__ == "__main__":
    main()

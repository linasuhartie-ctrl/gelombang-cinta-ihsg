# ──────────────────────────────────────────────────────────────────────────────
# NEW: DYNAMIC IHSG TICKER DISCOVERY
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=86400) # Simpan daftar ticker selama 24 jam
def get_all_ihsg_tickers():
    """Mengambil seluruh daftar saham yang terdaftar di IDX secara live."""
    try:
        # Kita gunakan Wikipedia sebagai sumber daftar emiten yang cukup update
        url = "https://id.wikipedia.org/wiki/Daftar_perusahaan_yang_tercatat_di_Bursa_Efek_Indonesia"
        tables = pd.read_html(url)
        
        all_tickers = []
        # Wikipedia membagi daftar saham dalam beberapa tabel (berdasarkan sektor/abjad)
        for df in tables:
            if 'Kode' in df.columns:
                # Ambil kolom 'Kode', bersihkan, dan tambahkan .JK
                tickers = df['Kode'].astype(str).str.strip().unique()
                all_tickers.extend([t + ".JK" for t in tickers if len(t) == 4])
        
        return sorted(list(set(all_tickers)))
    except Exception as e:
        st.error(f"Gagal mengambil daftar IHSG live: {e}")
        # Fallback: Jika scraping gagal, gunakan daftar minimalis agar app tidak crash
        return ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK"]

# ──────────────────────────────────────────────────────────────────────────────
# UPDATE PADA FUNGSI MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    st.sidebar.markdown("### 🗺️ Market Explorer")
    market = st.sidebar.radio("Universe:", ["IHSG (Scrape Live)", "Crypto Perps (Bybit API)"])
    
    # ... (Filter UI tetap sama) ...

    # Ticker loading dinamis
    if market == "IHSG (Scrape Live)":
        with st.spinner("Mengambil seluruh emiten dari IDX..."):
            tickers = get_all_ihsg_tickers()
    else:
        with st.spinner("Menghubungkan ke API Bybit..."):
            tickers = get_bybit_perps() # Fungsi Bybit API yang kita buat sebelumnya

    st.sidebar.caption(f"Total aset terdeteksi: {len(tickers)}")
    
    # ... (Sisa logika scanning tetap sama) ...

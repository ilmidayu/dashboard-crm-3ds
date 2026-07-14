import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np

# ==========================================
# 1. SETUP HALAMAN & CUSTOM CSS (TEMA BIRU 3DS)
# ==========================================
st.set_page_config(page_title="Dashboard CRM PT 3DS", page_icon="🔵", layout="wide")

st.markdown("""
    <style>
    /* Mengubah warna background metrik (Tema Biru) */
    div[data-testid="metric-container"] {
        background-color: #e6f2ff;
        border: 1px solid #0056b3;
        padding: 5% 10% 5% 10%;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    /* Warna header */
    h1, h2, h3, h4 { color: #003d80; }
    </style>
    """, unsafe_allow_html=True)


# ==========================================
# 2. FUNGSI TELEGRAM (VERSI ANTI GAGAL)
# ==========================================
def kirim_telegram(pesan):
    # Token dan Chat ID
    BOT_TOKEN = "8793828622:AAF55Kc59SJFzCGlPZKq3uvf3gz3yTy2GTQ" 
    CHAT_ID = "-5169991149"
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": pesan}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            st.error(f"⚠️ Gagal dari Telegram: {response.text}")
            return False
        return True
    except Exception as e:
        st.error(f"⚠️ Error Sistem: {e}")
        return False


# ==========================================
# 3. LOAD DATA & SIMULASI LOKASI
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv('dataset_final_clustering.csv')
    df['Tahun_Terakhir'] = 2026 - (df['Recency'] // 365).astype(int)
    
    # --- SIMULASI DATA LOKASI INDONESIA ---
    np.random.seed(42)
    lokasi_indo = {
        'DKI Jakarta': [-6.2088, 106.8456],
        'Surabaya': [-7.2504, 112.7688],
        'Bandung': [-6.9175, 107.6191],
        'Medan': [3.5952, 98.6722],
        'Makassar': [-5.1476, 119.4327],
        'Semarang': [-6.9667, 110.4167],
        'Bali': [-8.4095, 115.1889]
    }
    kota_pilihan = list(lokasi_indo.keys())
    df['Kota'] = np.random.choice(kota_pilihan, size=len(df))
    df['Lat'] = df['Kota'].map(lambda x: lokasi_indo[x][0])
    df['Lon'] = df['Kota'].map(lambda x: lokasi_indo[x][1])
    
    return df

df_raw = load_data()


# ==========================================
# 4. SIDEBAR MENU, LOGO, & GLOBAL FILTERS
# ==========================================
with st.sidebar:
    # --- MASUKKAN LINK LOGO DI SINI JIKA LOKAL ERROR ---
    try:
        st.image("logo_3ds.png", use_container_width=True)
    except:
        st.warning("⚠️ Masukkan file 'logo_3ds.png' di folder yang sama untuk menampilkan logo.")
        
    st.title("🎯 Menu Navigasi")
    st.markdown("---")
    menu = st.radio("Pilih Modul:", [
        "📊 Ringkasan Utama", 
        "👤 Profil Pelanggan", 
        "🚨 Warning Pelanggan", 
        "🗄️ Database Tabel"
    ])
    
    st.markdown("---")
    st.title("🎛️ Filter Data")
    
    list_tahun = sorted(df_raw['Tahun_Terakhir'].unique(), reverse=True)
    filter_tahun = st.selectbox("Tahun Transaksi:", ["Semua Tahun"] + list_tahun)
    filter_segmen = st.multiselect("Segmen Pelanggan:", df_raw['Segment_Name'].unique(), default=df_raw['Segment_Name'].unique())
    filter_recency = st.slider("Batas Maksimal Recency (Hari):", min_value=0, max_value=int(df_raw['Recency'].max()), value=int(df_raw['Recency'].max()))
    
    st.markdown("---")
    st.caption("© 2026 PT 3DS Analytics\nClustering: MFPCM")

# Terapkan Filter Global
df = df_raw.copy()
if filter_tahun != "Semua Tahun":
    df = df[df['Tahun_Terakhir'] == filter_tahun]
df = df[(df['Segment_Name'].isin(filter_segmen)) & (df['Recency'] <= filter_recency)]

# ==========================================
# MODUL 1: RINGKASAN UTAMA (LAYOUT BARU)
# ==========================================
if menu == "📊 Ringkasan Utama":
    st.title("📊 Ringkasan Utama")
    
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Pelanggan", f"{len(df)} PT/CV")
        col2.metric("Total Pendapatan", f"Rp {df['Monetary'].sum():,.0f}".replace(',', '.'))
        col3.metric("Rata-rata Transaksi", f"{df['Frequency'].mean():.1f} Kali")
        col4.metric("Rata-rata Kepuasan", f"{df['SKP'].mean():.2f} / 5.0")

# BARIS 1: Tabel Memanjang Full Width
    with st.container(border=True):
        st.markdown("#### Profil Agregat per Segmen")
        tabel_ringkasan = df.groupby('Segment_Name').agg(
            Recency_Rata2=('Recency', 'mean'),
            Frekuensi_Rata2=('Frequency', 'mean'),
            Total_Belanja=('Monetary', 'sum')
        ).reset_index()
        
        tabel_ringkasan['Recency_Rata2'] = tabel_ringkasan['Recency_Rata2'].round(1)
        tabel_ringkasan['Frekuensi_Rata2'] = tabel_ringkasan['Frekuensi_Rata2'].round(2)
        
        # --- KODE TAMBAHAN UNTUK FORMAT RUPIAH ---
        tabel_ringkasan['Total_Belanja'] = tabel_ringkasan['Total_Belanja'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))
        # -----------------------------------------
        
        st.dataframe(tabel_ringkasan, use_container_width=True)

    # BARIS 2: Pie Chart (Kiri) & Scatter Plot (Kanan)
    c1, c2 = st.columns([1, 1.5])
    with c1:
        with st.container(border=True):
            st.markdown("#### Kontribusi Pendapatan")
            fig_pie = px.pie(df, values='Monetary', names='Segment_Name', hole=0.4, color_discrete_sequence=['#0056b3', '#66b3ff'])
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)
            
    with c2:
        with st.container(border=True):
            st.markdown("#### Persebaran (Frequency vs Monetary)")
            fig_scatter = px.scatter(df, x='Frequency', y='Monetary', color='Segment_Name', 
                                     hover_data=['Customer', 'Recency', 'SKP', 'SKL'],
                                     log_y=True, size='SKP', opacity=0.7, color_discrete_sequence=['#0056b3', '#66b3ff'])
            fig_scatter.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_scatter, use_container_width=True)

    # BARIS 3: Peta Lokasi
    with st.container(border=True):
        st.markdown("#### 🗺️ Peta Persebaran Lokasi Pelanggan (Indonesia)")
        fig_map = px.scatter_mapbox(df, lat="Lat", lon="Lon", hover_name="Customer", hover_data=["Kota", "Segment_Name", "Monetary"],
                                    color="Segment_Name", size="Monetary", zoom=4.2, center={"lat": -2.5, "lon": 118.0},
                                    mapbox_style="carto-positron", color_discrete_sequence=['#0056b3', '#66b3ff'])
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

    st.info("💡 **Insight Keseluruhan:** Sebagian besar pendapatan perusahaan ditopang kuat oleh segmen *High Value*. Persebaran klien utama terpusat di kota-kota strategis. Disarankan untuk memfokuskan strategi retensi pada wilayah dengan kepadatan VIP tertinggi untuk mencegah *churn*.")


# ==========================================
# MODUL 2: PROFIL PELANGGAN
# ==========================================
elif menu == "👤 Profil Pelanggan":
    
    with st.container(border=True):
        st.markdown("### 🔍 Pencarian Profil Pelanggan")
        st.caption("Silakan klik pada kotak di bawah dan ketik nama PT/CV untuk mencari.")
        
        # Penambahan index=None dan placeholder agar form pencarian kosong di awal (bisa diketik)
        selected_cust = st.selectbox(
            "Ketik atau Pilih Nama Perusahaan:", 
            options=sorted(df['Customer'].unique()), 
            index=None, 
            placeholder="Ketik nama PT/CV di sini..."
        )
        
        if selected_cust:
            cust_data = df[df['Customer'] == selected_cust].iloc[0]
            
            st.markdown("---")
            c1, c2 = st.columns([1, 2])
            
            with c1:
                st.markdown("#### Info Profil")
                st.info(f"**Nama:** {cust_data['Customer']}\n\n"
                        f"**Segmen:** {cust_data['Segment_Name']}\n\n"
                        f"**Lokasi:** {cust_data['Kota']}\n\n"
                        f"**Skor Pelayanan (SKP):** {cust_data['SKP']}/5.0\n\n"
                        f"**Skor Layanan (SKL):** {cust_data['SKL']}/5.0")
                
            with c2:
                st.markdown("#### Ringkasan Transaksi")
                mc1, mc2, mc3 = st.columns(3)
                mc1.metric("Total Belanja", f"Rp {cust_data['Monetary']:,.0f}")
                mc2.metric("Total Transaksi", f"{cust_data['Frequency']} Kali")
                mc3.metric("Recency", f"{cust_data['Recency']} Hari")
            
            st.markdown("#### 💡 Rekomendasi Sistem")
            if cust_data['Segment_Name'] == 'High Value Customers' and cust_data['Recency'] > 60:
                st.error("🚨 **Risiko Churn Tinggi:** Segera hubungi untuk penawaran lisensi eksklusif.")
            elif cust_data['Segment_Name'] == 'High Value Customers':
                st.success("🌟 **Loyal & Aktif:** Pertahankan komunikasi rutin dengan Key Account Manager.")
            elif cust_data['Frequency'] >= 3:
                st.warning("📈 **Potensi Upselling:** Tawarkan paket bundling premium.")
            else:
                st.info("👤 **Reguler:** Lakukan nurturing dengan email marketing bulanan.")


# ==========================================
# MODUL 3: WARNING PELANGGAN
# ==========================================
elif menu == "🚨 Warning Pelanggan":
    st.title("🚨 Warning Pelanggan")
    
    vip_aman = df[(df['Segment_Name'] == 'High Value Customers') & (df['Recency'] <= 60)]
    vip_churn = df[(df['Segment_Name'] == 'High Value Customers') & (df['Recency'] > 60)]
    upsell_pot = df[(df['Segment_Name'] == 'Standard Value Customers') & (df['Frequency'] > 2) & (df['SKP'] >= 4.0)]
    
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Pelanggan VIP Aman", len(vip_aman))
        col2.metric("🚨 Risiko Churn (VIP > 60 Hari)", len(vip_churn))
        col3.metric("📈 Potensi Naik Segmen", len(upsell_pot))

    st.info("💡 **Insight Warning:** Pelanggan VIP dalam status 'Risiko Churn' adalah ancaman langsung terhadap *revenue* perusahaan. Segera lakukan eskalasi ke tim *Key Account* untuk pendekatan persuasif atau berikan promo khusus penahanan (retention promo).")

    with st.container(border=True):
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("#### Daftar Pelanggan Prioritas")
            df_intervensi = pd.concat([vip_churn, upsell_pot]).copy()
            def get_rekomendasi(row):
                if row['Segment_Name'] == 'High Value Customers': return "Retention Campaign"
                else: return "Upselling Opportunity"
                
            if not df_intervensi.empty:
                df_intervensi['Rekomendasi'] = df_intervensi.apply(get_rekomendasi, axis=1)
                
                sort_by = st.selectbox("🔀 Urutkan Data Tabel Berdasarkan:", ["Monetary (Nilai Belanja Tertinggi)", "Recency (Paling Lama Tidak Aktif)", "Nama Perusahaan (A-Z)"])
                if sort_by == "Monetary (Nilai Belanja Tertinggi)":
                    df_intervensi = df_intervensi.sort_values(by="Monetary", ascending=False)
                elif sort_by == "Recency (Paling Lama Tidak Aktif)":
                    df_intervensi = df_intervensi.sort_values(by="Recency", ascending=False)
                else:
                    df_intervensi = df_intervensi.sort_values(by="Customer", ascending=True)

                st.dataframe(df_intervensi[['Customer', 'Kota', 'Recency', 'Monetary', 'Rekomendasi']], use_container_width=True)
                
                if len(vip_churn) > 0:
                    if st.button("📤 Eksekusi Churn Alert ke Telegram", type="primary"):
                        with st.spinner("Mengirim pesan ke Telegram..."):
                            top_churn = vip_churn.sort_values(by='Monetary', ascending=False).head(3)['Customer'].tolist()
                            pesan = f"🚨 URGENT CHURN ALERT 🚨\nTerdapat {len(vip_churn)} VIP yang lama tidak aktif.\n\nPrioritas Follow-up:\n- " + "\n- ".join(top_churn)
                            
                            sukses = kirim_telegram(pesan)
                            if sukses:
                                st.success("Notifikasi Telegram berhasil terkirim ke HP!")
            else:
                st.success("Kondisi aman. Tidak ada pelanggan yang memerlukan intervensi mendesak.")

        # --- KODE TAMBAHAN UNTUK FORMAT RUPIAH ---
        tabel_ringkasan['Total_Belanja'] = tabel_ringkasan['Total_Belanja'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))        
        
        with c2:
            st.markdown("#### Aksi Disarankan")
            if not df_intervensi.empty:
                rekomendasi_counts = df_intervensi['Rekomendasi'].value_counts()
                fig_bar = px.bar(x=rekomendasi_counts.values, 
                                 y=rekomendasi_counts.index, 
                                 orientation='h', 
                                 color_discrete_sequence=['#0056b3'],
                                 labels={'x': 'Jumlah Pelanggan', 'y': ''})
                fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_bar, use_container_width=True)


# ==========================================
# MODUL 4: DATABASE TABEL
# ==========================================
elif menu == "🗄️ Database Tabel":
    st.title("🗄️ Master Database Pelanggan")
    st.caption("Data di bawah ini sudah mengikuti filter global pada Sidebar.")
    
    with st.container(border=True):
        st.markdown(f"**Menampilkan {len(df)} baris data.**")
        st.dataframe(df[['Customer', 'Kota', 'Recency', 'Frequency', 'Monetary', 'SKP', 'SKL', 'Tahun_Terakhir', 'Segment_Name']], use_container_width=True)

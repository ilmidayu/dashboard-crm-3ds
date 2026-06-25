import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os

# ==========================================
# 1. SETUP HALAMAN & TEMA (DIGITAL MARKETING)
# ==========================================
st.set_page_config(page_title="CRM & Marketing Analytics PT 3DS", page_icon="🎯", layout="wide")

st.markdown("""
    <style>
    .stMetric {
        background-color: #f1f8ff; 
        border-left: 5px solid #0056b3; 
        padding: 15px; 
        border-radius: 5px; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FUNGSI TELEGRAM (ANTI-GAGAL)
# ==========================================
def kirim_telegram(pesan):
    # 👇👇👇 GANTI DENGAN TOKEN DAN CHAT ID KAMU 👇👇👇
    BOT_TOKEN = "8793828622:AAF55Kc59SJFzCGlPZKq3uvf3gz3yTy2GTQ" 
    CHAT_ID = "-5169991149"
    # 👆👆👆 ========================================= 👆👆👆
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # parse_mode Markdown dihapus agar aman membaca karakter pada nama PT
    payload = {"chat_id": CHAT_ID, "text": pesan}
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            st.error(f"⚠️ Gagal mengirim ke Telegram: {response.text}")
            return False
        return True
    except Exception as e:
        st.error(f"⚠️ Error Sistem: {e}")
        return False

# ==========================================
# 3. LOAD DATA (TANPA MODEL MACHINE LEARNING)
# ==========================================
@st.cache_data
def load_data():
    return pd.read_csv('dataset_final_clustering.csv')

df = load_data()

# ==========================================
# 4. SIDEBAR NAVIGATION & LOGO
# ==========================================
with st.sidebar:
    try:
        st.image("logo_3ds.png", use_container_width=True)
    except:
        st.warning("⚠️ Gagal memuat logo dari link.")

    st.title("🎯 Marketing CRM Menu")
    st.markdown("---")
    menu = st.radio("Pilih Modul:", [
        "📈 CRM Overview", 
        "📊 Audience Profiling & Target", 
        "🚨 Churn & Retargeting Alert"
    ])

# ==========================================
# MODUL 1: CRM OVERVIEW 
# ==========================================
if menu == "📈 CRM Overview":
    st.title("📈 CRM & Sales Overview")
    st.markdown("Pantau performa retensi pelanggan dan sebaran segmentasi PT 3DS secara menyeluruh.")
    
    # --- METRIC CARDS ---
    total_revenue = df['Monetary'].sum()
    vip_df = df[df['Segment_Name'] == 'High Value Customers']
    vip_revenue = vip_df['Monetary'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Client Base", f"{len(df)} PT/CV")
    col2.metric("👑 Key Accounts (VIP)", f"{len(vip_df)} Client")
    col3.metric("Total Revenue", f"Rp {total_revenue/1e6:.0f} Juta")
    col4.metric("VIP Revenue Share", f"{(vip_revenue/total_revenue)*100:.1f}%")

    st.markdown("---")
    
    # --- BARIS 1: PIE CHART & BOX PLOT ---
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Proporsi Segmen Pelanggan**")
        fig_pie = px.pie(df, names='Segment_Name', hole=0.5, color_discrete_sequence=['#ff9999', '#66b3ff'])
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        st.write("**Distribusi Nilai Transaksi (Monetary) per Segmen**")
        fig_box = px.box(df, x='Segment_Name', y='Monetary', color='Segment_Name', log_y=True, color_discrete_sequence=['#ff9999', '#66b3ff'])
        st.plotly_chart(fig_box, use_container_width=True)

    # --- BARIS 2: SCATTER PLOT BESAR ---
    st.write("**Peta Persebaran Pelanggan (Frequency vs Monetary)**")
    fig_scatter = px.scatter(df, x='Frequency', y='Monetary', color='Segment_Name', 
                             hover_data=['Customer', 'Recency', 'SKP', 'SKL'],
                             log_y=True, size='SKP', opacity=0.7, color_discrete_sequence=['#ff9999', '#66b3ff'])
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # --- TABEL DATA ---
    with st.expander("Lihat Detail Data Tabel"):
        st.dataframe(df)

# ==========================================
# MODUL 2: AUDIENCE PROFILING & TARGET 
# ==========================================
elif menu == "📊 Audience Profiling & Target":
    st.title("📊 Profiling & Target Up-Selling")
    st.markdown("Analisis karakteristik audiens secara tiga dimensi dan daftar *Key Accounts* yang perlu segera di-follow up.")
    
    # --- TOP 5 KEY ACCOUNTS ---
    st.markdown("### 🏆 Top 5 Key Accounts (Target Utama Up-Selling)")
    st.info("Klien di bawah ini adalah penyumbang *revenue* terbesar. Pastikan Account Manager menjaga hubungan baik dengan mereka.")
    vip_df = df[df['Segment_Name'] == 'High Value Customers']
    top_5 = vip_df.sort_values(by='Monetary', ascending=False).head(5)
    st.dataframe(top_5[['Customer', 'Monetary', 'Frequency', 'Recency', 'SKP', 'SKL']], use_container_width=True)
    
    st.markdown("---")
    
    # --- 3D SCATTER PLOT ---
    st.markdown("### 🎲 Peta 3D Ruang RFM (Recency, Frequency, Monetary)")
    st.write("Putar grafik di bawah ini untuk melihat ruang pemisah antara pelanggan reguler dan VIP.")
    fig_3d = px.scatter_3d(df, x='Recency', y='Frequency', z='Monetary',
                           color='Segment_Name', opacity=0.7, hover_name='Customer',
                           color_discrete_sequence=['#ff9999', '#66b3ff'])
    fig_3d.update_layout(margin=dict(l=0, r=0, b=0, t=0))
    st.plotly_chart(fig_3d, use_container_width=True)

# ==========================================
# MODUL 3: CHURN & RETARGETING ALERT (TELEGRAM)
# ==========================================
elif menu == "🚨 Churn & Retargeting Alert":
    st.title("🚨 Churn Detection & Retargeting")
    st.markdown("Cari pelanggan VIP (High Value) yang sudah lama tidak bertransaksi dan kirimkan datanya ke Telegram tim *Digital Marketing*.")
    
    st.subheader("Filter Potensi Churn")
    batas_recency = st.slider("Ambang Batas Recency (Hari sejak transaksi terakhir):", min_value=15, max_value=180, value=60, step=15)
    
    vip_churn_risk = df[(df['Segment_Name'] == 'High Value Customers') & (df['Recency'] >= batas_recency)]
    
    st.error(f"⚠️ Ditemukan **{len(vip_churn_risk)} Pelanggan VIP** yang berisiko churn (Belum transaksi > {batas_recency} hari).")
    
    if len(vip_churn_risk) > 0:
        st.dataframe(vip_churn_risk[['Customer', 'Recency', 'Monetary', 'SKP']], use_container_width=True)
        
        if st.button("📤 Kirim Alert Target Campaign ke Telegram Tim Marketing"):
            with st.spinner("Mengirim data ke Telegram..."):
                top_3_churn = vip_churn_risk.sort_values(by='Monetary', ascending=False).head(3)['Customer'].tolist()
                nama_pt_str = "\n- ".join(top_3_churn)
                
                # Teks diubah tanpa format khusus agar aman dikirim ke Telegram
                pesan_marketing = f"""MARKETING CAMPAIGN ALERT
                
Terdapat {len(vip_churn_risk)} Klien VIP yang belum bertransaksi selama lebih dari {batas_recency} hari.

Top 3 Prioritas Retargeting:
- {nama_pt_str}

Action Plan: Mohon tim Digital Marketing segera eksekusi Email Retargeting Campaign berisi diskon perpanjangan lisensi / penawaran eksklusif untuk daftar perusahaan di atas.
"""
                sukses = kirim_telegram(pesan_marketing)
                if sukses:
                    st.success("✅ Pesan berhasil dikirim ke Telegram Manajer Digital Marketing!")
                    st.balloons()
    else:
        st.success("Kondisi aman! Tidak ada VIP yang berisiko churn pada ambang batas waktu ini.")

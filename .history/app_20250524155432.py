import streamlit as st
from config.db_connection import load_transactions, load_kategori
from utils.fp_growth import run_fp_growth
import pandas as pd

# Load CSS
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Judul Header
st.markdown("""
<div style="background-color:#006e6d;padding:10px;border-radius:10px">
    <h2 style="color:white;text-align:center;">FP-Growth Dashboard - Nuhsantara Merchandise</h2>
</div>
""", unsafe_allow_html=True)

# Sidebar navigasi utama
page = st.sidebar.radio("📂 Menu Navigasi", ["📋 Data Transaksi", "📈 FP-Growth Analisis"])
basis = st.sidebar.radio("📊 Analisis Berdasarkan:", ["Nama Produk", "Kategori Produk"])

# Load data sesuai basis
if basis == "Nama Produk":
    df = load_transactions()
else:
    df = load_kategori()
    df.rename(columns={"kategori_produk": "nama_produk"}, inplace=True)

# Halaman 1: Data Transaksi
if page == "📋 Data Transaksi":
    st.subheader("📋 Data Transaksi")
    st.dataframe(df, use_container_width=True)

    total_rows = df.shape[0]
    total_transaksi = df["no_transaksi"].nunique()
    st.info(f"🔢 Total baris data: {total_rows:,} | Total transaksi unik: {total_transaksi:,}")

# Halaman 2: FP-Growth
elif page == "📈 FP-Growth Analisis":
    st.markdown("### ⚙️ Parameter Analisis")
    min_support = st.slider("Minimum Support", 0.01, 1.0, 0.01, 0.01)
    min_conf = st.slider("Minimum Confidence", 0.01, 1.0, 0.60, 0.01)

    st.success("Klik tombol di bawah untuk menjalankan FP-Growth.")
    if st.button("🔍 Jalankan Analisis"):
        with st.spinner("Sedang memproses..."):
            freq_items, rules, simplified = run_fp_growth(df, min_support, min_conf)

        st.markdown("## 📌 Frequent Itemsets")
        st.dataframe(freq_items.reset_index(drop=True), use_container_width=True)
        st.info(f"✅ Total Frequent Itemsets: {freq_items.shape[0]:,}")

        st.markdown("## 🔗 Association Rules")
        st.dataframe(rules[["antecedents", "consequents", "rules", "support", "confidence", "lift"]].reset_index(drop=True), use_container_width=True)
        st.info(f"📈 Total Association Rules: {rules.shape[0]:,}")
        st.success(f"🧠 Total Rekomendasi Kalimat: {rules['kesimpulan'].count():,}")

        st.markdown("## 🧠 Kesimpulan Rekomendasi")
        for kalimat in rules["kesimpulan"].head(10):
            st.markdown(f"- {kalimat}")

        st.markdown("## 📎 Rules 1 Antecedent → Banyak Consequents")
        st.dataframe(simplified.reset_index(drop=True), use_container_width=True)
        st.warning(f"🔸 Total Simplified Rules: {simplified.shape[0]:,}")

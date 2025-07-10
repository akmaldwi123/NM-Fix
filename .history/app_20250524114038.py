import streamlit as st
from config.db_connection import load_transactions, load_kategori
from utils.fp_growth import run_fp_growth
import pandas as pd

# Load CSS
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("📊 FP-Growth Dashboard - Nuhsantara Merchandise")

# Pilihan basis analisis
basis = st.radio("Analisis berdasarkan:", ["Nama Produk", "Kategori Produk"])

# Parameter FP-Growth
min_support = st.slider("Minimum Support", 0.01, 1.0, 0.1, 0.01)
min_confidence = st.slider("Minimum Confidence", 0.01, 1.0, 0.5, 0.01)

# Ambil data
if basis == "Nama Produk":
    df = load_transactions()
else:
    df = load_kategori()
    df.rename(columns={"kategori_produk": "nama_produk"}, inplace=True)

st.markdown("### 📄 Data Transaksi")
st.dataframe(df)

if st.button("🔍 Jalankan FP-Growth"):
    with st.spinner("Memproses data..."):
        freq_items, rules = run_fp_growth(df, min_support, min_confidence)

    st.success("Analisis selesai!")

    st.subheader("📌 Frequent Itemsets")
    st.dataframe(freq_items)

    st.subheader("🔗 Association Rules")
    st.dataframe(rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']])

    # Export CSV
    csv = rules.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Unduh Association Rules", csv, "association_rules.csv", "text/csv")

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
    <h2 style="color:white;text-align:center;">📊 FP-Growth Dashboard - Nuhsantara Merchandise</h2>
</div>
""", unsafe_allow_html=True)

# Sidebar sebagai navigasi multipage
page = st.sidebar.radio("Navigasi Halaman", ["📋 Data", "📌 Frequent Itemsets", "🔗 Association Rules"])

# Parameter
st.sidebar.markdown("### Parameter Analisis")
min_support = st.sidebar.slider("Minimum Support", 0.01, 1.0, 0.01, 0.01)
min_conf = st.sidebar.slider("Minimum Confidence", 0.01, 1.0, 0.60, 0.01)
basis = st.sidebar.radio("Analisis berdasarkan:", ["Nama Produk", "Kategori Produk"])

# Load data
if basis == "Nama Produk":
    df = load_transactions()
else:
    df = load_kategori()
    df.rename(columns={"kategori_produk": "nama_produk"}, inplace=True)

# Eksekusi mining
freq_items, rules, simplified = run_fp_growth(df, min_support, min_conf)

# Halaman 1
if page == "📋 Data":
    st.subheader("📋 Data Transaksi")
    st.dataframe(df)

# Halaman 2
elif page == "📌 Frequent Itemsets":
    st.subheader("📌 Frequent Itemsets")
    st.dataframe(freq_items)

# Halaman 3
elif page == "🔗 Association Rules":
    st.subheader("🔗 Association Rules")
    st.dataframe(rules[["antecedents", "consequents", "rules", "support", "confidence", "lift"]])
    
    st.subheader("🧠 Kesimpulan Rekomendasi")
    for kalimat in rules["kesimpulan"].head(10):
        st.markdown(f"- {kalimat}")

    st.subheader("🔍 Association Rules (1 antecedent > 1 consequent)")
    st.dataframe(simplified[["antecedents", "consequents", "support", "confidence", "lift"]])

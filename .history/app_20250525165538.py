import streamlit as st
from config.db_connection import load_transactions, load_kategori
from utils.fp_growth import run_fp_growth
import pandas as pd

# Load CSS
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Judul Header dipisah dua baris tanpa tanda "-"
st.markdown("""
<div style="background-color:#006e6d;padding:10px;border-radius:10px;text-align:center;">
    <h2 style="color:white;margin:0;padding:0;line-height:1;">FP-Growth Dashboard<br>Nuhsantara Merchandise</h2>
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

# ===========================
# HALAMAN 1: DATA TRANSAKSI
# ===========================
if page == "📋 Data Transaksi":
    st.subheader("📋 Data Transaksi")
    df_display = df.copy()
    df_display.index = range(1, len(df_display) + 1)
    df_display.index.name = "No"
    st.dataframe(df_display, use_container_width=True)

    total_rows = df.shape[0]
    total_transaksi = df["no_transaksi"].nunique()
    st.info(f"🔢 Total baris data: {total_rows:,} | Total transaksi unik: {total_transaksi:,}")

# ===========================
# HALAMAN 2: FP-GROWTH
# ===========================
elif page == "📈 FP-Growth Analisis":
    st.markdown("### ⚙️ Parameter Analisis")
    min_support = st.slider("Minimum Support", 0.01, 1.0, 0.01, 0.01)
    min_conf = st.slider("Minimum Confidence", 0.01, 1.0, 0.60, 0.01)

    st.success("Klik tombol di bawah untuk menjalankan FP-Growth.")
    if st.button("🔍 Jalankan Analisis"):
        with st.spinner("Sedang memproses..."):
            freq_items, rules, simplified = run_fp_growth(df, min_support, min_conf)

        # ===== Frequent Itemsets =====
        st.markdown("## 📌 Frequent Itemsets")
        freq_items_display = freq_items.reset_index(drop=True)
        freq_items_display.index = range(1, len(freq_items_display) + 1)
        freq_items_display.index.name = "No"
        st.dataframe(freq_items_display, use_container_width=True)
        st.info(f"✅ Total Frequent Itemsets: {freq_items.shape[0]:,}")

        # ===== Association Rules (semua) =====
        st.markdown("## 🔗 Association Rules")
        rules_display = rules[["antecedents", "consequents", "rules", "support", "confidence", "lift"]].reset_index(drop=True)
        rules_display.index = range(1, len(rules_display) + 1)
        rules_display.index.name = "No"
        st.dataframe(rules_display, use_container_width=True)
        st.info(f"📈 Total Association Rules: {rules.shape[0]:,}")
        st.success(f"🧠 Total Kesimpulan Rekomendasi: {rules['kesimpulan'].count():,}")

        # ===== Kesimpulan utama (semua rules) =====
        st.markdown("### 🧠 Kesimpulan Rekomendasi (Top 10)")
        for i, kalimat in enumerate(rules["kesimpulan"].head(10), start=1):
            st.markdown(f"{i}. {kalimat}")

        # ===== Simplified Rules (1 antecedent & 1 consequent) =====
        st.markdown("---")
        st.markdown("## 📎 Rules 1 Antecedent → 1 Consequent")
        simp_display = simplified[["antecedents", "consequents", "support", "confidence", "lift"]].reset_index(drop=True)
        simp_display.index = range(1, len(simp_display) + 1)
        simp_display.index.name = "No"
        st.dataframe(simp_display, use_container_width=True)
        st.warning(f"🔸 Total Simplified Rules (1 ➝ 1): {simplified.shape[0]:,}")

        # ===== Kesimpulan Simplified =====
        st.markdown("### 🧠 Kesimpulan Simplified (Top 10)")
        for i, kalimat in enumerate(simplified["kesimpulan"].head(10), start=1):
            st.markdown(f"{i}. {kalimat}")
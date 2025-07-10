import streamlit as st
from config.db_connection import load_transactions, load_kategori
from utils.fp_growth import run_fp_growth
import pandas as pd

st.set_page_config(layout="wide")

# Load CSS
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Header

st.markdown("""
<div style="background-color:#006e6d;padding:30px;border-radius:10px;text-align:center;">
    <h2 style="color:white;margin:0;padding:0;line-height:1;">FP-Growth Dashboard<br>Nuhsantara Merchandise</h2>
</div>
""", unsafe_allow_html=True)

# Sidebar menu dan basis analisis
st.sidebar.image("static/logoo.png", width=230)
page = st.sidebar.radio("📂 Menu Navigasi", ["📥 Upload File", "📄 Data Transaksi", "📊 FP-Growth Analisis"])
basis_opsi = st.sidebar.radio("🧾 Analisis Berdasarkan:", ["Nama Produk", "Kategori Produk"])
kolom_analisis = "nama_produk" if basis_opsi == "Nama Produk" else "kategori_produk"

# ====================
# UPLOAD FILE SECTION
# ====================
if page == "📥 Upload File":
    st.subheader("📂 Upload File Transaksi")
    uploaded_file = st.file_uploader("Unggah file Excel atau CSV", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            df_uploaded = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

            if "no_transaksi" not in df_uploaded.columns:
                st.error("File harus memiliki kolom `no_transaksi`.")
                st.stop()

            if kolom_analisis not in df_uploaded.columns:
                st.warning(f"⚠️ Kolom `{kolom_analisis}` tidak tersedia di file upload.")
                st.stop()

            # Kolom yang akan dipakai
            selected_cols = ["no_transaksi", kolom_analisis]
            if "tanggal" in df_uploaded.columns:
                selected_cols.append("tanggal")

            df_filtered = df_uploaded[selected_cols].copy()

            # Simpan ke session state
            st.session_state.df_uploaded = df_filtered
            st.success("✅ File berhasil diunggah!")
            st.dataframe(df_filtered.head())

        except Exception as e:
            st.error(f"Gagal membaca file: {e}")


# ====================
# LOAD DATA
# ====================
if "df_uploaded" in st.session_state:
    df = st.session_state.df_uploaded.copy()
    if kolom_analisis not in df.columns:
        st.warning(f"⚠️ Kolom {kolom_analisis} tidak tersedia di file upload.")
        st.stop()
else:
    df = load_transactions() if kolom_analisis == "nama_produk" else load_kategori()
    if kolom_analisis not in df.columns:
        st.warning(f"⚠️ Kolom {kolom_analisis} tidak ditemukan di database.")
        st.stop()

# ====================
# DATA TRANSAKSI PAGE
# ====================
if page == "📄 Data Transaksi":
    st.subheader("📄 Data Transaksi")
    df_view = df.copy()

    if "tanggal" in df_view.columns:
        tanggal_tersedia = sorted(pd.to_datetime(df_view["tanggal"]).unique())
        tgl_start, tgl_end = st.date_input("Filter tanggal:", value=(min(tanggal_tersedia), max(tanggal_tersedia)))
        tgl_start = pd.to_datetime(tgl_start)
        tgl_end = pd.to_datetime(tgl_end)
        df_view["tanggal"] = pd.to_datetime(df_view["tanggal"])
        df_view = df_view[(df_view["tanggal"] >= tgl_start) & (df_view["tanggal"] <= tgl_end)]
        df_view["tanggal"] = df_view["tanggal"].dt.date
        df_view = df_view.sort_values(by="tanggal")
        st.session_state["filtered_df"] = df_view

    # Tampilkan hanya kolom relevan
    tampilkan_kolom = ["no_transaksi", kolom_analisis] + (["tanggal"] if "tanggal" in df_view.columns else [])
    df_tampil = df_view[tampilkan_kolom].copy()
    df_tampil.index = range(1, len(df_tampil) + 1)
    df_tampil.index.name = "No"
    st.dataframe(df_tampil, use_container_width=True)

    total_rows = df_view.shape[0]
    total_transaksi = df_view["no_transaksi"].nunique()
    st.info(f"🔢 Total baris data: {total_rows:,} | Total transaksi unik: {total_transaksi:,}")

# ====================
# ANALISIS FP-GROWTH
# ====================
elif page == "📊 FP-Growth Analisis":
    st.markdown("### ⚙️ Parameter Analisis")
    min_support = st.slider("Minimum Support", 0.01, 1.0, 0.01, 0.01)
    min_conf = st.slider("Minimum Confidence", 0.01, 1.0, 0.60, 0.01)

    df_fp = st.session_state.get("filtered_df", df.copy())
    if kolom_analisis not in df_fp.columns:
        st.warning("⚠️ Kolom produk tidak tersedia.")
        st.stop()

    # Validasi tanggal
    st.markdown("### 🧾 Informasi Data yang Akan Dianalisis")
    if "tanggal" in df_fp.columns:
        tanggal_tersedia = sorted(pd.to_datetime(df_fp["tanggal"]).unique())
        min_tanggal = min(tanggal_tersedia).date()
        max_tanggal = max(tanggal_tersedia).date()
        total_rows = df_fp.shape[0]
        total_transaksi = df_fp["no_transaksi"].nunique()
        st.info(f"📆 Periode Tanggal: `{min_tanggal}` s.d. `{max_tanggal}`")
        st.info(f"🔢 Total Baris Data: `{total_rows:,}` | Total Transaksi Unik: `{total_transaksi:,}`")
        if total_rows == 0:
            st.warning("⚠️ Data kosong. Silakan filter tanggal terlebih dahulu.")
            st.stop()
    else:
        st.warning("⚠️ Kolom tanggal tidak tersedia.")
        st.stop()

    st.success("Klik tombol di bawah untuk menjalankan FP-Growth.")

    if st.button("🔍 Jalankan Analisis"):
        with st.spinner("Sedang memproses FP-Growth..."):
            freq_items, rules, simplified = run_fp_growth(df_fp, min_support, min_conf, kolom_produk=kolom_analisis)

        st.markdown("## 📌 Frequent Itemsets")
        view_items = freq_items.reset_index(drop=True)
        view_items.index = range(1, len(view_items) + 1)
        view_items.index.name = "No"
        st.dataframe(view_items, use_container_width=True)
        st.info(f"✅ Total Frequent Itemsets: {len(freq_items):,}")

        st.markdown("## 🔗 Association Rules")
        view_rules = rules[["antecedents", "consequents", "rules", "support", "confidence", "lift"]].reset_index(drop=True)
        view_rules.index = range(1, len(view_rules) + 1)
        view_rules.index.name = "No"
        st.dataframe(view_rules, use_container_width=True)
        st.info(f"📈 Total Rules: {len(rules):,}")
        st.success(f"🧠 Total Kesimpulan: {rules['kesimpulan'].count():,}")

        st.markdown("### 🧠 Kesimpulan Rekomendasi (Top 10)")
        for i, kal in enumerate(rules["kesimpulan"].head(10), start=1):
            st.markdown(f"{i}. {kal}")

        st.markdown("---")
        st.markdown("## 📎 Rules 1 Antecedent ➞ 1 Consequent")
        simp = simplified[["antecedents", "consequents", "support", "confidence", "lift"]].reset_index(drop=True)
        simp.index = range(1, len(simp) + 1)
        simp.index.name = "No"
        st.dataframe(simp, use_container_width=True)
        st.warning(f"⚫ Total Simplified Rules (1 ➞ 1): {len(simplified):,}")

        st.markdown("### 🧠 Kesimpulan Simplified (Top 10)")
        for i, kal in enumerate(simplified["kesimpulan"].head(10), start=1):
            st.markdown(f"{i}. {kal}")

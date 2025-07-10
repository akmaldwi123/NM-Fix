import streamlit as st
from config.db_connection import load_transactions, load_kategori
from utils.fp_growth import run_fp_growth
import pandas as pd

st.set_page_config(layout="wide")

# Load CSS
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Judul Header (revisi jarak & padding)
st.markdown("""
<div style="background-color:#006e6d;padding:30px;border-radius:10px;text-align:center;">
    <h2 style="color:white;margin:0;padding:0;line-height:1;">FP-Growth Dashboard<br>Nuhsantara Merchandise</h2>
</div>
""", unsafe_allow_html=True)

# Sidebar
page = st.sidebar.radio("\U0001F4C1 Menu Navigasi", ["\U0001F4E5 Upload File", "\U0001F4C3 Data Transaksi", "\U0001F4CA FP-Growth Analisis"])

uploaded_file = None
if page == "\U0001F4E5 Upload File":
    st.subheader("\U0001F4C2 Upload File Transaksi")
    uploaded_file = st.file_uploader("Unggah file Excel atau CSV", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                uploaded_df = pd.read_csv(uploaded_file)
            else:
                uploaded_df = pd.read_excel(uploaded_file)

            # Validasi kolom wajib
            required = set(["no_transaksi"])
            if not required.issubset(uploaded_df.columns):
                st.error("File harus memiliki minimal kolom: no_transaksi dan nama_produk atau kategori_produk")
            else:
                col_detected = "nama_produk" if "nama_produk" in uploaded_df.columns else "kategori_produk"
                st.success("File berhasil diunggah dan dikenali!")
                st.dataframe(uploaded_df.head())
                st.session_state.df_uploaded = uploaded_df[["no_transaksi", col_detected] + (["tanggal"] if "tanggal" in uploaded_df.columns else [])].copy()
                st.session_state.kolom_produk = col_detected
        except Exception as e:
            st.error(f"Gagal membaca file: {e}")

# Analisis Berdasarkan
basis_opsi = st.sidebar.radio("🧾 Analisis Berdasarkan:", ["Nama Produk", "Kategori Produk"])
kolom_analisis = "nama_produk" if basis_opsi == "Nama Produk" else "kategori_produk"
# Fungsi load data
basis_opsi = st.sidebar.radio("\U0001F4C8 Analisis Berdasarkan:", ["Nama Produk", "Kategori Produk"])

# Tentukan sumber data
if "df_uploaded" in st.session_state:
    df = st.session_state.df_uploaded
    basis = "Nama Produk" if st.session_state.kolom_produk == "nama_produk" else "Kategori Produk"
else:
    if basis_opsi == "Nama Produk":
        df = load_transactions()
    else:
        df = load_kategori()
        df.rename(columns={"kategori_produk": "nama_produk"}, inplace=True)
    basis = basis_opsi

# Halaman Data Transaksi
if page == "\U0001F4C3 Data Transaksi":
    st.subheader("\U0001F4C3 Data Transaksi")
    df_view = df.copy()

    if "tanggal" in df_view.columns:
        tanggal_tersedia = sorted(df_view["tanggal"].unique())
        tgl_start, tgl_end = st.date_input(
            "Filter tanggal:",
            value=(min(tanggal_tersedia), max(tanggal_tersedia))
        )

        # Ubah input date menjadi Timestamp
        tgl_start = pd.to_datetime(tgl_start)
        tgl_end = pd.to_datetime(tgl_end)

        # Pastikan kolom tanggal juga dalam datetime format
        df_view["tanggal"] = pd.to_datetime(df_view["tanggal"])

        # Filter berdasarkan rentang tanggal
        df_view = df_view[
            (df_view["tanggal"] >= tgl_start) & (df_view["tanggal"] <= tgl_end)
        ]

        # Format hanya tanggal saja (tanpa jam)
        df_view["tanggal"] = df_view["tanggal"].dt.date

         # Urutkan berdasarkan tanggal
        df_view = df_view.sort_values(by="tanggal")

        # ✅ Simpan ke session_state agar digunakan di halaman FP-Growth
        st.session_state["filtered_df"] = df_view

    # Tampilkan tabel
    df_view.index = range(1, len(df_view) + 1)
    df_view.index.name = "No"
    st.dataframe(df_view, use_container_width=True)

     # Statistik
    total_rows = df_view.shape[0]
    total_transaksi = df_view["no_transaksi"].nunique()
    st.info(f"\U0001F522 Total baris data: {total_rows:,} | Total transaksi unik: {total_transaksi:,}")

# Halaman Analisis
elif page == "\U0001F4CA FP-Growth Analisis":
    st.markdown("### \u2699\ufe0f Parameter Analisis")
    min_support = st.slider("Minimum Support", 0.01, 1.0, 0.01, 0.01)
    min_conf = st.slider("Minimum Confidence", 0.01, 1.0, 0.60, 0.01)

    # Gunakan data dari session state (hasil filter tanggal)
    if "filtered_df" in st.session_state:
        df_fp = st.session_state["filtered_df"]
    else:
        df_fp = df  # fallback ke df default (tidak difilter)

    # Validasi Data FP-Growth
    st.markdown("### 🧾 Informasi Data yang Akan Dianalisis")

    if "tanggal" in df_fp.columns:
        tanggal_tersedia = sorted(df_fp["tanggal"].unique())
        min_tanggal = min(tanggal_tersedia)
        max_tanggal = max(tanggal_tersedia)
        total_rows = df_fp.shape[0]
        total_transaksi = df_fp["no_transaksi"].nunique()


        st.info(f"📆 Periode Tanggal: `{min_tanggal}` s.d. `{max_tanggal}`")
        st.info(f"🔢 Total Baris Data: `{total_rows:,}` | Total Transaksi Unik: `{total_transaksi:,}`")

        if total_rows == 0:
            st.warning("⚠️ Data kosong! Silakan sesuaikan filter tanggal di halaman *Data Transaksi* terlebih dahulu.")
            st.stop()
    else:
        st.warning("⚠️ Kolom tanggal tidak ditemukan. Tidak bisa lanjut FP-Growth.")
        st.stop()

    st.success("Klik tombol di bawah untuk menjalankan FP-Growth.")

    if st.button("\U0001F50D Jalankan Analisis"):
        with st.spinner("Sedang memproses FP-Growth..."):
            freq_items, rules, simplified = run_fp_growth(df_fp, min_support, min_conf)

        st.markdown("## \U0001F4CC Frequent Itemsets")
        view_items = freq_items.reset_index(drop=True)
        view_items.index = range(1, len(view_items) + 1)
        view_items.index.name = "No"
        st.dataframe(view_items, use_container_width=True)
        st.info(f"\u2705 Total Frequent Itemsets: {len(freq_items):,}")

        st.markdown("## \U0001F517 Association Rules")
        view_rules = rules[["antecedents", "consequents", "rules", "support", "confidence", "lift"]].reset_index(drop=True)
        view_rules.index = range(1, len(view_rules) + 1)
        view_rules.index.name = "No"
        st.dataframe(view_rules, use_container_width=True)
        st.info(f"\U0001F4C8 Total Rules: {len(rules):,}")
        st.success(f"\U0001F9E0 Total Kesimpulan: {rules['kesimpulan'].count():,}")

        st.markdown("### \U0001F9E0 Kesimpulan Rekomendasi (Top 10)")
        for i, kal in enumerate(rules["kesimpulan"].head(10), start=1):
            st.markdown(f"{i}. {kal}")

        st.markdown("---")
        st.markdown("## \U0001F4CE Rules 1 Antecedent \u279e 1 Consequent")
        simp = simplified[["antecedents", "consequents", "support", "confidence", "lift"]].reset_index(drop=True)
        simp.index = range(1, len(simp) + 1)
        simp.index.name = "No"
        st.dataframe(simp, use_container_width=True)
        st.warning(f"\u26ab Total Simplified Rules (1 \u279e 1): {len(simplified):,}")

        st.markdown("### \U0001F9E0 Kesimpulan Simplified (Top 10)")
        for i, kal in enumerate(simplified["kesimpulan"].head(10), start=1):
            st.markdown(f"{i}. {kal}")

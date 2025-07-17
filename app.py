import streamlit as st
import streamlit.components.v1 as components
from config.db_connection import load_transactions, load_kategori
from utils.fp_growth import run_fp_growth
import pandas as pd
import base64
from PIL import Image

st.set_page_config(
    page_title="Nuhsantara  Merchandise     ",
    page_icon="https://raw.githubusercontent.com/akmaldwi123/NM-Fix/main/static/logoo.png",
    layout="wide",
)

# ====== Gunakan st.query_params yang terbaru ======
query_params = st.query_params

if "global_page" in query_params:
    st.session_state.global_page = query_params["global_page"]
if "page" in query_params:
    st.session_state.page = query_params["page"]

# Inisialisasi default jika belum ada
if "global_page" not in st.session_state:
    st.session_state.global_page = "Beranda"
if "page" not in st.session_state:
    st.session_state.page = "Upload File"


# ===== Fungsi untuk update query params secara lengkap =====
def update_query_params(
    global_page=None, page=None, remove_keys=None, extra_params=None
):
    params = st.query_params.to_dict()

    if remove_keys:
        for key in remove_keys:
            params.pop(key, None)

    if global_page is not None:
        params["global_page"] = global_page
    if page is not None:
        params["page"] = page
    if extra_params:
        params.update(extra_params)
    st.query_params.from_dict(params)


def format_frozenset(fset):
    if isinstance(fset, frozenset):
        return ", ".join(sorted(fset))
    return fset


# CSS #
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ===== LANDING PAGE =====
if st.session_state.global_page == "Beranda":
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown(
            '<div class="landing-title">Selamat Datang di Sistem Analisis Data<br>Nuhsantara Merchandise</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="landing-desc">Sistem ini menyajikan visualisasi interaktif atas data penjualan dan persediaan barang<br>Sales and Inventory dapat membantu memantau tren, performa marketplace dan sales, serta efisiensi distribusi stok<br>FP-Growth digunakan untuk mengeksplorasi pola pembelian dan asosiasi antar produk<br>Dapatkan insight strategis untuk pengambilan keputusan bisnis berbasis data secara cepat dan akurat</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="landing-buttons-left">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Sales and Inventory", key="btn_bi"):
                st.session_state.global_page = "Sales and Inventory"
                update_query_params(
                    global_page="Sales and Inventory",
                    remove_keys=["page", "tgl_start", "tgl_end"],
                )
                st.rerun()
        with col2:
            if st.button("Analisis FP-Growth", key="btn_fp"):
                st.session_state.global_page = "FP-Growth"
                st.session_state.page = "Upload File"
                update_query_params(
                    global_page="FP-Growth",
                    remove_keys=["page", "tgl_start", "tgl_end"],
                )
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        logo_img = Image.open("static/logoo.png")
        st.image(logo_img, width=400)

# ===== POWER BI PAGE =====
elif st.session_state.global_page == "Sales and Inventory":
    if st.button("← Kembali ke Beranda"):
        st.session_state.global_page = "Beranda"
        update_query_params(
            global_page="Beranda", remove_keys=["page", "tgl_start", "tgl_end"]
        )
        st.rerun()

    components.iframe(
        "https://app.powerbi.com/view?r=eyJrIjoiYjViM2Q4NzMtM2U0Ny00OWM4LWJjNjUtZTFjN2M5YTEzODAwIiwidCI6IjkwYWZmZTBmLWMyYTMtNDEwOC1iYjk4LTZjZWI0ZTk0ZWYxNSIsImMiOjEwfQ%3D%3D&navContentPaneEnabled=false&filterPaneEnabled=false&toolbarHidden=true",
        height=600,
        width=1200,
    )
# &navContentPaneEnabled=false&filterPaneEnabled=false&toolbarHidden=true"
# ========== FP-GROWTH PAGE ==========
elif st.session_state.global_page == "FP-Growth":
    # Inisialisasi session state
    if "page" not in st.session_state:
        st.session_state.page = "Upload File"
    if "basis_opsi" not in st.session_state:
        st.session_state.basis_opsi = "Nama Produk"

    page = st.session_state.page
    kolom_analisis = (
        "nama_produk"
        if st.session_state.basis_opsi == "Nama Produk"
        else "kategori_produk"
    )

    #  Fungsi fallback jika belum upload file
    def get_current_df():
        if "df_uploaded" in st.session_state:
            return st.session_state.df_uploaded.copy()
        elif kolom_analisis == "nama_produk":
            return load_transactions()
        else:
            return load_kategori()

    #  Fungsi download template
    def generate_download_link(file_path, label="📥 Unduh Template File"):
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="template.xlsx">{label}</a>'
        return href

    # ========== SIDEBAR ==========
    with st.sidebar:
        st.image("static/logoo.png", width=230)

        st.markdown("**Menu Navigasi**")
        menu_options = {
            "Upload File": "📤 Upload File",
            "Data Transaksi": "📋 Data Transaksi",
            "FP-Growth Analisis": "📈 FP-Growth Analisis",
        }

        selected_menu = st.radio(
            label="",
            options=list(menu_options.keys()),
            index=list(menu_options.keys()).index(st.session_state.page),
            format_func=lambda x: menu_options[x],
            key="menu_navigasi",
            label_visibility="collapsed",
        )
        st.session_state.page = selected_menu
        page = selected_menu

        st.markdown("**Analisis Berdasarkan**")
        basis_options = {
            "Nama Produk": "📦 Nama Produk",
            "Kategori Produk": "🏷️ Kategori Produk",
        }

        selected_basis = st.radio(
            label="",
            options=list(basis_options.keys()),
            index=list(basis_options.keys()).index(st.session_state.basis_opsi),
            format_func=lambda x: basis_options[x],
            key="basis_analisis",
            label_visibility="collapsed",
        )
        st.session_state.basis_opsi = selected_basis
        kolom_analisis = (
            "nama_produk" if selected_basis == "Nama Produk" else "kategori_produk"
        )

    if st.button("← Kembali ke Beranda"):
        st.session_state.global_page = "Beranda"
        update_query_params(
            global_page="Beranda", remove_keys=["page", "tgl_start", "tgl_end"]
        )
        st.rerun()

    # ========== HALAMAN: UPLOAD FILE ==========
    if page == "Upload File":
        st.subheader("Upload File Transaksi")

        uploaded_file = st.file_uploader(
            "**Unggah file Excel atau CSV**", type=["csv", "xlsx"]
        )

        st.markdown(generate_download_link("template.xlsx"), unsafe_allow_html=True)

        st.markdown(
            """
        <div class='catatan-upload'>
            <strong>Catatan:</strong><br>
            File yang diunggah harus memiliki kolom berikut:<br>
            <ul class='kolom-list'>
                <li><span class="highlight-kolom">NO TRANSAKSI</span></li>
                <li><span class="highlight-kolom">NAMA PRODUK</span> atau <span class="highlight-kolom">KATEGORI PRODUK</span></li>
                <li><span class="highlight-kolom">TANGGAL</span> (opsional untuk filter berdasarkan waktu)</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        if uploaded_file:
            try:
                df_uploaded = (
                    pd.read_csv(uploaded_file)
                    if uploaded_file.name.endswith(".csv")
                    else pd.read_excel(uploaded_file)
                )
                rename_map = {
                    "NO TRANSAKSI": "no_transaksi",
                    "NAMA PRODUK": "nama_produk",
                    "KATEGORI PRODUK": "kategori_produk",
                    "TANGGAL": "tanggal",
                }
                df_uploaded.rename(
                    columns=lambda x: rename_map.get(x.strip().upper(), x), inplace=True
                )

                if df_uploaded.empty:
                    st.error("File yang diunggah kosong.")
                    st.stop()

                if "no_transaksi" not in df_uploaded.columns:
                    st.error("Kolom `NO TRANSAKSI` tidak ditemukan.")
                    st.stop()

                if kolom_analisis not in df_uploaded.columns:
                    kolom_hilang = kolom_analisis.replace("_", " ").upper()
                    st.error(f"Kolom {kolom_hilang} tidak ditemukan.")
                    st.stop()

                selected_cols = ["no_transaksi", kolom_analisis]
                if "tanggal" in df_uploaded.columns:
                    selected_cols.append("tanggal")

                df_filtered = df_uploaded[selected_cols].copy()
                st.session_state.df_uploaded = df_filtered
                st.success("File berhasil diunggah!")
                preview_df = df_filtered.head(10).copy()
                preview_df.columns = [
                    col.replace("_", " ").title() for col in preview_df.columns
                ]
                preview_df.index = range(1, len(preview_df) + 1)
                preview_df.index.name = "No"
                st.dataframe(preview_df)

            except Exception as e:
                st.error(f"Gagal membaca file")

    elif page == "Data Transaksi":
        st.subheader("Data Transaksi")
        df = get_current_df()

        if df.empty:
            st.warning(
                "Data kosong. Silakan unggah file atau pastikan koneksi ke database aktif."
            )
            st.stop()

        df_view = df.copy()

        if "tanggal" in df_view.columns:
            tanggal_tersedia = sorted(pd.to_datetime(df_view["tanggal"]).unique())
            tanggal_range = st.date_input(
                "**Filter tanggal**", (min(tanggal_tersedia), max(tanggal_tersedia))
            )

            if isinstance(tanggal_range, tuple) and len(tanggal_range) == 2:
                tgl_start, tgl_end = pd.to_datetime(tanggal_range[0]), pd.to_datetime(
                    tanggal_range[1]
                )
                df_view["tanggal"] = pd.to_datetime(df_view["tanggal"])
                df_view = df_view[
                    (df_view["tanggal"] >= tgl_start) & (df_view["tanggal"] <= tgl_end)
                ]
                df_view["tanggal"] = df_view["tanggal"].dt.date
                df_view = df_view.sort_values("tanggal")
                st.session_state["filtered_df"] = df_view
            else:
                st.warning(
                    "Silakan pilih rentang tanggal lengkap (awal dan akhir) untuk memfilter data."
                )
                st.stop()
        else:
            st.session_state["filtered_df"] = df_view

        tampilkan_kolom = ["no_transaksi", kolom_analisis]
        if "tanggal" in df_view.columns:
            tampilkan_kolom.append("tanggal")

        try:
            df_tampil = df_view[tampilkan_kolom].copy()
            df_tampil = df_tampil.rename(columns=lambda x: x.replace("_", " ").title())
            df_tampil.index = range(1, len(df_tampil) + 1)
            df_tampil.index.name = "No"
            st.dataframe(df_tampil, use_container_width=True)
            st.info(
                f"Total Baris Data: {df_view.shape[0]:,} | "
                f"Total Transaksi: {df_view['no_transaksi'].nunique():,}"
            )
        except KeyError as e:
            st.error(f"Kolom tidak ditemukan")
            st.stop()

    elif page == "FP-Growth Analisis":
        df_fp = st.session_state.get("filtered_df", get_current_df())

        if df_fp.empty:
            st.warning("Data kosong. Silakan unggah atau filter terlebih dahulu.")
            st.stop()

        if kolom_analisis not in df_fp.columns:
            st.warning("Kolom analisis tidak tersedia.")
            st.stop()

        if "tanggal" in df_fp.columns:
            tanggal_tersedia = sorted(pd.to_datetime(df_fp["tanggal"]).unique())
            min_tanggal = min(tanggal_tersedia).date()
            max_tanggal = max(tanggal_tersedia).date()
            periode_tanggal_html = f"<p><strong>Periode Tanggal:</strong> `{min_tanggal}` s.d. `{max_tanggal}`</p>"
        else:
            periode_tanggal_html = ""

        st.markdown(
            f"""
            <div class="card">
            <h4>Data yang Akan Dianalisis</h4>
            {periode_tanggal_html}
            <p><strong>Total Baris Data:</strong> `{df_fp.shape[0]:,}` | <strong>Total Transaksi:</strong> `{df_fp['no_transaksi'].nunique():,}`</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.success("Klik tombol dibawah untuk memulai analisis")
        if st.button("Mulai Analisis"):
            with st.spinner("Sedang memproses FP-Growth..."):
                try:
                    freq_items, rules, simplified = run_fp_growth(
                        df_fp, kolom_produk=kolom_analisis
                    )
                    if freq_items.empty:
                        st.warning(
                            "Tidak ditemukan kombinasi produk yang sering dibeli bersamaan."
                        )

                    elif rules.empty:
                        st.warning(
                            "Tidak ditemukan aturan asosiasi yang valid dari kombinasi produk."
                        )

                    else:
                        st.markdown("**Daftar Produk yang Sering Dibeli Bersamaan**")
                        view_items = freq_items.rename(
                            columns={"itemsets": "Kombinasi Produk"}
                        ).reset_index(drop=True)
                        view_items["Kombinasi Produk"] = view_items[
                            "Kombinasi Produk"
                        ].apply(format_frozenset)
                        view_items.index = range(1, len(view_items) + 1)
                        view_items.index.name = "No"
                        st.dataframe(view_items, use_container_width=True)
                        st.info(
                            f"Total Kombinasi Produk yang Sering Muncul: {len(freq_items):,}"
                        )
                        st.markdown("---")
                        st.markdown("**Aturan Asosiasi dari Kombinasi Produk**")
                        view_rules = rules[
                            [
                                "antecedents",
                                "consequents",
                                "support",
                                "confidence",
                                "lift",
                            ]
                        ].copy()
                        view_rules.columns = [
                            "Produk Awal",
                            "Produk Disarankan",
                            "Support",
                            "Confidence",
                            "Lift",
                        ]
                        view_rules["Produk Awal"] = view_rules["Produk Awal"].apply(
                            format_frozenset
                        )
                        view_rules["Produk Disarankan"] = view_rules[
                            "Produk Disarankan"
                        ].apply(format_frozenset)
                        view_rules.index = range(1, len(view_rules) + 1)
                        view_rules.index.name = "No"
                        st.dataframe(view_rules, use_container_width=True)
                        st.info(f"Total Aturan Asosiasi: {len(rules):,}")

                        # Penjelasan Metrik Support, Confidence, dan Lift
                        st.markdown("**Penjelasan Metrik Evaluasi**")
                        st.markdown(
                            """
                            <div class="kombinasi-card">
                                <p><strong>🔹 Support</strong><br>
                                Mengukur seberapa sering kombinasi produk muncul dalam seluruh transaksi.
                                Semakin tinggi nilai support, semakin populer kombinasi produk tersebut</p>
                                <p><strong>🔹 Confidence</strong><br>
                                Mengukur seberapa besar kemungkinan produk B dibeli setelah produk A dibeli.
                                Semakin tinggi confidence, semakin kuat asosiasi antar produk</p>
                                <p><strong>🔹 Lift</strong><br>
                                Mengukur kekuatan asosiasi antara dua produk dibandingkan dengan peluang terpisah.
                                Nilai lift &gt; 1 menunjukkan asosiasi positif</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.markdown("<br>", unsafe_allow_html=True)

                        st.markdown("**Rekomendasi Kombinasi Produk (Top 10)**")
                        for i, kal in enumerate(rules["kesimpulan"].head(10), start=1):
                            kalimat = kal.replace(
                                "**Kombinasi produk", "<strong>Kombinasi produk"
                            ).replace("memiliki:**", "memiliki:</strong>")
                            css_class = "odd" if i % 2 == 1 else "even"
                            st.markdown(
                                f'<div class="kombinasi-card {css_class}"><p><span style="font-weight:bold;">{i}. </span>{kalimat}</p></div>',
                                unsafe_allow_html=True,
                            )

                        st.markdown("---")
                        st.markdown("**Aturan 1 Produk Awal ➞ 1 Produk Disarankan**")
                        simp = simplified[
                            [
                                "antecedents",
                                "consequents",
                                "support",
                                "confidence",
                                "lift",
                            ]
                        ].copy()
                        simp.columns = [
                            "Produk Awal",
                            "Produk Disarankan",
                            "Support",
                            "Confidence",
                            "Lift",
                        ]
                        simp["Produk Awal"] = simp["Produk Awal"].apply(
                            format_frozenset
                        )
                        simp["Produk Disarankan"] = simp["Produk Disarankan"].apply(
                            format_frozenset
                        )
                        simp.index = range(1, len(simp) + 1)
                        simp.index.name = "No"
                        st.dataframe(simp, use_container_width=True)
                        st.info(
                            f"Total Aturan 1 Produk Awal ➞ 1 Produk Disarankan: {len(simplified):,}"
                        )
                        st.markdown("<br>", unsafe_allow_html=True)

                        st.markdown("**Rekomendasi Kombinasi Produk 1 ➞ 1 (Top 10)**")
                        for i, kal in enumerate(
                            simplified["kesimpulan"].head(10), start=1
                        ):
                            kalimat = kal.replace(
                                "**Kombinasi produk", "<strong>Kombinasi produk"
                            ).replace("memiliki:**", "memiliki:</strong>")
                            css_class = "odd" if i % 2 == 1 else "even"
                            st.markdown(
                                f'<div class="kombinasi-card {css_class}"><p><span style="font-weight:bold;">{i}. </span>{kalimat}</p></div>',
                                unsafe_allow_html=True,
                            )

                        # RINGKASAN KOMBINASI 1 ➞ 1 TANPA PENJELASAN (DALAM SATU CARD)
                        st.markdown("---")
                        st.markdown(
                            "**Rekomendasi Kombinasi Produk 1 ➞ 1 (Tanpa Penjelasan)**"
                        )

                        # Ambil semua data ringkasan dan urutkan berdasarkan indeks
                        ringkasan_rows = simplified.reset_index(drop=True)

                        # Tampilkan hanya 10 item pertama
                        ringkasan_text = ""
                        for idx in range(10):
                            row = ringkasan_rows.iloc[idx]
                            produk_awal = ", ".join(row["antecedents"])
                            produk_disarankan = ", ".join(row["consequents"])
                            ringkasan_text += f"{idx+1}. <strong>{produk_awal}</strong> → <strong>{produk_disarankan}</strong><br>"

                        # Tampilkan di card
                        st.markdown(
                            f"""
                            <div class="card ringkasan-kumpulan">
                                {ringkasan_text}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        st.markdown("<br>", unsafe_allow_html=True)
                        # Expander untuk tampilkan lebih banyak
                        with st.expander(
                            "**Tampilkan Semua Aturan (Tanpa Penjelasan Top 10)**"
                        ):
                            semua_text = ""
                            for idx, row in ringkasan_rows.iterrows():
                                produk_awal = ", ".join(row["antecedents"])
                                produk_disarankan = ", ".join(row["consequents"])
                                semua_text += f"{idx+1}. <strong>{produk_awal}</strong> → <strong>{produk_disarankan}</strong><br>"
                            st.markdown(
                                f"""
                                <div class="kombinasi-card" style="margin-top: 1rem;">
                                    {semua_text}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                except ValueError as ve:
                    st.error(
                        f"Proses FP-Growth gagal, tidak ditemukan kombinasi produk yang sering dibeli bersamaan / aturan asosiasi"
                    )
                except Exception as e:
                    st.error(f"Tidak Ditemukan")

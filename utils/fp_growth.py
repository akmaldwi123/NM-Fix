from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import pandas as pd


def format_frozenset(x):
    return ", ".join(sorted(x)) if isinstance(x, frozenset) else str(x)


def run_fp_growth(df_transaksi, kolom_produk="nama_produk"):
    # Hitung total transaksi unik
    total_transaksi = df_transaksi["no_transaksi"].nunique()

    # Tetapkan min_support dan min_confidence otomatis berdasarkan total transaksi
    if total_transaksi <= 200:
        min_support = 0.3
        min_confidence = 0.6
    elif total_transaksi <= 500:
        min_support = 0.1
        min_confidence = 0.6
    elif total_transaksi <= 1000:
        min_support = 0.02
        min_confidence = 0.7
    elif total_transaksi <= 10000:
        min_support = 0.01
        min_confidence = 0.7
    elif total_transaksi <= 50000:
        min_support = 0.02
        min_confidence = 0.7
    elif total_transaksi <= 100000:
        min_support = 0.01
        min_confidence = 0.7
    else:
        min_support = 0.005
        min_confidence = 0.7

    # Grouping transaksi berdasarkan kolom produk dinamis
    grouped = df_transaksi.groupby("no_transaksi")[kolom_produk].apply(list).tolist()

    # Transaction encoding
    te = TransactionEncoder()
    te_ary = te.fit(grouped).transform(grouped)
    df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

    # Jalankan FP-Growth
    freq_items = fpgrowth(df_encoded, min_support=min_support, use_colnames=True)

    # Tambah kolom length & frekuensi
    freq_items["Panjang Kombinasi"] = freq_items["itemsets"].apply(len)
    freq_items["Frekuensi"] = (freq_items["support"] * total_transaksi).astype(int)

    # Urutkan itemsets
    freq_items = freq_items.sort_values(
        by=["Panjang Kombinasi", "Frekuensi", "support"], ascending=[True, False, False]
    )

    # Format itemsets agar tidak tampil sebagai frozenset
    freq_items["itemsets"] = freq_items["itemsets"].apply(format_frozenset)

    # Buat aturan asosiasi
    rules = association_rules(
        freq_items, metric="confidence", min_threshold=min_confidence
    )
    rules = rules[rules["lift"] > 1]

    # Format kolom antecedents dan consequents agar tidak tampil sebagai frozenset
    rules["antecedents"] = rules["antecedents"].apply(format_frozenset)
    rules["consequents"] = rules["consequents"].apply(format_frozenset)

    # Format aturan menjadi string readable
    rules["rules"] = (
        rules["antecedents"].apply(lambda x: ", ".join(list(x)))
        + " → "
        + rules["consequents"].apply(lambda x: ", ".join(list(x)))
    )
    rules = rules.sort_values(by=["confidence", "lift"], ascending=[False, False])

    # Fungsi aman untuk membuat kesimpulan
    def buat_kesimpulan(row):
        try:
            return (
                f"**Kombinasi produk “{', '.join(list(row['antecedents']))} → {', '.join(list(row['consequents']))}” memiliki:**\n\n"
                f"- **Support** sebesar **{row['support']:.2%}**, artinya kombinasi ini muncul sebanyak {row['support']:.2%} dari total seluruh transaksi\n"
                f"- **Confidence** sebesar **{row['confidence']:.2%}**, mmenunjukkan bahwa dari semua transaksi yang mengandung produk awal, "
                f"sebanyak {row['confidence']:.2%} di antaranya juga membeli produk disarankan\n"
                f"- **Lift** sebesar **{row['lift']:.2f}**, berarti probabilitas pembelian produk awal dan produk disarankan secara bersamaan adalah "
                f"{row['lift']:.2f} kali lebih tinggi dibandingkan jika pembelian tersebut terjadi secara kebetulan atau tidak saling terkait\n\n"
            )
        except Exception as e:
            return f"Kesimpulan tidak dapat dihitung (Error: {str(e)})"

    # Tambah kolom kesimpulan (AMAN)
    rules["kesimpulan"] = rules.apply(buat_kesimpulan, axis=1)

    # Versi simplified: 1 antecedent & 1 consequent
    simplified = rules[
        (rules["antecedents"].apply(len) == 1) & (rules["consequents"].apply(len) == 1)
    ].copy()

    simplified["kesimpulan"] = simplified.apply(buat_kesimpulan, axis=1)

    return freq_items, rules, simplified

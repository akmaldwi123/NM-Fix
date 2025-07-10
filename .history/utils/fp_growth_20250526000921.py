from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import pandas as pd

def run_fp_growth(df_transaksi, min_support, min_confidence, kolom_produk="nama_produk"):
    # Grouping transaksi berdasarkan kolom produk dinamis
    grouped = df_transaksi.groupby("no_transaksi")[kolom_produk].apply(list).tolist()

    # Transaction encoding
    te = TransactionEncoder()
    te_ary = te.fit(grouped).transform(grouped)
    df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

    # Jalankan FP-Growth
    freq_items = fpgrowth(df_encoded, min_support=min_support, use_colnames=True)

    # Tambah kolom length & frekuensi
    total_transaksi = len(grouped)
    freq_items["length"] = freq_items["itemsets"].apply(len)
    freq_items["frekuensi"] = (freq_items["support"] * total_transaksi).astype(int)

    # Urutkan itemsets
    freq_items = freq_items.sort_values(by=["length", "frekuensi", "support"], ascending=[True, False, False])

    # Buat aturan asosiasi
    rules = association_rules(freq_items, metric="confidence", min_threshold=min_confidence)
    rules = rules[rules["lift"] > 1]
    rules["rules"] = rules["antecedents"].apply(lambda x: ', '.join(list(x))) + " → " + rules["consequents"].apply(lambda x: ', '.join(list(x)))
    rules = rules.sort_values(by=["confidence", "lift"], ascending=[False, False])

    # Tambah kesimpulan berbentuk kalimat
    rules["kesimpulan"] = rules.apply(lambda row: (
    f"📊 Jika pelanggan membeli **{', '.join(list(row['antecedents']))}**, maka ada peluang besar mereka juga akan membeli "
    f"**{', '.join(list(row['consequents']))}**.\n\n"
    f"- **Support** sebesar **{row['support']:.2%}**, artinya kombinasi ini muncul di {row['support']:.2%} dari total seluruh transaksi.\n"
    f"- **Confidence** sebesar **{row['confidence']:.2%}**, menunjukkan bahwa dari semua transaksi yang mengandung produk "
    f"{', '.join(list(row['antecedents']))}, sebanyak {row['confidence']:.2%} di antaranya juga membeli produk "
    f"{', '.join(list(row['consequents']))}.\n"
    f"- **Lift** sebesar **{row['lift']:.2f}**, yang berarti probabilitas pembelian kedua produk secara bersamaan adalah "
    f"{row['lift']:.2f} kali lebih tinggi dibandingkan jika pembelian tersebut terjadi secara kebetulan atau tidak saling terkait.\n\n"
    ), axis=1)


    # Versi simplified: 1 antecedent & 1 consequent
    simplified = rules[
        (rules["antecedents"].apply(len) == 1) &
        (rules["consequents"].apply(len) == 1)
    ].copy()

    simplified["kesimpulan"] = simplified.apply(lambda row: (
        f"Jika membeli **{', '.join(list(row['antecedents']))}**, maka kemungkinan besar juga membeli **{', '.join(list(row['consequents']))}** "
        f"(Support: {row['support']:.2f}, Confidence: {row['confidence']:.2f}, Lift: {row['lift']:.2f})"
    ), axis=1)

    return freq_items, rules, simplified

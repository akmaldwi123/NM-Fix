from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import pandas as pd

def run_fp_growth(df_transaksi, min_support, min_confidence):
    grouped = df_transaksi.groupby("no_transaksi")["nama_produk"].apply(list).tolist()
    te = TransactionEncoder()
    te_ary = te.fit(grouped).transform(grouped)
    df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

    # Jalankan FP-Growth
    freq_items = fpgrowth(df_encoded, min_support=min_support, use_colnames=True)
    
    # Tambah panjang & frekuensi
    total_transaksi = len(grouped)
    freq_items["length"] = freq_items["itemsets"].apply(lambda x: len(x))
    freq_items["frekuensi"] = (freq_items["support"] * total_transaksi).astype(int)

    freq_items = freq_items.sort_values(by=["length", "frekuensi", "support"], ascending=[True, False, False])

    # Aturan asosiasi
    rules = association_rules(freq_items, metric="confidence", min_threshold=min_confidence)
    rules = rules[rules["lift"] > 1]
    rules["rules"] = rules["antecedents"].apply(lambda x: ', '.join(list(x))) + " → " + rules["consequents"].apply(lambda x: ', '.join(list(x)))
    rules = rules.sort_values(by=["confidence", "lift"], ascending=[False, False])

    # Versi kalimat natural
    rules["kesimpulan"] = rules.apply(lambda row: (
        f"Jika membeli **{', '.join(list(row['antecedents']))}**, maka kemungkinan besar juga membeli **{', '.join(list(row['consequents']))}** "
        f"(Support: {row['support']:.2f}, Confidence: {row['confidence']:.2f}, Lift: {row['lift']:.2f})"
    ),
    axis=1)

    rules["kesimpulan"] = rules.apply(lambda row:
        f"Jika membeli **{', '.join(row['antecedents'])}**, maka cenderung membeli **{', '.join(row['consequents'])}** "
        f"(Support: {row['support']:.2f}, Confidence: {row['confidence']:.2f}, Lift: {row['lift']:.2f})", axis=1)

    # Versi simplified (1 antecedent, >1 consequent)
    simplified = rules[(rules["antecedents"].apply(len) == 1) & (rules["consequents"].apply(len) > 1)]

    return freq_items, rules, simplified

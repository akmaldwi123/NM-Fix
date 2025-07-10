from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import pandas as pd

def run_fp_growth(df_transaksi, min_support, min_confidence):
    grouped = df_transaksi.groupby("no_transaksi")["nama_produk"].apply(list).tolist()
    te = TransactionEncoder()
    te_ary = te.fit(grouped).transform(grouped)
    df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

    freq_items = fpgrowth(df_encoded, min_support=min_support, use_colnames=True)
    rules = association_rules(freq_items, metric="confidence", min_threshold=min_confidence)
    return freq_items, rules

# Hitung jumlah transaksi total
total_transaksi = df_transaksi["no_transaksi"].nunique()

# Tambahkan kolom length dan frekuensi
freq_items["length"] = freq_items["itemsets"].apply(lambda x: len(x))
freq_items["frekuensi"] = (freq_items["support"] * total_transaksi).astype(int)

# Sorting: panjang itemset naik, frekuensi turun, support turun
freq_items = freq_items.sort_values(by=["length", "frekuensi", "support"], ascending=[True, False, False])

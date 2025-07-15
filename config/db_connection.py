import pandas as pd

def load_transactions():
    fp = pd.read_csv("data/fact_penjualan.csv")
    dp = pd.read_csv("data/dim_produk.csv")
    dw = pd.read_csv("data/dim_waktu.csv")

    df = (
        fp.merge(dp, on="id_produk", how="left")
          .merge(dw, on="id_waktu", how="left")
          .loc[:, ["no_transaksi", "nama_produk", "tanggal"]]
          .sort_values("no_transaksi")
    )
    return df


def load_kategori():
    fp = pd.read_csv("data/fact_penjualan.csv")
    dp = pd.read_csv("data/dim_produk.csv")
    dw = pd.read_csv("data/dim_waktu.csv")

    df = (
        fp.merge(dp, on="id_produk", how="left")
          .merge(dw, on="id_waktu", how="left")
          .loc[:, ["no_transaksi", "kategori_produk", "tanggal"]]
          .sort_values("no_transaksi")
    )
    return df


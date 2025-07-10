import mysql.connector
import pandas as pd

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",        # Ganti jika pakai server
        user="root",             # Sesuaikan dengan MySQL kamu
        password="passwordmu",   # ← Ganti ini
        database="datawarehouse" # ← Ganti nama DB kamu
    )

def load_transactions():
    conn = get_db_connection()
    query = """
    SELECT no_transaksi, nama_produk
    FROM fact_penjualan
    JOIN dim_produk ON fact_penjualan.id_produk = dim_produk.id_produk
    ORDER BY no_transaksi;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def load_kategori():
    conn = get_db_connection()
    query = """
    SELECT no_transaksi, kategori_produk
    FROM fact_penjualan
    JOIN dim_produk ON fact_penjualan.id_produk = dim_produk.id_produk
    ORDER BY no_transaksi;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

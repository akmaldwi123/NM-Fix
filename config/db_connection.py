import mysql.connector
import pandas as pd


# Fungsi koneksi ke database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="etl_nm",
    )


# Query transaksi berdasarkan nama produk
def load_transactions():
    conn = get_db_connection()
    query = """
    SELECT fp.no_transaksi, dp.nama_produk, dw.tanggal
    FROM fact_penjualan fp
    JOIN dim_produk dp ON fp.id_produk = dp.id_produk
    JOIN dim_waktu dw ON fp.id_waktu = dw.id_waktu
    ORDER BY fp.no_transaksi;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# Query transaksi berdasarkan kategori produk
def load_kategori():
    conn = get_db_connection()
    query = """
    SELECT fp.no_transaksi, dp.kategori_produk, dw.tanggal
    FROM fact_penjualan fp
    JOIN dim_produk dp ON fp.id_produk = dp.id_produk
    JOIN dim_waktu dw ON fp.id_waktu = dw.id_waktu
    ORDER BY fp.no_transaksi;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

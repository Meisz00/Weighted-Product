import streamlit as st
import pandas as pd
import numpy as np
import os

# Fungsi Weighted Product Model
def weighted_product(df, bobot, jenis_kriteria, total_dana):
    total_bobot = sum(bobot.values())
    bobot_normalized = {k: v / total_bobot for k, v in bobot.items()}

    for col in bobot.keys():
        if jenis_kriteria[col] == "Cost":
            df[col] = 1 / df[col]

    df["Skor WPM"] = np.prod([df[col] ** bobot_normalized[col] for col in bobot.keys()], axis=0)
    df["Skor WPM Normalized"] = df["Skor WPM"] / df["Skor WPM"].sum()
    df["Dana Bantuan"] = df["Skor WPM Normalized"] * total_dana

    return df[["Sektor", "Skor WPM", "Dana Bantuan"]].sort_values(by="Skor WPM", ascending=False)

# Streamlit UI
st.set_page_config(page_title="Dana Bantuan WPM", layout="wide")

# Inisialisasi session state untuk navigasi
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

# Sidebar Menu dengan Button
with st.sidebar:
    st.header("Menu")
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_page = 'home'
    if st.button("📖 Tata Cara", use_container_width=True):
        st.session_state.current_page = 'tata_cara'
    if st.button("📊 Perhitungan", use_container_width=True):
        st.session_state.current_page = 'perhitungan'

# CSS styling
css = """
<style>
    /* Background styling */
    body {
        background-image: url('https://images.pexels.com/photos/10067197/pexels-photo-10067197.jpeg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .stApp {
        background-color: rgba(255, 255, 255, 0.7);
    }
    
    /* Target semua kemungkinan class untuk header di Streamlit */
    .element-container div.stMarkdown h1,
    header.css-18ni7ap.e8zbici2,
    div.css-1629p8f.e16nr0p31 h1,
    div.css-1629p8f.e16nr0p31 h2,
    div.css-1629p8f.e16nr0p31 h3,
    .css-10trblm.e16nr0p30,
    .css-zt5igj.ev15ef950,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stHeader"] {
        color: black !important;
    }
    /* Target untuk konten di home */
    .home-content {
        color: black !important;
    }
</style>
"""

# Halaman Home
if st.session_state.current_page == 'home':
    st.markdown(css, unsafe_allow_html=True)
    
    st.markdown("<h1 style='color: black !important;'>Aplikasi Perhitungan Dana Bantuan dengan Weighted Product</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: black !important;'>🏠 Selamat Datang di Aplikasi Dana Bantuan</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="home-content">
    Aplikasi ini dirancang untuk membantu Anda menghitung alokasi dana bantuan menggunakan metode <strong>Weighted Product Model (WPM)</strong>.
    <br><br>
    Dengan aplikasi ini, Anda dapat:
    <br>
    - Mengunggah data sektor yang membutuhkan bantuan.<br>
    - Mengatur bobot dan kriteria untuk setiap sektor.<br>
    - Menghitung dana bantuan yang sesuai berdasarkan skor.
    </div>
    """, unsafe_allow_html=True)

# Tata Cara Penggunaan
elif st.session_state.current_page == 'tata_cara':
    st.header("📖 Tata Cara Penggunaan")
    st.write("""
    1. Upload file dalam format **CSV atau Excel** yang **hanya berisi data numerik**.
    2. Pilih variabel yang akan digunakan untuk perhitungan.
    3. Tentukan bobot tiap variabel (1-5), lalu bobot akan dinormalisasi otomatis.
    4. Pilih apakah variabel termasuk **Cost** (semakin kecil semakin baik) atau **Benefit** (semakin besar semakin baik).
    5. Masukkan total dana yang tersedia.
    6. Klik **Hitung Dana Bantuan** untuk melihat hasilnya.
    """)
    
    st.subheader("📌 Keterangan Bobot")
    
    # HTML table dengan center alignment
    html_table = """
    <style>
        .custom-table {
            width: 100%;
            text-align: center;
            border-collapse: collapse;
        }
        .custom-table th, .custom-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        .custom-table th {
            background-color: #f0f2f6;
        }
    </style>
    <table class="custom-table">
        <tr>
            <th>Nilai Bobot</th>
            <th>Keterangan</th>
        </tr>
        <tr>
            <td>1</td>
            <td>Tidak terlalu penting</td>
        </tr>
        <tr>
            <td>2</td>
            <td>Kurang penting</td>
        </tr>
        <tr>
            <td>3</td>
            <td>Cukup penting</td>
        </tr>
        <tr>
            <td>4</td>
            <td>Penting</td>
        </tr>
        <tr>
            <td>5</td>
            <td>Sangat penting</td>
        </tr>
    </table>
    """
    
    st.markdown(html_table, unsafe_allow_html=True)

# Perhitungan Dana Bantuan
elif st.session_state.current_page == 'perhitungan':
    st.header("📊 Perhitungan Dana Bantuan")

    uploaded_file = st.file_uploader("Upload CSV atau Excel", type=["csv", "xlsx"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

        if df.select_dtypes(include=["object"]).shape[1] > 0:
            st.warning("⚠️ Data yang diupload mengandung kolom kategori. Harap ubah semua data menjadi numerik sebelum digunakan!")

        st.write("Data yang diupload:")
        st.dataframe(df)

        selected_columns = st.multiselect("Pilih variabel untuk perhitungan:", df.columns)

        bobot = {}
        jenis_kriteria = {}
        for col in selected_columns:
            bobot[col] = st.slider(f"Bobot untuk {col} (1-5):", 1, 5, 3)
            jenis_kriteria[col] = st.radio(f"Jenis Kriteria untuk {col}:", ["Benefit", "Cost"], horizontal=True)

        total_dana = st.number_input("Total Dana Bantuan (Rp):", min_value=0, value=1000000000, step=1000000)

        if st.button("Hitung Dana Bantuan"):
            hasil = weighted_product(df[selected_columns], bobot, jenis_kriteria, total_dana)
            st.write("📊 **Hasil Perhitungan Dana Bantuan:**")
            st.table(hasil)

            st.bar_chart(hasil.set_index("Sektor")["Dana Bantuan"])
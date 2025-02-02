import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Fungsi Weighted Product Model
def weighted_product(df, id_column, bobot, jenis_kriteria):
    calculation_df = df.copy()
    
    total_bobot = sum(bobot.values())
    bobot_normalized = {k: v / total_bobot for k, v in bobot.items()}

    for col in bobot.keys():
        if jenis_kriteria[col] == "Cost":
            calculation_df[col] = 1 / calculation_df[col]

    calculation_df["Skor WPM"] = np.prod([calculation_df[col] ** bobot_normalized[col] for col in bobot.keys()], axis=0)
    calculation_df["Skor WPM Normalized"] = calculation_df["Skor WPM"] / calculation_df["Skor WPM"].sum()
    
    result_df = pd.concat([df[id_column], calculation_df[["Skor WPM", "Skor WPM Normalized"]]], axis=1)
    return result_df.sort_values(by="Skor WPM", ascending=False)

def find_optimal_allocation(sorted_results):
    cumulative_scores = np.cumsum(sorted_results["Skor WPM Normalized"])
    optimal_count = len(cumulative_scores[cumulative_scores <= 0.8])
    return max(1, optimal_count)

def allocate_funds(result_df, total_dana, num_recipients):
    selected_df = result_df.head(num_recipients).copy()
    total_score = selected_df["Skor WPM"].sum()
    selected_df["Skor WPM Normalized"] = selected_df["Skor WPM"] / total_score
    selected_df["Dana Bantuan"] = selected_df["Skor WPM Normalized"] * total_dana
    # Bulatkan dana bantuan ke bilangan bulat
    selected_df["Dana Bantuan"] = selected_df["Dana Bantuan"].round(0).astype(int)
    return selected_df

# Streamlit UI
st.set_page_config(page_title="Dana Bantuan WPM", layout="wide")

# Inisialisasi session state untuk navigasi
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

# CSS styling
home_css = """
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
</style>
"""

table_css = """
<style>
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
    
    /* Styling untuk tabel hasil */
    .dataframe {
        margin: 0 auto;
        text-align: center !important;
    }
    .dataframe th {
        text-align: center !important;
    }
    .dataframe td {
        text-align: center !important;
    }
    /* Memastikan semua elemen dalam tabel tercentered */
     /* Styling untuk tabel hasil */
    div[data-testid="stTable"] table {
        width: 100%;
        border-collapse: collapse;
    }

    /* Header tabel */
    div[data-testid="stTable"] th {
        background-color: #f0f2f6 !important;
        font-weight: bold !important;
        text-align: center !important;
        padding: 10px !important;
        color: black !important;
    }

    /* Isi tabel */
    div[data-testid="stTable"] td {
        text-align: center !important;
        padding: 8px !important;
    }
</style>
"""

# Sidebar Menu dengan Button
with st.sidebar:
    st.header("Menu")
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_page = 'home'
    if st.button("📖 Tata Cara", use_container_width=True):
        st.session_state.current_page = 'tata_cara'
    if st.button("📊 Perhitungan", use_container_width=True):
        st.session_state.current_page = 'perhitungan'

# Halaman-halaman
if st.session_state.current_page == 'home':
    st.markdown(home_css + table_css, unsafe_allow_html=True)
    
    st.markdown("<h1 style='color: black !important;'>Perhitungan Dana Bantuan dengan Metode Weighted Product</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: black !important;'>🏠 Selamat Datang di Situs Dana Bantuan</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="home-content">
    Situs ini dirancang untuk membantu Anda menghitung alokasi dana bantuan menggunakan metode <strong>Weighted Product</strong> dengan modal yang dimiliki.
    <br><br>
    Dengan situs ini, Anda dapat:
    <br>
    - Menghitung alokasi dana bantuan untuk seluruh alternatif.<br>
    - Menghitung alokasi dana bantuan dengan jumlah alternatif yang optimal.<br>
    - Menghitung alokasi dana bantuan dengan jumlah alternatif yang diinginkan.
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_page == 'tata_cara':
    st.markdown(table_css, unsafe_allow_html=True)
    st.header("📖 Tata Cara Penggunaan")
    st.write("""
    1. Upload file dalam format **CSV atau Excel** yang **berisi data teks** hanya untuk ID/label patokan dan **berisi data numerik** untuk seluruh kriteria yang digunakan.
    2. Pilih variabel yang akan digunakan untuk perhitungan.
    3. Tentukan bobot tiap variabel (1-5) dengan ketentuan seperti tabel di bawah, lalu bobot akan dinormalisasi otomatis.
    4. Pilih apakah variabel termasuk **Cost** (semakin kecil semakin baik) atau **Benefit** (semakin besar semakin baik).
    5. Masukkan total dana yang tersedia.
    6. Pilih metode alokasi dana, apakah dana akan dibagi ke seluruh alternatif atau ada nominal tertentu.
    7. Klik **Hitung Dana Bantuan** untuk melihat hasilnya.
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

elif st.session_state.current_page == 'perhitungan':
    st.markdown(table_css, unsafe_allow_html=True)
    st.header("📊 Perhitungan Dana Bantuan")

    uploaded_file = st.file_uploader("Upload CSV atau Excel", type=["csv", "xlsx"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

        if df.select_dtypes(include=["object"]).shape[1] > 1:
            st.warning("⚠️ Data yang diupload mengandung kolom dengan tipe data teks. Harap ubah data menjadi numerik untuk kolom kriteria, kecuali kolom label/ID! (Abaikan pesan ini jika kolom kriteria sudah bertipe data numerik).")

        st.write("Data yang diupload:")
        st.dataframe(df)

        string_columns = df.select_dtypes(include=['object']).columns
        id_column = st.selectbox("Pilih kolom ID/Label:", df.columns if len(string_columns) == 0 else string_columns)
        
        available_columns = [col for col in df.columns if col != id_column]
        selected_columns = st.multiselect("Pilih variabel untuk perhitungan:", available_columns)

        bobot = {}
        jenis_kriteria = {}
        for col in selected_columns:
            with st.container():
                st.markdown(f"<div class='box'><b>{col}</b>", unsafe_allow_html=True)
                bobot[col] = st.slider(f"Bobot untuk {col} (1-5):", 1, 5, 3)
                jenis_kriteria[col] = st.radio(f"Jenis Kriteria untuk {col}:", ["Benefit", "Cost"], horizontal=True)
                st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)

        total_dana = st.number_input("Total Dana Bantuan (Rp):", min_value=0, value=1000000000, step=1000000)
        
        allocation_type = st.radio(
            "Pilih metode alokasi dana:",
            ["Alokasi untuk Seluruh Alternatif", "Alokasi untuk Jumlah Alternatif Optimal", "Alokasi Custom"],
            horizontal=True
        )

        custom_allocation_count = None
        if allocation_type == "Alokasi Custom":
            custom_allocation_count = st.number_input(
                "Jumlah penerima dana:",
                min_value=1,
                max_value=len(df),
                value=min(5, len(df))
            )

        if st.button("Hitung Dana Bantuan"):
            if len(selected_columns) > 0:
                hasil = weighted_product(df, id_column, bobot, jenis_kriteria)
                
                if allocation_type == "Alokasi untuk Seluruh Alternatif":
                    num_recipients = len(df)
                    st.write(f"📋 **Menampilkan {num_recipients} penerima dana**")
                elif allocation_type == "Alokasi untuk Jumlah Alternatif Optimal":
                    num_recipients = find_optimal_allocation(hasil)
                    st.write(f"🎯 **Jumlah optimal penerima dana: {num_recipients} penerima**")
                else:
                    num_recipients = custom_allocation_count
                    st.write(f"📋 **Menampilkan {num_recipients} penerima dana teratas**")
                
                final_results = allocate_funds(hasil, total_dana, num_recipients)
                
                st.write("📊 **Hasil Perhitungan Dana Bantuan:**")
                display_results = final_results[[id_column, "Dana Bantuan"]].copy()
                # Format Dana Bantuan sebagai string dengan format ribuan
                display_results["Dana Bantuan"] = display_results["Dana Bantuan"].apply(lambda x: f"Rp{x:,.0f}")
                st.table(display_results.set_index(id_column).rename_axis(None))

                st.write("📊 **Visualisasi Alokasi Dana:**")
                chart_data = final_results[[id_column, "Dana Bantuan"]].copy()
                chart_data = chart_data.sort_values(by="Dana Bantuan", ascending=False)  # Urutkan dari terbesar ke terkecil
                chart = alt.Chart(chart_data).mark_bar(color='#8ab3cf').encode(
                    x=alt.X("Dana Bantuan:Q", title="Dana Bantuan (Rp)"),
                    y=alt.Y(f"{id_column}:N", sort="-x", title="Perusahaan/UMKM"),
                    tooltip=[id_column, alt.Tooltip("Dana Bantuan:Q", title="Dana Bantuan", format=",")]
                ).properties(
                    width=700,
                    height=500
                ).configure_axis(
                    labelFontSize=12
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.error("Pilih minimal satu variabel untuk perhitungan!")
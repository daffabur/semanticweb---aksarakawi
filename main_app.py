# main_app.py
import streamlit as st

# --- Konfigurasi Halaman (HARUS PALING ATAS!) ---
st.set_page_config(
    page_title="Pencarian Aksara Kawi (Semantic Web)",
    page_icon="📜",
    layout="wide"
)

# --- Inject Global CSS ---
# Blok CSS ini tetap di sini agar styling tombol, alert, dll. konsisten di semua halaman
st.markdown("""
    <style>
        /* Mengatur font untuk body secara umum untuk Aksara Kawi */
        body {
            font-family: 'Noto Sans Javanese', sans-serif; /* Pastikan font Aksara Kawi tersedia atau di-load */
        }

        /* Styling untuk semua tombol Streamlit secara general */
        .stButton > button {
            font-size: 58px !important; /* UKURAN FONT SUPER GEDE! */
            padding: 25px 10px !important; /* Padding lebih besar */
            width: 100% !important;
            min-width: unset !important;
            height: auto !important;
            line-height: 1; /* Penting untuk mencegah pemotongan aksara */
            display: flex; /* Menggunakan flexbox untuk alignment konten */
            justify-content: center; /* Pusatkan secara horizontal */
            align-items: center; /* Pusatkan secara vertikal */
            border-radius: 8px; /* Sudut sedikit membulat */
            border: 1px solid #444; /* Border tipis */
            background-color: #262730; /* Warna background tombol (dark mode) */
            color: #ffffff; /* Warna teks tombol */
            transition: all 0.2s ease-in-out; /* Efek transisi halus */
        }
        .stButton > button:hover {
            background-color: #383a48; /* Warna hover sedikit berbeda */
            border-color: #666;
            transform: translateY(-2px); /* Sedikit naik saat hover */
        }

        /* Styling untuk teks latin di bawah tombol */
        .stButton > button + p {
            font-size: 1.2em !important; /* Ukuran font latin diperbesar */
            text-align: center;
            color: #a0a0a0; /* Warna abu-abu yang lebih terang */
            margin-top: 5px; /* Jarak dari tombol */
        }

        /* Mengatur jarak antar subheader kategori dan tombol */
        h3 {
            margin-top: 30px !important; /* Jarak atas subheader */
            margin-bottom: 15px !important; /* Jarak bawah subheader */
        }

        /* Styling untuk text_area hasil input di sidebar */
        [data-testid="stSidebar"] textarea {
            font-family: 'Noto Sans Javanese', sans-serif !important; /* Pastikan font Kawi di text area juga */
            font-size: 28px !important; /* Ukuran font di text_area */
            line-height: 1.5 !important;
            height: 200px !important; /* Tingkatkan tinggi text_area di sidebar */
        }
        
        /* Styling untuk alert messages */
        .stAlert {
            padding: 1rem 1.25rem;
            border-radius: 0.5rem;
            font-size: 1.1em;
            font-weight: bold; /* Teks alert juga dibikin tebal */
        }
        .stAlert.success { background-color: #1a5e2c; color: #e6ffe6; border-color: #0d381c; } /* Warna hijau lebih gelap, teks lebih terang */
        .stAlert.error { background-color: #8c1e21; color: #ffe6e6; border-color: #4a0d0e; } /* Warna merah lebih gelap, teks lebih terang */
        .stAlert.warning { background-color: #806800; color: #fffacd; border-color: #ffeeba; } /* Warna kuning lebih gelap, teks lebih terang */


        /* --- Styling Spesifik untuk HASIL TRANSLITERASI & ARTI --- */
        .result-box {
            background-color: #33363e; /* Background box hasil, lebih terang dari background utama */
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border: 1px solid #555;
        }
        .result-label {
            font-weight: bold;
            color: #f0f2f6; /* Warna label (Transliterasi Latin, Arti Bahasa Indonesia) */
            font-size: 1.1em;
            margin-bottom: 5px;
            display: block; /* Agar label di baris sendiri */
        }
        .result-value {
            font-family: 'monospace'; /* Font monospace untuk transliterasi biar jelas */
            font-size: 1.3em; /* Ukuran font hasil lebih besar */
            font-weight: bold; /* Teks hasil dibikin tebal */
            color: #00ff99; /* Warna teks transliterasi yang sangat kontras (hijau terang) */
            background-color: #1a1c22; /* Background untuk teks hasil */
            padding: 5px 10px;
            border-radius: 5px;
            display: inline-block; /* Agar background mengikuti teks */
            word-wrap: break-word; /* Mencegah teks terlalu panjang */
            white-space: normal; /* Pastikan word-wrap berfungsi */
        }
        .result-value.arti {
            font-family: 'sans-serif'; /* Font default untuk arti */
            font-size: 1.2em; /* Ukuran font arti */
            color: #87ceeb; /* Warna teks arti yang kontras (biru muda) */
        }

    </style>
    """, unsafe_allow_html=True)

# Konfigurasi endpoint SPARQL
SPARQL_ENDPOINT = "http://localhost:3030/projekSemweb/sparql"

# Inisialisasi session_state jika belum ada
if "hasil_input" not in st.session_state:
    st.session_state.hasil_input = ""
if "search_history" not in st.session_state: # Tetap inisialisasi meskipun tidak dipakai di homepage
    st.session_state.search_history = []


# --- Fungsi Query SPARQL (Dipindahkan ke sini!) ---
@st.cache_data(ttl=3600) # Cache hasil query selama 1 jam
def perform_sparql_query(query_type, search_term):
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    
    # Query disesuaikan berdasarkan jenis pencarian
    if query_type == "aksara":
        query = f"""
            PREFIX : <http://contoh.org/prasasti#>
            SELECT ?aksaraValue ?latin ?arti WHERE {{
                ?a a :AksaraKawi ;
                    :aksaraValue "{search_term}" ;
                    :hasTransliterasi ?l ;
                    :hasArti ?r .
                ?l :valueLatin ?latin .
                ?r :valueArti ?arti .
            }}
        """
    elif query_type == "latin":
        query = f"""
            PREFIX : <http://contoh.org/prasasti#>
            SELECT ?aksaraValue ?latin ?arti WHERE {{
                ?a a :AksaraKawi ;
                    :aksaraValue ?aksaraValue ;
                    :hasTransliterasi ?l ;
                    :hasArti ?r .
                FILTER regex(?latin, "{search_term}", "i") . # Pencarian case-insensitive
                ?r :valueArti ?arti .
            }}
        """
    elif query_type == "arti":
        query = f"""
            PREFIX : <http://contoh.org/prasasti#>
            SELECT ?aksaraValue ?latin ?arti WHERE {{
                ?a a :AksaraKawi ;
                    :aksaraValue ?aksaraValue ;
                    :hasTransliterasi ?l ;
                    :hasArti ?r .
                ?l :valueLatin ?latin .
                FILTER regex(?arti, "{search_term}", "i") . # Pencarian case-insensitive
            }}
        """
    else:
        return None # Harusnya tidak terjadi

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        return sparql.query().convert()
    except Exception as e:
        st.error(f"Koneksi ke SPARQL endpoint gagal: {e}. Pastikan server Fuseki Anda berjalan di {SPARQL_ENDPOINT}")
        return None

# --- Import halaman langsung dari root folder ---
import page_aksara_kawi
import page_latin
import page_arti

# --- Konten Homepage Minimalis ---
st.title("📜 Aplikasi Pencarian Aksara Kawi") # Judul aplikasi tetap ada
st.markdown("---")

st.header("Pilih Jenis Pencarian:")

pilihan_pencarian = st.selectbox(
    "Pilih metode pencarian Anda:",
    [
        "Homepage",
        "Cari Berdasarkan Aksara Kawi",
        "Cari Berdasarkan Transliterasi Latin",
        "Cari Berdasarkan Arti Bahasa Indonesia"
    ]
)

# Konten berdasarkan pilihan
if pilihan_pencarian == "Homepage":
    st.info("Selamat datang! Silakan pilih metode pencarian dari dropdown di atas.")
    # st.image("https://raw.githubusercontent.com/streamlit/docs/main/docs/images/illustration-hero.png", caption="Ilustrasi") # Hapus gambar
    # st.markdown("---") # Hapus pemisah
    # st.subheader("Deskripsi Proyek:") # Hapus deskripsi proyek
    # st.markdown("""...""") # Hapus deskripsi proyek
    pass # Biarkan kosong atau tambahkan pesan singkat jika mau

elif pilihan_pencarian == "Cari Berdasarkan Aksara Kawi":
    page_aksara_kawi.app()

elif pilihan_pencarian == "Cari Berdasarkan Transliterasi Latin":
    page_latin.app()

elif pilihan_pencarian == "Cari Berdasarkan Arti Bahasa Indonesia":
    page_arti.app()

st.markdown("---")

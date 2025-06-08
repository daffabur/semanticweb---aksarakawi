# page_aksara_kawi.py

import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON

# Konfigurasi endpoint SPARQL (Penting: Pastikan ini sesuai dengan setup Fuseki Anda)
SPARQL_ENDPOINT = "http://localhost:3030/projekSemweb/sparql"

# Inisialisasi session_state untuk halaman ini
if "hasil_input_aksara" not in st.session_state:
    st.session_state.hasil_input_aksara = ""
if "search_history_aksara" not in st.session_state:
    st.session_state.search_history_aksara = []

# --- Inject Global CSS (Harus ada di setiap file halaman) ---
st.markdown("""
    <style>
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
        .stAlert.warning { background-color: #806800; color: #fffacd; border-color: #554400; } /* Warna kuning lebih gelap, teks lebih terang */


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
        /* Styling untuk tampilan histori di sidebar */
        [data-testid="stSidebar"] .result-box {
            background-color: #2a2c34; /* Lebih gelap dari main result box */
            border: 1px solid #333;
            padding: 10px;
            margin-bottom: 10px;
        }
        [data-testid="stSidebar"] .result-label {
            font-size: 1em;
        }
        [data-testid="stSidebar"] .result-value {
            font-size: 1.1em;
            padding: 3px 6px;
        }


    </style>
    """, unsafe_allow_html=True)


# Data keyboard Aksara Kawi
keyboard_data = [
    {
        "kategori": "Vokal Mandiri",
        "karakter": [
            {"label": "ꦄ", "latin": "a"}, {"label": "ꦆ", "latin": "i"}, {"label": "ꦈ", "latin": "u"},
            {"label": "ꦌ", "latin": "e"}, {"label": "ꦎ", "latin": "o"},
        ]
    },
    {
        "kategori": "Aksara Dasar",
        "karakter": [
            {"label": "ꦲ", "latin": "ha"}, {"label": "ꦤ", "latin": "na"}, {"label": "ꦕ", "latin": "ca"},
            {"label": "ꦗ", "latin": "ja"}, {"label": "ꦫ", "latin": "ra"}, {"label": "ꦏ", "latin": "ka"},
            {"label": "ꦢ", "latin": "da"}, {"label": "ꦠ", "latin": "ta"}, {"label": "ꦱ", "latin": "sa"},
            {"label": "ꦭ", "latin": "la"}, {"label": "ꦪ", "latin": "ya"}, {"label": "ꦝ", "latin": "dha"},
            {"label": "ꦛ", "latin": "tha"}, {"label": "ꦚ", "latin": "nya"}, {"label": "ꦒ", "latin": "ga"},
            {"label": "ꦥ", "latin": "pa"}, {"label": "ꦧ", "latin": "ba"}, {"label": "ꦔ", "latin": "nga"},
            {"label": "ꦩ", "latin": "ma"}, {"label": "ꦮ", "latin": "wa"}, {"label": "ꦯ", "latin": "sha"},
        ]
    },
    {
        "kategori": "Sandhangan",
        "karakter": [
            {"label": "ꦶ", "latin": "i"}, {"label": "ꦺ", "latin": "e"}, {"label": "ꦼ", "latin": "ê"},
            {"label": "ꦷ", "latin": "ī"}, {"label": "ꦴ", "latin": "ā"}, {"label": "ꦁ", "latin": "cecak telu"},
            {"label": "ꦾ", "latin": "ya"}, {"label": "ꦿ", "latin": "ra"}, {"label": "ꦽ", "latin": "rê"},
            {"label": "ꦸ", "latin": "u"}, {"label": "꦳", "latin": "cecak"},
        ]
    },
    {
        "kategori": "Simbol & Penghubung",
        "karakter": [
            {"label": "꧀", "latin": "pangkah"}, {"label": "꧁", "latin": "awalan"},
            {"label": "꧂", "latin": "akhiran"}, {"label": "ꦂ", "latin": "r"},
            {"label": "꧄", "latin": "s"}, {"label": "꧅", "latin": "sw"},
            {"label": "꧆", "latin": "end"}
        ]
    }
]

# Fungsi pencarian SPARQL utama (perform_sparql_query)
@st.cache_data(ttl=3600)
def perform_sparql_query(query_type, search_term):
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    
    # --- FIX: Memastikan SELECT selalu mengambil ?aksaraValue, ?latin, ?arti ---
    # Dan perbaikan FILTER regex agar sesuai dengan struktur RDF
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
                ?l :valueLatin ?latin .
                FILTER regex(?latin, "{search_term}", "i") . # Filter langsung pada variabel ?latin
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
                ?r :valueArti ?arti .
                FILTER regex(?arti, "{search_term}", "i") . # Filter langsung pada variabel ?arti
            }}
        """
    else:
        return None

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        return sparql.query().convert()
    except Exception as e:
        st.error(f"Gagal mengambil data dari SPARQL endpoint: {e}. Pastikan server Fuseki Anda berjalan di {SPARQL_ENDPOINT} dan data ontologi/RDF sudah dimuat dengan benar.")
        return None

# Fungsi utama untuk halaman ini
def app():
    st.title("⌨️ Keyboard Aksara Kawi")
    st.markdown("---") # Pemisah antara judul halaman dan sidebar content

    # --- Sidebar untuk Input Teks dan Kontrol (Aksara Kawi) ---
    with st.sidebar:
        st.header("📝 Aksara Kawi Anda")
        st.markdown("Ketikan Aksara Kawi Anda Akan Muncul di Sini:")
        st.text_area(
            "Hasil Ketikan:",
            value=st.session_state.hasil_input_aksara,
            height=200,
            key="aksara_sidebar_output_text_area", # Key unik untuk sidebar
            label_visibility="collapsed"
        )

        col_a1, col_a2 = st.columns(2)
        with col_a1:
            if st.button("⬅️ Hapus Terakhir", key="aksara_sidebar_hapus_terakhir", use_container_width=True):
                st.session_state.hasil_input_aksara = st.session_state.hasil_input_aksara[:-1]
                st.rerun()
        with col_a2:
            if st.button("🗑️ Hapus Semua", key="aksara_sidebar_hapus_semua", use_container_width=True):
                st.session_state.hasil_input_aksara = ""
                st.rerun()
        
        st.markdown("---")
        st.subheader("🔍 Hasil Pencarian Aksara Kawi")
        st.info("Tekan tombol 'Cari Aksara Kawi di Database' untuk melihat hasil.")
        
        # Tombol cari di sidebar
        if st.button("🚀 Cari Aksara Kawi di Database", key="aksara_sidebar_cari_button", use_container_width=True, type="primary"):
            if st.session_state.hasil_input_aksara.strip() == "":
                st.warning("⚠️ Masukkan Aksara Kawi terlebih dahulu.")
            else:
                with st.spinner(f"Mencari data untuk '{st.session_state.hasil_input_aksara}'..."):
                    results = perform_sparql_query("aksara", st.session_state.hasil_input_aksara)
                    if results:
                        bindings = results["results"]["bindings"]
                        if bindings:
                            st.success("✅ Data Aksara Kawi ditemukan:")
                            # Tampilkan setiap hasil di sidebar
                            for i, row in enumerate(bindings):
                                st.markdown(f"<div class='result-box'>", unsafe_allow_html=True)
                                st.markdown(f"<p class='result-label'>Hasil {i+1}:</p>", unsafe_allow_html=True)
                                
                                # --- BAGIAN INI DIHAPUS SESUAI PERMINTAAN ---
                                # aksara_value = row['aksaraValue']['value'] if 'aksaraValue' in row else "N/A"
                                # st.markdown(f"<p class='result-label'>Aksara Kawi:</p>", unsafe_allow_html=True)
                                # st.markdown(f"<span class='result-value'>{aksara_value}</span>", unsafe_allow_html=True)
                                # --- END HAPUS ---

                                # Pastikan key ada sebelum diakses
                                latin_value = row['latin']['value'] if 'latin' in row else "N/A"
                                arti_value = row['arti']['value'] if 'arti' in row else "N/A"
                                
                                st.markdown(f"<p class='result-label' style='margin-top: 10px;'>Transliterasi Latin:</p>", unsafe_allow_html=True)
                                st.markdown(f"<span class='result-value'>{latin_value}</span>", unsafe_allow_html=True)
                                
                                st.markdown(f"<p class='result-label' style='margin-top: 10px;'>Arti Bahasa Indonesia:</p>", unsafe_allow_html=True)
                                st.markdown(f"<span class='result-value arti'>{arti_value}</span>", unsafe_allow_html=True)
                                
                                st.markdown(f"</div>", unsafe_allow_html=True)
                        else:
                            st.error(f"❌ Tidak ditemukan data untuk Aksara Kawi: **{st.session_state.hasil_input_aksara}** di database.")
                    else:
                        # Error sudah ditangani di perform_sparql_query, ini hanya fallback
                        st.warning("😔 Gagal melakukan pencarian. Periksa koneksi atau data di database.")
    
    st.markdown("---") # Garis pemisah di sidebar
    st.caption("Panel Kontrol Aksara Kawi")


    # --- Bagian Keyboard Aksara Kawi (Konten Utama) ---
    st.markdown("---") # Ini tetap di konten utama untuk pemisah visual
    st.header("Ketik Aksara Kawi untuk Mencari") # Mengganti st.markdown sebelumnya

    # Tombol keyboard Aksara Kawi
    for data in keyboard_data:
        st.subheader(f"✨ {data['kategori']}")
        cols_per_row = 10
        num_rows = (len(data["karakter"]) + cols_per_row - 1) // cols_per_row

        for row_idx in range(num_rows):
            cols = st.columns(cols_per_row)
            for i in range(cols_per_row):
                char_idx = row_idx * cols_per_row + i
                if char_idx < len(data["karakter"]):
                    item = data["karakter"][char_idx]
                    with cols[i]:
                        if st.button(item["label"], key=f"aksara-{data['kategori']}-{item['label']}-button"):
                            st.session_state.hasil_input_aksara += item["label"]
                            st.rerun()
                        st.markdown(f"<p style='text-align:center; color:#a0a0a0; font-size:1.2em; margin-top: 5px;'>{item['latin']}</p>", unsafe_allow_html=True)
        st.markdown("---")
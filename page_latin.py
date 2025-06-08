# page_latin.py

import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON

# Konfigurasi endpoint SPARQL (Penting: Pastikan ini sesuai dengan setup Fuseki Anda)
SPARQL_ENDPOINT = "http://localhost:3030/projekSemweb/sparql"

# Inisialisasi session_state
if "input_latin" not in st.session_state:
    st.session_state.input_latin = ""
# --- Hapus inisialisasi histori pencarian untuk halaman ini ---
# if "search_history_latin" not in st.session_state:
#     st.session_state.search_history_latin = []

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


# Fungsi pencarian SPARQL utama (perform_sparql_query)
@st.cache_data(ttl=3600)
def perform_sparql_query(query_type, search_term):
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    
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
    st.title("🔡 Cari Berdasarkan Transliterasi Latin")
    st.markdown("---") # Pemisah antara judul halaman dan sidebar content

    # --- Sidebar untuk Input Teks dan Kontrol (Latin) ---
    with st.sidebar:
        st.header("📝 Masukkan Teks Latin")
        st.session_state.input_latin = st.text_input(
            "Transliterasi Latin:",
            value=st.session_state.input_latin,
            placeholder="Contoh: sabdakalanda",
            key="latin_sidebar_input_field", # Key unik
            label_visibility="collapsed"
        )

        # Tombol cari di sidebar
        if st.button("🚀 Cari Latin di Database", key="latin_sidebar_cari_button", use_container_width=True, type="primary"):
            if st.session_state.input_latin.strip() == "":
                st.warning("⚠️ Masukkan teks Latin terlebih dahulu.")
            else:
                with st.spinner(f"Mencari data untuk '{st.session_state.input_latin}'..."):
                    results = perform_sparql_query("latin", st.session_state.input_latin)
                    if results:
                        bindings = results["results"]["bindings"]
                        if bindings:
                            st.success("✅ Data ditemukan:")
                            # --- Histori Pencarian TIDAK DISIMPAN/DITAMPILKAN di sini ---
                            # Simpan hasil pencarian ke history (jika nanti mau diaktifkan lagi)
                            # st.session_state.search_history_latin.append({
                            #     "input": st.session_state.input_latin,
                            #     "results": bindings
                            # })
                            # Tampilkan setiap hasil
                            for i, row in enumerate(bindings):
                                st.markdown(f"<div class='result-box'>", unsafe_allow_html=True)
                                st.markdown(f"<p class='result-label'>Hasil {i+1}:</p>", unsafe_allow_html=True)
                                
                                # Pastikan key ada sebelum diakses
                                aksara_value = row['aksaraValue']['value'] if 'aksaraValue' in row else "N/A"
                                latin_value = row['latin']['value'] if 'latin' in row else "N/A"
                                arti_value = row['arti']['value'] if 'arti' in row else "N/A"

                                st.markdown(f"<p class='result-label'>Aksara Kawi:</p>", unsafe_allow_html=True)
                                st.markdown(f"<span class='result-value'>{aksara_value}</span>", unsafe_allow_html=True)
                                
                                st.markdown(f"<p class='result-label' style='margin-top: 10px;'>Transliterasi Latin:</p>", unsafe_allow_html=True)
                                st.markdown(f"<span class='result-value'>{latin_value}</span>", unsafe_allow_html=True)
                                
                                st.markdown(f"<p class='result-label' style='margin-top: 10px;'>Arti Bahasa Indonesia:</p>", unsafe_allow_html=True)
                                st.markdown(f"<span class='result-value arti'>{arti_value}</span>", unsafe_allow_html=True)
                                
                                st.markdown(f"</div>", unsafe_allow_html=True)
                        else:
                            st.error(f"❌ Tidak ditemukan data untuk Latin: **{st.session_state.input_latin}** di database.")
                    else:
                        # Error sudah ditangani di perform_sparql_query, ini hanya fallback
                        st.warning("😔 Gagal melakukan pencarian. Periksa koneksi atau data di database.")
        
        # Tombol Clear Input di sidebar
        if st.button("🗑️ Bersihkan Input Latin", key="latin_sidebar_clear_button", use_container_width=True):
            st.session_state.input_latin = ""
            st.rerun()
        
        # --- Bagian Histori Pencarian Latin DIHAPUS ---
        # if st.session_state.search_history_latin:
        #     st.markdown("---")
        #     st.subheader("📜 Histori Pencarian Latin")
        #     for i, history in enumerate(st.session_state.search_history_latin):
        #         st.markdown(f"**Pencarian {i+1}:** `{history['input']}`")
        #         for j, row in enumerate(history['results']):
        #             st.markdown(f"<div class='result-box'>", unsafe_allow_html=True)
        #             st.markdown(f"<p class='result-label'>Hasil {j+1}:</p>", unsafe_allow_html=True)
        #             
        #             aksara_value = row['aksaraValue']['value'] if 'aksaraValue' in row else "N/A"
        #             latin_value = row['latin']['value'] if 'latin' in row else "N/A"
        #             arti_value = row['arti']['value'] if 'arti' in row else "N/A"
        #
        #             st.markdown(f"<p class='result-label'>Aksara Kawi:</p>", unsafe_allow_html=True)
        #             st.markdown(f"<span class='result-value'>{aksara_value}</span>", unsafe_allow_html=True)
        #             
        #             st.markdown(f"<p class='result-label' style='margin-top: 10px;'>Latin:</p>", unsafe_allow_html=True)
        #             st.markdown(f"<span class='result-value'>{latin_value}</span>", unsafe_allow_html=True)
        #             
        #             st.markdown(f"<p class='result-label' style='margin-top: 10px;'>Arti:</p>", unsafe_allow_html=True)
        #             st.markdown(f"<span class='result-value arti'>{arti_value}</span>", unsafe_allow_html=True)
        #             
        #             st.markdown(f"</div>", unsafe_allow_html=True)
        #         st.markdown("---")
        
        st.markdown("---") # Garis pemisah di sidebar
        st.caption("Panel Kontrol Transliterasi Latin")

    # --- Konten Utama (Tidak Ada Apa-apa, karena input sudah di sidebar) ---
    st.header("Hasil Pencarian Anda akan muncul di Sidebar setelah Anda mencari.")
    st.info("Anda bisa mengetik transliterasi Latin di sidebar kiri, lalu tekan tombol 'Cari Latin di Database'.")
    st.markdown("---")
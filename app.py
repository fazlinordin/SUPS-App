import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date

st.set_page_config(page_title="SUPS HJEM V2.8", layout="wide")

# --- KONFIGURASI API ---
URL_API = "https://script.google.com/macros/s/AKfycbzir4NpkjGqR7XuBTFfxg8tziu7fBSlrHKgUICM_KSfC0MnRScdXh_8oi7uTGfHe01mkg/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- SENARAI UBAT (Sila lengkapkan list mengikut keperluan) ---
MASTER_UBAT = sorted(["Amlodipine 10mg", "Atorvastatin 20mg", "Metformin 500mg", "Simvastatin 40mg", "Warfarin 2mg", "Gliclazide 80mg", "Aspirin 150mg"])

# --- FUNGSI LOAD DATA ---
def load_data():
    try:
        df = pd.read_csv(f"{URL_SHEET_CSV}&cache={datetime.now().timestamp()}")
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

# --- INITIALIZE SESSION STATE (Bakul Ubat) ---
if 'bakul_ubat' not in st.session_state:
    st.session_state.bakul_ubat = []

# --- UI ---
st.sidebar.title("🏥 SUPS HJEM")
menu = st.sidebar.radio("MENU", ["📝 DAFTAR PESAKIT", "📊 SUMMARY BATCH"])

if menu == "📝 DAFTAR PESAKIT":
    st.header("Pendaftaran & Penyediaan Ubat")
    
    # 1. Maklumat Pesakit
    with st.container(border=True):
        st.subheader("👤 Maklumat Pesakit")
        c1, c2, c3 = st.columns(3)
        nama = c1.text_input("Nama Penuh:").upper()
        ic = c2.text_input("No. IC:")
        batch = c3.selectbox("Batch:", [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]])
        
        c4, c5 = st.columns(2)
        t_ubat = c4.date_input("Tarikh Ambil Ubat:", value=date.today())
        t_clinic = c5.date_input("Tarikh TCA Klinik:", value=None)

    # 2. Input Ubat Satu Persatu
    with st.container(border=True):
        st.subheader("💊 Masukkan Ubat Satu Persatu")
        u1, u2, u3 = st.columns([2, 1, 1])
        
        pilih_u = u1.selectbox("Pilih Nama Ubat:", ["-- Pilih Ubat --"] + MASTER_UBAT)
        isi_q = u2.text_input("Kuantiti (cth: 30 biji):")
        
        if u3.button("➕ Tambah Ubat", use_container_width=True):
            if pilih_u != "-- Pilih Ubat --" and isi_q:
                # Masukkan ke dalam session state
                st.session_state.bakul_ubat.append({"ubat": pilih_u, "qty": isi_q})
            else:
                st.warning("Pilih ubat dan isi kuantiti!")

    # 3. Paparan Senarai Sementara (Bakul)
    if st.session_state.bakul_ubat:
        st.write("### 🛒 Senarai Ubat Ditambah:")
        for i, item in enumerate(st.session_state.bakul_ubat):
            st.write(f"{i+1}. **{item['ubat']}** — {item['qty']}")
        
        col_clear, col_save = st.columns([1, 4])
        
        if col_clear.button("🗑️ Kosongkan Bakul", type="secondary"):
            st.session_state.bakul_ubat = []
            st.rerun()
            
        if col_save.button("💾 SIMPAN SEMUA KE DATABASE", type="primary", use_container_width=True):
            if nama and ic:
                # Gabungkan semua ubat & kuantiti jadi satu string
                gabung_ubat = " | ".join([x['ubat'] for x in st.session_state.bakul_ubat])
                gabung_qty = " | ".join([x['qty'] for x in st.session_state.bakul_ubat])
                
                data_json = {
                    "Nama": nama, "IC": ic, "TCA_Ubat": str(t_ubat),
                    "TCA_Clinic": str(t_clinic) if t_clinic else "",
                    "Ubat_List": gabung_ubat,
                    "Batch": batch,
                    "Kuantiti": gabung_qty
                }
                
                try:
                    res = requests.post(URL_API, json=data_json)
                    if res.status_code == 200:
                        st.success(f"Rekod {nama} berjaya disimpan!")
                        st.session_state.bakul_ubat = [] # Reset bakul
                        st.balloons()
                    else: st.error("Gagal simpan ke API.")
                except Exception as e: st.error(f"Error: {e}")
            else:
                st.error("Nama dan IC wajib diisi sebelum simpan!")

elif menu == "📊 SUMMARY BATCH":
    st.header("📋 Checklist Ringkasan")
    # Kod paparan sama seperti sebelum ini (pilih batch & paparan jadual)
    # ... (Guna kod Summary dari Versi 2.7) ...

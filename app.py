import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime, date

st.set_page_config(page_title="SUPS HJEM V3.2", layout="wide")

# --- KONFIGURASI ---
URL_API = "https://script.google.com/macros/s/AKfycbzir4NpkjGqR7XuBTFfxg8tziu7fBSlrHKgUICM_KSfC0MnRScdXh_8oi7uTGfHe01mkg/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

def load_data():
    try:
        df = pd.read_csv(f"{URL_SHEET_CSV}&cache={datetime.now().timestamp()}")
        df.columns = df.columns.str.strip().str.upper()
        return df
    except:
        return pd.DataFrame()

# --- FUNGSI EKSTRAK NOMBOR (Untuk Kira Total) ---
def ekstrak_angka(teks):
    try:
        # Cari nombor dalam teks (cth: "30 BIJI" -> 30)
        angka = re.findall(r'\d+', str(teks))
        return int(angka[0]) if angka else 0
    except:
        return 0

# --- FUNGSI TUKAR KE FORMAT MELINTANG DENGAN TOTAL ---
def convert_to_matrix_with_total(df_filtered):
    rows = []
    for _, row in df_filtered.iterrows():
        ubats = str(row['UBAT_LIST']).split(' | ')
        qtys = str(row['KUANTITI']).split(' | ')
        for u, q in zip(ubats, qtys):
            rows.append({
                'NAMA PESAKIT': row['NAMA'],
                'UBAT': u.strip(),
                'KUANTITI': q.strip(),
                'NILAI': ekstrak_angka(q)
            })
    
    if not rows:
        return pd.DataFrame()
        
    new_df = pd.DataFrame(rows)
    
    # 1. Buat Matrix Utama (Ubat vs Pesakit)
    matrix = new_df.pivot_table(index='UBAT', columns='NAMA PESAKIT', values='KUANTITI', aggfunc='first').fillna('')
    
    # 2. Kira Jumlah Besar (Total) setiap ubat
    total_series = new_df.groupby('UBAT')['NILAI'].sum()
    
    # 3. Masukkan Kolum TOTAL di posisi pertama (sebelah nama ubat)
    matrix.insert(0, 'TOTAL (BIJI/UNIT)', total_series)
    
    return matrix

# --- INITIALIZE BAKUL UBAT ---
if 'bakul_ubat' not in st.session_state:
    st.session_state.bakul_ubat = []

# --- MASTER LIST UBAT ---
# Sila masukkan senarai 131 ubat anda di sini
MASTER_UBAT = sorted(["Amlodipine 10mg", "Atorvastatin 20mg", "Metformin 500mg", "Simvastatin 40mg", "Warfarin 2mg"]) 

st.sidebar.title("🏥 SUPS HJEM")
menu = st.sidebar.radio("NAVIGASI", ["📝 DAFTAR & TAMBAH UBAT", "📊 SUMMARY BATCH"])

if menu == "📝 DAFTAR & TAMBAH UBAT":
    st.header("Pendaftaran & Penyediaan Ubat")
    
    with st.container(border=True):
        st.subheader("👤 Maklumat Pesakit")
        c1, c2, c3 = st.columns(3)
        nama = c1.text_input("Nama Penuh:").upper()
        ic = c2.text_input("No. IC:")
        batch = c3.selectbox("Pilih Batch:", [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]])
        
        c4, c5 = st.columns(2)
        t_ubat = c4.date_input("Tarikh Ambil Ubat:", value=date.today())
        t_clinic = c5.date_input("Tarikh TCA Klinik:", value=None)

    with st.container(border=True):
        st.subheader("💊 Tambah Ubat")
        u1, u2, u3 = st.columns([2, 1, 1])
        pilih_u = u1.selectbox("Pilih Nama Ubat:", ["-- Pilih --"] + MASTER_UBAT)
        isi_q = u2.text_input("Kuantiti (cth: 30 BIJI):")
        
        if u3.button("➕ Tambah", use_container_width=True):
            if pilih_u != "-- Pilih --" and isi_q:
                st.session_state.bakul_ubat.append({"ubat": pilih_u, "qty": isi_q})
                st.rerun()

    if st.session_state.bakul_ubat:
        st.write("### 🛒 Senarai Sementara")
        st.table(pd.DataFrame(st.session_state.bakul_ubat))
        
        col_clear, col_save = st.columns([1, 4])
        if col_clear.button("🗑️ Kosongkan"):
            st.session_state.bakul_ubat = []
            st.rerun()
            
        if col_save.button("💾 SIMPAN SEMUA DATA", type="primary", use_container_width=True):
            if nama and ic:
                gabung_ubat = " | ".join([x['ubat'] for x in st.session_state.bakul_ubat])
                gabung_qty = " | ".join([x['qty'] for x in st.session_state.bakul_ubat])
                
                data_json = {
                    "Nama": nama, "IC": ic, "TCA_Ubat": str(t_ubat), 
                    "TCA_Clinic": str(t_clinic) if t_clinic else "", 
                    "Ubat_List": gabung_ubat, "Batch": batch, "Kuantiti": gabung_qty
                }
                
                try:
                    res = requests.post(URL_API, json=data_json)
                    if res.status_code == 200:
                        st.success(f"Berjaya Simpan Rekod {nama}!")
                        st.session_state.bakul_ubat = []
                        st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")

elif menu == "📊 SUMMARY BATCH":
    st.header("📋 Ringkasan & Total Penggunaan Ubat")
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    df = load_data()
    if not df.empty:
        batch_sel = st.selectbox("Pilih Batch:", [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]])
        df_batch = df[df['BATCH'] == batch_sel].copy()
        
        if not df_batch.empty:
            st.subheader(f"Jadual Penggunaan Ubat - {batch_sel}")
            
            # Panggil fungsi matrix yang ada TOTAL
            df_matrix = convert_to_matrix_with_total(df_batch)
            
            # Paparkan jadual
            st.dataframe(df_matrix, use_container_width=True)
            
            # Button Download
            csv_data = df_matrix.to_csv().encode('utf-8')
            st.download_button(
                label="📥 Download Checklist & Total (Excel Style)",
                data=csv_data,
                file_name=f"Checklist_Total_{batch_sel}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("Tiada data ditemui untuk batch ini.")

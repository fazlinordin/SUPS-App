import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="SUPS HJEM - Format Checklist", layout="wide")

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

# --- UI ---
st.sidebar.title("SUPS HJEM")
menu = st.sidebar.radio("MENU", ["📝 DAFTAR PESAKIT", "📊 RINGKASAN BATCH"])

if menu == "📝 DAFTAR PESAKIT":
    st.header("Pendaftaran SPUB Baru")
    # Kod pendaftaran (Kekal sama seperti sebelum ini)
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Penuh Pesakit:").upper()
            ic = st.text_input("No. IC:")
            batch_pilihan = st.selectbox("Pilih Batch:", [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]])
        with col2:
            tca_u = st.date_input("TCA Ubat:")
            tca_c = st.date_input("TCA Clinic (Jika Ada):", value=None)
        
        st.write("---")
        # List ubat dari file Excel anda (contoh sebahagian)
        MASTER_UBAT = ["Amlodipine 10mg", "Atorvastatin 20mg", "Metformin 500mg", "Simvastatin 40mg", "Warfarin 2mg"] 
        pilihan_ubat = st.multiselect("Pilih Ubat (Boleh pilih banyak):", MASTER_UBAT)
        kuantiti = st.text_input("Kuantiti (Contoh: 30 BIJI / 1 KOTAK):")
        
        submit = st.form_submit_button("💾 SIMPAN KE DATABASE")

    if submit and nama and ic:
        data_json = {
            "Nama": nama, "IC": ic, "TCA_Ubat": str(tca_u), 
            "TCA_Clinic": str(tca_c) if tca_c else "", 
            "Ubat_List": " | ".join(pilihan_ubat), 
            "Batch": batch_pilihan, "Kuantiti": kuantiti.upper()
        }
        r = requests.post(URL_API, json=data_json)
        if r.status_code == 200: st.success("Data Berjaya Masuk!"); st.balloons()

elif menu == "📊 RINGKASAN BATCH":
    st.header("📋 Checklist Penyediaan Ubat")
    
    if st.button("🔄 Refresh Senarai"):
        st.cache_data.clear()
        st.rerun()

    df = load_data()

    if not df.empty:
        senarai_m = ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"]
        batch_list = [f"{m} - Batch {b}" for m in senarai_m for b in [1, 2]]
        pilihan = st.selectbox("Pilih Batch Untuk Semakan:", batch_list)
        
        df_filtered = df[df['BATCH'] == pilihan].copy()
        
        if not df_filtered.empty:
            # --- SUSUNAN KOLUM SEPERTI PERMINTAAN FAZLI ---
            # Kita letak Ubat dan Kuantiti di sebelah kiri
            df_display = df_filtered[["UBAT_LIST", "KUANTITI", "NAMA", "IC", "TCA_UBAT", "TCA_CLINIC"]]
            
            # Tukar tajuk kolum supaya lebih mesra pengguna
            df_display.columns = ["SENARAI UBAT", "KUANTITI", "NAMA PESAKIT", "NO. IC", "TARIKH AMBIL", "TARIKH KLINIK"]
            
            st.write(f"Menunjukkan **{len(df_display)}** pesakit dalam **{pilihan}**")
            
            # Paparkan jadual
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Download button
            csv = df_display.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Muat Turun Checklist (CSV)", csv, f"Checklist_{pilihan}.csv", "text/csv")
        else:
            st.info("Tiada rekod untuk batch ini.")

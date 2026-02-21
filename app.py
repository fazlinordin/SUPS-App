import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="SUPS by Fazli Ver.2.4", layout="wide")

URL_API = "https://script.google.com/macros/s/AKfycbzir4NpkjGqR7XuBTFfxg8tziu7fBSlrHKgUICM_KSfC0MnRScdXh_8oi7uTGfHe01mkg/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

def load_data():
    try:
        # Tambah cachebuster supaya sentiasa ambil data paling baru
        df = pd.read_csv(f"{URL_SHEET_CSV}&cache={datetime.now().timestamp()}")
        # PENTING: Bersihkan nama kolum (buang space depan/belakang dan tukar ke UPPERCASE)
        df.columns = df.columns.str.strip().str.upper()
        return df
    except Exception as e:
        st.error(f"Gagal tarik data: {e}")
        return pd.DataFrame()

def kira_jarak_ubat_ke_klinik(t_ubat_str, t_clinic_str):
    if pd.isna(t_clinic_str) or str(t_clinic_str).strip() == "" or str(t_clinic_str).lower() in ["none", "nan"]:
        return ""
    try:
        t_ubat = pd.to_datetime(t_ubat_str).date()
        t_clinic = pd.to_datetime(t_clinic_str).date()
        beza = (t_clinic - t_ubat).days
        return f"{beza} hari" if beza >= 0 else f"Lepas {abs(beza)} hari"
    except:
        return ""

# --- MASTER LIST UBAT ---
MASTER_UBAT = ["acetazolamide 250mg tab", "atorvastatin 20 mg", "metformin xr 750 mg", "Simvastatin 40 mg", "Warfarin 2mg"] # (Sila tambah list penuh anda di sini)

SENARAI_BATCH = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

st.sidebar.title("SUPS by Fazli")
menu = st.sidebar.radio("Menu Utama", ["📝 Daftar Pesakit Baru", "📊 Summary & Download"])

if menu == "📝 Daftar Pesakit Baru":
    st.header("📋 Daftar Pesakit & Ubat SPUB")
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Penuh:").upper()
            ic = st.text_input("No. IC (Tanpa -):")
            batch_pilihan = st.selectbox("Pilih Batch:", SENARAI_BATCH)
        with col2:
            tca_u = st.date_input("TCA Ubat:")
            ada_clinic = st.checkbox("Ada Tarikh TCA Clinic?", value=False)
            tca_c = st.date_input("TCA Clinic:", value=None) if ada_clinic else ""
        st.write("---")
        pilihan_ubat = st.multiselect("1. Pilih Nama Ubat:", MASTER_UBAT)
        kuantiti = st.text_input("2. Masukkan Kuantiti (Contoh: 30 BIJI):")
        ubat_manual = st.text_area("3. Ubat Tiada Dalam List?")
        submit = st.form_submit_button("💾 SIMPAN REKOD", use_container_width=True)

    if submit:
        if nama and ic:
            final_ubat = " | ".join(pilihan_ubat) if not ubat_manual else f"{' | '.join(pilihan_ubat)} | {ubat_manual.upper()}"
            data_json = {"Nama": nama, "IC": ic, "TCA_Ubat": str(tca_u), "TCA_Clinic": str(tca_c) if ada_clinic else "", "Ubat_List": final_ubat, "Batch": batch_pilihan, "Kuantiti": kuantiti.upper()}
            try:
                r = requests.post(URL_API, json=data_json)
                if r.status_code == 200:
                    st.success(f"Rekod {nama} Berjaya Disimpan!")
                    st.balloons()
                else: st.error("Gagal simpan ke Google Sheets.")
            except Exception as e: st.error(f"Error: {e}")
        else: st.warning("⚠️ Sila isi Nama dan No IC.")

elif menu == "📊 Summary & Download":
    st.header("🔍 Semakan Rekod")
    if st.button("🔄 Segarkan Data (Refresh)"):
        st.rerun()

    df_main = load_data()

    if not df_main.empty:
        batch_to_filter = st.selectbox("Pilih Batch untuk Lihat:", SENARAI_BATCH)
        
        # Nama kolum sekarang sudah jadi UPPERCASE dalam kod ni
        kolum_wujud = df_main.columns.tolist()
        
        if 'BATCH' in kolum_wujud:
            df_filtered = df_main[df_main['BATCH'] == batch_to_filter].copy()
            
            if not df_filtered.empty:
                # Guna nama kolum uppercase untuk elak KeyError
                if 'TCA_UBAT' in kolum_wujud and 'TCA_CLINIC' in kolum_wujud:
                    df_filtered['JARAK'] = df_filtered.apply(
                        lambda x: kira_jarak_ubat_ke_klinik(x['TCA_UBAT'], x['TCA_CLINIC']), axis=1
                    )
                
                st.dataframe(df_filtered, use_container_width=True)
                st.download_button(f"📥 Download CSV", df_filtered.to_csv(index=False).encode('utf-8'), f"{batch_to_filter}.csv", "text/csv")
            else:
                st.info(f"Tiada rekod untuk {batch_to_filter}.")
        else:
            st.error(f"Kolum 'Batch' tak jumpa. Kolum yang ada: {kolum_wujud}")
    else:
        st.info("Data kosong atau Sheets tidak di-set kepada 'Anyone with the link can view'.")

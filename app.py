import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date

st.set_page_config(page_title="SUPS HJEM V2.9", layout="wide")

# --- KONFIGURASI ---
URL_API = "https://script.google.com/macros/s/AKfycbzir4NpkjGqR7XuBTFfxg8tziu7fBSlrHKgUICM_KSfC0MnRScdXh_8oi7uTGfHe01mkg/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- MASTER LIST UBAT (Sila pastikan senarai penuh 131 ubat ada di sini) ---
MASTER_UBAT = sorted(["Amlodipine 10mg", "Atorvastatin 20mg", "Metformin 500mg", "Simvastatin 40mg", "Warfarin 2mg", "Gliclazide 80mg", "Aspirin 150mg"])

def load_data():
    try:
        df = pd.read_csv(f"{URL_SHEET_CSV}&cache={datetime.now().timestamp()}")
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

def hitung_countdown(t_clinic_str):
    if pd.isna(t_clinic_str) or str(t_clinic_str).strip() == "" or str(t_clinic_str).lower() in ["none", "nan"]:
        return "N/A"
    try:
        t_clinic = pd.to_datetime(t_clinic_str).date()
        baki = (t_clinic - date.today()).days
        if baki > 0: return f"⏳ {baki} Hari Lagi"
        elif baki == 0: return "🔴 HARI INI"
        else: return f"✅ Selesai"
    except: return "-"

if 'bakul_ubat' not in st.session_state:
    st.session_state.bakul_ubat = []

# --- UI ---
st.sidebar.title("🏥 SUPS HJEM")
menu = st.sidebar.radio("MENU", ["📝 DAFTAR & TAMBAH UBAT", "📊 SUMMARY BATCH"])

if menu == "📝 DAFTAR & TAMBAH UBAT":
    st.header("Pendaftaran Pesakit & Penyediaan Ubat")
    
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
        st.subheader("💊 Tambah Ubat Satu-Persatu")
        u1, u2, u3 = st.columns([2, 1, 1])
        pilih_u = u1.selectbox("Pilih Nama Ubat:", ["-- Pilih Ubat --"] + MASTER_UBAT)
        isi_q = u2.text_input("Kuantiti (cth: 30 biji):")
        
        if u3.button("➕ Tambah Ke Senarai", use_container_width=True):
            if pilih_u != "-- Pilih Ubat --" and isi_q:
                st.session_state.bakul_ubat.append({"ubat": pilih_u, "qty": isi_q})
                st.rerun()

    if st.session_state.bakul_ubat:
        st.write("### 🛒 Senarai Ubat Pesakit Ini:")
        # Papar dalam bentuk dataframe ringkas supaya kemas
        st.table(pd.DataFrame(st.session_state.bakul_ubat))
        
        col_clear, col_save = st.columns([1, 4])
        if col_clear.button("🗑️ Kosongkan"):
            st.session_state.bakul_ubat = []
            st.rerun()
            
        if col_save.button("💾 SIMPAN SEMUA DATA", type="primary", use_container_width=True):
            if nama and ic:
                gabung_ubat = " | ".join([x['ubat'] for x in st.session_state.bakul_ubat])
                gabung_qty = " | ".join([x['qty'] for x in st.session_state.bakul_ubat])
                data_json = {"Nama": nama, "IC": ic, "TCA_Ubat": str(t_ubat), "TCA_Clinic": str(t_clinic) if t_clinic else "", "Ubat_List": gabung_ubat, "Batch": batch, "Kuantiti": gabung_qty}
                res = requests.post(URL_API, json=data_json)
                if res.status_code == 200:
                    st.success("Berjaya!"); st.session_state.bakul_ubat = []; st.balloons()
            else: st.error("Sila isi Nama & IC!")

elif menu == "📊 SUMMARY BATCH":
    st.header("📋 Ringkasan Checklist SPUB")
    if st.button("🔄 Segarkan Data (Refresh)"):
        st.cache_data.clear()
        st.rerun()

    df = load_data()
    if not df.empty:
        pilihan = st.selectbox("Tapis Batch:", [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]])
        df_view = df[df['BATCH'] == pilihan].copy()
        
        if not df_view.empty:
            # 1. Kira Countdown
            df_view['COUNTDOWN'] = df_view['TCA_CLINIC'].apply(hitung_countdown)
            
            # 2. SUSUNAN KOLUM BARU (Ikut permintaan Fazli - Ubat di Kiri)
            # Susunan: Ubat -> Kuantiti -> Countdown -> Nama -> IC -> Tarikh-tarikh
            df_final = df_view[["UBAT_LIST", "KUANTITI", "COUNTDOWN", "NAMA", "IC", "TCA_UBAT", "TCA_CLINIC"]]
            
            # 3. Tukar Nama Header supaya kemas
            df_final.columns = ["💊 SENARAI UBAT", "📦 KUANTITI", "⏰ STATUS KLINIK", "👤 NAMA PESAKIT", "🆔 NO. IC", "📅 TARIKH AMBIL", "📅 TARIKH TCA"]
            
            st.dataframe(df_final, use_container_width=True, hide_index=True)
            
            # Butang Download
            st.download_button("📥 Muat Turun Checklist", df_final.to_csv(index=False).encode('utf-8'), f"{pilihan}.csv", "text/csv")
        else: st.info("Tiada data.")

import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io
import time

# --- 1. TETAPAN HALAMAN ---
st.set_page_config(page_title="SUPS HJEM V8.0", layout="wide")

# Inisialisasi memori aplikasi (Session State)
if 'bakul' not in st.session_state:
    st.session_state.bakul = []
if 'batch_kekal' not in st.session_state:
    st.session_state.batch_kekal = "Mac - Batch 1"
if 'tengah_simpan' not in st.session_state:
    st.session_state.tengah_simpan = False

URL_API = "https://script.google.com/macros/s/AKfycbyeZXuPoyqsORGh_-kPC8lVTiFe41qZvQ4V8gBQU_BXnmP30zufcjSDxN6HnqyzQRRu/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- 2. SENARAI MASTER UBAT ---
MASTER_UBAT = sorted([
    "Abacavir 300mg Tablet", "Acarbose 50 mg Tablet", "Acetazolamide 250 mg Tablet",
    "Acetylsalicylic Acid 100 mg, Glycine 45 mg Tablet", "Acyclovir 200 mg Tablet",
    "Amlodipine 5 mg Tablet", "Amlodipine 10 mg Tablet", "Atenolol 50 mg Tablet",
    "Atorvastatin 20 mg Tablet", "Atorvastatin 40 mg Tablet", "Bisoprolol Fumarate 2.5 mg Tablet",
    "Bisoprolol Fumarate 5 mg Tablet", "Calamine Lotion", "Cetirizine HCl 10mg Tablet",
    "Chlorpheniramine Maleate 4mg Tablet", "Dexamethasone 0.1% Eye Drop", "Diclofenac 1% Emulgel",
    "Enalapril 5 mg Tablet", "Enalapril 10 mg Tablet", "Folic Acid 5 mg Tablet",
    "Frusemide 40 mg Tablet", "Fusidic Acid 2% Cream", "Fusidic Acid 2% Ointment", 
    "Gliclazide 80 mg Tablet", "Hydrochlorothiazide 25 mg Tablet", "Metformin HCl 500 mg Tablet",
    "Metoprolol Tartrate 100 mg Tablet", "Omeprazole 20 mg Capsule", "Paracetamol 500 mg Tablet",
    "Perindopril 4 mg Tablet", "Perindopril 8 mg Tablet", "Salbutamol 100 mcg/dose Inhaler",
    "Simvastatin 10 mg Tablet", "Simvastatin 20 mg Tablet", "Simvastatin 40 mg Tablet",
    "Vitamin B Complex Tablet", "Warfarin Sodium 1 mg Tablet"
])

def load_data():
    try:
        r = requests.get(f"{URL_SHEET_CSV}&t={time.time()}")
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

# --- 3. NAVIGASI ---
menu = st.sidebar.radio("NAVIGASI", ["📝 INPUT", "📊 SUMMARY"])
BATCH_OPTIONS = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    
    # --- BAHAGIAN A: INPUT PESAKIT (Guna Form untuk Auto-Reset) ---
    with st.form("form_pesakit", clear_on_submit=True):
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            nama_raw = c1.text_input("Nama:")
            ic_input = c2.text_input("IC:")
            idx_b = BATCH_OPTIONS.index(st.session_state.batch_kekal)
            batch_input = c3.selectbox("Batch:", BATCH_OPTIONS, index=idx_b)
            
            c4, c5 = st.columns(2)
            t_u = c4.date_input("TCA Ambil Ubat (Hari Ini):", value=date.today())
            t_d = c5.date_input("TCA Klinik (Dr) [Opsional]:", value=date.today())
            
            # COUNTDOWN (Auto-Calculate)
            if t_d > t_u:
                baki = (t_d - t_u).days
                st.success(f"🎯 **Sila bekalkan ubat untuk: {baki} Hari**")

        st.write("") # Jarak

        # --- BAHAGIAN B: BAKUL SEMENTARA ---
        st.subheader("🛒 Bakul Sementara")
        if st.session_state.bakul:
            for i, itm in enumerate(st.session_state.bakul):
                col_u, col_q, col_d = st.columns([4, 1, 0.5])
                col_u.write(f"{itm['u']}")
                col_q.write(f"{itm['q']}")
                if col_d.form_submit_button("🗑️", help="Padam item ini"):
                    st.session_state.bakul.pop(i)
                    st.rerun()
            
            st.divider()
            
            # --- BAHAGIAN C: BUTANG SIMPAN (Bawah Bakul) ---
            if st.session_state.tengah_simpan:
                st.write("⏳ **SEDANG MENYIMPAN DATA KE CLOUD...**")
                st.form_submit_button("SEDANG MENYIMPAN...", disabled=True, use_container_width=True)
            else:
                if st.form_submit_button("💾 SIMPAN DATA", type="primary", use_container_width=True):
                    if nama_raw and ic_input and st.session_state.bakul:
                        st.session_state.tengah_simpan = True
                        # Proses Nama jadi HURUF BESAR
                        nama_final = nama_raw.upper().strip()
                        
                        payload = {
                            "Nama": nama_final, 
                            "IC": f"'{ic_input.strip()}",
                            "TCA_Ubat": str(t_u), 
                            "TCA_Clinic": str(t_d), 
                            "Batch": batch_input,
                            "Ubat_List": " | ".join([x['u'] for x in st.session_state.bakul]),
                            "Kuantiti": " | ".join([x['q'] for x in st.session_state.bakul])
                        }
                        
                        try:
                            requests.post(URL_API, json=payload, timeout=15)
                            st.session_state.bakul = [] # Kosongkan bakul
                            st.session_state.batch_kekal = batch_input # Kekalkan batch untuk pesakit seterusnya
                            st.session_state.tengah_simpan = False
                            st.success(f"Data {nama_final} berjaya disimpan!")
                            time.sleep(1)
                            st.rerun() # Refresh untuk reset form (Nama & IC kosong)
                        except:
                            st.error("Ralat Rangkaian! Sila cuba lagi.")
                            st.session_state.tengah_simpan = False
                    else:
                        st.error("Lengkapkan Nama, IC dan sekurang-kurangnya 1 ubat!")
        else:
            st.info("Bakul kosong. Tambah ubat di kotak bawah.")

    # --- BAHAGIAN D: PILIH UBAT (Di luar form supaya tak reset form masa tambah ubat) ---
    with st.container(border=True):
        st.write("**Pilih Ubat:**")
        u1, u2 = st.columns([3, 1])
        p_u = u1.selectbox("Nama Ubat:", ["-- PILIH --"] + MASTER_UBAT, label_visibility="collapsed")
        p_q = u2.text_input("Qty:", placeholder="Contoh: 30", label_visibility="collapsed")
        
        if st.button("➕ Tambah Ke Bakul", use_container_width=True):
            if p_u != "-- PILIH --" and p_q:
                st.session_state.bakul.append({"u": p_u, "q": p_q})
                st.rerun()

elif menu == "📊 SUMMARY":
    st.header("Checklist & Durasi Bekalan")
    # (Kod Summary kekal sama seperti V7.7 yang stabil)
    df = load_data()
    if not df.empty:
        idx_s = BATCH_OPTIONS.index(st.session_state.batch_kekal)
        p_batch = st.selectbox("Pilih Batch:", BATCH_OPTIONS, index=idx_s)
        df_f = df[df['BATCH'] == p_batch].copy()
        
        if not df_f.empty:
            labels = df_f['NAMA'].unique()
            matrix = {}
            matrix["🆔 NO. IC"] = {l: str(df_f[df_f['NAMA']==l]['IC'].iloc[0]).replace("'","") for l in labels}
            matrix["⏳ DURASI"] = {l: f"{(pd.to_datetime(df_f[df_f['NAMA']==l]['TCA_CLINIC'].iloc[0]) - pd.to_datetime(df_f[df_f['NAMA']==l]['TCA_UBAT'].iloc[0])).days} HARI" for l in labels}
            
            # Logik paparan ubat dalam jadual
            ub_batch = []
            for u_s in df_f['UBAT_LIST']: ub_batch.extend(str(u_s).split(' | '))
            for ub in sorted(list(set(ub_batch))):
                matrix[ub] = {}
                for l in labels:
                    p = df_f[df_f['NAMA'] == l].iloc[0]
                    un, uq = str(p['UBAT_LIST']).split(' | '), str(p['KUANTITI']).split(' | ')
                    matrix[ub][l] = uq[un.index(ub)] if ub in un else ""

            st.dataframe(pd.DataFrame(matrix).T, use_container_width=True)

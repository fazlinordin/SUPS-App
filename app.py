import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io
import time

# --- 1. SETTING AWAL ---
st.set_page_config(page_title="SUPS HJEM V8.1", layout="wide")

if 'bakul' not in st.session_state:
    st.session_state.bakul = []
if 'batch_kekal' not in st.session_state:
    st.session_state.batch_kekal = "Mac - Batch 1"
if 'proses_simpan' not in st.session_state:
    st.session_state.proses_simpan = False

URL_API = "https://script.google.com/macros/s/AKfycbyeZXuPoyqsORGh_-kPC8lVTiFe41qZvQ4V8gBQU_BXnmP30zufcjSDxN6HnqyzQRRu/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- 2. MASTER UBAT ---
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

# --- 3. UI ---
menu = st.sidebar.radio("NAVIGASI", ["📝 INPUT", "📊 SUMMARY"])
BATCH_OPTIONS = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    
    # FORM UTAMA (Untuk Nama, IC, Tarikh & Simpan)
    with st.form("borang_pesakit", clear_on_submit=True):
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            nama_raw = c1.text_input("Nama:")
            ic = c2.text_input("IC:")
            idx_b = BATCH_OPTIONS.index(st.session_state.batch_kekal)
            batch = c3.selectbox("Batch:", BATCH_OPTIONS, index=idx_b)
            
            c4, c5 = st.columns(2)
            t_u = c4.date_input("TCA Ambil Ubat (Hari Ini):", value=date.today())
            t_d = c5.date_input("TCA Klinik (Dr):", value=date.today())
            
            if t_d > t_u:
                st.success(f"🎯 **Sila bekalkan ubat untuk: {(t_d - t_u).days} Hari**")

        st.write("")
        st.subheader("🛒 Bakul Sementara")
        
        # Papar bakul di dalam form
        if st.session_state.bakul:
            for i, itm in enumerate(st.session_state.bakul):
                st.write(f"✅ {itm['u']} --- Qty: {itm['q']}")
            
            st.write("")
            if st.session_state.proses_simpan:
                st.form_submit_button("⏳ SEDANG MENYIMPAN...", disabled=True, use_container_width=True)
            else:
                simpan = st.form_submit_button("💾 SIMPAN DATA", type="primary", use_container_width=True)
        else:
            st.info("Bakul kosong. Tambah ubat di bawah.")
            simpan = False

    # BAHAGIAN PILIH UBAT (Di luar form supaya tak reset form masa klik 'Tambah')
    st.divider()
    with st.container(border=True):
        st.write("**Pilih Ubat:**")
        u1, u2 = st.columns([3, 1])
        p_u = u1.selectbox("Nama Ubat:", ["-- PILIH --"] + MASTER_UBAT, label_visibility="collapsed")
        p_q = u2.text_input("Qty:", placeholder="Contoh: 30", label_visibility="collapsed")
        
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("➕ Tambah Ke Bakul", use_container_width=True):
            if p_u != "-- PILIH --" and p_q:
                st.session_state.bakul.append({"u": p_u, "q": p_q})
                st.rerun()
        if col_btn2.button("🗑️ Kosongkan Bakul", use_container_width=True):
            st.session_state.bakul = []
            st.rerun()

    # LOGIK PROSES SIMPAN
    if simpan:
        if nama_raw and ic and st.session_state.bakul:
            st.session_state.proses_simpan = True
            payload = {
                "Nama": nama_raw.upper().strip(), "IC": f"'{ic.strip()}",
                "TCA_Ubat": str(t_u), "TCA_Clinic": str(t_d), "Batch": batch,
                "Ubat_List": " | ".join([x['u'] for x in st.session_state.bakul]),
                "Kuantiti": " | ".join([x['q'] for x in st.session_state.bakul])
            }
            try:
                requests.post(URL_API, json=payload, timeout=10)
                st.session_state.bakul = []
                st.session_state.proses_simpan = False
                st.session_state.batch_kekal = batch
                st.success("Berjaya Disimpan!")
                time.sleep(1); st.rerun()
            except:
                st.session_state.bakul = []; st.session_state.proses_simpan = False
                st.rerun()
        else:
            st.error("Lengkapkan maklumat & ubat!")

elif menu == "📊 SUMMARY":
    st.header("Checklist & Durasi Bekalan")
    df = load_data()
    if not df.empty:
        idx_s = BATCH_OPTIONS.index(st.session_state.batch_kekal)
        p_batch = st.selectbox("Pilih Batch:", BATCH_OPTIONS, index=idx_s)
        st.session_state.batch_kekal = p_batch
        df_f = df[df['BATCH'] == p_batch].copy()
        if not df_f.empty:
            # Menu Padam
            with st.expander("🗑️ PADAM REKOD PESAKIT"):
                list_pt = sorted(df_f['NAMA'].unique())
                p_padam = st.selectbox("Pilih Pesakit:", ["-- PILIH --"] + list_pt)
                if st.button("❗ PADAM"):
                    if p_padam != "-- PILIH --":
                        requests.post(URL_API, json={"action": "DELETE", "Nama": p_padam, "Batch": p_batch})
                        st.warning("Memadam..."); time.sleep(1); st.rerun()

            labels = df_f['NAMA'].unique()
            matrix = {}
            matrix["🆔 NO. IC"] = {l: str(df_f[df_f['NAMA']==l]['IC'].iloc[0]).replace("'","") for l in labels}
            matrix["⏳ DURASI"] = {l: f"{(pd.to_datetime(df_f[df_f['NAMA']==l]['TCA_CLINIC'].iloc[0]) - pd.to_datetime(df_f[df_f['NAMA']==l]['TCA_UBAT'].iloc[0])).days} HARI" for l in labels}
            
            u_b = []
            for u_s in df_f['UBAT_LIST']: u_b.extend(str(u_s).split(' | '))
            for ub in sorted(list(set(u_b))):
                matrix[ub] = {}
                for l in labels:
                    p = df_f[df_f['NAMA'] == l].iloc[0]
                    un, uq = str(p['UBAT_LIST']).split(' | '), str(p['KUANTITI']).split(' | ')
                    matrix[ub][l] = uq[un.index(ub)] if ub in un else ""

            res_df = pd.DataFrame(matrix).T
            st.dataframe(res_df.style.apply(lambda x: ['background-color: #DDEBF7' if i%2==0 else '' for i in range(len(x))], axis=0), use_container_width=True)

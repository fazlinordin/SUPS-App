import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io
import time

# --- 1. SETTING & KONFIGURASI ---
st.set_page_config(page_title="SUPS HJEM V5.8", layout="wide")

if 'bakul' not in st.session_state:
    st.session_state.bakul = []

# URL Google Sheets & Apps Script
URL_API = "https://script.google.com/macros/s/AKfycbyeZXuPoyqsORGh_-kPC8lVTiFe41qZvQ4V8gBQU_BXnmP30zufcjSDxN6HnqyzQRRu/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- 2. MASTER UBAT (Ditambah Fusidic Acid 2% Ointment) ---
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
    # ... anda boleh tambah ubat lain di sini jika perlu ...
])

# --- 3. FUNGSI LOAD DATA ---
def load_data():
    try:
        # Tambah timestamp untuk elakkan caching
        r = requests.get(f"{URL_SHEET_CSV}&t={time.time()}")
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = df.columns.str.strip().str.upper()
        return df
    except:
        return pd.DataFrame()

# --- 4. ANTARAMUKA (UI) ---
menu = st.sidebar.radio("NAVIGASI", ["📝 INPUT", "📊 SUMMARY"])

# Pilihan Batch
BATCH_OPTIONS = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    
    with st.form("input_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        nama = c1.text_input("Nama Pesakit:").upper()
        ic = c2.text_input("No. IC:")
        batch = c3.selectbox("Pilih Batch:", BATCH_OPTIONS)
        
        c4, c5 = st.columns(2)
        tca_u = c4.date_input("TCA Ambil Ubat:", value=date.today())
        tca_d = c5.date_input("TCA Klinik (Dr):", value=date.today())
        
        submitted = st.form_submit_button("💾 SIMPAN DATA KE CLOUD")

    st.divider()
    
    # Bahagian Tambah Ubat (Bakul)
    st.subheader("🛒 Bakul Ubat")
    u1, u2 = st.columns([3, 1])
    pilih_u = u1.selectbox("Pilih Nama Ubat:", ["-- SILIH --"] + MASTER_UBAT)
    pilih_q = u2.text_input("Kuantiti (Unit):")
    
    if st.button("➕ Tambah ke Bakul"):
        if pilih_u != "-- PILIH --" and pilih_q:
            st.session_state.bakul.append({"ubat": pilih_u, "qty": pilih_q})
            st.rerun()

    # Papar senarai dalam bakul
    if st.session_state.bakul:
        for i, item in enumerate(st.session_state.bakul):
            b1, b2, b3 = st.columns([3, 1, 0.5])
            b1.write(f"💊 {item['ubat']}")
            b2.write(f"{item['qty']}")
            if b3.button("🗑️", key=f"del_{i}"):
                st.session_state.bakul.pop(i)
                st.rerun()

    if submitted:
        if nama and ic and st.session_state.bakul:
            with st.spinner("Sedang menyimpan..."):
                payload = {
                    "Nama": nama,
                    "IC": ic,
                    "TCA_Ubat": str(tca_u),
                    "TCA_Clinic": str(tca_d),
                    "Batch": batch,
                    "Ubat_List": " | ".join([x['ubat'] for x in st.session_state.bakul]),
                    "Kuantiti": " | ".join([x['qty'] for x in st.session_state.bakul])
                }
                res = requests.post(URL_API, json=payload)
                if res.status_code == 200:
                    st.success(f"Data {nama} berjaya disimpan!")
                    st.session_state.bakul = []
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Gagal hantar ke Cloud.")
        else:
            st.warning("Sila isi Nama, IC dan sekurang-kurangnya 1 ubat.")

# --- 5. SUMMARY (NAMA + IC DALAM EXCEL) ---
elif menu == "📊 SUMMARY":
    st.header("Ringkasan Pengambilan Ubat")
    df = load_data()
    
    if not df.empty:
        pilih_batch = st.selectbox("Tapis mengikut Batch:", BATCH_OPTIONS)
        df_f = df[df['BATCH'] == pilih_batch].copy()
        
        if not df_f.empty:
            # Gabungkan Nama & IC untuk paparan dan download
            df_f['PESAKIT'] = df_f['NAMA'] + " (" + df_f['IC'].astype(str) + ")"
            
            # Buat Matrix Ubat
            matrix = {}
            labels = df_f['PESAKIT'].unique()
            
            # Header info
            matrix["📅 TCA AMBIL"] = {l: df_f[df_f['PESAKIT']==l]['TCA_UBAT'].iloc[0] for l in labels}
            matrix["👨‍⚕️ TCA KLINIK"] = {l: df_f[df_f['PESAKIT']==l]['TCA_CLINIC'].iloc[0] for l in labels}
            
            # Senarai ubat unik dalam batch
            senarai_ubat_batch = []
            for u_str in df_f['UBAT_LIST']:
                senarai_ubat_batch.extend(str(u_str).split(' | '))
            
            for ub in sorted(list(set(senarai_ubat_batch))):
                matrix[ub] = {}
                for l in labels:
                    p_data = df_f[df_f['PESAKIT'] == l].iloc[0]
                    u_list = str(p_data['UBAT_LIST']).split(' | ')
                    q_list = str(p_data['KUANTITI']).split(' | ')
                    matrix[ub][l] = q_list[u_list.index(ub)] if ub in u_list else ""
            
            res_df = pd.DataFrame(matrix).T
            st.dataframe(res_df, use_container_width=True)
            
            # Button Download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                res_df.to_excel(writer, sheet_name='Ringkasan')
            st.download_button(
                label="📥 MUAT TURUN EXCEL (TERMASUK IC)",
                data=output.getvalue(),
                file_name=f"Summary_{pilih_batch}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Tiada data ditemui untuk batch ini.")
    else:
        st.error("Gagal menarik data dari Google Sheets.")

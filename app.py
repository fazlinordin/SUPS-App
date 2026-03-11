import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io
import time

# --- 1. SETTING UTAMA ---
st.set_page_config(page_title="SUPS HJEM V6.9", layout="wide")

# Inisialisasi Session State (Wajib ada supaya bakul tak hilang)
if 'bakul' not in st.session_state:
    st.session_state.bakul = []

URL_API = "https://script.google.com/macros/s/AKfycbyeZXuPoyqsORGh_-kPC8lVTiFe41qZvQ4V8gBQU_BXnmP30zufcjSDxN6HnqyzQRRu/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- 2. MASTER LIST UBAT ---
MASTER_UBAT = sorted([
    "Abacavir 300mg Tablet", "Amlodipine 5 mg Tablet", "Atorvastatin 40 mg Tablet",
    "Ezetimibe 10 mg Tablet", "Metformin HCl 500 mg Tablet", "Simvastatin 10 mg Tablet",
    "Tiotropium 2.5mcg and Olodaterol 2.5mcg inhalation (Catridge only)"
]) 

# --- 3. FUNGSI TEKNIKAL ---
def load_data():
    try:
        r = requests.get(f"{URL_SHEET_CSV}&cache={int(time.time())}")
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

def hitung_hari(t1, t2):
    try:
        # Penukaran tarikh yang lebih "gentle" supaya durasi tak hilang
        d1 = pd.to_datetime(t1).date()
        d2 = pd.to_datetime(t2).date()
        return f"{(d2 - d1).days} HARI"
    except: return "-"

# --- 4. UI INPUT ---
menu = st.sidebar.radio("NAVIGASI", ["📝 INPUT", "📊 SUMMARY"])
SENARAI_BATCH = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    
    # Bahagian Maklumat Pesakit
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        # Gunakan value dari session_state untuk Nama & IC supaya boleh di-reset
        nama_in = c1.text_input("Nama:", key="in_nama").upper()
        ic_in = c2.text_input("IC:", key="in_ic")
        batch_in = c3.selectbox("Batch:", SENARAI_BATCH)
        
        c4, c5 = st.columns(2)
        t_u = c4.date_input("TCA Ambil Ubat (Hari Ini):", value=date.today())
        t_d = c5.date_input("TCA Klinik (Dr) [Opsional]:", value=None)

    # Bahagian Tambah Ubat (Guna balik gaya V5.8)
    with st.container(border=True):
        u1, u2 = st.columns([3, 1])
        p_u = u1.selectbox("Pilih Ubat:", ["-- PILIH --"] + MASTER_UBAT)
        p_q = u2.text_input("Qty:")
        if st.button("➕ Tambah Ke Bakul"):
            if p_u != "-- PILIH --" and p_q:
                st.session_state.bakul.append({"u": p_u, "q": p_q})
                st.rerun()

    # Paparan Bakul Sementara (Ada butang DELETE/Tong Sampah)
    if st.session_state.bakul:
        st.write("### 🛒 Bakul Sementara")
        for i, itm in enumerate(st.session_state.bakul):
            col_u, col_q, col_del = st.columns([3, 1, 0.5])
            col_u.write(itm['u'])
            col_q.write(itm['q'])
            if col_del.button("🗑️", key=f"del_{i}"):
                st.session_state.bakul.pop(i)
                st.rerun()
        
        # Butang Simpan
        if st.button("💾 SIMPAN DATA", type="primary", use_container_width=True):
            payload = {
                "Nama": nama_in, "IC": ic_in, "TCA_Ubat": str(t_u), 
                "TCA_Clinic": str(t_d) if t_d else "-", "Batch": batch_in,
                "Ubat_List": " | ".join([x['u'] for x in st.session_state.bakul]),
                "Kuantiti": " | ".join([x['q'] for x in st.session_state.bakul])
            }
            res = requests.post(URL_API, json=payload)
            if res.status_code == 200:
                st.session_state.bakul = [] # Kosongkan bakul
                st.success("Berjaya Disimpan!")
                time.sleep(1)
                st.rerun() # Ini akan reset text_input secara automatik

# --- 5. UI SUMMARY ---
elif menu == "📊 SUMMARY":
    st.header("Checklist & Durasi Bekalan")
    df = load_data()
    if not df.empty:
        b_pilih = st.selectbox("Pilih Batch:", SENARAI_BATCH)
        df_f = df[df['BATCH'] == b_pilih]
        
        if not df_f.empty:
            # Bina jadual Summary
            names = df_f['NAMA'].unique()
            summary_list = []
            
            # Row Tarikh & Durasi
            r_u = {"ITEM": "📅 TCA AMBIL"}
            r_d = {"ITEM": "👨‍⚕️ TCA DR"}
            r_dur = {"ITEM": "⏳ DURASI"}
            
            for n in names:
                d = df_f[df_f['NAMA'] == n].iloc[0]
                r_u[n] = d['TCA_UBAT']
                r_d[n] = d['TCA_CLINIC']
                r_dur[n] = hitung_hari(d['TCA_UBAT'], d['TCA_CLINIC'])
            
            summary_list.extend([r_u, r_d, r_dur])
            
            # Row Ubat
            all_u = []
            for _, row in df_f.iterrows():
                all_u.extend(str(row['UBAT_LIST']).split(' | '))
            
            for ub in sorted(list(set(all_u))):
                r_u = {"ITEM": ub}
                for n in names:
                    d = df_f[df_f['NAMA'] == n].iloc[0]
                    ul = str(d['UBAT_LIST']).split(' | ')
                    ql = str(d['KUANTITI']).split(' | ')
                    r_u[n] = ql[ul.index(ub)] if ub in ul else ""
                summary_list.append(r_u)
                
            st.dataframe(pd.DataFrame(summary_list).set_index("ITEM"), use_container_width=True)

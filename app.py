import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io
import time

# --- 1. SETTING ---
st.set_page_config(page_title="SUPS HJEM V8.5", layout="wide")

if 'bakul' not in st.session_state:
    st.session_state.bakul = []

URL_API = "https://script.google.com/macros/s/AKfycbyeZXuPoyqsORGh_-kPC8lVTiFe41qZvQ4V8gBQU_BXnmP30zufcjSDxN6HnqyzQRRu/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- 2. MASTER LIST ---
MASTER_UBAT = sorted(["Amlodipine 5 mg Tablet", "Atorvastatin 40 mg Tablet", "Ezetimibe 10 mg Tablet", "Metformin HCl 500 mg Tablet", "Tiotropium 2.5mcg and Olodaterol 2.5mcg inhalation (Catridge only)"])

# --- 3. FUNGSI ---
def load_data():
    try:
        # Tambah random number supaya data sentiasa 'fresh'
        r = requests.get(f"{URL_SHEET_CSV}&t={int(time.time())}")
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

# --- 4. UI INPUT ---
menu = st.sidebar.radio("NAVIGASI", ["📝 INPUT", "📊 SUMMARY"])
BATCH_OPTIONS = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    
    with st.form("input_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        nama = c1.text_input("Nama:").upper()
        ic = c2.text_input("IC:")
        batch = c3.selectbox("Batch:", BATCH_OPTIONS)
        
        c4, c5 = st.columns(2)
        t_u = c4.date_input("TCA Ambil Ubat:", value=date.today())
        # TIPS: Jika klinik belum tahu, setkan tarikh jauh ke depan atau sama dengan hari ini
        t_d = c5.date_input("TCA Klinik (Dr):", value=date.today()) 
        
        submit_data = st.form_submit_button("💾 SIMPAN & RESET")

    st.divider()
    
    with st.container(border=True):
        u1, u2 = st.columns([3, 1])
        p_u = u1.selectbox("Pilih Ubat:", ["-- PILIH --"] + MASTER_UBAT)
        p_q = u2.text_input("Qty:")
        if st.button("➕ Tambah"):
            if p_u != "-- PILIH --" and p_q:
                st.session_state.bakul.append({"u": p_u, "q": p_q})
                st.rerun()

    if st.session_state.bakul:
        for i, itm in enumerate(st.session_state.bakul):
            col_u, col_q, col_del = st.columns([3, 1, 0.5])
            col_u.write(f"✅ {itm['u']}")
            col_q.write(itm['q'])
            if col_del.button("🗑️", key=f"del_{i}"):
                st.session_state.bakul.pop(i)
                st.rerun()

    if submit_data:
        if nama and ic and st.session_state.bakul:
            payload = {
                "Nama": nama, "IC": ic, "TCA_Ubat": str(t_u), 
                "TCA_Clinic": str(t_d), "Batch": batch,
                "Ubat_List": " | ".join([x['u'] for x in st.session_state.bakul]),
                "Kuantiti": " | ".join([x['q'] for x in st.session_state.bakul])
            }
            requests.post(URL_API, json=payload)
            st.session_state.bakul = []
            st.success("Data Berjaya Disimpan!")
            time.sleep(1)
            st.rerun()

# --- 5. UI SUMMARY (KAEDAH BARU: NO-FAIL MATRIX) ---
elif menu == "📊 SUMMARY":
    st.header("Checklist & Durasi")
    df = load_data()
    
    if not df.empty:
        pilih_batch = st.selectbox("Pilih Batch:", BATCH_OPTIONS)
        # Filter ikut batch
        df_f = df[df['BATCH'] == pilih_batch].copy()
        
        if not df_f.empty:
            # Bina jadual secara manual menggunakan Dictionary
            names = df_f['NAMA'].unique()
            matrix = {}
            
            # Kita senaraikan baris-baris wajib dulu
            rows_wajib = ["📅 TCA AMBIL", "👨‍⚕️ TCA DR", "⏳ DURASI"]
            
            for row_name in rows_wajib:
                matrix[row_name] = {}
                for n in names:
                    p_data = df_f[df_f['NAMA'] == n].iloc[0]
                    
                    if row_name == "📅 TCA AMBIL":
                        matrix[row_name][n] = p_data['TCA_UBAT']
                    elif row_name == "👨‍⚕️ TCA DR":
                        matrix[row_name][n] = p_data['TCA_CLINIC']
                    elif row_name == "⏳ DURASI":
                        try:
                            # Cuba kira durasi
                            d1 = pd.to_datetime(p_data['TCA_UBAT']).date()
                            d2 = pd.to_datetime(p_data['TCA_CLINIC']).date()
                            matrix[row_name][n] = f"{(d2 - d1).days} HARI"
                        except:
                            matrix[row_name][n] = "DATA TIDAK CUKUP"

            # Tambah baris ubat
            all_ubats = []
            for u_str in df_f['UBAT_LIST']:
                all_ubats.extend(str(u_str).split(' | '))
            
            for ub in sorted(list(set(all_ubats))):
                matrix[ub] = {}
                for n in names:
                    p_data = df_f[df_f['NAMA'] == n].iloc[0]
                    u_list = str(p_data['UBAT_LIST']).split(' | ')
                    q_list = str(p_data['KUANTITI']).split(' | ')
                    if ub in u_list:
                        matrix[ub][n] = q_list[u_list.index(ub)]
                    else:
                        matrix[ub][n] = ""

            # Paparkan Matrix
            res_df = pd.DataFrame(matrix).T
            st.dataframe(res_df, use_container_width=True)

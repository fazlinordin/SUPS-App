import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io
import time

# --- 1. SETTING UTAMA ---
st.set_page_config(page_title="SUPS HJEM V7.5", layout="wide")

if 'bakul' not in st.session_state:
    st.session_state.bakul = []

URL_API = "https://script.google.com/macros/s/AKfycbyeZXuPoyqsORGh_-kPC8lVTiFe41qZvQ4V8gBQU_BXnmP30zufcjSDxN6HnqyzQRRu/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- 2. MASTER LIST UBAT --- (Sila masukkan senarai penuh Fazli)
MASTER_UBAT = sorted(["Amlodipine 5 mg Tablet", "Atorvastatin 40 mg Tablet", "Ezetimibe 10 mg Tablet", "Metformin HCl 500 mg Tablet", "Tiotropium 2.5mcg and Olodaterol 2.5mcg inhalation (Catridge only)"]) 

# --- 3. FUNGSI ---
def load_data():
    try:
        r = requests.get(f"{URL_SHEET_CSV}&cache={int(time.time())}")
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

def hitung_durasi_tepat(t1, t2):
    """Logik pengiraan durasi yang paling stabil"""
    if not t1 or not t2 or str(t2) == "-" or str(t2).strip() == "": return "-"
    try:
        # Tukar format YYYY-MM-DD kepada date object
        d1 = pd.to_datetime(t1).date()
        d2 = pd.to_datetime(t2).date()
        selisih = (d2 - d1).days
        return f"{selisih} HARI"
    except:
        return "-"

# --- 4. UI INPUT ---
menu = st.sidebar.radio("NAVIGASI", ["📝 INPUT", "📊 SUMMARY"])
SENARAI_BATCH = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    
    # Guna Form dengan clear_on_submit=True untuk RESET IC & NAMA
    with st.form("main_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        nama_in = c1.text_input("Nama:").upper()
        ic_in = c2.text_input("IC:")
        batch_in = c3.selectbox("Batch:", SENARAI_BATCH)
        
        c4, c5 = st.columns(2)
        t_u = c4.date_input("TCA Ambil Ubat:", value=date.today())
        t_d = c5.date_input("TCA Klinik (Dr):", value=None)
        
        simpan_click = st.form_submit_button("💾 SIMPAN SEMUA DATA", use_container_width=True)

    st.divider()
    
    # Bahagian Bakul (Di luar form supaya boleh delete/tambah)
    with st.container(border=True):
        u1, u2 = st.columns([3, 1])
        p_u = u1.selectbox("Pilih Ubat:", ["-- PILIH --"] + MASTER_UBAT)
        p_q = u2.text_input("Qty:")
        if st.button("➕ Tambah Ke Bakul"):
            if p_u != "-- PILIH --" and p_q:
                st.session_state.bakul.append({"u": p_u, "q": p_q})
                st.rerun()

    if st.session_state.bakul:
        st.write("### 🛒 Bakul Sementara")
        for i, itm in enumerate(st.session_state.bakul):
            col_u, col_q, col_del = st.columns([3, 1, 0.5])
            col_u.write(itm['u'])
            col_q.write(itm['q'])
            if col_del.button("🗑️", key=f"del_{i}"):
                st.session_state.bakul.pop(i)
                st.rerun()

    if simpan_click:
        if not nama_in or not ic_in or not st.session_state.bakul:
            st.error("Sila isi Nama, IC, dan Tambah Ubat dahulu!")
        else:
            payload = {
                "Nama": nama_in, "IC": ic_in, "TCA_Ubat": str(t_u), 
                "TCA_Clinic": str(t_d) if t_d else "-", "Batch": batch_in,
                "Ubat_List": " | ".join([x['u'] for x in st.session_state.bakul]),
                "Kuantiti": " | ".join([x['q'] for x in st.session_state.bakul])
            }
            res = requests.post(URL_API, json=payload)
            if res.status_code == 200:
                st.session_state.bakul = []
                st.success("Berjaya Simpan! IC dan Nama telah di-reset.")
                time.sleep(1.5)
                st.rerun()

# --- 5. UI SUMMARY (DURASI FIXED) ---
elif menu == "📊 SUMMARY":
    st.header("Checklist & Durasi Bekalan")
    df = load_data()
    
    if not df.empty:
        b_pilih = st.selectbox("Pilih Batch:", SENARAI_BATCH)
        df_f = df[df['BATCH'] == b_pilih]
        
        if not df_f.empty:
            # Pastikan tarikh adalah dalam format datetime supaya boleh tolak
            df_f['TCA_UBAT'] = pd.to_datetime(df_f['TCA_UBAT'], errors='coerce')
            df_f['TCA_CLINIC'] = pd.to_datetime(df_f['TCA_CLINIC'], errors='coerce')
            
            names = df_f['NAMA'].unique()
            final_summary = []
            
            # 1. Baris TCA AMBIL
            r_u = {"ITEM": "📅 TCA AMBIL"}
            for n in names:
                val = df_f[df_f['NAMA'] == n]['TCA_UBAT'].iloc[0]
                r_u[n] = val.strftime('%d-%m-%Y') if pd.notnull(val) else "-"
            final_summary.append(r_u)
            
            # 2. Baris TCA CLINIC
            r_d = {"ITEM": "👨‍⚕️ TCA DR"}
            for n in names:
                val = df_f[df_f['NAMA'] == n]['TCA_CLINIC'].iloc[0]
                r_d[n] = val.strftime('%d-%m-%Y') if pd.notnull(val) else "-"
            final_summary.append(r_d)
            
            # 3. Baris DURASI (Logik Baru)
            r_dur = {"ITEM": "⏳ DURASI"}
            for n in names:
                d1 = df_f[df_f['NAMA'] == n]['TCA_UBAT'].iloc[0]
                d2 = df_f[df_f['NAMA'] == n]['TCA_CLINIC'].iloc[0]
                if pd.notnull(d1) and pd.notnull(d2):
                    diff = (d2 - d1).days
                    r_dur[n] = f"{diff} HARI"
                else:
                    r_dur[n] = "-"
            final_summary.append(r_dur)
            
            # 4. Baris Ubat-ubatan
            all_u = []
            for _, r in df_f.iterrows():
                all_u.extend(str(r['UBAT_LIST']).split(' | '))
            
            for ub in sorted(list(set(all_u))):
                r_ubat = {"ITEM": ub}
                for n in names:
                    d_p = df_f[df_f['NAMA'] == n].iloc[0]
                    u_l = str(d_p['UBAT_LIST']).split(' | ')
                    q_l = str(d_p['KUANTITI']).split(' | ')
                    r_ubat[n] = q_l[u_l.index(ub)] if ub in u_l else ""
                final_summary.append(r_ubat)
                
            st.dataframe(pd.DataFrame(final_summary).set_index("ITEM"), use_container_width=True)

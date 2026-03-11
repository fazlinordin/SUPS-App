import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io
import time

# --- 1. SETTING ---
st.set_page_config(page_title="SUPS HJEM V6.8", layout="wide")

# Gunakan 'count' untuk paksa kotak input reset (IC & Nama)
if 'count' not in st.session_state:
    st.session_state.count = 0
if 'bakul' not in st.session_state:
    st.session_state.bakul = []

URL_API = "https://script.google.com/macros/s/AKfycbyeZXuPoyqsORGh_-kPC8lVTiFe41qZvQ4V8gBQU_BXnmP30zufcjSDxN6HnqyzQRRu/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- 2. MASTER LIST --- (Sila masukkan list penuh anda nanti)
MASTER_UBAT = sorted(["Atorvastatin 40 mg Tablet", "Ezetimibe 10 mg Tablet", "Amlodipine 5 mg Tablet", "Metformin HCl 500 mg Tablet"])

# --- 3. FUNGSI ---
def load_data():
    try:
        r = requests.get(f"{URL_SHEET_CSV}&cache={int(time.time())}")
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

def hitung_durasi(tca_u, tca_d):
    try:
        # Paksa tukar ke format tarikh tak kira apa pun format asal
        d1 = pd.to_datetime(tca_u).date()
        d2 = pd.to_datetime(tca_d).date()
        diff = (d2 - d1).days
        return f"{diff} HARI"
    except:
        return "N/A"

# --- 4. NAVIGASI ---
menu = st.sidebar.radio("MENU", ["📝 INPUT", "📊 SUMMARY"])
BATCH_LIST = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    
    # Guna 'key' yang berubah (count) untuk paksa reset Nama & IC
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        nama = c1.text_input("Nama:", key=f"nama_{st.session_state.count}").upper()
        ic = c2.text_input("IC:", key=f"ic_{st.session_state.count}")
        batch = c3.selectbox("Batch:", BATCH_LIST)
        
        c4, c5 = st.columns(2)
        t_u = c4.date_input("TCA Ambil Ubat:", value=date.today())
        t_d = c5.date_input("TCA Klinik Dr:", value=None)

    with st.form("form_ubat", clear_on_submit=True):
        u1, u2 = st.columns([3, 1])
        sel_u = u1.selectbox("Pilih Ubat:", ["-- PILIH --"] + MASTER_UBAT)
        sel_q = u2.text_input("Kuantiti:")
        if st.form_submit_button("Tambah"):
            if sel_u != "-- PILIH --" and sel_q:
                st.session_state.bakul.append({"u": sel_u, "q": sel_q})
                st.rerun()

    if st.session_state.bakul:
        for itm in st.session_state.bakul:
            st.write(f"✅ {itm['u']} ({itm['q']})")
        
        if st.button("💾 SIMPAN SEMUA", type="primary"):
            payload = {
                "Nama": nama, "IC": ic, "TCA_Ubat": str(t_u), 
                "TCA_Clinic": str(t_d) if t_d else "-", "Batch": batch,
                "Ubat_List": " | ".join([x['u'] for x in st.session_state.bakul]),
                "Kuantiti": " | ".join([x['q'] for x in st.session_state.bakul])
            }
            requests.post(URL_API, json=payload)
            
            # PROSES RESET
            st.session_state.bakul = []
            st.session_state.count += 1  # Tukar key supaya kotak Nama/IC kosong
            st.success("Berjaya Disimpan!")
            time.sleep(1)
            st.rerun()

elif menu == "📊 SUMMARY":
    st.header("Checklist & Durasi")
    df = load_data()
    if not df.empty:
        pilih_b = st.selectbox("Pilih Batch:", BATCH_LIST)
        df_f = df[df['BATCH'] == pilih_b]
        
        if not df_f.empty:
            names = df_f['NAMA'].unique()
            final_data = []
            
            # Bina baris tarikh & durasi
            row_u = {"ITEM": "📅 TCA AMBIL"}
            row_d = {"ITEM": "👨‍⚕️ TCA DR"}
            row_dur = {"ITEM": "⏳ DURASI"}
            
            for n in names:
                d_p = df_f[df_f['NAMA'] == n].iloc[0]
                row_u[n] = d_p['TCA_UBAT']
                row_d[n] = d_p['TCA_CLINIC']
                row_dur[n] = hitung_durasi(d_p['TCA_UBAT'], d_p['TCA_CLINIC'])
            
            final_data.extend([row_u, row_d, row_dur])
            
            # Bina baris ubat
            all_u = []
            for _, r in df_f.iterrows():
                all_u.extend(str(r['UBAT_LIST']).split(' | '))
            
            for ub in sorted(list(set(all_u))):
                row_ubat = {"ITEM": ub}
                for n in names:
                    d_p = df_f[df_f['NAMA'] == n].iloc[0]
                    u_l = str(d_p['UBAT_LIST']).split(' | ')
                    q_l = str(d_p['KUANTITI']).split(' | ')
                    row_ubat[n] = q_l[u_l.index(ub)] if ub in u_l else ""
                final_data.append(row_ubat)
                
            st.dataframe(pd.DataFrame(final_data).set_index("ITEM"), use_container_width=True)

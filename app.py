import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io
import time

# --- 1. SETTING ---
st.set_page_config(page_title="SUPS HJEM V5.8 ULTIMATE", layout="wide")

# Session State untuk simpan ubat dalam bakul & reset input
if 'bakul' not in st.session_state:
    st.session_state.bakul = []

URL_API = "https://script.google.com/macros/s/AKfycbyeZXuPoyqsORGh_-kPC8lVTiFe41qZvQ4V8gBQU_BXnmP30zufcjSDxN6HnqyzQRRu/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- 2. MASTER LIST UBAT ---
# (Gunakan list penuh Fazli di sini)
MASTER_UBAT = sorted(["Abacavir 300mg Tablet", "Amlodipine 5 mg Tablet", "Metformin HCl 500 mg Tablet", "Atorvastatin 40 mg Tablet"])

# --- 3. FUNGSI TEKNIKAL ---
def load_data():
    try:
        r = requests.get(f"{URL_SHEET_CSV}&cache={int(time.time())}")
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

def kira_durasi(t1, t2):
    try:
        # Cuba kesan format tarikh secara automatik
        d1 = pd.to_datetime(t1).date()
        d2 = pd.to_datetime(t2).date()
        diff = (d2 - d1).days
        return f"{diff} HARI"
    except:
        return "TIADA DATA"

# --- 4. UI INPUT ---
menu = st.sidebar.radio("NAVIGASI", ["📝 INPUT", "📊 SUMMARY"])
SENARAI_BATCH = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    
    # Guna form supaya butang Tambah Ubat tak reset Nama/IC
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        # Gunakan key untuk memudahkan reset manual
        nama = c1.text_input("Nama:", key="input_nama").upper()
        ic = c2.text_input("IC:", key="input_ic")
        batch = c3.selectbox("Batch:", SENARAI_BATCH)
        
        c4, c5 = st.columns(2)
        t_u = c4.date_input("TCA Ambil Ubat:", value=date.today())
        t_d = c5.date_input("TCA Klinik Dr:", value=None)

    # Bahagian Tambah Ubat
    with st.form("tambah_ubat", clear_on_submit=True):
        u1, u2 = st.columns([3, 1])
        p_u = u1.selectbox("Pilih Ubat:", ["-- PILIH --"] + MASTER_UBAT)
        p_q = u2.text_input("Kuantiti:")
        if st.form_submit_button("Tambah ke Bakul"):
            if p_u != "-- PILIH --" and p_q:
                st.session_state.bakul.append({"u": p_u, "q": p_q})
                st.rerun()

    # Paparan Bakul
    if st.session_state.bakul:
        st.write("### 🛒 Senarai Ubat")
        for i, itm in enumerate(st.session_state.bakul):
            st.text(f"{i+1}. {itm['u']} - {itm['q']}")
        
        if st.button("💾 SIMPAN SEMUA DATA", type="primary"):
            if not nama or not ic:
                st.error("Sila isi Nama dan IC sebelum simpan!")
            else:
                payload = {
                    "Nama": nama, "IC": ic, "TCA_Ubat": str(t_u), 
                    "TCA_Clinic": str(t_d) if t_d else "-", "Batch": batch,
                    "Ubat_List": " | ".join([x['u'] for x in st.session_state.bakul]),
                    "Kuantiti": " | ".join([x['q'] for x in st.session_state.bakul])
                }
                
                with st.spinner("Sedang menyimpan..."):
                    res = requests.post(URL_API, json=payload)
                    if res.status_code == 200:
                        # RESET SEMUA
                        st.session_state.bakul = []
                        # Cara paksa reset text_input:
                        st.session_state.input_nama = ""
                        st.session_state.input_ic = ""
                        st.success("Berjaya Disimpan! Nama & IC telah dikosongkan.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Gagal menyambung database!")

# --- 5. UI SUMMARY ---
elif menu == "📊 SUMMARY":
    st.header("Checklist & Durasi Bekalan")
    df_raw = load_data()
    
    if not df_raw.empty:
        batch_pilihan = st.selectbox("Pilih Batch:", SENARAI_BATCH)
        df_f = df_raw[df_raw['BATCH'] == batch_pilihan]
        
        if not df_f.empty:
            # Bina Jadual Durasi (Row 1-3)
            headers = []
            names = df_f['NAMA'].unique()
            
            row_u = {"ITEM": "📅 TCA AMBIL"}
            row_d = {"ITEM": "👨‍⚕️ TCA DR"}
            row_dur = {"ITEM": "⏳ DURASI"}
            
            for n in names:
                data = df_f[df_f['NAMA'] == n].iloc[0]
                row_u[n] = data['TCA_UBAT']
                row_d[n] = data['TCA_CLINIC']
                row_dur[n] = kira_durasi(data['TCA_UBAT'], data['TCA_CLINIC'])
            
            headers = [row_u, row_d, row_dur]
            
            # Bina Jadual Ubat
            all_u = []
            for _, r in df_f.iterrows():
                all_u.extend(str(r['UBAT_LIST']).split(' | '))
            
            unique_ubats = sorted(list(set(all_u)))
            
            ubat_rows = []
            for ub in unique_ubats:
                row = {"ITEM": ub}
                for n in names:
                    data = df_f[df_f['NAMA'] == n].iloc[0]
                    u_list = str(data['UBAT_LIST']).split(' | ')
                    q_list = str(data['KUANTITI']).split(' | ')
                    row[n] = q_list[u_list.index(ub)] if ub in u_list else ""
                ubat_rows.append(row)
            
            # Gabung & Papar
            final_df = pd.DataFrame(headers + ubat_rows).set_index("ITEM")
            st.dataframe(final_df, use_container_width=True)
        else:
            st.warning("Tiada data untuk batch ini.")

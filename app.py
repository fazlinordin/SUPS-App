import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io
import time

# --- 1. SETTING AWAL ---
st.set_page_config(page_title="SUPS HJEM V5.8 REPAIR", layout="wide")

# Inisialisasi Session State (Tempat simpan data sementara)
if 'bakul' not in st.session_state:
    st.session_state.bakul = []
if 'input_nama' not in st.session_state:
    st.session_state.input_nama = ""
if 'input_ic' not in st.session_state:
    st.session_state.input_ic = ""

URL_API = "https://script.google.com/macros/s/AKfycbyeZXuPoyqsORGh_-kPC8lVTiFe41qZvQ4V8gBQU_BXnmP30zufcjSDxN6HnqyzQRRu/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- 2. MASTER LIST UBAT LENGKAP ---
# Sila masukkan list ubat anda di sini (Saya pendekkan untuk ruang, guna list panjang tadi ya)
MASTER_UBAT = sorted(["Abacavir 300mg Tablet", "Amlodipine 5 mg Tablet", "Metformin HCl 500 mg Tablet", "Simvastatin 10 mg Tablet"]) 

# --- 3. FUNGSI ---
def load_data():
    try:
        r = requests.get(f"{URL_SHEET_CSV}&cache={int(time.time())}")
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

def hitung_hari(t1, t2):
    try:
        d1 = pd.to_datetime(t1).date()
        d2 = pd.to_datetime(t2).date()
        return f"{(d2 - d1).days} HARI"
    except: return "-"

# --- 4. UI ---
menu = st.sidebar.radio("MENU", ["📝 INPUT", "📊 SUMMARY"])
SENARAI_BATCH = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    
    # Guna form untuk handle reset dengan lebih bersih
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        # Link terus ke session state
        nama_in = c1.text_input("Nama:", value=st.session_state.input_nama, key="nama_key").upper()
        ic_in = c2.text_input("IC:", value=st.session_state.input_ic, key="ic_key")
        batch_in = c3.selectbox("Batch:", SENARAI_BATCH)
        
        c4, c5 = st.columns(2)
        t_u = c4.date_input("TCA Ambil Ubat:", value=date.today())
        t_d = c5.date_input("TCA Klinik Dr:", value=None)

    with st.form("u_form", clear_on_submit=True):
        u1, u2 = st.columns([3, 1])
        p_u = u1.selectbox("Ubat:", ["-- PILIH --"] + MASTER_UBAT)
        p_q = u2.text_input("Kuantiti:")
        if st.form_submit_button("Tambah"):
            if p_u != "-- PILIH --" and p_q:
                st.session_state.bakul.append({"u": p_u, "q": p_q})
                # Simpan nama & ic supaya tak hilang masa tambah ubat
                st.session_state.input_nama = nama_in
                st.session_state.input_ic = ic_in
                st.rerun()

    if st.session_state.bakul:
        st.write("### 🛒 Senarai Ubat")
        for i, itm in enumerate(st.session_state.bakul):
            st.text(f"{i+1}. {itm['u']} - {itm['q']}")
        
        if st.button("💾 SIMPAN SEMUA", type="primary"):
            payload = {
                "Nama": nama_in, "IC": ic_in, "TCA_Ubat": str(t_u), 
                "TCA_Clinic": str(t_d) if t_d else "-", "Batch": batch_in,
                "Ubat_List": " | ".join([x['u'] for x in st.session_state.bakul]),
                "Kuantiti": " | ".join([x['q'] for x in st.session_state.bakul])
            }
            requests.post(URL_API, json=payload)
            
            # --- BAGIAN RESET (PENTING) ---
            st.session_state.bakul = []
            st.session_state.input_nama = "" # Kosongkan Nama
            st.session_state.input_ic = ""   # Kosongkan IC
            
            st.success("Data Berjaya Disimpan!")
            time.sleep(1)
            st.rerun()

elif menu == "📊 SUMMARY":
    st.header("Ringkasan Batch")
    df = load_data()
    if not df.empty:
        b_pilih = st.selectbox("Pilih Batch:", SENARAI_BATCH)
        df_f = df[df['BATCH'] == b_pilih]
        
        if not df_f.empty:
            # Guna cara manual bina Matrix supaya Durasi tak lari
            matrix_final = []
            names = df_f['NAMA'].unique()
            
            # 1. Baris Durasi
            row_dur = {"ITEM": "⏳ DURASI"}
            row_t_u = {"ITEM": "📅 TCA AMBIL"}
            row_t_d = {"ITEM": "👨‍⚕️ TCA DR"}
            
            for n in names:
                data_p = df_f[df_f['NAMA'] == n].iloc[0]
                row_dur[n] = hitung_hari(data_p['TCA_UBAT'], data_p['TCA_CLINIC'])
                row_t_u[n] = data_p['TCA_UBAT']
                row_t_d[n] = data_p['TCA_CLINIC']
            
            matrix_final.append(row_t_u)
            matrix_final.append(row_t_d)
            matrix_final.append(row_dur)
            
            # 2. Baris Ubat
            all_ubats = []
            for _, r in df_f.iterrows():
                u_lists = str(r['UBAT_LIST']).split(' | ')
                all_ubats.extend(u_lists)
            
            for ubat_unique in sorted(list(set(all_ubats))):
                row_u = {"ITEM": ubat_unique}
                for n in names:
                    data_p = df_f[df_f['NAMA'] == n].iloc[0]
                    u_p = str(data_p['UBAT_LIST']).split(' | ')
                    q_p = str(data_p['KUANTITI']).split(' | ')
                    if ubat_unique in u_p:
                        idx = u_p.index(ubat_unique)
                        row_u[n] = q_p[idx]
                    else:
                        row_u[n] = ""
                matrix_final.append(row_u)
                
            res_df = pd.DataFrame(matrix_final).set_index("ITEM")
            st.dataframe(res_df, use_container_width=True)

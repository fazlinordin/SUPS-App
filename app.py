import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io
import time

# --- 1. SETTING & KONFIGURASI ---
st.set_page_config(page_title="SUPS HJEM V5.9", layout="wide")

if 'bakul' not in st.session_state:
    st.session_state.bakul = []

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

# --- 3. FUNGSI LOAD DATA ---
def load_data():
    try:
        r = requests.get(f"{URL_SHEET_CSV}&t={time.time()}")
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = df.columns.str.strip().str.upper()
        return df
    except:
        return pd.DataFrame()

# --- 4. FUNGSI DOWNLOAD EXCEL (FIX IC FORMAT) ---
def to_excel_v59(df):
    output = io.BytesIO()
    # Pastikan semua data ditukar ke string untuk elak Scientific Notation
    df_string = df.astype(str)
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_string.to_excel(writer, sheet_name='Summary')
        workbook  = writer.book
        worksheet = writer.sheets['Summary']
        
        # Format untuk memastikan IC dibaca sebagai teks (Quote prefix)
        text_format = workbook.add_format({'num_format': '@'})
        
        # Cari baris mana yang ada "🆔 NO. IC"
        for row_num, index_val in enumerate(df.index):
            if "IC" in str(index_val):
                # Set format Teks untuk seluruh baris IC tersebut
                worksheet.set_row(row_num + 1, None, text_format)
                
        worksheet.set_column(0, 0, 40) # Lebar kolum Nama Ubat
        worksheet.set_column(1, len(df.columns), 20, text_format) # Lebar kolum Pesakit & format teks
        
    return output.getvalue()

# --- 5. UI ---
menu = st.sidebar.radio("NAVIGASI", ["📝 INPUT", "📊 SUMMARY"])
BATCH_OPTIONS = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    with st.form("input_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        nama = c1.text_input("Nama Pesakit:").upper()
        ic = c2.text_input("No. IC (Tanpa -):")
        batch = c3.selectbox("Pilih Batch:", BATCH_OPTIONS)
        c4, c5 = st.columns(2)
        tca_u = c4.date_input("TCA Ambil Ubat:", value=date.today())
        tca_d = c5.date_input("TCA Klinik (Dr):", value=date.today())
        submitted = st.form_submit_button("💾 SIMPAN DATA")

    st.divider()
    st.subheader("🛒 Bakul Ubat")
    u1, u2 = st.columns([3, 1])
    pilih_u = u1.selectbox("Pilih Nama Ubat:", ["-- PILIH --"] + MASTER_UBAT)
    pilih_q = u2.text_input("Kuantiti:")
    
    if st.button("➕ Tambah"):
        if pilih_u != "-- PILIH --" and pilih_q:
            st.session_state.bakul.append({"ubat": pilih_u, "qty": pilih_q})
            st.rerun()

    if st.session_state.bakul:
        for i, item in enumerate(st.session_state.bakul):
            b1, b2, b3 = st.columns([3, 1, 0.5])
            b1.write(f"💊 {item['ubat']}")
            b2.write(f"{item['qty']}")
            if b3.button("🗑️", key=f"del_{i}"):
                st.session_state.bakul.pop(i); st.rerun()

    if submitted:
        if nama and ic and st.session_state.bakul:
            payload = {
                "Nama": nama, "IC": f"'{ic}", # Tambah single quote supaya Google Sheet baca sebagai teks
                "TCA_Ubat": str(tca_u), "TCA_Clinic": str(tca_d), "Batch": batch,
                "Ubat_List": " | ".join([x['ubat'] for x in st.session_state.bakul]),
                "Kuantiti": " | ".join([x['qty'] for x in st.session_state.bakul])
            }
            res = requests.post(URL_API, json=payload)
            if res.status_code == 200:
                st.success("Berjaya!"); st.session_state.bakul = []; time.sleep(1); st.rerun()

elif menu == "📊 SUMMARY":
    st.header("Checklist & Durasi Bekalan")
    df = load_data()
    if not df.empty:
        pilih_batch = st.selectbox("Pilih Batch:", BATCH_OPTIONS)
        df_f = df[df['BATCH'] == pilih_batch].copy()
        if not df_f.empty:
            matrix = {}
            labels = df_f['NAMA'].unique()
            
            # Format IC sebagai teks
            matrix["🆔 NO. IC"] = {l: str(df_f[df_f['NAMA']==l]['IC'].iloc[0]).replace("'","") for l in labels}
            matrix["📅 TCA AMBIL"] = {l: df_f[df_f['NAMA']==l]['TCA_UBAT'].iloc[0] for l in labels}
            matrix["👨‍⚕️ TCA DR"] = {l: df_f[df_f['NAMA']==l]['TCA_CLINIC'].iloc[0] for l in labels}
            
            # Durasi
            def get_dur(n):
                try:
                    d1 = pd.to_datetime(df_f[df_f['NAMA']==n]['TCA_UBAT'].iloc[0]).date()
                    d2 = pd.to_datetime(df_f[df_f['NAMA']==n]['TCA_CLINIC'].iloc[0]).date()
                    return f"{(d2 - d1).days} HARI"
                except: return "-"
            matrix["⏳ DURASI"] = {l: get_dur(l) for l in labels}
            
            # Ubat
            u_batch = []
            for u_s in df_f['UBAT_LIST']: u_batch.extend(str(u_s).split(' | '))
            for ub in sorted(list(set(u_batch))):
                matrix[ub] = {}
                for l in labels:
                    p = df_f[df_f['NAMA'] == l].iloc[0]
                    ul, ql = str(p['UBAT_LIST']).split(' | '), str(p['KUANTITI']).split(' | ')
                    matrix[ub][l] = ql[ul.index(ub)] if ub in ul else ""
            
            res_df = pd.DataFrame(matrix).T
            st.dataframe(res_df, use_container_width=True)
            
            st.download_button(
                label="📥 MUAT TURUN EXCEL (FIX IC)",
                data=to_excel_v59(res_df),
                file_name=f"Summary_{pilih_batch}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

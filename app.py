import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io
import time
import re

# --- 1. SETTING AWAL ---
st.set_page_config(page_title="SUPS HJEM V6.3", layout="wide")

if 'bakul' not in st.session_state:
    st.session_state.bakul = []
if 'pilihan_batch' not in st.session_state:
    st.session_state.pilihan_batch = "Mac - Batch 1"
if 'input_nama' not in st.session_state:
    st.session_state.input_nama = ""
if 'input_ic' not in st.session_state:
    st.session_state.input_ic = ""

URL_API = "https://script.google.com/macros/s/AKfycbyeZXuPoyqsORGh_-kPC8lVTiFe41qZvQ4V8gBQU_BXnmP30zufcjSDxN6HnqyzQRRu/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- 2. MASTER LIST UBAT (Kekalkan yang asal) ---
MASTER_UBAT = sorted([
    "Abacavir 300mg Tablet", "Abacavir Sulphate 600mg + Lamivudine 300mg Tablet", "Acarbose 50 mg Tablet", 
    "Acetazolamide 250 mg Tablet", "Acetylsalicylic Acid 100 mg, Glycine 45 mg Tablet", "Acetylsalicylic Acid 150 mg Dispersible Tablet", 
    "Acetylsalicylic Acid 300 mg Soluble Tablet", "Acitretin 25mg Capsule", "Acriflavine 0.1% Lotion", 
    "Acyclovir 5% Cream", "Acyclovir 200 mg Tablet", "Acyclovir 800 mg Tablet", "Adadapalene 0.1% Gel", 
    "Agomelatine 25mg Tablet", "Albendazole 200 mg Tablet", "Albendazole 200 mg/5 ml Suspension", "Alcohol 70% Solution", 
    "Amlodipine 5 mg Tablet", "Amlodipine 10 mg Tablet", "Atorvastatin 20 mg Tablet", "Atorvastatin 40 mg Tablet",
    "Bisoprolol Fumarate 2.5 mg Tablet", "Bisoprolol Fumarate 5 mg Tablet", "Metformin HCl 500 mg Tablet",
    "Paracetamol 500 mg Tablet", "Perindopril 4 mg Tablet", "Simvastatin 10 mg Tablet", "Vitamin B Complex Tablet"
    # ... (Tambah ubat lain jika perlu, saya ringkaskan untuk ruang)
])

# --- 3. FUNGSI PEMBERSIHAN TARIKH (PENTING) ---
def parse_date(val):
    val = str(val).strip().split('T')[0] # Buang timestamp jika ada
    if not val or val in ["-", "None", "nan", ""]: return None
    
    # Cuba pelbagai format tarikh yang mungkin masuk
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(val, fmt).date()
        except ValueError:
            continue
    return None

def load_data():
    try:
        df = pd.read_csv(f"{URL_SHEET_CSV}&cache={datetime.now().timestamp()}")
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

def hitung_durasi_v2(t_ubat, t_klinik):
    d1 = parse_date(t_ubat)
    d2 = parse_date(t_klinik)
    if d1 and d2:
        diff = (d2 - d1).days
        return f"{diff} HARI"
    return "TIADA DATA"

def convert_to_matrix_final(df_f):
    if df_f.empty: return pd.DataFrame()
    matrix_data, info_u, info_d, info_dur, calc_data = [], {}, {}, {}, []
    
    for _, row in df_f.iterrows():
        p = str(row['NAMA']).strip().upper()
        raw_u = row.get('TCA_UBAT', '-')
        raw_d = row.get('TCA_CLINIC', '-')
        
        # Simpan info untuk header
        dt_u = parse_date(raw_u)
        dt_d = parse_date(raw_d)
        
        info_u[p] = dt_u.strftime("%d/%m/%Y") if dt_u else "-"
        info_d[p] = dt_d.strftime("%d/%m/%Y") if dt_d else "-"
        info_dur[p] = hitung_durasi_v2(raw_u, raw_d)
        
        # Proses list ubat
        u_list = str(row['UBAT_LIST']).split(' | ')
        q_list = str(row['KUANTITI']).split(' | ')
        for u, q in zip(u_list, q_list):
            u_up, q_str = u.strip().upper(), q.strip()
            matrix_data.append({'UBAT': u_up, 'PESAKIT': p, 'QTY': q_str})
            # Cari nombor sahaja untuk TOTAL
            nums = re.findall(r'\d+', q_str)
            if nums:
                calc_data.append({'UBAT': u_up, 'VAL': int(nums[0])})
    
    if not matrix_data: return pd.DataFrame()
    
    df_m = pd.DataFrame(matrix_data)
    matrix = df_m.pivot_table(index='UBAT', columns='PESAKIT', values='QTY', aggfunc='first').fillna("")
    
    if calc_data:
        totals = pd.DataFrame(calc_data).groupby('UBAT')['VAL'].sum().astype(int)
        matrix.insert(0, "📊 TOTAL", totals)

    header = pd.DataFrame([info_u, info_d, info_dur], index=["📅 TCA AMBIL", "👨‍⚕️ TCA DR", "⏳ DURASI"])
    header.insert(0, "📊 TOTAL", "")
    return pd.concat([header, matrix], sort=False).fillna("")

def to_excel_colored(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=True, sheet_name='Summary')
    workbook  = writer.book
    worksheet = writer.sheets['Summary']
    
    # Formats
    fmt_header = workbook.add_format({'bg_color': '#4F81BD', 'font_color': 'white', 'bold': True, 'border': 1, 'align': 'center'})
    fmt_durasi = workbook.add_format({'bg_color': '#FFEB9C', 'bold': True, 'border': 1, 'align': 'center'}) # Warna kuning untuk Durasi
    fmt_total  = workbook.add_format({'bg_color': '#D9D9D9', 'bold': True, 'border': 1, 'align': 'center'})
    
    # Apply styling
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num + 1, value, fmt_header)
    
    for row_num in range(len(df)):
        idx_name = df.index[row_num]
        if idx_name == "⏳ DURASI":
            worksheet.set_row(row_num + 1, None, fmt_durasi)
        
    worksheet.set_column(0, 0, 45)
    worksheet.set_column(1, len(df.columns), 18)
    writer.close()
    return output.getvalue()

# --- 4. UI ---
menu = st.sidebar.radio("NAVIGASI", ["📝 INPUT", "📊 SUMMARY"])
SENARAI_BATCH = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        nama_input = c1.text_input("Nama:", value=st.session_state.input_nama).upper().strip()
        st.session_state.input_nama = nama_input
        ic_input = c2.text_input("IC:", value=st.session_state.input_ic).strip()
        st.session_state.input_ic = ic_input
        batch = c3.selectbox("Batch:", SENARAI_BATCH, index=SENARAI_BATCH.index(st.session_state.pilihan_batch))
        st.session_state.pilihan_batch = batch
        
        c4, c5 = st.columns(2)
        t_u = c4.date_input("TCA Ambil Ubat (Hari Ini):", value=date.today())
        t_d = c5.date_input("TCA Klinik (Dr) [Opsional]:", value=None)

    with st.form("ubat_form"):
        u1, u2 = st.columns([3, 1])
        p_u = u1.selectbox("Pilih Ubat:", ["-- PILIH --"] + MASTER_UBAT)
        p_q = u2.text_input("Qty:")
        if st.form_submit_button("➕ Tambah Ke Bakul"):
            if p_u != "-- PILIH --" and p_q:
                st.session_state.bakul.append({"u": p_u, "q": p_q})
                st.rerun()

    if st.session_state.bakul:
        st.write("### 🛒 Bakul Sementara")
        for i, item in enumerate(st.session_state.bakul):
            st.text(f"{item['u']} - {item['q']}")
        
        if st.button("💾 SIMPAN DATA", type="primary", use_container_width=True):
            payload = {
                "Nama": nama_input, "IC": ic_input, "TCA_Ubat": str(t_u), 
                "TCA_Clinic": str(t_d) if t_d else "-", "Batch": batch,
                "Ubat_List": " | ".join([x['u'] for x in st.session_state.bakul]),
                "Kuantiti": " | ".join([x['q'] for x in st.session_state.bakul])
            }
            requests.post(URL_API, json=payload)
            st.session_state.bakul = []; st.session_state.input_nama = ""; st.session_state.input_ic = ""
            st.success("Data disimpan!"); time.sleep(1); st.rerun()

elif menu == "📊 SUMMARY":
    st.header("Checklist & Durasi Bekalan")
    df = load_data()
    if not df.empty:
        b_sel = st.selectbox("Pilih Batch:", SENARAI_BATCH, index=SENARAI_BATCH.index(st.session_state.pilihan_batch))
        df_f = df[df['BATCH'] == b_sel]
        if not df_f.empty:
            res = convert_to_matrix_final(df_f)
            st.dataframe(res, use_container_width=True, height=600)
            st.download_button("📥 Download Excel", to_excel_colored(res), f"{b_sel}.xlsx")
        else: st.info("Tiada data.")

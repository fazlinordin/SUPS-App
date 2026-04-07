import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io
import time

# --- 1. SETTING AWAL ---
st.set_page_config(page_title="SUPS HJEM V6.4", layout="wide")

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

# --- 3. FUNGSI ---
def load_data():
    try:
        r = requests.get(f"{URL_SHEET_CSV}&t={time.time()}")
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

# --- 4. UI INPUT ---
menu = st.sidebar.radio("NAVIGASI", ["📝 INPUT", "📊 SUMMARY"])
BATCH_OPTIONS = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    
    # Guna container untuk nampak kemas
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        nama = c1.text_input("Nama:").upper()
        ic = c2.text_input("IC:")
        batch = c3.selectbox("Batch:", BATCH_OPTIONS)
        
        c4, c5 = st.columns(2)
        t_u = c4.date_input("TCA Ambil Ubat (Hari Ini):", value=date.today())
        t_d = c5.date_input("TCA Klinik (Dr) [Opsional]:", value=None)
        
        # --- LOGIK COUNTDOWN (KOTAK HIJAU) ---
        if t_d:
            baki_hari = (t_d - t_u).days
            if baki_hari > 0:
                st.success(f"🎯 **Sila bekalkan ubat untuk: {baki_hari} Hari**")
            elif baki_hari == 0:
                st.warning("⚠️ Temujanji Klinik adalah pada hari yang sama.")
            else:
                st.error("⚠️ Tarikh Klinik mestilah selepas tarikh ambil ubat.")

    # Form untuk Ubat
    with st.form("input_form", clear_on_submit=True):
        st.subheader("Pilih Ubat")
        u1, u2 = st.columns([3, 1])
        p_u = u1.selectbox("Pilih Ubat:", ["-- PILIH --"] + MASTER_UBAT)
        p_q = u2.text_input("Qty:")
        tambah = st.form_submit_button("➕ Tambah Ke Bakul")
        
        if tambah:
            if p_u != "-- PILIH --" and p_q:
                st.session_state.bakul.append({"ubat": p_u, "qty": p_q})
                st.rerun()

    # Paparan Bakul
    if st.session_state.bakul:
        st.divider()
        for i, item in enumerate(st.session_state.bakul):
            col_a, col_b, col_c = st.columns([3, 1, 0.5])
            col_a.write(f"✅ {item['ubat']}")
            col_b.write(item['qty'])
            if col_c.button("🗑️", key=f"del_{i}"):
                st.session_state.bakul.pop(i)
                st.rerun()
        
        if st.button("💾 SIMPAN SEMUA DATA PESAKIT", type="primary", use_container_width=True):
            if nama and ic:
                payload = {
                    "Nama": nama, "IC": f"'{ic}", "TCA_Ubat": str(t_u), 
                    "TCA_Clinic": str(t_d) if t_d else "-", "Batch": batch,
                    "Ubat_List": " | ".join([x['ubat'] for x in st.session_state.bakul]),
                    "Kuantiti": " | ".join([x['qty'] for x in st.session_state.bakul])
                }
                requests.post(URL_API, json=payload)
                st.session_state.bakul = []
                st.success("Data Berjaya Disimpan!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Sila isi Nama dan IC sebelum simpan.")

# --- 5. UI SUMMARY ---
elif menu == "📊 SUMMARY":
    st.header("Checklist & Durasi Bekalan")
    df = load_data()
    if not df.empty:
        pilih_batch = st.selectbox("Pilih Batch:", BATCH_OPTIONS)
        df_f = df[df['BATCH'] == pilih_batch].copy()
        if not df_f.empty:
            labels = df_f['NAMA'].unique()
            matrix = {}
            
            # Row Info
            matrix["🆔 NO. IC"] = {l: str(df_f[df_f['NAMA']==l]['IC'].iloc[0]).replace("'","") for l in labels}
            matrix["📅 TCA AMBIL"] = {l: df_f[df_f['NAMA']==l]['TCA_UBAT'].iloc[0] for l in labels}
            matrix["👨‍⚕️ TCA DR"] = {l: df_f[df_f['NAMA']==l].get('TCA_CLINIC', pd.Series(['-'])).iloc[0] for l in labels}
            
            def get_dur(n):
                try:
                    d1 = pd.to_datetime(df_f[df_f['NAMA']==n]['TCA_UBAT'].iloc[0]).date()
                    # Cuba cari kolum TCA_CLINIC atau TCA_CLINIC_DR
                    col_target = 'TCA_CLINIC' if 'TCA_CLINIC' in df_f.columns else 'TCA_CLINIC'
                    d2_val = df_f[df_f['NAMA']==n][col_target].iloc[0]
                    if d2_val == "-": return "-"
                    d2 = pd.to_datetime(d2_val).date()
                    return f"{(d2 - d1).days} HARI"
                except: return "-"
            
            matrix["⏳ DURASI"] = {l: get_dur(l) for l in labels}
            
            # Row Ubat
            u_batch = []
            for u_s in df_f['UBAT_LIST']: u_batch.extend(str(u_s).split(' | '))
            for ub in sorted(list(set(u_batch))):
                matrix[ub] = {}
                rt = 0
                for l in labels:
                    p = df_f[df_f['NAMA'] == l].iloc[0]
                    un, uq = str(p['UBAT_LIST']).split(' | '), str(p['KUANTITI']).split(' | ')
                    if ub in un:
                        val = uq[un.index(ub)]
                        matrix[ub][l] = val
                        try: rt += int(''.join(filter(str.isdigit, str(val))))
                        except: pass
                    else: matrix[ub][l] = ""
                matrix[ub]["📊 TOTAL"] = rt if rt > 0 else ""

            res_df = pd.DataFrame(matrix).T
            cols = ["📊 TOTAL"] + list(labels)
            res_df = res_df[cols]

            # Warna Zebra
            def zebra(x):
                c = 'background-color: #DDEBF7'
                df1 = pd.DataFrame('', index=x.index, columns=x.columns)
                df1.iloc[::2, :] = c
                return df1

            st.dataframe(res_df.style.apply(zebra, axis=None), use_container_width=True)
            
            # Download Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                res_df.astype(str).to_excel(writer, sheet_name='Summary')
                wb, ws = writer.book, writer.sheets['Summary']
                f1 = wb.add_format({'bg_color': '#DDEBF7', 'border': 1, 'num_format': '@'})
                f2 = wb.add_format({'bg_color': '#FFFFFF', 'border': 1, 'num_format': '@'})
                for r in range(len(res_df) + 1):
                    fmt = f1 if r % 2 == 0 and r > 0 else f2
                    ws.set_row(r, None, fmt)
                ws.set_column(0, 0, 40)
            st.download_button("📥 MUAT TURUN EXCEL", output.getvalue(), f"Summary_{pilih_batch}.xlsx")

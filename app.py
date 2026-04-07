import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io
import time

# --- 1. SETTING AWAL ---
st.set_page_config(page_title="SUPS HJEM V7.0", layout="wide")

if 'bakul' not in st.session_state:
    st.session_state.bakul = []
if 'proses_simpan' not in st.session_state:
    st.session_state.proses_simpan = False
if 'batch_kekal' not in st.session_state:
    st.session_state.batch_kekal = "Mac - Batch 1"

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

def load_data():
    try:
        r = requests.get(f"{URL_SHEET_CSV}&t={time.time()}")
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

# --- 3. UI NAVIGASI ---
menu = st.sidebar.radio("NAVIGASI", ["📝 INPUT", "📊 SUMMARY"])
BATCH_OPTIONS = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        nama_input = c1.text_input("Nama:")
        nama = nama_input.upper().strip()
        ic = c2.text_input("IC:")
        idx_b = BATCH_OPTIONS.index(st.session_state.batch_kekal)
        batch = c3.selectbox("Batch:", BATCH_OPTIONS, index=idx_b)
        st.session_state.batch_kekal = batch
        
        c4, c5 = st.columns(2)
        t_u = c4.date_input("TCA Ambil Ubat (Hari Ini):", value=date.today())
        t_d = c5.date_input("TCA Klinik (Dr) [Opsional]:", value=None)
        if t_d:
            baki = (t_d - t_u).days
            if baki > 0: st.success(f"🎯 **Sila bekalkan ubat untuk: {baki} Hari**")

    with st.form("ubat_form", clear_on_submit=True):
        u1, u2 = st.columns([3, 1])
        p_u = u1.selectbox("Pilih Ubat:", ["-- PILIH --"] + MASTER_UBAT)
        p_q = u2.text_input("Qty:")
        if st.form_submit_button("➕ Tambah Ke Bakul"):
            if p_u != "-- PILIH --" and p_q:
                st.session_state.bakul.append({"u": p_u, "q": p_q}); st.rerun()

    if st.session_state.bakul:
        st.divider()
        for i, item in enumerate(st.session_state.bakul):
            col_a, col_b, col_c = st.columns([3, 1, 0.5])
            col_a.write(f"✅ {item['u']}"); col_b.write(item['q'])
            if col_c.button("🗑️", key=f"del_{i}"):
                st.session_state.bakul.pop(i); st.rerun()
        
        if st.session_state.proses_simpan:
            st.button("⏳ SEDANG MENYIMPAN DATA...", disabled=True, use_container_width=True)
            payload = {"Nama": nama, "IC": f"'{ic}", "TCA_Ubat": str(t_u), "TCA_Clinic": str(t_d) if t_d else "-", "Batch": batch, "Ubat_List": " | ".join([x['u'] for x in st.session_state.bakul]), "Kuantiti": " | ".join([x['q'] for x in st.session_state.bakul])}
            try:
                requests.post(URL_API, json=payload, timeout=5)
                st.session_state.bakul = []
                st.session_state.proses_simpan = False
                st.success("Data Berjaya Disimpan!"); time.sleep(1); st.rerun()
            except:
                st.session_state.bakul = []
                st.session_state.proses_simpan = False
                st.success("Data Sedang Diproses!"); time.sleep(1); st.rerun()
        else:
            if st.button("💾 SIMPAN DATA KE CLOUD", type="primary", use_container_width=True):
                if nama and ic:
                    st.session_state.proses_simpan = True
                    st.rerun()
                else: st.warning("Isi Nama dan IC.")

elif menu == "📊 SUMMARY":
    st.header("Checklist & Durasi Bekalan")
    df = load_data()
    if not df.empty:
        idx_s = BATCH_OPTIONS.index(st.session_state.batch_kekal)
        p_batch = st.selectbox("Pilih Batch:", BATCH_OPTIONS, index=idx_s)
        st.session_state.batch_kekal = p_batch
        df_f = df[df['BATCH'] == p_batch].copy()
        if not df_f.empty:
            with st.expander("🗑️ PADAM REKOD PESAKIT"):
                list_pt = sorted(df_f['NAMA'].unique())
                p_padam = st.selectbox("Pilih Pesakit:", ["-- PILIH --"] + list_pt)
                if st.button("❗ PADAM SEKARANG"):
                    if p_padam != "-- PILIH --":
                        requests.post(URL_API, json={"action": "DELETE", "Nama": p_padam, "Batch": p_batch})
                        st.warning(f"Memadam {p_padam}..."); time.sleep(1); st.rerun()

            labels = df_f['NAMA'].unique()
            matrix = {}
            matrix["🆔 NO. IC"] = {l: str(df_f[df_f['NAMA']==l]['IC'].iloc[0]).replace("'","") for l in labels}
            matrix["📅 TCA AMBIL"] = {l: df_f[df_f['NAMA']==l]['TCA_UBAT'].iloc[0] for l in labels}
            matrix["👨‍⚕️ TCA DR"] = {l: df_f[df_f['NAMA']==l].get('TCA_CLINIC', pd.Series(['-'])).iloc[0] for l in labels}
            
            def get_dur(n):
                try:
                    d1 = pd.to_datetime(df_f[df_f['NAMA']==n]['TCA_UBAT'].iloc[0]).date()
                    d2_v = df_f[df_f['NAMA']==n].get('TCA_CLINIC', pd.Series(['-'])).iloc[0]
                    if d2_v == "-": return "-"
                    d2 = pd.to_datetime(d2_v).date()
                    return f"{(d2 - d1).days} HARI"
                except: return "-"
            matrix["⏳ DURASI"] = {l: get_dur(l) for l in labels}
            
            u_b = []
            for u_s in df_f['UBAT_LIST']: u_b.extend(str(u_s).split(' | '))
            for ub in sorted(list(set(u_b))):
                matrix[ub] = {}
                rt = 0
                for l in labels:
                    p = df_f[df_f['NAMA'] == l].iloc[0]
                    un, uq = str(p['UBAT_LIST']).split(' | '), str(p['KUANTITI']).split(' | ')
                    if ub in un:
                        val = uq[un.index(ub)]; matrix[ub][l] = val
                        try: rt += int(''.join(filter(str.isdigit, str(val))))
                        except: pass
                    else: matrix[ub][l] = ""
                matrix[ub]["📊 TOTAL"] = rt if rt > 0 else ""

            res_df = pd.DataFrame(matrix).T
            cols = ["📊 TOTAL"] + list(labels)
            res_df = res_df[cols]
            
            # FIX STYLING: Cara baru yang takkan error
            def apply_style(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                for i in range(len(df)):
                    if i % 2 == 0:
                        styles.iloc[i, :] = 'background-color: #DDEBF7'
                return styles

            st.dataframe(res_df.style.apply(apply_style, axis=None), use_container_width=True)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                res_df.astype(str).to_excel(writer, sheet_name='Summary')
            st.download_button("📥 MUAT TURUN EXCEL", output.getvalue(), f"Summary_{p_batch}.xlsx")

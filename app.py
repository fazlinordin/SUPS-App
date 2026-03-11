import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io
import time

# --- 1. SETTING ---
st.set_page_config(page_title="SUPS HJEM V8.0", layout="wide")

if 'bakul' not in st.session_state:
    st.session_state.bakul = []

URL_API = "https://script.google.com/macros/s/AKfycbyeZXuPoyqsORGh_-kPC8lVTiFe41qZvQ4V8gBQU_BXnmP30zufcjSDxN6HnqyzQRRu/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- 2. MASTER LIST --- (Guna senarai ubat Fazli)
MASTER_UBAT = sorted(["Amlodipine 5 mg Tablet", "Atorvastatin 40 mg Tablet", "Ezetimibe 10 mg Tablet", "Metformin HCl 500 mg Tablet", "Tiotropium 2.5mcg and Olodaterol 2.5mcg inhalation (Catridge only)"])

# --- 3. FUNGSI ---
def load_data():
    try:
        # Tambah timestamp supaya data sentiasa paling baru (tak sangkut cache)
        r = requests.get(f"{URL_SHEET_CSV}&refresh={int(time.time())}")
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

# --- 4. UI INPUT ---
menu = st.sidebar.radio("NAVIGASI", ["📝 INPUT", "📊 SUMMARY"])
BATCH_OPTIONS = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    
    # Reset Nama & IC menggunakan clear_on_submit
    with st.form("input_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        nama = c1.text_input("Nama:").upper()
        ic = c2.text_input("IC:")
        batch = c3.selectbox("Batch:", BATCH_OPTIONS)
        
        c4, c5 = st.columns(2)
        t_u = c4.date_input("TCA Ambil Ubat:", value=date.today())
        t_d = c5.date_input("TCA Klinik (Dr):", value=date.today()) # Set default ke harini supaya tak null
        
        submit_data = st.form_submit_button("💾 SIMPAN DATA & RESET", use_container_width=True)

    st.divider()
    
    # Bakul Ubat
    with st.container(border=True):
        u1, u2 = st.columns([3, 1])
        p_u = u1.selectbox("Pilih Ubat:", ["-- PILIH --"] + MASTER_UBAT)
        p_q = u2.text_input("Qty:")
        if st.button("➕ Tambah Ubat"):
            if p_u != "-- PILIH --" and p_q:
                st.session_state.bakul.append({"u": p_u, "q": p_q})
                st.rerun()

    if st.session_state.bakul:
        for i, itm in enumerate(st.session_state.bakul):
            col_u, col_q, col_del = st.columns([3, 1, 0.5])
            col_u.write(itm['u'])
            col_q.write(itm['q'])
            if col_del.button("🗑️", key=f"del_{i}"):
                st.session_state.bakul.pop(i)
                st.rerun()

    if submit_data:
        if not nama or not ic or not st.session_state.bakul:
            st.warning("Pastikan Nama, IC dan Ubat telah diisi!")
        else:
            payload = {
                "Nama": nama, "IC": ic, "TCA_Ubat": str(t_u), 
                "TCA_Clinic": str(t_d), "Batch": batch,
                "Ubat_List": " | ".join([x['u'] for x in st.session_state.bakul]),
                "Kuantiti": " | ".join([x['q'] for x in st.session_state.bakul])
            }
            requests.post(URL_API, json=payload)
            st.session_state.bakul = []
            st.success("Data Berjaya Disimpan! Sila ke tab SUMMARY.")
            time.sleep(1)
            st.rerun()

# --- 5. UI SUMMARY (LOGIK PALING SIMPLE & GERENTI KELUAR) ---
elif menu == "📊 SUMMARY":
    st.header("Checklist & Durasi")
    df = load_data()
    
    if not df.empty:
        pilih_batch = st.selectbox("Pilih Batch:", BATCH_OPTIONS)
        df_f = df[df['BATCH'] == pilih_batch].copy()
        
        if not df_f.empty:
            # TUKAR TARIKH (PENTING!)
            df_f['TCA_UBAT'] = pd.to_datetime(df_f['TCA_UBAT'], errors='coerce')
            df_f['TCA_CLINIC'] = pd.to_datetime(df_f['TCA_CLINIC'], errors='coerce')
            
            # KIRA DURASI TERUS DALAM DATAFRAME
            def buat_durasi(row):
                if pd.notnull(row['TCA_UBAT']) and pd.notnull(row['TCA_CLINIC']):
                    diff = (row['TCA_CLINIC'] - row['TCA_UBAT']).days
                    return f"{diff} HARI"
                return "-"

            df_f['DURASI'] = df_f.apply(buat_durasi, axis=1)

            # BINA MATRIX UNTUK PAPARAN
            names = df_f['NAMA'].unique()
            final_rows = []
            
            # Baris 1: TCA Ambil
            r1 = {"ITEM": "📅 TCA AMBIL"}
            # Baris 2: TCA Klinik
            r2 = {"ITEM": "👨‍⚕️ TCA DR"}
            # Baris 3: DURASI
            r3 = {"ITEM": "⏳ DURASI"}
            
            for n in names:
                data = df_f[df_f['NAMA'] == n].iloc[0]
                r1[n] = data['TCA_UBAT'].strftime('%d/%m/%y') if pd.notnull(data['TCA_UBAT']) else "-"
                r2[n] = data['TCA_CLINIC'].strftime('%d/%m/%y') if pd.notnull(data['TCA_CLINIC']) else "-"
                r3[n] = data['DURASI']
            
            final_rows.extend([r1, r2, r3])
            
            # Baris Ubat
            all_u = []
            for u_str in df_f['UBAT_LIST']:
                all_u.extend(str(u_str).split(' | '))
            
            for ub in sorted(list(set(all_u))):
                r_u = {"ITEM": ub}
                for n in names:
                    data = df_f[df_f['NAMA'] == n].iloc[0]
                    u_list = str(data['UBAT_LIST']).split(' | ')
                    q_list = str(data['KUANTITI']).split(' | ')
                    r_u[n] = q_list[u_list.index(ub)] if ub in u_list else ""
                final_rows.append(r_u)

            st.dataframe(pd.DataFrame(final_rows).set_index("ITEM"), use_container_width=True)
        else:
            st.info("Tiada pesakit dalam batch ini.")

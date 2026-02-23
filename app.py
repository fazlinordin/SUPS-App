import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date

st.set_page_config(page_title="SUPS HJEM - Smart Checklist", layout="wide")

# --- KONFIGURASI ---
URL_API = "https://script.google.com/macros/s/AKfycbzir4NpkjGqR7XuBTFfxg8tziu7fBSlrHKgUICM_KSfC0MnRScdXh_8oi7uTGfHe01mkg/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- SENARAI 131 UBAT DARI EXCEL FAZLI ---
MASTER_UBAT = [
    "acetazolamide 250mg tab", "acetylsalicyclic acid 150 mg dispersible tab", "Acitretin 25mg capsule", "ACTRAPID",
    "acyclovir 800mg tab", "adapalene 0.1% gel", "allopurinol 100mg tablet", "amlodipine 10mg + valsartan 160",
    "amorolfine 5% nail lacquer", "Apixaban 2.5mg film coated tablet", "apixaban 5mg film coated tablet", "aqueous cream",
    "aripiprazole 10mg", "artificial tears/eye lubricant (single use)", "ascorbic acid 100mg", "atorvastatin 20 mg",
    "atorvastatin 40mg", "baclofen 10 mg", "beclomethasone dipr 100mcg", "benzoyl peroxide 5% gel", "betametasone 17 valerate",
    "brimonidine tartrate 0.15%", "budesonide 160mcg", "calcitriol 0.25 mcg", "calcium carbonate 500mg", "carbamazepine 400mg CR",
    "celexocib 200mg", "cetrizine hcl 10mg", "clopidogrel 75mg tab", "coal tar (LPC) ointment", "dabigatran 150mg",
    "dapagliflozin 10mg", "dexamethasone eye drops", "diltiazem 30mg", "empagliflozin 25mg tab", "ezetimibe 10 mg",
    "felodipine 10mg ER", "fenofibrate 145mg", "finasteride 5 mg", "fluticasone 125mcg", "gabapentin 300mg",
    "gliclazide 80 mg", "gliclazide mr 60mg", "IBERET FOLIC", "insugen 30/70", "INSULATARD", "Insulin glargine lantus",
    "latanaprost 0.005%", "levetiracetam 500mg", "loratadine 10mg", "metformin xr 750 mg", "methotrexate 2.5mg",
    "mirtazapine 15 mg", "mirtazapine 30 mg", "MIXTARD", "montelukast 10 mg", "olanzapine 10mg", "omeprazole 20mg",
    "pantoprazole 40mg", "quetiapine 100mg IR", "quetiapine 200mg ER", "Simvastatin 40 mg", "spironolactone 25mg",
    "tamsulosin HCL 400mcg", "theophyline sr 250mg", "Topiramate 100mg", "valsartan 160mg", "vildagliptin 50 mg",
    "vitamin b1 b6 b12", "Warfarin 2mg", "Warfarin 5mg", "White Soft Paraffin"
] # Nota: Sila tambah lagi jika perlu mengikut list Excel asal

def load_data():
    try:
        df = pd.read_csv(f"{URL_SHEET_CSV}&cache={datetime.now().timestamp()}")
        df.columns = df.columns.str.strip().str.upper()
        return df
    except:
        return pd.DataFrame()

def hitung_countdown(t_clinic_str):
    if pd.isna(t_clinic_str) or str(t_clinic_str).strip() == "" or str(t_clinic_str).lower() in ["none", "nan"]:
        return "N/A"
    try:
        t_clinic = pd.to_datetime(t_clinic_str).date()
        hari_ini = date.today()
        baki = (t_clinic - hari_ini).days
        if baki > 0: return f"⏳ {baki} Hari Lagi"
        elif baki == 0: return "🔴 HARI INI"
        else: return f"✅ Selesai ({abs(baki)} hari lepas)"
    except: return "Format Salah"

# --- UI ---
st.sidebar.title("🏥 SUPS HJEM V2.7")
menu = st.sidebar.radio("NAVIGASI", ["📝 DAFTAR & TAMBAH UBAT", "📊 SUMMARY & COUNTDOWN"])

if menu == "📝 DAFTAR & TAMBAH UBAT":
    st.header("Pendaftaran Pesakit & Pesanan Ubat")
    
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("NAMA PENUH:").upper()
            ic = st.text_input("NO. IC:")
            batch = st.selectbox("BATCH:", [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]])
        with col2:
            t_ubat = st.date_input("TARIKH AMBIL UBAT:", value=date.today())
            t_clinic = st.date_input("TARIKH TCA KLINIK:", value=None)

        st.write("---")
        st.subheader("💊 Pemilihan Ubat (Banyak)")
        # Fungsi multiselect bertindak sebagai 'Tambah Ubat'
        pilihan = st.multiselect("Pilih Semua Ubat Pesakit:", sorted(MASTER_UBAT))
        kuantiti_detail = st.text_area("Masukkan Kuantiti (Contoh: Amlodipine 30 biji, Metformin 60 biji):")
        
        submit = st.form_submit_button("💾 SIMPAN SEMUA DATA KE GOOGLE SHEETS")

    if submit:
        if nama and ic and pilihan:
            data_json = {
                "Nama": nama, "IC": ic, "TCA_Ubat": str(t_ubat), 
                "TCA_Clinic": str(t_clinic) if t_clinic else "", 
                "Ubat_List": " | ".join(pilihan), 
                "Batch": batch, "Kuantiti": kuantiti_detail.upper()
            }
            try:
                res = requests.post(URL_API, json=data_json)
                if res.status_code == 200:
                    st.success(f"Rekod {nama} berjaya disimpan!")
                    st.balloons()
                else: st.error("Ralat simpanan API.")
            except Exception as e: st.error(f"Error: {e}")
        else: st.warning("⚠️ Sila pastikan Nama, IC dan Ubat telah dipilih.")

elif menu == "📊 SUMMARY & COUNTDOWN":
    st.header("📋 Checklist & Countdown Klinik")
    
    if st.button("🔄 Segarkan Data (Refresh)"):
        st.cache_data.clear()
        st.rerun()

    df = load_data()
    if not df.empty:
        batch_sel = st.selectbox("Tapis mengikut Batch:", [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]])
        
        df_view = df[df['BATCH'] == batch_sel].copy()
        
        if not df_view.empty:
            # Tambah Countdown secara automatik
            df_view['COUNTDOWN'] = df_view['TCA_CLINIC'].apply(hitung_countdown)
            
            # SUSUNAN: Ubat & Kuantiti di kiri, Countdown, baru maklumat pesakit
            df_final = df_view[["UBAT_LIST", "KUANTITI", "COUNTDOWN", "NAMA", "IC", "TCA_UBAT", "TCA_CLINIC"]]
            df_final.columns = ["SENARAI UBAT", "KUANTITI", "COUNTDOWN KLINIK", "NAMA PESAKIT", "NO. IC", "TCA UBAT", "TCA KLINIK"]
            
            st.dataframe(df_final, use_container_width=True, hide_index=True)
            
            # Summary Ringkas
            st.write(f"**Jumlah Pesakit Batch Ini:** {len(df_final)}")
        else:
            st.info("Tiada data untuk batch ini.")

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="SUPS by Fazli Ver.1", layout="wide")

# 1. Sambungan Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        return conn.read(worksheet="Sheet1", ttl=0)
    except:
        return pd.DataFrame(columns=["Nama", "IC", "TCA_Ubat", "TCA_Clinic", "Ubat_List", "Batch"])

df = load_data()

# FUNGSI BARU: Kira jarak hari antara TCA Ubat ke TCA Klinik
def kira_jarak_ubat_ke_klinik(t_ubat_str, t_clinic_str):
    # Jika salah satu tarikh tiada, jangan tunjuk apa-apa
    if not t_clinic_str or t_clinic_str == "" or t_clinic_str == "None":
        return ""
    if not t_ubat_str or t_ubat_str == "" or t_ubat_str == "None":
        return ""
        
    try:
        # Tukar string kepada format tarikh
        t_ubat = datetime.strptime(t_ubat_str, '%Y-%m-%d').date()
        t_clinic = datetime.strptime(t_clinic_str, '%Y-%m-%d').date()
        
        # Kira beza hari
        beza = (t_clinic - t_ubat).days
        
        if beza > 0:
            return f"{beza} hari"
        elif beza == 0:
            return "Hari yang sama"
        else:
            return f"Lepas {abs(beza)} hari"
    except:
        return ""

# --- Senarai Batch 2026 ---
SENARAI_BATCH = [
    "Mac - Batch 1 (1-15hb)", "Mac - Batch 2 (16-31hb)",
    "April - Batch 1", "April - Batch 2",
    "Mei - Batch 1", "Mei - Batch 2",
    "Jun - Batch 1", "Jun - Batch 2",
    "Julai - Batch 1", "Julai - Batch 2",
    "Ogos - Batch 1", "Ogos - Batch 2",
    "September - Batch 1", "September - Batch 2",
    "Oktober - Batch 1", "Oktober - Batch 2",
    "November - Batch 1", "November - Batch 2",
    "Disember - Batch 1", "Disember - Batch 2"
]

# --- Navigasi Sidebar ---
st.sidebar.title("SUPS by Fazli")
menu = st.sidebar.radio("Menu Utama", ["📝 Daftar Pesakit Baru", "📊 Summary & Download"])

# --- 1. DAFTAR PESAKIT BARU ---
if menu == "📝 Daftar Pesakit Baru":
    st.header("📋 Borang Input Data Pesakit")
    
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Penuh (Huruf Besar):").upper()
            ic = st.text_input("No. Kad Pengenalan (Tanpa -):")
            batch_pilihan = st.selectbox("Pilih Batch/Bulan:", SENARAI_BATCH)
            
        with col2:
            tca_u = st.date_input("TCA Ubat (Tarikh Ambil Ubat):")
            ada_clinic = st.checkbox("Ada Tarikh TCA Clinic?", value=False)
            tca_c = st.date_input("TCA Clinic:", value=None) if ada_clinic else ""
            
        st.write("---")
        st.subheader("💊 Senarai Ubat")
        ubat = st.text_area("Masukkan Nama Ubat & Kuantiti")
        
        submit = st.form_submit_button("💾 SIMPAN REKOD", use_container_width=True)

    if submit:
        if nama and ic and ubat:
            new_row = pd.DataFrame([{
                "Nama": nama,
                "IC": ic,
                "TCA_Ubat": str(tca_u),
                "TCA_Clinic": str(tca_c) if ada_clinic else "",
                "Ubat_List": ubat,
                "Batch": batch_pilihan
            }])
            
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success(f"Berjaya! Rekod {nama} disimpan.")
            st.balloons()
        else:
            st.warning("⚠️ Nama, IC dan Senarai Ubat wajib diisi.")

# --- 2. SUMMARY & DOWNLOAD ---
elif menu == "📊 Summary & Download":
    st.header("🔍 Semakan & Muat Turun Rekod")
    
    if df.empty:
        st.warning("Tiada rekod dijumpai.")
    else:
        batch_to_filter = st.selectbox("Pilih Batch untuk Lihat:", SENARAI_BATCH)
        df_filtered = df[df['Batch'] == batch_to_filter].copy()
        
        if df_filtered.empty:
            st.info(f"Tiada rekod untuk {batch_to_filter}.")
        else:
            # PENGIRAAN JARAK HARI (UBAT KE KLINIK)
            df_filtered['Duration_to_Clinic'] = df_filtered.apply(
                lambda x: kira_jarak_ubat_ke_klinik(x['TCA_Ubat'], x['TCA_Clinic']), axis=1
            )
            
            st.write(f"Menunjukkan **{len(df_filtered)}** rekod.")
            
            # Susunan kolum untuk paparan Summary
            cols = ["Nama", "IC", "TCA_Ubat", "TCA_Clinic", "Duration_to_Clinic", "Ubat_List"]
            st.dataframe(df_filtered[cols], use_container_width=True)
            
            csv_data = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Muat Turun Data {batch_to_filter}",
                data=csv_data,
                file_name=f'SUPS_{batch_to_filter}.csv',
                mime='text/csv',
                use_container_width=True
            )

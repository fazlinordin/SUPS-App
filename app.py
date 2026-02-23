import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date

st.set_page_config(page_title="SUPS HJEM V3.0", layout="wide")

# (Guna URL API dan URL CSV yang sama)
URL_API = "https://script.google.com/macros/s/AKfycbzir4NpkjGqR7XuBTFfxg8tziu7fBSlrHKgUICM_KSfC0MnRScdXh_8oi7uTGfHe01mkg/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- FUNGSI DOWNLOAD FORMAT MELINTANG (EXCEL STYLE) ---
def convert_to_matrix(df_filtered):
    # Kita pecahkan data ubat_list dan kuantiti yang digabung tadi
    rows = []
    for _, row in df_filtered.iterrows():
        ubats = str(row['UBAT_LIST']).split(' | ')
        qtys = str(row['KUANTITI']).split(' | ')
        for u, q in zip(ubats, qtys):
            rows.append({
                'Nama Pesakit': row['NAMA'],
                'Ubat': u,
                'Kuantiti': q
            })
    
    new_df = pd.DataFrame(rows)
    # Pusingkan jadual (Pivot)
    matrix = new_df.pivot(index='Ubat', columns='Nama Pesakit', values='Kuantiti').fillna('')
    return matrix

# --- UI BAGIAN SUMMARY ---
# (Bahagian Daftar Pesakit kekal sama seperti Versi 2.9)

# ... (Kod Navigasi & Daftar) ...

elif menu == "📊 SUMMARY BATCH":
    st.header("📋 Ringkasan & Download Excel Style")
    df = load_data()
    
    if not df.empty:
        pilihan = st.selectbox("Pilih Batch:", [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]])
        df_batch = df[df['BATCH'] == pilihan].copy()
        
        if not df_batch.empty:
            st.write("### Preview Data (Format Menegak)")
            st.dataframe(df_batch, use_container_width=True)
            
            # --- MAGIC BUTTON DOWNLOAD MELINTANG ---
            st.write("---")
            st.subheader("📥 Muat Turun Format Excel (Melintang)")
            df_matrix = convert_to_matrix(df_batch)
            
            st.write("Preview Fail yang akan di-download:")
            st.dataframe(df_matrix) # Tunjuk rupa melintang sebelum download
            
            csv_matrix = df_matrix.to_csv().encode('utf-8')
            st.download_button(
                label="🚀 DOWNLOAD FORMAT EXCEL (CHECKLIST)",
                data=csv_matrix,
                file_name=f"Checklist_SPUB_{pilihan}.csv",
                mime="text/csv",
                use_container_width=True
            )

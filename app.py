import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime, date

st.set_page_config(page_title="SUPS HJEM V3.3", layout="wide")

# --- KONFIGURASI ---
URL_API = "https://script.google.com/macros/s/AKfycbzir4NpkjGqR7XuBTFfxg8tziu7fBSlrHKgUICM_KSfC0MnRScdXh_8oi7uTGfHe01mkg/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- SENARAI LENGKAP 131 UBAT DARI EXCEL FAZLI ---
MASTER_UBAT = sorted([
    "acetazolamide 250mg tab", "acetylsalicyclic acid 150 mg dispersible tab", "Acitretin 25mg capsule", "ACTRAPID",
    "acyclovir 800mg tab", "adapalene 0.1% gel", "allopurinol 100mg tablet", "amlodipine 10mg + valsartan 160",
    "amorolfine 5% nail lacquer", "Apixaban 2.5mg film coated tablet", "apixaban 5mg film coated tablet", "aqueous cream",
    "aripiprazole 10mg", "artificial tears/eye lubricant opth sol (single use)", "artificial tears/eye lubricant opthalmic solution",
    "ascorbic acid 100mg", "atorvastatin 20 mg", "atorvastatin 40mg", "baclofen 10 mg", 
    "beclomethasone dipr 100mcg, formoterol 6mcg inh.", "benzoyl peroxide 5% gel", "betametasone 17 valerate 1 in 4 cream (0.025%)",
    "betametasone 17 valerate 1 in 2 cream (0.05%)", "betametasone valearate 1:2 oinment", "betamethasone 17 valerate 0.1% ointment",
    "betamethasone 17-valerate 0.1% cream", "brimonidine tartrate 0.15% opth sol.", 
    "budesonide 160mcg and formeterol 4.5mcg turbuhaler 120 doses", "calcipotrio 50 mcg/g betametasone 0.5mg/g oint",
    "calcitriol 0.25 mcg", "calcium carbonate 500mg", "calcium lactate 300mg", "carbamazepine 400mg CR", "Carbamide (urea) 10% Cream",
    "celexocib 200mg", "cetrimide 2% lotion", "cetrizine hcl 10mg", "Clobetasol Propionate 0.05% Oint.", "clobetasone butyrate 0.05% cream",
    "clobetasone butyrate 0.05% oinmt", "clopidogrel 75mg tab", "coal tar (LPC) 3% ointment", "coal tar (lpc) 6% oinment",
    "coal tar 1 % salicyclic acid 2 % shampoo (sebitar)", "Coal Tar 12% salicylic acid 2% Sulphur 4% Oint.", "dabigatran etexilate 150mg cap",
    "dapagliflozin 10mg", "dexamethasone sodium phosphate 0.1% eye drops", "dexamethasone,neomycin,polymyxin B eyedrop (maxitrol)",
    "diltiazem 30mg", "dorzolamide hcl 2% opth. Sol.", "dutasteride 0.5mg + tamsulosin 0.4mg cap", "dydrogesterone 10 mg tab",
    "empagliflozin 25mg tab", "emulsifying ointment BP (emulsificant oint)", "ezetimibe 10 mg tab", "felodipine 10mg ER", "fenofibrate 145mg",
    "ferric ammonium citrate 400mg/5ml (FAC)", "finasteride 5 mg", "flupenthixol decoante depot 20mg/ml inj",
    "fluticasone propionate 125mcg/dose evohaler", "fluvoxamine 50mg", "fusidic acid 1% eye drops", "gabapentin 300mg",
    "gemfibrozil 300mg", "gliclazide 80 mg", "gliclazide mr 60mg", "hypromellose 0.3% eye drop (preser. Fre)", "IBERET FOLIC",
    "insugen 30/70", "insugen N", "INSUGEN R", "INSULATARD", "Insulin glargine lantus", "INSUPEN",
    "Ipratropium br 20mcg fenoterol 50mcg/dose BERODUAL", "ivabradine 5 mg", "ketoprofen 2.5% gel", "lactulose 3.35g/5 ml liquid",
    "lamotrigine 100mg tab", "Lamotrigine 50mg tab", "latanaprost 0.005% eye drop", "levetiracetam 500mg", "loratadine 10mg",
    "lorazepam 1mg", "metformin xr 750 mg", "methotrexate 2.5mg", "mirabegron 50 mg PROLONGED RELEASE tab", "mirtazapine 15 mg orodispersible tab",
    "mirtazapine 30 mg orodispersible tab", "mirtazapine 15mg orodispersible tab", "mirtazapine 30mg orodispersible tab", "MIXTARD", 
    "mometasone furoate 0.1% cream", "montelukast 10 mg", "moxifloxacin 0.5% ophthalmic solution",
    "nepafenac 0.1% w/v eye suspension (5ml)", "olanzapine 10mg tab", "omeprazole 20mg capsule", "paliperidone 75mg prolonged release injection",
    "pantoprazole 40mg", "pine tar 1% coal tar 1% salicyclic acid 2% shampoo sebitar", "quetiapine fumarate 100mg IR tab",
    "quetiapine fumarate 200mg ER", "quetiapine fumarate 50mg extended release tab", "salicyclic acid 5% oinment",
    "salicyclic acid, sulphur and liquid coal tar ointment", "salicylic acid 10% ointment", "salmeterol 25mcg , fluticasone propionate 125mcg evohaler",
    "salmeterol 50mcg +fluticasone 500mcg accuhaler", "Simvastatin 40 mg", "sodium bicarbonate, citric acid, sod citrate, tartaric acid 4g/sachet",
    "sodium valproate 200mg/5ml syrup (EPILIM)", "spironolactone 25mg", "sulphamethoxazole 400mg trimethoprim 80mg tab", 
    "sunscreen SPF 50 lotion/cream", "tamsulosin HCL 400mcg ER", "theophyline sr 250mg", "timolol maleate 0.5% eye drop (pres. Free) 10 ml", 
    "tiotropium 2.5mcg & olodaterol 2.5mcg/actuation,inh(Ctrdge only)", "tiotropium 2.5mcg / puff inhalation (catrigde only)", 
    "Topiramate 100mg", "tramadol 50mg", "tretinoin 0.05% cream", "ursodeoxycholic acid 250mg capsule", "valsartan 160mg", 
    "valsartan 80mg", "verapamil 40mg tab", "vildagliptin 50 mg tab", "vitamin b1 b6 b12", "warfarin 1mg", "Warfarin 2mg", 
    "Warfarin 5mg", "white petroleum anhydrous liq linolin, mineral oil eye oint", "White Soft Paraffin BP (White Petroleum Jelly BP)"
])

def load_data():
    try:
        df = pd.read_csv(f"{URL_SHEET_CSV}&cache={datetime.now().timestamp()}")
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

def ekstrak_angka(teks):
    try:
        angka = re.findall(r'\d+', str(teks))
        return int(angka[0]) if angka else 0
    except: return 0

def convert_to_matrix_with_total(df_filtered):
    rows = []
    for _, row in df_filtered.iterrows():
        ubats = str(row['UBAT_LIST']).split(' | ')
        qtys = str(row['KUANTITI']).split(' | ')
        for u, q in zip(ubats, qtys):
            rows.append({
                'NAMA PESAKIT': row['NAMA'],
                'UBAT': u.strip(),
                'KUANTITI': q.strip(),
                'NILAI': ekstrak_angka(q)
            })
    if not rows: return pd.DataFrame()
    new_df = pd.DataFrame(rows)
    matrix = new_df.pivot_table(index='UBAT', columns='NAMA PESAKIT', values='KUANTITI', aggfunc='first').fillna('')
    total_series = new_df.groupby('UBAT')['NILAI'].sum()
    matrix.insert(0, 'TOTAL (BIJI)', total_series)
    return matrix

if 'bakul_ubat' not in st.session_state:
    st.session_state.bakul_ubat = []

# --- UI ---
st.sidebar.title("🏥 SUPS HJEM V3.3")
menu = st.sidebar.radio("NAVIGASI", ["📝 DAFTAR & TAMBAH UBAT", "📊 SUMMARY BATCH"])

if menu == "📝 DAFTAR & TAMBAH UBAT":
    st.header("Pendaftaran Pesakit & Penyediaan Ubat")
    with st.container(border=True):
        st.subheader("👤 Maklumat Pesakit")
        c1, c2, c3 = st.columns(3)
        nama = c1.text_input("Nama Penuh:").upper()
        ic = c2.text_input("No. IC:")
        batch = c3.selectbox("Pilih Batch:", [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]])
        c4, c5 = st.columns(2)
        t_ubat = c4.date_input("Tarikh Ambil Ubat:", value=date.today())
        t_clinic = c5.date_input("Tarikh TCA Klinik:", value=None)

    with st.container(border=True):
        st.subheader("💊 Tambah Ubat (Satu-Persatu)")
        u1, u2, u3 = st.columns([2, 1, 1])
        pilih_u = u1.selectbox("Pilih Nama Ubat:", ["-- Pilih --"] + MASTER_UBAT)
        isi_q = u2.text_input("Kuantiti (cth: 30 BIJI):")
        if u3.button("➕ Tambah", use_container_width=True):
            if pilih_u != "-- Pilih --" and isi_q:
                st.session_state.bakul_ubat.append({"ubat": pilih_u, "qty": isi_q})
                st.rerun()

    if st.session_state.bakul_ubat:
        st.write("### 🛒 Senarai Sementara")
        st.table(pd.DataFrame(st.session_state.bakul_ubat))
        col_clear, col_save = st.columns([1, 4])
        if col_clear.button("🗑️ Kosongkan"):
            st.session_state.bakul_ubat = []
            st.rerun()
        if col_save.button("💾 SIMPAN SEMUA DATA", type="primary", use_container_width=True):
            if nama and ic:
                data_json = {
                    "Nama": nama, "IC": ic, "TCA_Ubat": str(t_ubat), "TCA_Clinic": str(t_clinic) if t_clinic else "", 
                    "Ubat_List": " | ".join([x['ubat'] for x in st.session_state.bakul_ubat]), 
                    "Batch": batch, "Kuantiti": " | ".join([x['qty'] for x in st.session_state.bakul_ubat])
                }
                res = requests.post(URL_API, json=data_json)
                if res.status_code == 200:
                    st.success(f"Berjaya Simpan!"); st.session_state.bakul_ubat = []; st.balloons()
            else: st.error("Isi Nama & IC!")

elif menu == "📊 SUMMARY BATCH":
    st.header("📋 Ringkasan & Total Penggunaan")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear(); st.rerun()
    df = load_data()
    if not df.empty:
        pilihan = st.selectbox("Pilih Batch:", [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]])
        df_batch = df[df['BATCH'] == pilihan].copy()
        if not df_batch.empty:
            df_matrix = convert_to_matrix_with_total(df_batch)
            st.dataframe(df_matrix, use_container_width=True)
            st.download_button("📥 Download Excel Style", df_matrix.to_csv().encode('utf-8'), f"{pilihan}.csv", "text/csv", use_container_width=True)
        else: st.info("Tiada data.")

import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# Set konfigurasi halaman
st.set_page_config(page_title="SUPS by Fazli Ver.1", layout="wide")

# --- SAMBUNGAN GOOGLE SHEETS ---
# Pastikan anda masukkan URL Google Sheet anda di dalam .streamlit/secrets.toml
conn = st.connection("gsheets", type=GSheetsConnection)

# Fungsi untuk ambil data sedia ada (untuk autofill)
def get_existing_data():
    try:
        return conn.read(worksheet="Sheet1", ttl=5)
    except:
        return pd.DataFrame(columns=["Nama", "IC", "TCA_Ubat", "TCA_Clinic", "Ubat_List"])

# --- DATABASE MASTER LIST UBAT (Sama seperti sebelum ini) ---
MASTER_UBAT = [
    "acetazolamide 250mg tab", "acetylsalicyclic acid 150 mg dispersible tab", "Acitretin 25mg capsule", "ACTRAPID",
    "acyclovir 800mg tab", "adapalene 0.1% gel", "allopurinol 100mg tablet", "amlodipine 10mg + valsartan 160",
    "amorolfine 5% nail lacquer", "Apixaban 2.5mg film coated tablet", "apixaban 5mg film coated tablet", "aqueous cream",
    "aripiprazole 10mg", "artificial tears/eye lubricant opth sol (single use)", "artificial tears/eye lubricant opthalmic solution",
    "ascorbic acid 100mg", "atorvastatin 20 mg", "atorvastatin 40mg", "baclofen 10 mg", "beclomethasone dipr 100mcg, formoterol 6mcg inh.",
    "benzoyl peroxide 5% gel", "betametasone 17 valerate 1 in 2 cream (0.05%)", "betametasone valearate 1:2 oinment",
    "betamethasone 17 valerate 0.1% ointment", "betamethasone 17-valerate 0.1% cream", "brimonidine tartrate 0.15% opth sol.",
    "budesonide 160mcg and formeterol 4.5mcg turbuhaler 120 doses", "calcipotrio 50 mcg/g betametasone 0.5mg/g oint",
    "calcitriol 0.25 mcg", "calcium carbonate 500mg", "calcium lactate 300mg", "carbamazepine 400mg CR",
    "Carbamide (urea) 10% Cream", "celexocib 200mg", "cetrimide 2% lotion", "cetrizine hcl10mg", "Clobetasol Propionate 0.05% Oint.",
    "clobetasone butyrate 0.05% cream", "clobetasone butyrate 0.05% oinmt", "clopidogrel 75mg tab", "coal tar (LPC) 3% ointment",
    "coal tar (lpc) 6% oinment", "coal tar 1 % salicyclic acid 2 % shampoo (sebitar)", "Coal Tar 12% salicylic acid 2% Sulphur 4% Oint.",
    "dabigatran etexilate 150mg cap", "dapagliflozin 10mg", "dexamethasone sodium phosphate 0.1% eye drops",
    "dexamethasone,neomycin,polymyxin B eyedrop (maxitrol)", "diltiazem 30mg", "dorzolamide hcl 2% opth. Sol.",
    "dutasteride 0.5mg + tamsulosin 0.4mg cap", "empagliflozin 25mg tab", "emulsifying ointment BP (emulsificant oint)",
    "ezetimibe 10 mg tab", "felodipine 10mg ER", "fenofibrate 145mg", "ferric ammonium citrate 400mg/5ml (FAC)", "finasteride 5 mg",
    "flupenthixol decoante depot 20mg/ml inj", "fluticasone propionate 125mcg/dose evohaler", "fluvoxamine 50mg",
    "fusidic acid 1% eye drops", "gabapentin 300mg", "gemfibrozil 300mg", "gliclazide 80 mg", "gliclazide mr 60mg",
    "hypromellose 0.3% eye drop (preser. Fre)", "IBERET FOLIC", "insugen 30/70", "insugen N", "INSUGEN R", "INSULATARD",
    "Insulin glargine lantus", "INSUPEN", "Ipratropium br 20mcg fenoterol 50mcg/dose BERODUAL", "ivabradine 5 mg",
    "ketoprofen 2.5% gel", "lactulose 3.35g/5 ml liquid", "lamotrigine 100mg tab", "Lamotrigine 50mg tab",
    "latanaprost 0.005% eye drop", "levetiracetam 500mg", "loratadine 10mg", "lorazepam 1mg", "metformin xr 750 mg",
    "methotrexate 2.5mg", "mirabegron 50 mg PROLONGED RELEASE tab", "mirtazapine 15 mg orodispersible tab",
    "mirtazapine 30 mg orodispersible tab", "MIXTARD", "mometasone furoate 0.1% cream", "montelukast 10 mg",
    "moxifloxacin 0.5% ophthalmic solution", "nepafenac 0.1% w/v eye suspension (5ml)", "olanzapine 10mg tab",
    "omeprazole 20mg capsule", "paliperidone 75mg prolonged release injection", "pantoprazole 40mg",
    "pine tar 1% coal tar 1% salicyclic acid 2% shampoo sebitar", "quetiapine fumarate 100mg IR tab",
    "quetiapine fumarate 200mg ER", "quetiapine fumarate 50mg extended release tab", "salicyclic acid 5% oinment",
    "salicyclic acid, sulphur and liquid coal tar ointment", "salicylic acid 10% ointment",
    "salmeterol 25mcg , fluticasone propionate 125mcg evolaher", "salmeterol 50mcg +fluticasone 500mcg accuhaler",
    "Simvastatin 40 mg", "sodium valproate 200mg/5ml syrup (EPILIM)", "spironolactone 25mg",
    "sulphamethoxazole 400mg trimethoprim 80mg tab", "sunscreen SPF 50 lotion/cream", "tamsulosin HCL 400mcg ER",
    "theophyline sr 250mg", "timolol maleate 0.5% eye drop (pres. Free) 10 ml",
    "tiotropium 2.5mcg & olodaterol 2.5mcg/actuation,inh(Ctrdge only)", "tiotropium 2.5mcg / puff inhalation (catrigde only)",
    "Topiramate 100mg", "tramadol 50mg", "tretinoin 0.05% cream", "ursodeoxycholic acid 250mg capsule",
    "valsartan 160mg", "valsartan 80mg", "verapamil 40mg tab", "vildagliptin 50 mg tab", "vitamin b1 b6 b12",
    "warfarin 1mg", "Warfarin 2mg", "Warfarin 5mg", "white petroleum anhydrous liq linolin, mineral oil eye oint",
    "White Soft Paraffin BP (White Petroleum Jelly BP)"
]

# --- SESSION STATE ---
if 'temp_ubat' not in st.session_state:
    st.session_state['temp_ubat'] = []

# --- UI SIDEBAR ---
st.sidebar.title("SUPS by Fazli")
st.sidebar.subheader("Ver.1 (Google Sheets Link)")
menu = st.sidebar.radio("Navigasi", ["Pendaftaran Pesakit", "Summary by Patient", "Summary Semua Ubat"])

# Load Data dari Google Sheets
df_master = get_existing_data()

# --- 1. PENDAFTARAN PESAKIT ---
if menu == "Pendaftaran Pesakit":
    st.header("📋 Input Data Pesakit (Sync to Cloud)")
    
    # Autofill Feature
    all_names = df_master['Nama'].tolist() if not df_master.empty else []
    search_name = st.selectbox("Cari Nama (Untuk Autofill):", [""] + sorted(list(set(all_names))))
    
    existing_data = df_master[df_master['Nama'] == search_name].iloc[0] if search_name else None

    col1, col2 = st.columns(2)
    with col1:
        nama = st.text_input("Nama:", value=existing_data['Nama'] if existing_data is not None else "").upper()
        ic = st.text_input("No. IC:", value=existing_data['IC'] if existing_data is not None else "")
    with col2:
        tca_ubat = st.date_input("TCA Ubat:", value=date.today())
        tca_clinic = st.date_input("TCA Clinic:", value=date.today())

    st.markdown("---")
    st.subheader("💊 Masukkan Senarai Ubat")
    
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        nama_ubat = st.selectbox("Pilih Ubat:", MASTER_UBAT)
    with c2:
        kuantiti = st.number_input("Kuantiti:", min_value=1, step=1)
    with c3:
        st.write("##")
        if st.button("➕ Tambah"):
            st.session_state['temp_ubat'].append(f"{nama_ubat} ({kuantiti})")

    if st.session_state['temp_ubat']:
        st.write("**Ubat yang dipilih:**", ", ".join(st.session_state['temp_ubat']))
        if st.button("🗑️ Kosongkan"):
            st.session_state['temp_ubat'] = []

    if st.button("💾 CONFIRM & SIMPAN KE CLOUD", use_container_width=True):
        if nama and ic and st.session_state['temp_ubat']:
            # Sediakan data baru
            new_row = pd.DataFrame([{
                "Nama": nama,
                "IC": ic,
                "TCA_Ubat": str(tca_ubat),
                "TCA_Clinic": str(tca_clinic),
                "Ubat_List": "; ".join(st.session_state['temp_ubat'])
            }])
            
            # Cantumkan dengan data lama dan update Google Sheet
            updated_df = pd.concat([df_master, new_row], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            
            st.session_state['temp_ubat'] = [] 
            st.success(f"Rekod {nama} Berjaya Disimpan ke Google Sheets!")
        else:
            st.error("Sila isi Nama, IC, dan tambah ubat.")

# --- 2. SUMMARY BY PATIENT (Data dari Cloud) ---
elif menu == "Summary by Patient":
    st.header("🔍 Rekod dari Cloud (Google Sheets)")
    if df_master.empty:
        st.info("Tiada data di Google Sheets.")
    else:
        st.dataframe(df_master, use_container_width=True)

# --- 3. SUMMARY SEMUA UBAT (Analisis Data) ---
elif menu == "Summary Semua Ubat":
    st.header("📊 Analisis Stok")
    if df_master.empty:
        st.info("Tiada data.")
    else:
        # Logik ringkas untuk pecahkan string ubat dan kira total
        all_meds_flat = []
        for item in df_master['Ubat_List']:
            meds = item.split("; ")
            for m in meds:
                try:
                    name_part = m.split(" (")[0]
                    qty_part = int(m.split(" (")[1].replace(")", ""))
                    all_meds_flat.append({"Ubat": name_part, "Qty": qty_part})
                except:
                    continue
        
        summary_df = pd.DataFrame(all_meds_flat).groupby('Ubat')['Qty'].sum().reset_index()
        st.table(summary_df)
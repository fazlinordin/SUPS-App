import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="SUPS by Fazli Ver.1.9", layout="wide")

# Link Web App yang Fazli berikan
URL_API = "https://script.google.com/macros/s/AKfycbxAnCNi_nIUnZew_p1S5nzLtcQipqqVg36GvRJtwkw-SZ7H8Vyc9wicdRA-tjU8I9eP2g/exec"

# Untuk baca data (Summary)
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        return conn.read(worksheet="Sheet1", ttl=0)
    except:
        return pd.DataFrame(columns=["Nama", "IC", "TCA_Ubat", "TCA_Clinic", "Ubat_List", "Batch", "Kuantiti"])

df = load_data()

# --- FUNGSI KIRA JARAK HARI ---
def kira_jarak_ubat_ke_klinik(t_ubat_str, t_clinic_str):
    if not t_clinic_str or t_clinic_str == "" or t_clinic_str == "None":
        return ""
    try:
        t_ubat = datetime.strptime(str(t_ubat_str), '%Y-%m-%d').date()
        t_clinic = datetime.strptime(str(t_clinic_str), '%Y-%m-%d').date()
        beza = (t_clinic - t_ubat).days
        return f"{beza} hari" if beza >= 0 else f"Lepas {abs(beza)} hari"
    except:
        return ""

# --- MASTER LIST UBAT (131 JENIS) ---
MASTER_UBAT = [
    "acetazolamide 250mg tab", "acetylsalicyclic acid 150 mg dispersible tab", "Acitretin 25mg capsule", "ACTRAPID",
    "acyclovir 800mg tab", "adapalene 0.1% gel", "allopurinol 100mg tablet", "amlodipine 10mg + valsartan 160",
    "amorolfine 5% nail lacquer", "Apixaban 2.5mg film coated tablet", "apixaban 5mg film coated tablet", "aqueous cream",
    "aripiprazole 10mg", "artificial tears/eye lubricant opth sol (single use)", "artificial tears/eye lubricant opthalmic solution",
    "ascorbic acid 100mg", "atorvastatin 20 mg", "atorvastatin 40mg", "baclofen 10 mg", "beclomethasone dipr 100mcg, formoterol 6mcg inh.",
    "benzoyl peroxide 5% gel", "betametasone 17 valerate 1 in 2 cream (0.05%)", "betametasone valearate 1:2 oinment",
    "betamethasone 17 valerate 0.1% ointment", "betamethasone 17-valerate 0.1% cream", "brimonidine tartrate 0.15% opth sol.",
    "budesonide 160mcg and formeterol 4.5mcg turbuhaler 120 doses", "calcipotrio 50 mcg/g betametasone 0.5mg/g oint",
    "calcitriol 0.25 mcg", "calcium carbonate 500mg", "calcium lactate 300mg", "carbamazepine 400mg CR", "Carbamide (urea) 10% Cream",
    "celexocib 200mg", "cetrimide 2% lotion", "cetrizine hcl 10mg", "Clobetasol Propionate 0.05% Oint.", "clobetasone butyrate 0.05% cream",
    "clobetasone butyrate 0.05% oinmt", "clopidogrel 75mg tab", "coal tar (LPC) 3% ointment", "coal tar (lpc) 6% oinment",
    "coal tar 1 % salicyclic acid 2 % shampoo (sebitar)", "Coal Tar 12% salicylic acid 2% Sulphur 4% Oint.", "dabigatran etexilate 150mg cap",
    "dapagliflozin 10mg", "dexamethasone sodium phosphate 0.1% eye drops", "dexamethasone,neomycin,polymyxin B eyedrop (maxitrol)",
    "diltiazem 30mg", "dorzolamide hcl 2% opth. Sol.", "dutasteride 0.5mg + tamsulosin 0.4mg cap", "empagliflozin 25mg tab",
    "emulsifying ointment BP (emulsificant oint)", "ezetimibe 10 mg tab", "felodipine 10mg ER", "fenofibrate 145mg",
    "ferric ammonium citrate 400mg/5ml (FAC)", "finasteride 5 mg", "flupenthixol decoante depot 20mg/ml inj",
    "fluticasone propionate 125mcg/dose evohaler", "fluvoxamine 50mg", "fusidic acid 1% eye drops", "gabapentin 300mg",
    "gemfibrozil 300mg", "gliclazide 80 mg", "gliclazide mr 60mg", "hypromellose 0.3% eye drop (preser. Fre)", "IBERET FOLIC",
    "insugen 30/70", "insugen N", "INSUGEN R", "INSULATARD", "Insulin glargine lantus", "INSUPEN",
    "Ipratropium br 20mcg fenoterol 50mcg/dose BERODUAL", "ivabradine 5 mg", "ketoprofen 2.5% gel", "lactulose 3.35g/5 ml liquid",
    "lamotrigine 100mg tab", "Lamotrigine 50mg tab", "latanaprost 0.005% eye drop", "levetiracetam 500mg", "loratadine 10mg",
    "lorazepam 1mg", "metformin xr 750 mg", "methotrexate 2.5mg", "mirabegron 50 mg PROLONGED RELEASE tab", "mirtazapine 15 mg orodispersible tab",
    "mirtazapine 30 mg orodispersible tab", "MIXTARD", "mometasone furoate 0.1% cream", "montelukast 10 mg", "moxifloxacin 0.5% ophthalmic solution",
    "nepafenac 0.1% w/v eye suspension (5ml)", "olanzapine 10mg tab", "omeprazole 20mg capsule", "paliperidone 75mg prolonged release injection",
    "pantoprazole 40mg", "pine tar 1% coal tar 1% salicyclic acid 2% shampoo sebitar", "quetiapine fumarate 100mg IR tab",
    "quetiapine fumarate 200mg ER", "quetiapine fumarate 50mg extended release tab", "salicyclic acid 5% oinment",
    "salicyclic acid, sulphur and liquid coal tar ointment", "salicylic acid 10% ointment", "salmeterol 25mcg , fluticasone propionate 125mcg evolaher",
    "salmeterol 50mcg +fluticasone 500mcg accuhaler", "Simvastatin 40 mg", "sodium valproate 200mg/5ml syrup (EPILIM)",
    "spironolactone 25mg", "sulphamethoxazole 400mg trimethoprim 80mg tab", "sunscreen SPF 50 lotion/cream", "tamsulosin HCL 400mcg ER",
    "theophyline sr 250mg", "timolol maleate 0.5% eye drop (pres. Free) 10 ml", "tiotropium 2.5mcg & olodaterol 2.5mcg/actuation,inh(Ctrdge only)",
    "tiotropium 2.5mcg / puff inhalation (catrigde only)", "Topiramate 100mg", "tramadol 50mg", "tretinoin 0.05% cream",
    "ursodeoxycholic acid 250mg capsule", "valsartan 160mg", "valsartan 80mg", "verapamil 40mg tab", "vildagliptin 50 mg tab",
    "vitamin b1 b6 b12", "warfarin 1mg", "Warfarin 2mg", "Warfarin 5mg", "white petroleum anhydrous liq linolin, mineral oil eye oint",
    "White Soft Paraffin BP (White Petroleum Jelly BP)"
]

SENARAI_BATCH = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

# --- UI SIDEBAR ---
st.sidebar.title("SUPS by Fazli")
menu = st.sidebar.radio("Menu Utama", ["📝 Daftar Pesakit Baru", "📊 Summary & Download"])

if menu == "📝 Daftar Pesakit Baru":
    st.header("📋 Daftar Pesakit & Ubat SPUB")
    
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Penuh:").upper()
            ic = st.text_input("No. IC (Tanpa -):")
            batch_pilihan = st.selectbox("Pilih Batch:", SENARAI_BATCH)
        with col2:
            tca_u = st.date_input("TCA Ubat:")
            ada_clinic = st.checkbox("Ada Tarikh TCA Clinic?", value=False)
            tca_c = st.date_input("TCA Clinic:", value=None) if ada_clinic else ""

        st.write("---")
        st.subheader("💊 Masukkan Ubat & Kuantiti")
        pilihan_ubat = st.multiselect("1. Pilih Nama Ubat:", MASTER_UBAT)
        kuantiti = st.text_input("2. Masukkan Kuantiti (Contoh: 30 BIJI / 1 KOTAK):")
        ubat_manual = st.text_area("3. Ubat Tiada Dalam List? (Taip di sini):")
        
        submit = st.form_submit_button("💾 SIMPAN REKOD", use_container_width=True)

    if submit:
        if nama and ic:
            list_ubat_str = " | ".join(pilihan_ubat)
            final_ubat = list_ubat_str if not ubat_manual else f"{list_ubat_str} | {ubat_manual.upper()}"
            
            # Memastikan struktur JSON ditutup dengan betul
            data_json = {
                "Nama": nama,
                "IC": ic,
                "TCA_Ubat": str(tca_u),
                "TCA_Clinic": str(tca_c) if ada_clinic else "",
                "Ubat_List": final_ubat,
                "Batch": batch_pilihan,
                "Kuantiti": kuantiti.upper()
            }

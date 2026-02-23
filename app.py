import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime, date

st.set_page_config(page_title="SUPS HJEM V3.5", layout="wide")

URL_API = "https://script.google.com/macros/s/AKfycbzir4NpkjGqR7XuBTFfxg8tziu7fBSlrHKgUICM_KSfC0MnRScdXh_8oi7uTGfHe01mkg/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- MASTER LIST (131 UBAT) ---
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
    # Mengambil hanya nombor bulat dari teks kuantiti
    angka = re.findall(r'\d+', str(teks))
    return sum(int(a) for a in angka) if angka else 0

def convert_to_matrix_with_total(df_filtered):
    data_list = []
    for _, row in df_filtered.iterrows():
        ubats = str(row['UBAT_LIST']).split(' | ')
        qtys = str(row['KUANTITI']).split(' | ')
        for u, q in zip(ubats, qtys):
            data_list.append({
                'NAMA PESAKIT': str(row['NAMA']).strip().upper(),
                'UBAT': str(u).strip().upper(), # Tukar ke UPPER untuk sorting yang betul
                'KUANTITI_TEXT': str(q).strip(),
                'KUANTITI_VAL': ekstrak_angka(q)
            })
    
    if not data_list: return pd.DataFrame()
    
    temp_df = pd.DataFrame(data_list)
    
    # 1. Pivot Table untuk paparan melintang
    matrix = temp_df.pivot_table(index='UBAT', columns='NAMA PESAKIT', values='KUANTITI_TEXT', aggfunc='first').fillna('')
    
    # 2. Susun Index A-Z (Upper case menjamin susunan yang betul)
    matrix = matrix.sort_index()
    
    # 3. Kira TOTAL
    total_val = temp_df.groupby('UBAT')['KUANTITI_VAL'].sum()
    matrix.insert(0, 'TOTAL (BIJI/UNIT)', total_val)
    
    return matrix

if 'bakul' not in st.session_state: st.session_state.bakul = []

# --- UI ---
menu = st.sidebar.radio("NAVIGASI", ["📝 INPUT", "📊 SUMMARY"])

if menu == "📝 INPUT":
    st.header("Input Pesakit & Ubat")
    with st.form("main_form"):
        c1, c2, c3 = st.columns(3)
        nama = c1.text_input("Nama:").upper()
        ic = c2.text_input("IC:")
        batch = c3.selectbox("Batch:", [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]])
        
        st.write("---")
        u1, u2 = st.columns([3, 1])
        pilih_u = u1.selectbox("Pilih Ubat:", ["-- PILIH --"] + MASTER_UBAT)
        qty_u = u2.text_input("Qty (Contoh: 30):")
        
        if st.form_submit_button("➕ Tambah ke Bakul"):
            if pilih_u != "-- PILIH --" and qty_u:
                st.session_state.bakul.append({"u": pilih_u, "q": qty_u})

    if st.session_state.bakul:
        st.table(pd.DataFrame(st.session_state.bakul))
        if st.button("💾 SIMPAN SEMUA"):
            u_list = " | ".join([x['u'] for x in st.session_state.bakul])
            q_list = " | ".join([x['q'] for x in st.session_state.bakul])
            payload = {"Nama": nama, "IC": ic, "Ubat_List": u_list, "Kuantiti": q_list, "Batch": batch}
            r = requests.post(URL_API, json=payload)
            if r.status_code == 200:
                st.success("Tersimpan!"); st.session_state.bakul = []; st.balloons()

elif menu == "📊 SUMMARY":
    st.header("Checklist & Total")
    df = load_data()
    if not df.empty:
        batch_sel = st.selectbox("Tapis Batch:", sorted(df['BATCH'].unique()))
        df_f = df[df['BATCH'] == batch_sel]
        res = convert_to_matrix_with_total(df_f)
        st.dataframe(res, use_container_width=True)
        st.download_button("📥 Download CSV", res.to_csv().encode('utf-8'), "Checklist.csv")

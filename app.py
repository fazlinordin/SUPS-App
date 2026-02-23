import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date

st.set_page_config(page_title="SUPS HJEM V3.6", layout="wide")

URL_API = "https://script.google.com/macros/s/AKfycbzir4NpkjGqR7XuBTFfxg8tziu7fBSlrHKgUICM_KSfC0MnRScdXh_8oi7uTGfHe01mkg/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- SENARAI RASMI 131 UBAT (Pastikan Nama Unik & Konsisten) ---
MASTER_UBAT = sorted([
    "ACETAZOLAMIDE 250MG TAB", "ACETYLSALICYCLIC ACID 150 MG DISPERSIBLE TAB", "ACITRETIN 25MG CAPSULE", "ACTRAPID",
    "ACYCLOVIR 800MG TAB", "ADAPALENE 0.1% GEL", "ALLOPURINOL 100MG TABLET", "AMLODIPINE 10MG + VALSARTAN 160",
    "AMOROLFINE 5% NAIL LACQUER", "APIXABAN 2.5MG FILM COATED TABLET", "APIXABAN 5MG FILM COATED TABLET", "AQUEOUS CREAM",
    "ARIPIPRAZOLE 10MG", "ARTIFICIAL TEARS EYE LUBRICANT (SINGLE USE)", "ARTIFICIAL TEARS EYE LUBRICANT SOLUTION",
    "ASCORBIC ACID 100MG", "ATORVASTATIN 20 MG", "ATORVASTATIN 40MG", "BACLOFEN 10 MG", 
    "BECLOMETHASONE DIPR 100MCG, FORMOTEROL 6MCG INH.", "BENZOYL PEROXIDE 5% GEL", "BETAMETASONE 17 VALERATE 1 IN 4 CREAM (0.025%)",
    "BETAMETASONE 17 VALERATE 1 IN 2 CREAM (0.05%)", "BETAMETASONE VALEARATE 1:2 OINMENT", "BETAMETHASONE 17 VALERATE 0.1% OINTMENT",
    "BETAMETHASONE 17-VALERATE 0.1% CREAM", "BRIMONIDINE TARTRATE 0.15% OPTH SOL.", 
    "BUDESONIDE 160MCG AND FORMETEROL 4.5MCG TURBUHALER 120 DOSES", "CALCIPOTRIO 50 MCG/G BETAMETASONE 0.5MG/G OINT",
    "CALCITRIOL 0.25 MCG", "CALCIUM CARBONATE 500MG", "CALCIUM LACTATE 300MG", "CARBAMAZEPINE 400MG CR", "CARBAMIDE (UREA) 10% CREAM",
    "CELEXOCIB 200MG", "CETRIMIDE 2% LOTION", "CETRIZINE HCL 10MG", "CLOBETASOL PROPIONATE 0.05% OINT.", "CLOBETASONE BUTYRATE 0.05% CREAM",
    "CLOBETASONE BUTYRATE 0.05% OINMT", "CLOPIDOGREL 75MG TAB", "COAL TAR (LPC) 3% OINTMENT", "COAL TAR (LPC) 6% OINMENT",
    "COAL TAR 1 % SALICYCLIC ACID 2 % SHAMPOO", "COAL TAR 12% SALICYLIC ACID 2% SULPHUR 4% OINT.", "DABIGATRAN ETEXILATE 150MG CAP",
    "DAPAGLIFLOZIN 10MG", "DEXAMETHASONE SODIUM PHOSPHATE 0.1% EYE DROPS", "DEXAMETHASONE,NEOMYCIN,POLYMYXIN B (MAXITROL)",
    "DILTIAZEM 30MG", "DORZOLAMIDE HCL 2% OPTH. SOL.", "DUTASTERIDE 0.5MG + TAMSULOSIN 0.4MG CAP", "DYDROGESTERONE 10 MG TAB",
    "EMPAGLIFLOZIN 25MG TAB", "EMULSIFYING OINTMENT BP", "EZETIMIBE 10 MG TAB", "FELODIPINE 10MG ER", "FENOFIBRATE 145MG",
    "FERRIC AMMONIUM CITRATE 400MG/5ML", "FINASTERIDE 5 MG", "FLUPENTHIXOL DECOANTE DEPOT 20MG/ML INJ",
    "FLUTICASONE PROPIONATE 125MCG/DOSE EVOHALER", "FLUVOXAMINE 50MG", "FUSIDIC ACID 1% EYE DROPS", "GABAPENTIN 300MG",
    "GEMFIBROZIL 300MG", "GLICLAZIDE 80 MG", "GLICLAZIDE MR 60MG", "HYPROMELLOSE 0.3% EYE DROP", "IBERET FOLIC",
    "INSUGEN 30/70", "INSUGEN N", "INSUGEN R", "INSULATARD", "INSULIN GLARGINE LANTUS", "INSUPEN",
    "BERODUAL INHALER", "IVABRADINE 5 MG", "KETOPROFEN 2.5% GEL", "LACTULOSE LIQUID",
    "LAMOTRIGINE 100MG TAB", "LAMOTRIGINE 50MG TAB", "LATANAPROST 0.005% EYE DROP", "LEVETIRACETAM 500MG", "LORATADINE 10MG",
    "LORAZEPAM 1MG", "METFORMIN XR 750 MG", "METHOTREXATE 2.5MG", "MIRABEGRON 50 MG", "MIRTAZAPINE 15 MG",
    "MIRTAZAPINE 30 MG", "MIXTARD", "MOMETASONE FUROATE 0.1% CREAM", "MONTELUKAST 10 MG", "MOXIFLOXACIN 0.5% OPHTHALMIC SOLUTION",
    "NEPAFENAC 0.1% W/V EYE SUSPENSION", "OLANZAPINE 10MG TAB", "OMEPRAZOLE 20MG CAPSULE", "PALIPERIDONE INJECTION",
    "PANTOPRAZOLE 40MG", "SEBITAR SHAMPOO", "QUETIAPINE FUMARATE 100MG IR",
    "QUETIAPINE FUMARATE 200MG ER", "QUETIAPINE FUMARATE 50MG ER", "SALICYCLIC ACID 5% OINMENT",
    "SALICYCLIC ACID, SULPHUR AND LIQUID COAL TAR", "SALICYLIC ACID 10% OINTMENT", "SALMETEROL 25/FLUTICASONE 125 EVOHALER",
    "SALMETEROL 50/FLUTICASONE 500 ACCUHALER", "SIMVASTATIN 40 MG", "URINARY ALKALINIZER SACHET",
    "SODIUM VALPROATE SYRUP", "SPIRONOLACTONE 25MG", "COTRIMOXAZOLE 480MG TAB", 
    "SUNSCREEN SPF 50", "TAMSULOSIN HCL 400MCG ER", "THEOPHYLINE SR 250MG", "TIMOLOL MALEATE 0.5% EYE DROP", 
    "TIOTROPIUM & OLODATEROL RESPIMAT", "TIOTROPIUM RESPIMAT", 
    "TOPIRAMATE 100MG", "TRAMADOL 50MG", "TRETINOIN 0.05% CREAM", "URSODEOXYCHOLIC ACID 250MG CAPSULE", "VALSARTAN 160MG", 
    "VALSARTAN 80MG", "VERAPAMIL 40MG TAB", "VILDAGLIPTIN 50 MG TAB", "VITAMIN B1 B6 B12", "WARFARIN 1MG", "WARFARIN 2MG", 
    "WARFARIN 5MG", "WHITE PETROLEUM EYE OINT", "WHITE PETROLEUM JELLY"
])

def load_data():
    try:
        df = pd.read_csv(f"{URL_SHEET_CSV}&cache={datetime.now().timestamp()}")
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

def convert_to_matrix_full(df_filtered):
    # 1. Bina senarai ubat asas (Semua 131 ubat mesti ada)
    matrix = pd.DataFrame(index=MASTER_UBAT)
    matrix.index.name = "💊 NAMA UBAT"
    
    if df_filtered.empty:
        return matrix

    # 2. Proses data pesakit
    pesakit_data = []
    for _, row in df_filtered.iterrows():
        n_pesakit = str(row['NAMA']).strip().upper()
        u_list = str(row['UBAT_LIST']).split(' | ')
        q_list = str(row['KUANTITI']).split(' | ')
        
        for u, q in zip(u_list, q_list):
            u_clean = u.strip().upper()
            if u_clean in MASTER_UBAT:
                # Simpan kuantiti teks untuk paparan pesakit
                matrix.at[u_clean, n_pesakit] = q.strip()
                # Simpan nilai angka untuk kira TOTAL
                try:
                    num = int(''.join(filter(str.isdigit, q)))
                except: num = 0
                pesakit_data.append({'U': u_clean, 'V': num})

    # 3. Kira TOTAL (Hanya ambil dari data pesakit tadi)
    if pesakit_data:
        df_calc = pd.DataFrame(pesakit_data)
        totals = df_calc.groupby('U')['V'].sum()
        matrix.insert(0, "📊 TOTAL (BIJI)", totals)
    else:
        matrix.insert(0, "📊 TOTAL (BIJI)", 0)

    return matrix.fillna("")

if 'bakul' not in st.session_state: st.session_state.bakul = []

# --- UI ---
menu = st.sidebar.radio("MENU", ["📝 INPUT", "📊 SUMMARY"])

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        nama = c1.text_input("Nama:").upper()
        ic = c2.text_input("IC:")
        batch = st.selectbox("Batch:", [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]])
        
        u1, u2 = st.columns([3, 1])
        p_u = u1.selectbox("Ubat:", ["-- PILIH --"] + MASTER_UBAT)
        p_q = u2.text_input("Qty:")
        
        if st.button("➕ Tambah Ubat"):
            if p_u != "-- PILIH --" and p_q:
                st.session_state.bakul.append({"u": p_u, "q": p_q})
                st.rerun()

    if st.session_state.bakul:
        st.table(pd.DataFrame(st.session_state.bakul))
        if st.button("💾 SIMPAN SEMUA", type="primary"):
            u_str = " | ".join([x['u'] for x in st.session_state.bakul])
            q_str = " | ".join([x['q'] for x in st.session_state.bakul])
            requests.post(URL_API, json={"Nama": nama, "IC": ic, "Ubat_List": u_str, "Kuantiti": q_str, "Batch": batch})
            st.success("Data Berjaya Disimpan!"); st.session_state.bakul = []; st.balloons()

elif menu == "📊 SUMMARY":
    st.header("Checklist Master (A-Z)")
    df = load_data()
    if not df.empty:
        b_sel = st.selectbox("Pilih Batch:", sorted(df['BATCH'].unique()))
        df_f = df[df['BATCH'] == b_sel]
        
        # Jana matrix Checklist Penuh
        final_table = convert_to_matrix_full(df_f)
        
        st.dataframe(final_table, use_container_width=True, height=600)
        st.download_button("📥 Muat Turun CSV", final_table.to_csv().encode('utf-8'), f"Checklist_{b_sel}.csv")

import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date

# --- 1. SETTING AWAL ---
st.set_page_config(page_title="SUPS HJEM V4.7", layout="wide")

if 'bakul' not in st.session_state:
    st.session_state.bakul = []

URL_API = "https://script.google.com/macros/s/AKfycbzir4NpkjGqR7XuBTFfxg8tziu7fBSlrHKgUICM_KSfC0MnRScdXh_8oi7uTGfHe01mkg/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- 2. MASTER LIST UBAT ---
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
    "CALCITRIOL 0.25 MCG", "CALCIUM CARBONATE 500MG", "CALCIUM LAKTATE 300MG", "CARBAMAZEPINE 400MG CR", "CARBAMIDE (UREA) 10% CREAM",
    "CELEXOCIB 200MG", "CETRIMIDE 2% LOTION", "CETRIZINE HCL 10MG", "CLOBETASOL PROPIONATE 0.05% OINT.", "CLOBETASONE BUTYRATE 0.05% CREAM",
    "CLOBETASONE BUTYRATE 0.05% OINMT", "CLOPIDOGREL 75MG TAB", "COAL TAR (LPC) 3% OINTMENT", "COAL TAR (LPC) 6% OINMENT",
    "COAL TAR 1 % SALICYCLIC ACID 2 % SHAMPOO", "COAL TAR 12% SALICYLIC ACID 2% SULPHUR 4% OINT.", "DABIGATRAN ETEXILATE 150MG CAP",
    "DAPAGLIFLOZIN 10MG", "DEXAMETHASONE SODIUM PHOSPHATE 0.1% EYE DROPS", "DEXAMETHASONE,NEOMYCIN,POLYMYXIN B (MAXITROL)",
    "DILTIAZEM 30MG", "DORZOLAMIDE HCL 2% OPTH. SOL.", "DUTASTERIDE 0.5MG + TAMSULOSIN 0.4MG CAP", "DYDROGESTERONE 10 MG TAB",
    "EMPAGLIFLOZIN 25MG TAB", "EMULSIFYING OINTMENT BP", "EZETIMIBE 10 MG TAB", "FELODIPINE 10MG ER", "FENOFIBRATE 145MG",
    "FERRIC AMMONIUM CITRATE 400MG/5ML", "FINASTERIDE 5 MG", "FLUPENTHIXOL DECOANTE DEPOT 20MG/ML INJ",
    "FLUTICASONE PROPIONATE 125MCG/DOSE EVOHALER", "FLUVOXAMINE 50MG", "FUSIDIC ACID 1% EYE DROPS", "GABAPENTIN 300MG",
    "GEMFIBROZIL 300MG", "GLICLAZIDE 80 MG", "GLICLAZIDE MR 60MG", "HUMAN, PREMIXED (DIABULYN-30/70) 100 IU/ML PENFILL", "HYPROMELLOSE 0.3% EYE DROP", "IBERET FOLIC",
    "INSUGEN 30/70", "INSUGEN N", "INSUGEN R", "INSULATARD", "INSULIN GLARGINE LANTUS", "INSUPEN",
    "BERODUAL INHALER", "IVABRADINE 5 MG", "KETOPROFEN 2.5% GEL", "LACTULOSE LIQUID",
    "LAMOTRIGINE 100MG TAB", "LAMOTRIGINE 50MG TAB", "LATANAPROST 0.005% EYE DROP", "LEVETIRACETAM 500MG", "LORATADINE 10MG",
    "LORAZEPAM 1MG", "METFORMIN XR 750 MG", "METHOTREXATE 2.5MG", "MIRABEGRON 50 MG", "MIRTAZAPINE 15 MG",
    "MIRTAZAPINE 30 MG", "MIXTARD", "MOMETASONE FUROATE 0.1% CREAM", "MONTELUKAST 10 MG", "MOXIFLOXACIN 0.5% OPHTHALMIC SOLUTION",
    "NEPAFENAC 0.1% W/V EYE SUSPENSION", "OLANZAPINE 10MG TAB", "OMEPRAZOLE 20MG CAPSULE", "PALIPERIDONE INJECTION",
    "PANTOPRAZOLE 40MG", "SACUBITRIL 49MG, VALSARTAN 51MG TABLET", "SEBITAR SHAMPOO", "QUETIAPINE FUMARATE 100MG IR",
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

# --- 3. FUNGSI LOGIK ---
def load_data():
    try:
        df = pd.read_csv(f"{URL_SHEET_CSV}&cache={datetime.now().timestamp()}")
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

def hitung_durasi(tca_u, tca_d):
    if not tca_u or not tca_d or tca_u == "-" or tca_d == "-": return "-"
    try:
        d1 = datetime.strptime(str(tca_u), "%Y-%m-%d")
        d2 = datetime.strptime(str(tca_d), "%Y-%m-%d")
        return f"{(d2 - d1).days} HARI"
    except: return "-"

def convert_to_matrix_final(df_f):
    if df_f.empty: return pd.DataFrame()
    matrix_data, info_u, info_d, info_dur, calc_dict = [], {}, {}, {}, {}

    # Proses Data
    for _, row in df_f.iterrows():
        p = str(row['NAMA']).strip().upper()
        tu, td = str(row.get('TCA_UBAT', '-')), str(row.get('TCA_CLINIC', '-'))
        info_u[p], info_d[p], info_dur[p] = tu, td, hitung_durasi(tu, td)
        
        u_list, q_list = str(row['UBAT_LIST']).split(' | '), str(row['KUANTITI']).split(' | ')
        for u, q in zip(u_list, q_list):
            u_up, q_str = u.strip().upper(), q.strip()
            matrix_data.append({'UBAT_ORIG': u_up, 'PESAKIT': p, 'QTY': q_str})
            try:
                num = int(''.join(filter(str.isdigit, q_str)))
                calc_dict[u_up] = calc_dict.get(u_up, 0) + num
            except: pass

    # Bina DataFrame Matrix
    df_m = pd.DataFrame(matrix_data)
    # Tukar Nama Ubat kepada format (TOTAL) NAMA
    df_m['UBAT'] = df_m['UBAT_ORIG'].apply(lambda x: f"({calc_dict.get(x, 0)}) {x}")
    
    matrix = df_m.pivot_table(index='UBAT', columns='PESAKIT', values='QTY', aggfunc='first').fillna("")
    
    # Header Info
    header = pd.DataFrame([info_u, info_d, info_dur], index=["📅 TCA AMBIL", "👨‍⚕️ TCA DR", "⏳ DURASI"])
    return pd.concat([header, matrix], sort=False).fillna("")

# --- 4. UI ---
menu = st.sidebar.radio("NAVIGASI", ["📝 INPUT", "📊 SUMMARY"])

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    with st.form("main_form"):
        c1, c2, c3 = st.columns(3)
        nama = c1.text_input("Nama:").upper()
        ic = c2.text_input("IC:").upper()
        batch = c3.selectbox("Batch:", [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]])
        
        c4, c5 = st.columns(2)
        t_u = c4.date_input("TCA Ambil Ubat:", value=date.today())
        t_d = c5.date_input("TCA Klinik (Dr):", value=None)
        
        st.divider()
        u1, u2 = st.columns([3, 1])
        p_u = u1.selectbox("Pilih Ubat:", ["-- PILIH --"] + MASTER_UBAT)
        p_q = u2.text_input("Qty:")
        
        if st.form_submit_button("➕ Tambah"):
            if p_u != "-- PILIH --" and p_q:
                st.session_state.bakul.append({"u": p_u, "q": p_q})
                st.rerun()

    if st.session_state.bakul:
        st.write("### 🛒 Bakul Sementara")
        for i, item in enumerate(st.session_state.bakul):
            col_a, col_b, col_c = st.columns([3, 1, 1])
            col_a.write(f"**{item['u']}**")
            col_b.write(f"{item['q']}")
            if col_c.button("🗑️", key=f"del_{i}"):
                st.session_state.bakul.pop(i)
                st.rerun()

        if st.button("💾 SIMPAN KE GOOGLE SHEET", type="primary"):
            payload = {
                "Nama": nama, "IC": ic, "TCA_Ubat": str(t_u), 
                "TCA_Clinic": str(t_d) if t_d else "-",
                "Ubat_List": " | ".join([x['u'] for x in st.session_state.bakul]),
                "Kuantiti": " | ".join([x['q'] for x in st.session_state.bakul]),
                "Batch": batch
            }
            requests.post(URL_API, json=payload)
            st.success("Tersimpan!"); st.session_state.bakul = []; st.balloons()

elif menu == "📊 SUMMARY":
    st.header("Checklist & Durasi Bekalan")
    df = load_data()
    if not df.empty:
        b_sel = st.selectbox("Pilih Batch:", sorted(df['BATCH'].unique()))
        df_f = df[df['BATCH'] == b_sel]
        res = convert_to_matrix_final(df_f)
        st.dataframe(res, use_container_width=True, height=600)
        st.download_button("📥 Muat Turun CSV", res.to_csv().encode('utf-8'), f"{b_sel}.csv")

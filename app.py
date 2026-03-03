import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io

# --- 1. SETTING AWAL ---
st.set_page_config(page_title="SUPS HJEM V5.5", layout="wide")

if 'bakul' not in st.session_state:
    st.session_state.bakul = []
if 'pilihan_batch' not in st.session_state:
    st.session_state.pilihan_batch = "Mac - Batch 1"

URL_API = "https://script.google.com/macros/s/AKfycbyeZXuPoyqsORGh_-kPC8lVTiFe41qZvQ4V8gBQU_BXnmP30zufcjSDxN6HnqyzQRRu/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- 2. MASTER LIST UBAT ---
# (Senarai ubat kekal sama seperti sebelumnya)
MASTER_UBAT = sorted([
    "ACETAZOLAMIDE 250MG TAB", "Tiotropium 2.5mcg/puff inhalation Catridge+Inhaler", "ALENDRONATE SODIUM 70MG TAB", "ACETYLSALICYCLIC ACID 150 MG DISPERSIBLE TAB", "ACITRETIN 25MG CAPSULE", "ACTRAPID",
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

# --- 3. FUNGSI ---
def load_data():
    try:
        df = pd.read_csv(f"{URL_SHEET_CSV}&cache={datetime.now().timestamp()}")
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

def format_tarikh(t_str):
    if not t_str or t_str == "-" or str(t_str).strip() == "": return "-"
    try:
        dt = datetime.strptime(str(t_str), "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except: return str(t_str)

def hitung_durasi(tca_u, tca_d):
    if not tca_u or not tca_d or tca_u == "-" or tca_d == "-": return "TIADA DATA"
    try:
        d1 = tca_u if isinstance(tca_u, date) else datetime.strptime(str(tca_u), "%Y-%m-%d").date()
        d2 = tca_d if isinstance(tca_d, date) else datetime.strptime(str(tca_d), "%Y-%m-%d").date()
        return f"{(d2 - d1).days} HARI"
    except: return "TIADA DATA"

def convert_to_matrix_final(df_f):
    if df_f.empty: return pd.DataFrame()
    matrix_data, info_u, info_d, info_dur, calc_data = [], {}, {}, {}, []
    for _, row in df_f.iterrows():
        p = str(row['NAMA']).strip().upper()
        tu, td = str(row.get('TCA_UBAT', '-')), str(row.get('TCA_CLINIC', '-'))
        info_u[p], info_d[p], info_dur[p] = format_tarikh(tu), format_tarikh(td), hitung_durasi(tu, td)
        u_list, q_list = str(row['UBAT_LIST']).split(' | '), str(row['KUANTITI']).split(' | ')
        for u, q in zip(u_list, q_list):
            u_up, q_str = u.strip().upper(), q.strip()
            matrix_data.append({'UBAT': u_up, 'PESAKIT': p, 'QTY': q_str})
            try:
                num = int(''.join(filter(str.isdigit, q_str)))
                calc_data.append({'UBAT': u_up, 'VAL': num})
            except: pass
    df_m = pd.DataFrame(matrix_data)
    matrix = df_m.pivot_table(index='UBAT', columns='PESAKIT', values='QTY', aggfunc='first').fillna("")
    if calc_data:
        totals = pd.DataFrame(calc_data).groupby('UBAT')['VAL'].sum().astype(int)
        matrix.insert(0, "📊 TOTAL", totals)
    header = pd.DataFrame([info_u, info_d, info_dur], index=["📅 TCA AMBIL", "👨‍⚕️ TCA DR", "⏳ DURASI"])
    header.insert(0, "📊 TOTAL", "")
    return pd.concat([header, matrix], sort=False).fillna("")

def to_excel_colored(df):
    output = io.BytesIO()
    try:
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=True, sheet_name='Summary')
        workbook  = writer.book
        worksheet = writer.sheets['Summary']
        fmt_yellow = workbook.add_format({'bg_color': '#FFFFE0', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        fmt_white  = workbook.add_format({'bg_color': '#FFFFFF', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        fmt_header = workbook.add_format({'bg_color': '#C0C0C0', 'bold': True, 'border': 1, 'align': 'center'})
        fmt_ubat_y = workbook.add_format({'bg_color': '#FFFF00', 'border': 1, 'align': 'left'})
        fmt_ubat_w = workbook.add_format({'bg_color': '#FFFFFF', 'border': 1, 'align': 'left'})
        num_cols = len(df.columns) + 1
        for row_num in range(len(df) + 1):
            if row_num == 0: worksheet.set_row(row_num, None, fmt_header)
            else:
                is_yellow = row_num % 2 == 0
                current_fmt = fmt_yellow if is_yellow else fmt_white
                ubat_fmt = fmt_ubat_y if is_yellow else fmt_ubat_w
                worksheet.set_row(row_num, None, current_fmt)
                worksheet.write(row_num, 0, df.index[row_num-1], ubat_fmt)
        worksheet.set_column(0, 0, 45)
        worksheet.set_column(1, 1, 12)
        worksheet.set_column(2, num_cols, 18)
        writer.close()
    except: df.to_excel(output, index=True)
    return output.getvalue()

# --- 4. UI ---
menu = st.sidebar.radio("NAVIGASI", ["📝 INPUT", "📊 SUMMARY"])
SENARAI_BATCH = [f"{m} - Batch {b}" for m in ["Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"] for b in [1, 2]]

if menu == "📝 INPUT":
    st.header("Pendaftaran Pesakit")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        nama = c1.text_input("Nama:").upper()
        ic = c2.text_input("IC:").upper()
        idx_batch = SENARAI_BATCH.index(st.session_state.pilihan_batch)
        batch = c3.selectbox("Batch:", SENARAI_BATCH, index=idx_batch)
        st.session_state.pilihan_batch = batch 
        
        c4, c5 = st.columns(2)
        t_u = c4.date_input("TCA Ambil Ubat (Hari Ini):", value=date.today())
        # TCA DR sekarang boleh kosong
        t_d = c5.date_input("TCA Klinik (Dr) [Opsional]:", value=None)
        
        if t_d:
            baki = (t_d - t_u).days
            if baki > 0: st.success(f"🎯 **Sila bekalkan ubat untuk: {baki} Hari**")
        else:
            st.info("ℹ️ Tarikh klinik dikosongkan. Durasi tidak akan dikira.")

    with st.form("ubat_form", clear_on_submit=True):
        u1, u2 = st.columns([3, 1])
        p_u = u1.selectbox("Pilih Ubat:", ["-- PILIH --"] + MASTER_UBAT)
        p_q = u2.text_input("Qty:")
        if st.form_submit_button("➕ Tambah Ke Bakul"):
            if p_u != "-- PILIH --" and p_q:
                st.session_state.bakul.append({"u": p_u, "q": p_q}); st.rerun()

    if st.session_state.bakul:
        st.write("### 🛒 Bakul Sementara")
        for i, item in enumerate(st.session_state.bakul):
            col_a, col_b, col_c = st.columns([3, 1, 1])
            col_a.write(f"**{item['u']}**"); col_b.write(f"{item['q']}")
            if col_c.button("🗑️", key=f"del_{i}"):
                st.session_state.bakul.pop(i); st.rerun()
        
        if st.button("💾 SIMPAN DATA", type="primary", use_container_width=True):
            if nama and ic: # Hanya Nama & IC wajib
                payload = {
                    "Nama": nama, 
                    "IC": ic, 
                    "TCA_Ubat": str(t_u), 
                    "TCA_Clinic": str(t_d) if t_d else "-", # Hantar tanda sengkang jika kosong
                    "Ubat_List": " | ".join([x['u'] for x in st.session_state.bakul]), 
                    "Kuantiti": " | ".join([x['q'] for x in st.session_state.bakul]), 
                    "Batch": batch
                }
                requests.post(URL_API, json=payload)
                st.success("Tersimpan!"); st.session_state.bakul = []; st.balloons()
            else: 
                st.error("Sila isi Nama dan IC sebelum simpan!")

elif menu == "📊 SUMMARY":
    st.header("Checklist & Durasi Bekalan")
    df = load_data()
    if not df.empty:
        idx_batch_s = SENARAI_BATCH.index(st.session_state.pilihan_batch)
        b_sel = st.selectbox("Pilih Batch:", SENARAI_BATCH, index=idx_batch_s)
        st.session_state.pilihan_batch = b_sel 
        df_f = df[df['BATCH'] == b_sel]
        
        if not df_f.empty:
            with st.expander("🗑️ PADAM REKOD PESAKIT"):
                pesakit_list = sorted(df_f['NAMA'].unique())
                p_padam = st.selectbox("Pilih Pesakit:", ["-- PILIH --"] + pesakit_list)
                if st.button("❗ PADAM"):
                    if p_padam != "-- PILIH --":
                        requests.post(URL_API, json={"action": "DELETE", "Nama": p_padam, "Batch": b_sel})
                        st.warning("Memadam..."); st.rerun()
            
            res = convert_to_matrix_final(df_f)
            st.dataframe(res.style.apply(lambda x: ['background-color: #FFFF00' if i % 2 == 0 else '' for i in range(len(res))], axis=0), use_container_width=True, height=500)
            excel_data = to_excel_colored(res)
            st.download_button(label="📥 Muat Turun Excel (.xlsx)", data=excel_data, file_name=f"{b_sel}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info(f"Tiada data untuk {b_sel}")






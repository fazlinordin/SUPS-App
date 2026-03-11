import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import io
import time

# --- 1. SETTING AWAL ---
st.set_page_config(page_title="SUPS HJEM V6.1", layout="wide")

if 'bakul' not in st.session_state:
    st.session_state.bakul = []
if 'pilihan_batch' not in st.session_state:
    st.session_state.pilihan_batch = "Mac - Batch 1"
if 'input_nama' not in st.session_state:
    st.session_state.input_nama = ""
if 'input_ic' not in st.session_state:
    st.session_state.input_ic = ""

URL_API = "https://script.google.com/macros/s/AKfycbyeZXuPoyqsORGh_-kPC8lVTiFe41qZvQ4V8gBQU_BXnmP30zufcjSDxN6HnqyzQRRu/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/18K_lW1HUvA28cG6b5tf9RR3ckF8ONyALzDejvMhTvtI/export?format=csv"

# --- 2. MASTER LIST UBAT ---
# (Kekalkan list ubat yang panjang ini)
MASTER_UBAT = sorted([
    "Abacavir 300mg Tablet", "Abacavir Sulphate 600mg + Lamivudine 300mg Tablet", "Acarbose 50 mg Tablet", 
    "Acetazolamide 250 mg Tablet", "Acetylsalicylic Acid 100 mg, Glycine 45 mg Tablet", "Acetylsalicylic Acid 150 mg Dispersible Tablet", 
    "Acetylsalicylic Acid 300 mg Soluble Tablet", "Acitretin 25mg Capsule", "Acriflavine 0.1% Lotion", 
    "Acyclovir 5% Cream", "Acyclovir 200 mg Tablet", "Acyclovir 800 mg Tablet", "Adadapalene 0.1% Gel", 
    "Agomelatine 25mg Tablet", "Albendazole 200 mg Tablet", "Albendazole 200 mg/5 ml Suspension", "Alcohol 70% Solution", 
    "Alcohol 96% (For External Use Only)", "Alcohol 96% (For Internal Use Only)", "Alendronate Sodium 70 mg Tablet", 
    "Alendronate Sodium 70 mg and Cholecalciferol 5600 IU Tablet", "Alfuzosin HCl 10 mg Tablet", "Alkaline Nasal Douche", 
    "Allopurinol 100 mg Tablet", "Allopurinol 300 mg Tablet", "Alprazolam 0.25 mg Tablet", "Alprazolam 0.5 mg Tablet", 
    "Amiloride HCl 5 mg + Hydrochlorothiazide 50 mg Tablet", "Amisulpride 400 mg Tablet", "Amitriptyline HCl 25 mg Tablet", 
    "Amlodipine 5 mg Tablet", "Amlodipine 10 mg Tablet", "Amlodipine 10 mg and Valsartan 160 mg Tablet", 
    "Amlodipine 10mg/Valsartan 160mg/Hydrochlorothiazide 25mg Tab", "Amoxicillin 250mg Capsule", "Amoxicillin 500mg Capsule", 
    "Amoxicillin 250mg/5mL Oral Solution", "Amoxicillin Trihydrate 125 mg/5 ml Syrup", "Amoxicillin 500 mg + Clavulanate 125 mg Tablet", 
    "Amoxicillin + Clavulanate 228 mg/5 ml Syrup", "Amorolfine 5 % Nail Lacquer", "Ampicillin + Sulbactam 375mg Tab", 
    "Apixaban 2.5 mg Film-coated Tablet", "Apixaban 5 mg Film-coated Tablet", "Aqueous Cream", "Aripiprazole 10mg Tablet", 
    "Artificial Tears/Eye Lubricant Ophthalmic Gel", "Artificial Tears/Eye Lubricant Ophthalmic Solution", 
    "Artificial Tears/Eye Lubricant Ophthalmic Solution (Preservative Free)", "Artificial Tears/Eye Lubricant Ophthalmic Solution (Single Use)", 
    "Ascorbic Acid 100 mg Tablet", "Atenolol 50 mg Tablet", "Atenolol 100 mg Tablet", "Atorvastatin 20 mg Tablet", 
    "Atorvastatin 40 mg Tablet", "Atorvastatin 80 mg Tablet", "Atropine Sulphate 1mg/ml Injection", "Atropine Sulphate 1% Eye Drops", 
    "Azathioprine 50 mg Tablet", "Azithromycin 250 mg Tablet", "Baclofen 10 mg Tablet", "BCG Vaccine Freeze-Dried Inj", 
    "Beclomethasone Dipropionate 50 mcg/dose Nasal Spray", "Beclomethasone Dipropionate 100 mcg/dose Inhalation", 
    "Beclomethasone Dipr. 100mcg, Formoterol 6mcg Inhalation", "Benzathine Penicillin 2.4MIU (1.8g) Injection", 
    "Benzhexol 2 mg Tablet", "Benzoic Acid Compound Ointment (Whitfields)", "Benzoyl Peroxide 5% Gel", 
    "Benzydamine HCl 0.15% Solution (Difflam)", "Benzydamine HCl 0.15% Solution (Easiflam)", "Benzyl Benzoate 12.5% Emulsion (Child)", 
    "Benzyl Benzoate 25 % Emulsion (Adult)", "Benzyl Benzoate, Zinc Oxide & Balsam Peru Suppository (Anusol)", 
    "Betahistine Dihydrochloride 24mg Tablet", "Betamethasone 17-Valerate 0.025% (1 in 4) Cream", "Betamethasone 17-Valerate 0.05% (1 in 2) Cream", 
    "Betamethasone 17-Valerate 0.1% Cream", "Betamethasone 17-Valerate 0.1% Ointment", "Betamethasone Valerate 1 in 2 Ointment", 
    "Betamethasone Valerate 1 in 10 Ointment", "Betaxolol 0.25% Eye Suspension", "Bimatoprost 0.03% Ophthalmic Solution", 
    "Bisacodyl 5 mg Tablet", "Bisacodyl 10 mg Suppository", "Bisoprolol Fumarate 2.5 mg Tablet", "Bisoprolol Fumarate 5 mg Tablet", 
    "Brimonidine Tartrate 0.15% Ophthalmic Solution", "Brinzolamide 1%, Brimonidine 0.2% Ophthalmic Suspension", 
    "Bromhexine HCl 4 mg/5 ml Elixir", "Bromhexine HCl 8mg Tablet", "Bromocriptine Mesilate 2.5mg Tablet", "Bromocriptine Mesilate 5mg Tablet", 
    "Budesonide 64mcg Nasal Spray", "Budesonide 100mcg Nasal Spray", "Budesonide 200mcg/dose Inhalation (300 Doses)", 
    "Budesonide Pressurised Inhalation BP 200mcg", "Budesonide 160mcg and Formoterol 4.5mcg Turbuhaler (120doses)", 
    "Calamine Cream", "Calamine Lotion", "Calcipotriol 50 mcg/g + Betamethasone 0.5 mg/g Gel", "Calcipotriol 50 mcg/g + Betamethasone 0.5 mg/g Ointment", 
    "Calcitriol 0.25mcg Capsule", "Calcium Carbonate 500mg Tablet", "Calcium Gluconate 10% Injection", "Calcium Lactate 300mg Tablet", 
    "Calcium Polystyrene Sulphonate Powder, 5g/sachet", "Captopril 25mg Tablet", "Carbamazepine 200mg Tablet", 
    "Carbamazepine 200mg CR Tablet", "Carbamazepine 400mg CR Tablet", "Carbamide (Urea) 10 % Cream", "Carbimazole 5mg Tablet", 
    "Carvedilol 6.25mg Tablet", "Celecoxib 200mg Capsule", "Cephalexin Monohydrate 250mg Capsule", "Cephalexin Monohydrate 500mg Capsule", 
    "Ceftriaxone 500mg Injection", "Cefuroxime Axetil 125mg Tablet", "Cetirizine HCl 10mg Tablet", "Cetrimide 2% Lotion", 
    "Charcoal Activated 250mg Tablet", "Chloramphenicol 0.5% Eye Drops", "Chloramphenicol 1% Eye Ointment", "Chloramphenicol 5% w/v Ear Drops", 
    "Chlorhexidine 1:200 in Alcohol with Emollient", "Chlorhexidine 1 in 200 (0.5%) in Alcohol 70%", "Chlorhexidine 1 in 2000 (0.05%) in Alcohol 70%", 
    "Chlorhexidine Gluconate 0.2% Mouthwash", "Chlorhexidine Gluconate 5% Solution", "Chlorhexidine gluconate 1% Cream (Obstetric)", 
    "Chlorpheniramine Maleate 2 mg/5 ml Syrup", "Chlorpheniramine Maleate 4mg Tablet", "Chlorpheniramine 10mg/ml Injection", 
    "Chlorpromazine HCl 25 mg Tablet", "Chlorpromazine HCl 100 mg Tablet", "Cholecalciferol 25,000 IU per 1ml Oral Solution", 
    "Cinnarizine 25 mg Tablet", "Clobetasol Propionate 0.05% Cream", "Clobetasol Propionate 0.05% Ointment", 
    "Clobetasone Butyrate 0.05% Cream", "Clobetasone Butyrate 0.05% Ointment", "Clopidogrel 75 mg Tablet", 
    "Clotrimazole 1% Cream", "Clotrimazole 500 mg Vaginal Tablet", "Clozapine 100 mg Tablet", "Cloxacillin Sodium 125 mg/5 ml Suspension", 
    "Cloxacillin Sodium 250mg Capsule", "Cloxacillin 500mg Capsule", "Coal Tar (LPC) 3% Ointment", "Coal Tar (LPC) 6% Ointment", 
    "Coal Tar 12% Salicylic acid 2% Sulphur 4% Ointment", "Colchicine 0.5 mg Tablet", "Compound Zinc Paste BP (25%w/w)", 
    "Conjugated Oestrogens 0.625mg Tablet", "Copper Sulphate Crystal", "Crotamiton 10 % Cream", "Dabigatran Etexilate 110 mg Capsule", 
    "Dabigatran Etexilate 150 mg Capsule", "Daclatasvir 60mg Tablet", "Danazol 200 mg Capsule", "Dapagliflozin 10 mg Film-Coated Tablet", 
    "Dapsone 100 mg Tablet", "Desloratadine 5 mg Tablet", "Desvenlafaxine 50 mg EXTENDED RELEASE Tablet", "Dexamethasone Acetate 0.1% Eye Drop", 
    "Dexamethasone sodium phosphate 0.1% Eye Drops", "Dexamethasone,Neomycin,Polymyxin B Eye Drop (Maxitrol)", 
    "Dextrose 5% 500ml IV soln", "Dextrose 10% 500mL IV soln", "Dextrose 50% 10mL Inj", "Dextrose Powder", 
    "Diazepam 5 mg Rectal Solution", "Diazepam 10 mg/2 ml Injection", "Diclofenac 1% Emulgel", "Diclofenac Sodium 50 mg Tablet", 
    "Diclofenac Sodium 75mg/3 ml Injection", "Dienogest 2mg Tablet", "Digoxin 0.25 mg Tablet", "Diltiazem HCl 30 mg Tablet", 
    "Diosmin 450 mg and Hesperidin 50 mg Tablet", "Diphenhydramine HCl Expectorant (Adult)", "Diphenhydramine HCl Expectorant (Paediatric) 7mg/5ml", 
    "Diphenoxylate with Atropine Sulphate Tablet", "Diphtheria and Tetanus Vaccine", "Diptheria-Tetanus-Pertussis-IPV-Hib Vaccine", 
    "Distilled Water", "Dolutegravir 50 mg Tablet", "Domperidone 1 mg/ml Suspension", "Domperidone 10 mg Tablet", 
    "Donepezil HCl 5 mg Tablet", "Donepezil HCl 10 mg Tablet", "Dorzolamide HCl 2% Ophthalmic Solution", 
    "Dorzolamide 2%, Timolol 0.5% Eye drop", "Doxazosin Mesilate 4 mg CR Tablet", "Doxycycline 100 mg Capsule", 
    "Duloxetine 60 mg Capsule", "Dutasteride 0.5 mg Capsule", "Dutasteride 0.5mg and Tamsulosin 0.4mg Capsule", 
    "Dydrogesterone 10 mg Tablet", "Ear Wax Softener (Ear Drop)", "Efavirenz 200 mg Capsule/Tablet", "Efavirenz 600 mg Tablet", 
    "Empagliflozin 10 mg Tablet", "Empagliflozin 25 mg Tablet", "Emulsifying Ointment BP", "Enalapril 5 mg Tablet", 
    "Enalapril 10 mg Tablet", "Enalapril 20 mg Tablet", "Enoxaparin Sodium 20 mg Injection", "Enoxaparin Sodium 60 mg Injection", 
    "Entacapone 200 mg Tablet", "Eperisone HCl 50 mg Tablet", "Erythromycin Ethylsuccinate 200 mg/5 ml Suspension", 
    "Erythromycin Ethylsuccinate 400 mg Tablet", "Escitalopram 10 mg Tablet", "ESOMEprazole 40 mg Tablet", 
    "Estradiol 2mg + Norgestrel 0.5mg (Combo Pack)", "Ethambutol HCl 400 mg Tablet", "Ethinyloestradiol 30mcg + Levonorgestrel 150mcg Tab", 
    "Etonogestrel 68 mg Implant", "Etoricoxib 90 mg Tablet", "Etoricoxib 120 mg Tablet", "Ezetimibe 10 mg Tablet", 
    "Ezetimibe 10 mg + Simvastatin 20 mg Tablet", "Felodipine 10 mg EXTENDED RELEASE Tablet", "Fenofibrate 145mg Tablet", 
    "Fentanyl 25 mcg/h Transdermal Patch", "Ferric Ammonium Citrate 400mg/5ml (FAC)", "Ferrous 350mg, Folic 1mg, Vit C, B6, B12, Zinc Capsule", 
    "Ferrous CR 525mg, Folic 800mcg, Vit C, B-Complex Tablet", "Ferrous Fumarate 200 mg Tablet", 
    "Ferrous Iron (Elemental Iron > 100mg), Vitamin & Mineral Capsule", "Finasteride 5 mg Tablet", "Fluconazole 100 mg Capsule", 
    "Fludrocortisone Acetate 0.1 mg Tablet", "Flunarizine HCl 5 mg Capsule", "Fluoxetine HCl 20 mg Capsule/Tablet", 
    "Flupenthixol Decanoate Depot 20mg/ml lnjection", "Fluphenazine Decanoate 25mg/ml Inj", "Fluticasone Furoate 27.5 mcg/dose Nasal Spray (60 doses)", 
    "Fluticasone Furoate 27.5 mcg/dose Nasal Spray (120 doses)", "Fluticasone propionate 125 mcg/dose Evohaler (120doses)", 
    "Fluticasone Propionate 125 mcg/dose Inhalation (120doses)", "Fluvoxamine 50 mg Tablet", "Fluvoxamine 100 mg Tablet", 
    "Folic Acid 5 mg Tablet", "Frusemide 10mg/ml Injection (20mg/2ml)", "Frusemide 40 mg Tablet", "Fusidic Acid 2% Cream", 
    "Fusidic Acid 1% Eye Drops", "Fusidic Acid 2% in Betamethasone Valerate 0.1% Cream", "Gabapentin 300 mg Capsule", 
    "Gabapentin 600 mg Tablet", "Gamma Benzene Hexachloride 0.1 % Lotion", "Gamma Benzene Hexachloride 1% Lotion", 
    "Gemfibrozil 300 mg Capsule", "Glibenclamide 5 mg Tablet", "Gliclazide 30 mg MODIFIED RELEASE Tablet", 
    "Gliclazide 60 mg MODIFIED RELEASE Tablet", "Gliclazide 80 mg Tablet", "Glycerin (Liquid)", "Glycerine 25% in Aqueous Cream", 
    "Glycerin 25%, Sodium Chloride 15% Enema (Ravin)", "Glyceryl Trinitrate 0.5 mg Tablet", 
    "Glycopyrronium 50mcg Inhalation Powder Hard Capsules", "Griseofulvin 125mg Tablet", "Haloperidol 1.5 mg Tablet", 
    "Haloperidol 5mg Tablet", "Hepatitis B 10mcg HbsAg Vaccine (Pediatric)", "Hepatitis B 20mcg HbsAg Vaccine (Adult)", 
    "Hydrochlorothiazide 25 mg Tablet", "Hydrochlorothiazide 50 mg Tablet", "Hydrocortisone 1% Cream", "Hydrocortisone 10 mg Tablet", 
    "Hydrocortisone Sodium Succinate 100mg Injection", "Hydrogen Peroxide 5 volume (1.5%) Mouthwash", "Hydrogen Peroxide 20 volume Solution (6%)", 
    "Hydrogen Peroxide 130 Volume Liquid", "Hydroxychloroquine 200 mg Tablet (UNIQUIN)", "Hydroxychloroquine 200 mg Tablet (PLAQUENIL)", 
    "Hydroxychloroquine Sulphate 200 mg Film Coated Tablet", "Hydroxyurea 500 mg Capsule", "Hyoscine N-Butylbromide 1 mg/ml Liquid", 
    "Hyoscine N-Butylbromide 10 mg Tablet", "Hyoscine N-Butylbromide 20mg/ml Injection", "Hypromellose 0.3% Eye Drop (Preservative Free)", 
    "Hypromellose 0.3% Eye Drops (with preservative)", "Ibuprofen 200 mg Tablet", "Imatinib Mesylate 400 mg Tablet", 
    "Indacaterol maleate 150mcg Inhalation Capsule", "Indacaterol Maleate 110mcg & Glycopyrronium Bromide 50mcg Inhalation", 
    "Indomethacin 25 mg Capsule", "Industrial Methylated Spirit (96%) BP - IMS", "Insulin aspart (Novorapid) 100 IU/ml FlexPen", 
    "Insulin aspart 30%/aspart protamine 70%(NovoMix-30) 100 IU/ml FlexPen", "Insulin detemir (Levemir) 100 IU/ml FlexPen", 
    "Insulin glargine (Basalog One) 100 IU/ml Prefilled Pen", "Insulin glargine (Lantus) 100 IU/ml Pre-filled Pen", 
    "Insulin isophane (Insulatard) 100 IU/mL Penfill", "Insulin isophane (Insuman Basal) 100 IU/mL Penfill", 
    "Insulin lispro 25% /lispro protamin 75%(Humalog Mix-25) 100 IU/mL Penfill", "Insulin lispro 50% /lispro protamin 50%(Humalog Mix-50) 100 IU/mL Penfill", 
    "Insulin Recombinant Neutral Human Short-acting (Insugen-R) 100 IU/mL Penfill", 
    "Insulin Recombinant Neutral Synthetic Human Short-acting (Diabulyn-R) 100 IU/mL Penfill", 
    "Insulin Recombinant Synthetic Human, Intermediate-Acting (Insugen-N) 100 IU/mL Penfill", 
    "Insulin Recombinant Synthetic Human, Intermediate-Acting (Diabulyn-N) 100 IU/mL Penfill", 
    "Insulin Recombinant Synthetic Human, Premixed (Insugen-30/70) 100 IU/mL Penfill", 
    "Insulin Recombinant Synthetic Human, Premixed (Diabulyn-30/70) 100 IU/mL Penfill", "Insulin regular (Actrapid) 100 IU/mL Penfill", 
    "Insulin regular/isophane (Humulin 30/70) 100 IU/mL Penfill", "Insulin regular/isophane (Insuman Comb) 100 IU/mL Penfill", 
    "Insulin regular/isophane (Mixtard-30) 100 IU/mL Penfill", "Ipratropium Br 20 mcg Fenoterol 50 mcg/dose Inhalation", 
    "Ipratropium Bromide 0.025% Nebulising Soln (UDV)", "Irbesartan 150 mg Tablet", "Irbesartan 300 mg Tablet", 
    "Iron Dextran 50mg/ml Injection", "Isoniazid 100 mg Tablet", "Isosorbide Dinitrate 10 mg Tablet", "Isosorbide-5-Mononitrate 60 mg SR Tablet", 
    "Itraconazole 100 mg Capsule", "Ivabradine 5 mg Tablet", "Ketoprofen 2.5% Gel", "Ketorolac Tromethamine 0.5% Eye drops", 
    "Labetalol HCl 100 mg Tablet", "Labetalol HCl 200 mg Tablet", "Lactulose 3.35 g/5 ml Liquid", "Lamivudine 150 mg Tablet", 
    "Lamotrigine 50 mg Tablet", "Lamotrigine 100 mg Tablet", "Latanoprost 0.005% Eye Drops", "Leflunomide 10 mg Tablet", 
    "Leflunomide 20 mg Tablet", "Letrozole 2.5 mg Tablet", "Levetiracetam 500 mg Tablet", "Levodopa 200 mg, Benserazide 50 mg Tablet", 
    "Levodopa 100 mg, Carbidopa 25 mg + Entacapone 200 mg Tablet", "Levothyroxine Sodium 25 mcg Tablet", 
    "Levothyroxine Sodium 50 mcg Tablet", "Levothyroxine Sodium 100 mcg Tablet", "Lidocaine 2.5%-Chlorhexidine 0.5%-Triamcinolone 0.1% Gel/Lotion", 
    "Lignocaine 2% Jelly", "LIGNOcaine HCl (Lidocaine) 2% Injection (10ml)", "Liquid Paraffin", "Lithium Carbonate 300 mg Tablet", 
    "Lopinavir 200 mg and Ritonavir 50 mg Tablet", "Loratadine 1 mg/ml Syrup", "Loratadine 10 mg Tablet", "Lorazepam 1 mg Tablet", 
    "Losartan 50 mg Tablet (LOSAGEN)", "Losartan 50 mg Tablet", "Losartan 100 mg Tablet (LOSAGEN)", "Losartan 100 mg Tablet", 
    "Magnesium Sulphate 50% Injection", "Magnesium Trisilicate Mixture", "Magnesium Trisilicate Tablet", "Measles, Mumps Rubella Vaccine Live", 
    "Measles Rubella Virus Vaccine Live, Attenuated (10 Doses)", "Mecobalamin 500 mcg Tablet", 
    "Meclozine HCl 25 mg and Pyridoxine 50 mg Tablet", "Medroxyprogesterone Acetate 5 mg Tablet", "Mefenamic Acid 250 mg Capsule", 
    "Memantine HCI 10 mg Tablet", "Meningococcal ACYW 135 Vaccine (10 doses)", "Metformin HCl 500 mg Tablet", 
    "Metformin HCl 500 mg EXTENDED RELEASE Tablet", "Metformin HCl 750mg EXTENDED RELEASE Tablet", 
    "Metformin 500 mg and Glibenclamide 2.5 mg Tablet", "Metformin 500 mg and Glibenclamide 5 mg Tablet", "Methadone 5mg/ml Syrup", 
    "Methotrexate 2.5 mg Tablet", "Methyldopa 250 mg Tablet", "Methylphenidate HCl 10 mg Tablet", "Methyl Salicylate 25% Ointment", 
    "Metoclopramide HCl 10 mg Tablet", "Metoclopramide HCl 10mg/2ml Injection", "Metoprolol Tartrate 100 mg Tablet", 
    "Metronidazole 200 mg Tablet", "Miconazole 2% Cream", "Midazolam 5 mg/ml Injection", "Mirabegron 50 mg PROLONGED RELEASE Tablet", 
    "Mirtazapine 15 mg Orodispersible Tablet", "Mirtazapine 30 mg Orodispersible Tablet", "Mometasone Furoate 0.1% Cream", 
    "Mometasone Furoate 50 mcg Aqueous Nasal Spray (Axcel)", "Mometasone Furoate 50 mcg Aqueous Nasal Spray", 
    "Montelukast Sodium 10 mg Tablet", "Morphine HCl 10 mg/5 ml Solution", "Morphine Sulphate 10 mg/ml Injection", 
    "Multivitamin Drops for Infant/Paediatric", "Multivitamin Syrup", "Mupirocin 2% Ointment", "Mycophenolate Mofetil 500 mg tablet (MYCOFIT)", 
    "Naltrexone HCl 50 mg Tablet", "Neomycin 0.5% Cream", "Nepafenac 0.1% w/v Eye Suspension", "Nevirapine 200 mg Tablet", 
    "Nicotine 10 mg/ 16 hour Transdermal Patch", "Nicotine 15 mg/ 16 hour Transdermal Patch", "Nicotine 2 mg Gum", "Nicotine 4 mg Gum", 
    "Nifedipine 10 mg Tablet", "Nystatin 100,000 units/ml Suspension", "Nystatin 100,000 units/g Cream", "Olanzapine 5 mg Tablet", 
    "Olanzapine 10 mg Tablet", "Olanzapine 10 mg DISINTEGRATING Tablet", "Olopatadine HCl 0.2% Opthalmic Solution", 
    "Omeprazole 20 mg Capsule", "Oral Rehydration Salt", "Oseltamivir 75 mg Capsule", "Oxytocin 5U + Ergometrine 0.5mg/ml Inj", 
    "Oxytocin 10 units/ml Injection", "Paliperidone 75 mg Prolonged Release Injection", "Paliperidone 150 mg Prolonged Release Injection", 
    "Paliperidone 6 mg EXTENDED RELEASE Tablet", "Pantoprazole 40 mg Tablet", "Pantoprazole 40mg Injection", "Paracetamol 120 mg/5 ml Syrup", 
    "Paracetamol 250 mg/5 ml Syrup", "Paracetamol 125 mg Suppository", "Paracetamol 250 mg Suppository", "Paracetamol 500 mg Tablet", 
    "Perindopril 4 mg Tablet", "Perindopril 8 mg Tablet", "Perindopril 4 mg and Indapamide 1.25 mg Tablet", 
    "Perindopril 10mg and Indapamide 2.5mg Film Coated tablet", "Permethrin 1% w/v Lotion", "Permethrin 5% w/v Lotion", 
    "Pethidine HCl 50 mg/ml Injection", "Phenobarbitone 30 mg Tablet", "Phenoxymethyl Penicillin 125 mg Tablet", 
    "Phen phenytoin Sodium 100 mg Capsule", "Pine Tar 1%, Coal Tar 1%, Salicylic Acid 2% Shampoo (Sebitar)", "Piracetam 1.2 g Tablet", 
    "Potassium Chloride 600 mg SR Tablet", "Potassium Chloride 1g/10ml Injection", "Potassium Chloride 1gm/10ml Mixture", 
    "Potassium Chloride powder", "Potassium Citrate 3g/10ml Mixture BPC", "Potassium Permanganate 0.1% Solution", 
    "Potassium Permanganate 1 in 1000 Solution", "Potassium Permanganate Crystal", "Povidone Iodine 10% Solution", "Prazosin HCl 1 mg Tablet", 
    "Prazosin HCl 2 mg Tablet", "Prazosin HCl 5 mg Tablet", "Pre/Post-Natal (Zincofer) Vitamin and Mineral Capsule", "Prednisolone 1 mg Tablet", 
    "Prednisolone 5 mg Tablet", "Pregabalin 75 mg Capsule", "Pregabalin 150 mg Capsules", "Probenecid 500 mg Tablet", 
    "Prochlorperazine Maleate 5mg Tablet", "Prochlorperazine Mesylate 12.5 mg/ml Injection", "Prolase Tablet", 
    "Promethazine HCl 5 mg/5 ml Syrup", "Propiverine HCl 15 mg Tablet", "Propranolol HCl 40 mg Tablet", "Propylthiouracil 50 mg Tablet", 
    "Pyrazinamide 500 mg Tablet", "Pyridoxine HCl 10 mg Tablet", "Quetiapine Fumarate 50 mg EXTENDED RELEASE Tablet", 
    "Quetiapine Fumarate 100mg IR Tablet", "Quetiapine Fumarate 200mg IR Tablet", "Quetiapine Fumarate 200 mg EXTENDED RELEASE Tablet", 
    "Quetiapine Fumarate 300 mg EXTENDED RELEASE Tablet", "Quetiapine Fumarate 400 mg EXTENDED RELEASE Tablet", 
    "Ravidasvir Hydrochloride 200mg Tablet", "Rifampicin 150 mg Capsule", "Rifampicin 300 mg Capsule", 
    "Rifampicin 150mg + Isoniazid 75mg Tablet (Akurit-2)", "Rifampicin/Isoniazid/Pyrazinamide/Ethambutol (Akurit-4) Tab", "Risperidone 1 mg Tablet", 
    "Risperidone 2 mg Tablet", "Rosuvastatin 20 mg Tablet", "Sacubitril 49mg, Valsartan 51mg Tablet", "Salbutamol 2 mg Tablet", 
    "Salbutamol 2 mg/5 ml Syrup", "Salbutamol 100 mcg/dose Inhaler (200 doses)", "Salbutamol 0.5 % Nebulising Solution", 
    "Salicylazosulphapyridine (Sulfasalazine) 500 mg Tablet", "Salicylic Acid 2% Ointment", "Salicylic Acid 5% Ointment", 
    "Salicylic Acid 10% Ointment", "Salicylic Acid 20% Ointment", "Salicylic acid, Sulphur and Liquid Coal Tar Ointment", 
    "Salmeterol 25mcg, Fluticasone Propionate 125mcg Evohaler", "Salmeterol 50mcg, Fluticasone Propionate 250mcg Accuhaler", 
    "Salmeterol 50mcg, Fluticasone Propionate 500mcg Accuhaler", "Saxagliptin 5 mg Tablet", "Selegiline HCl 5 mg Tablet", 
    "Sertraline HCI 50 mg Tablet", "Silver Sulfadiazine 1% Cream", "Simvastatin 10 mg Tablet", "Simvastatin 40 mg Tablet", 
    "Sodium Bicarbonate Powder BP/USP", "Sodium Bicarbonate Oral Powder", "Sodium Bicarbonate 5% Ear Drops (10ml)", 
    "Sodium Bicarbonate 5% Bulk Solution for Ear Drop", "Sodium Bicarbonate, Citric Acid, Sodium Citrate, Tartaric Acid Sachet", 
    "Sodium Chloride 0.9% 500mL IV soln", "Sodium Chloride 0.9% 500mL Irrigation Soln", "Sodium Chloride 0.45% 500mL IV soln", 
    "Sodium Chloride 0.9% Nasal Drops", "Sodium Chloride 0.9% Eye Drops", "Sodium Chloride 0.9% with Dextrose 5% 500mL IV soln", 
    "Sodium Chloride 0.18% with Dextrose 4.23% 500mL IV soln", "Sodium Chloride BP (Powder)", "Sodium Lactate Compound 500mL IV soln", 
    "Sodium Valproate 200 mg Tablet", "Sodium Valproate 200 mg/5 ml Syrup (EPILIM)", "Sodium Valproate 200 mg/5 ml Syrup (HOVID)", 
    "Sodium Valproate 200 mg/5 ml Syrup (Standard)", "Sofosbuvir 400 mg Tablet", "Sofosbuvir 400mg Film-Coated Tablets", 
    "Solifenacin Succinate 5mg Tablet/Capsule", "Spironolactone 25 mg Tablet", "Sterile Water for Injection 10mL", 
    "Sulphamethoxazole 200 mg & Trimethoprim 40 mg/5ml Susp", "Sulphamethoxazole 400 mg + Trimethoprim 80 mg Tablet", 
    "Sumatriptan 50 mg Tablet", "Sunscreen SPF 50+ Lotion/ Cream", "Syrup BP / Simple Syrup", "Tamoxifen Citrate 20 mg Tablet", 
    "Tamsulosin HCl 400 mcg EXTENDED RELEASE Tablet", "Telmisartan 40 mg Tablet", "Telmisartan 80 mg Tablet", 
    "Telmisartan 80mg + Amlodipine 5mg Tab", "Telmisartan 80mg + Amlodipine 10mg Tab", "Tenofovir Disoproxil Fumarate 300 mg Tablet", 
    "Tenofovir Disoproxil Fumarate 300mg, Emtricitabine 200mg Tab", "Terazosin HCl 2 mg Tablet", "Terazosin HCl 5 mg Tablet", 
    "Terbutaline Sulphate 2.5 mg Tablet", "Terbutaline Sulphate 10 mg/ml Nebulising Solution", "Tetanus Toxoid Injection (10 doses)", 
    "Thalidomide 50 mg Capsule", "Theophylline 125 mg Tablet", "Theophylline 250 mg Long Acting Tablet", "Thiamine Mononitrate 10 mg Tablet", 
    "Tibolone 2.5 mg Tablet", "Ticagrelor 90 mg Tablet", "Ticlopidine HCl 250 mg Tablet", "Timolol Maleate 0.5% Eye Drops", 
    "Timolol Maleate 0.5% Eye Drops, Preservative Free (10 ml)", "Tiotropium 2.5mcg/puff inhalation (Catridge + Inhaler)", 
    "Tiotropium 2.5mcg/puff inhalation (Catridge only)", "Tiotropium 2.5mcg and Olodaterol 2.5mcg inhalation (Catridge only)", 
    "Tiotropium 2.5mcg and Olodaterol 2.5mcg inhalation (Inhaler set)", "Tolterodine Tartrate ER 4 mg Capsule", "Topiramate 100 mg Tablet", 
    "Tramadol HCl 50 mg Capsule/Tablet", "Tranexamic Acid 250 mg Capsule", "Travoprost 0.004% +Timolol 0.5% Eye Drops", "Tretinoin 0.05% Cream", 
    "Triamcinolone Acetonide 0.1% Oral Paste", "Trimetazidine 20 mg Tablet", "Triprolidine 1.25mg and Pseudoephedrine 30mg/5ml Syrup", 
    "Triprolidine HCl 2.5 mg and Pseudoephedrine HCl 60 mg Tablet", "Tropicamide 1% Eye Drops", "Tuberculin PPD 2 TU/0.1ml Dose Inj", 
    "Typhoid Vaccine (20 doses)", "Ursodeoxycholic Acid 250 mg Capsule", "Valproic Acid/Sodium Valproate (ER) 500mg Tablet", 
    "Valsartan 80 mg Tablet", "Valsartan 160 mg Tablet", "Varenicline Tartrate 0.5mg and 1mg Tablet (STARTER PACK)", 
    "Varenicline Tartrate 1 mg Tablet", "Venlafaxine HCl 75 mg EXTENDED RELEASE Capsule", "Venlafaxine HCl 150 mg EXTENDED RELEASE Capsule", 
    "Verapamil 40 mg Tablet", "Vildagliptin 50 mg Tablet", "Vildagliptin 50 mg and Metformin HCl 1000 mg Tablet", 
    "Vitamin B1, B6, B12 Tablet", "Vitamin B Complex Tablet", "Vitamin K1 (Phytomenadione) 1 mg / ml Injection", 
    "Vortioxetine 10 mg Tablet", "Warfarin Sodium 1 mg Tablet", "Warfarin Sodium 2 mg Tablet", "Warfarin Sodium 5 mg Tablet", 
    "White Petroleum Anhydrous Eye Ointment", "White Soft Paraffin BP (White Petroleum Jelly BP)", 
    "Zidovudine 300 mg + Lamivudine 150 mg Tablet", "Zinc Oxide Cream (15%)", "Zinc Oxide Cream BP (32% w/w)", "Zolpidem Tartrate 10 mg Tablet", 
    "Zuclopenthixol 20 mg/ml Drops", "Zuclopenthixol Decanoate 200mg/ml Injection"
])

# --- 3. FUNGSI ---
def load_data():
    try:
        df = pd.read_csv(f"{URL_SHEET_CSV}&cache={datetime.now().timestamp()}")
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

def format_tarikh(t_str):
    if not t_str or t_str == "-" or str(t_str).strip() == "" or str(t_str) == "None": return "-"
    try:
        dt = datetime.strptime(str(t_str), "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except: return str(t_str)

def hitung_durasi(tca_u, tca_d):
    if not tca_u or not tca_d or tca_u == "-" or tca_d == "-" or tca_d == "None": return "TIADA DATA"
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
        fmt_blue  = workbook.add_format({'bg_color': '#DDEBF7', 'border': 1, 'align': 'center'})
        fmt_white = workbook.add_format({'bg_color': '#FFFFFF', 'border': 1, 'align': 'center'})
        fmt_header = workbook.add_format({'bg_color': '#4F81BD', 'font_color': 'white', 'bold': True, 'border': 1, 'align': 'center'})
        fmt_ubat_b = workbook.add_format({'bg_color': '#DDEBF7', 'border': 1, 'align': 'left'})
        fmt_ubat_w = workbook.add_format({'bg_color': '#FFFFFF', 'border': 1, 'align': 'left'})
        num_cols = len(df.columns) + 1 
        for row_num in range(len(df) + 1):
            if row_num == 0: worksheet.set_row(row_num, None, fmt_header)
            else:
                is_blue = row_num % 2 == 0
                current_fmt = fmt_blue if is_blue else fmt_white
                ubat_fmt = fmt_ubat_b if is_blue else fmt_ubat_w
                worksheet.set_row(row_num, None, current_fmt)
                worksheet.write(row_num, 0, df.index[row_num-1], ubat_fmt)
        worksheet.set_column(0, 0, 45); worksheet.set_column(1, num_cols, 18)
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
        nama_input = c1.text_input("Nama:", value=st.session_state.input_nama, key="nama_raw").upper().strip()
        st.session_state.input_nama = nama_input
        
        ic_input = c2.text_input("IC:", value=st.session_state.input_ic, key="ic_raw").strip()
        st.session_state.input_ic = ic_input
        
        idx_batch = SENARAI_BATCH.index(st.session_state.pilihan_batch)
        batch = c3.selectbox("Batch:", SENARAI_BATCH, index=idx_batch)
        st.session_state.pilihan_batch = batch 
        
        c4, c5 = st.columns(2)
        t_u = c4.date_input("TCA Ambil Ubat (Hari Ini):", value=date.today())
        t_d = c5.date_input("TCA Klinik (Dr) [Opsional]:", value=None)

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
            if st.session_state.input_nama and st.session_state.input_ic:
                payload = {
                    "Nama": st.session_state.input_nama, 
                    "IC": st.session_state.input_ic, 
                    "TCA_Ubat": str(t_u), 
                    "TCA_Clinic": str(t_d) if t_d else "-", 
                    "Ubat_List": " | ".join([x['u'] for x in st.session_state.bakul]), 
                    "Kuantiti": " | ".join([x['q'] for x in st.session_state.bakul]), 
                    "Batch": batch
                }
                try:
                    with st.spinner("Menghantar..."):
                        resp = requests.post(URL_API, json=payload, timeout=10)
                    if resp.status_code == 200:
                        st.success("✅ Berjaya Disimpan!")
                        st.session_state.input_nama = ""; st.session_state.input_ic = ""; st.session_state.bakul = []
                        time.sleep(1.5); st.rerun()
                    else: st.error("Server Error!")
                except: st.error("Gagal menyambung database!")
            else: st.error("Sila isi Nama dan IC!")

elif menu == "📊 SUMMARY":
    st.header("Checklist & Durasi Bekalan")
    df = load_data()
    if not df.empty:
        idx_batch_s = SENARAI_BATCH.index(st.session_state.pilihan_batch)
        b_sel = st.selectbox("Pilih Batch:", SENARAI_BATCH, index=idx_batch_s)
        st.session_state.pilihan_batch = b_sel 
        df_f = df[df['BATCH'] == b_sel]
        if not df_f.empty:
            res = convert_to_matrix_final(df_f)
            st.dataframe(res, use_container_width=True, height=500)
            excel_data = to_excel_colored(res)
            st.download_button(label="📥 Download Excel", data=excel_data, file_name=f"{b_sel}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else: st.info(f"Tiada data untuk {b_sel}")

import re
from preprocess_dataset import discharge_condition

text = [
"1. Albuterol Inhaler 2 PUFF IH Q4H: PRN wheezing, SOB 2. Emtricitabine-Tenofovir (Truvada) 1 TAB PO DAILY 3. Furosemide 40 mg PO DAILY RX *furosemide 40 mg 1 tablet(s) by mouth Daily Disp #*30 Tablet Refills: *3 4. Ipratropium Bromide Neb 1 NEB IH Q6H SOB 5. Nicotine Patch 14 mg TD DAILY 6. Raltegravir 400 mg PO BID 7. Spironolactone 50 mg PO DAILY 8. Acetaminophen 500 mg PO Q6H: PRN pain", 
"1. Acetaminophen 500 mg PO Q6H: PRN pain,fever 2. Albuterol Inhaler 2 PUFF IH Q6H: PRN wheezing, SOB 3. Calcium Carbonate 1250 mg PO BID 4. ___ (Truvada) 1 TAB PO DAILY 5. Furosemide 40 mg PO DAILY 6. Lactulose 15 mL PO TID 7. Raltegravir 400 mg PO BID 8. Rifaximin 550 mg PO BID 9. Sulfameth/Trimethoprim DS 1 TAB PO DAILY 10. Tiotropium Bromide 1 CAP IH DAILY", 
"1. Omeprazole 20 mg PO BID"
]

text = [
    "1. HCV Cirrhosis 2. No history of abnormal Pap smears. 3. She had calcification in her breast, which was removed previously and per patient not, it was benign. 4. For HIV disease, she is being followed by Dr. ___ Dr. ___. 5. COPD 6. Past history of smoking. 7. She also had a skin lesion, which was biopsied and showed skin cancer per patient report and is scheduled for a complete removal of the skin lesion in ___ of this year. 8. She also had another lesion in her forehead with purple discoloration. It was biopsied to exclude the possibility of ___'s sarcoma, the results is pending. 9. A 15 mm hypoechoic lesion on her ultrasound on ___ and is being monitored by an MRI. 10. History of dysplasia of anus in ___. 11. Bipolar affective disorder, currently manic, mild, and PTSD. 12. History of cocaine and heroin use.",
    "- GERD - Hypercholesterolemia - Kidney stones - Mitral valve prolapse - Uterine fibroids - Osteoporosis - Migraine headaches"]

text = [
    "The Preadmission Medication list is accurate and complete. 1. Furosemide 20 mg PO DAILY 2. Spironolactone 50 mg PO DAILY 3. Albuterol Inhaler 2 PUFF IH Q4H: PRN wheezing, SOB 4. Raltegravir 400 mg PO BID 5. Emtricitabine-Tenofovir (Truvada) 1 TAB PO DAILY 6. Nicotine Patch 14 mg TD DAILY 7. Ipratropium Bromide Neb 1 NEB IH Q6H SOB", 
    "The Preadmission Medication list is accurate and complete. 1. Albuterol Inhaler 2 PUFF IH Q6H: PRN wheezing, SOB 2. ___ (Truvada) 1 TAB PO DAILY 3. Furosemide 20 mg PO DAILY 4. Raltegravir 400 mg PO BID 5. Spironolactone 50 mg PO DAILY 6. Acetaminophen 500 mg PO Q6H: PRN pain,fever 7. Tiotropium Bromide 1 CAP IH DAILY 8. Rifaximin 550 mg PO BID 9. Calcium Carbonate 1250 mg PO BID 10. Lactulose 15 mL PO TID 11. Sulfameth/Trimethoprim DS 1 TAB PO DAILY", 
    "The Preadmission Medication list is accurate and complete. 1. Omeprazole 20 mg PO BID"]

text = ["Mental Status: Clear and coherent. Level of Consciousness: Alert and interactive. Activity Status: Ambulatory - Independent."]


reg = r"Mental Status: |Level of Consciousness: |Activity Status: "

# # for t in text:
# #     tmp = f"{re.split(reg, t)}"
# #     print(type(tmp))
# #     print(tmp)
# tmp = re.split(reg, text[0])
# tmp[0] = re.sub(r"-\s", "", tmp[0])
# print(f"{tmp}")
# print(str(tmp))

# for t in text:
#     print(numbers_to_array(t))
# print(re.split(reg,text[0]))

# tmp = re.split(reg,text[0])[1:]

# print(dict(zip(["Mental Status", "Level of Consciousness", "Activity Status"], [t.strip() for t in tmp])))
# # for k in zip(["Mental Status", "Level of Consciousness", "Activity Status"], [t.strip() for t in tmp]):
# #     print(k)
# print(len(tmp))
print(discharge_condition(text[0]))
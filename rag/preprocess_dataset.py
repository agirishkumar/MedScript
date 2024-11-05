import re

from exceptiongroup import catch
from google.oauth2 import service_account
from constants import ABBREVIATIONS, SECTION_NAMES, MIMIC_DATASET_BUCKET_NAME, SERVICE_ACCOUNT_FILEPATH

import pandas as pd
import json
from io import StringIO
from google.cloud import storage
import os
# from rag.logging import data_logger

# sample_data = [
#     "<SEX> F <SERVICE> MEDICINE <ALLERGIES> No Known Allergies / Adverse Drug Reactions <ATTENDING> ___ <CHIEF COMPLAINT> Worsening ABD distension and pain <MAJOR SURGICAL OR INVASIVE PROCEDURE> Paracentesis <HISTORY OF PRESENT ILLNESS> ___ HCV cirrhosis c/b ascites, hiv on ART, h/o IVDU, COPD, bioplar, PTSD, presented from OSH ED with worsening abd distension over past week. Pt reports self-discontinuing lasix and spirnolactone ___ weeks ago, because she feels like ""they don't do anything"" and that she ""doesn't want to put more chemicals in her."" She does not follow Na-restricted diets. In the past week, she notes that she has been having worsening abd distension and discomfort. She denies ___ edema, or SOB, or orthopnea. She denies f/c/n/v, d/c, dysuria. She had food poisoning a week ago from eating stale cake (n/v 20 min after food ingestion), which resolved the same day. She denies other recent illness or sick contacts. She notes that she has been noticing gum bleeding while brushing her teeth in recent weeks. she denies easy bruising, melena, BRBPR, hemetesis, hemoptysis, or hematuria. Because of her abd pain, she went to OSH ED and was transferred to ___ for further care. Per ED report, pt has brief period of confusion - she did not recall the ultrasound or bloodwork at osh. She denies recent drug use or alcohol use. She denies feeling confused, but reports that she is forgetful at times. In the ED, initial vitals were 98.4 70 106/63 16 97%RA Labs notable for ALT/AST/AP ___ __: ___, Tbili1.6, WBC 5K, platelet 77, INR 1.6 <PAST MEDICAL HISTORY> 1. HCV Cirrhosis 2. No history of abnormal Pap smears. 3. She had calcification in her breast, which was removed previously and per patient not, it was benign. 4. For HIV disease, she is being followed by Dr. ___ Dr. ___. 5. COPD 6. Past history of smoking. 7. She also had a skin lesion, which was biopsied and showed skin cancer per patient report and is scheduled for a complete removal of the skin lesion in ___ of this year. 8. She also had another lesion in her forehead with purple discoloration. It was biopsied to exclude the possibility of ___'s sarcoma, the results is pending. 9. A 15 mm hypoechoic lesion on her ultrasound on ___ and is being monitored by an MRI. 10. History of dysplasia of anus in ___. 11. Bipolar affective disorder, currently manic, mild, and PTSD. 12. History of cocaine and heroin use. <SOCIAL HISTORY> ___ <FAMILY HISTORY> She a total of five siblings, but she is not talking to most of them. She only has one brother that she is in touch with and lives in ___. She is not aware of any known GI or liver disease in her family. Her last alcohol consumption was one drink two months ago. No regular alcohol consumption. Last drug use ___ years ago. She quit smoking a couple of years ago. <PHYSICAL EXAM> VS: 98.1 107/61 78 18 97RA General: in NAD HEENT: CTAB, anicteric sclera, OP clear Neck: supple, no LAD CV: RRR,S1S2, no m/r/g Lungs: CTAb, prolonged expiratory phase, no w/r/r Abdomen: distended, mild diffuse tenderness, +flank dullness, cannot percuss liver/spleen edge ___ distension GU: no foley Ext: wwp, no c/e/e, + clubbing Neuro: AAO3, converse normally, able to recall 3 times after 5 minutes, CN II-XII intact Discharge: PHYSICAL EXAMINATION: VS: 98 105/70 95 General: in NAD HEENT: anicteric sclera, OP clear Neck: supple, no LAD CV: RRR,S1S2, no m/r/g Lungs: CTAb, prolonged expiratory phase, no w/r/r Abdomen: distended but improved, TTP in RUQ, GU: no foley Ext: wwp, no c/e/e, + clubbing Neuro: AAO3, CN II-XII intact <PERTINENT RESULTS> ___ 10: 25PM GLUCOSE-109* UREA N-25* CREAT-0.3* SODIUM-138 POTASSIUM-3.4 CHLORIDE-105 TOTAL CO2-27 ANION GAP-9 ___ 10: 25PM estGFR-Using this ___ 10: 25PM ALT(SGPT)-100* AST(SGOT)-114* ALK PHOS-114* TOT BILI-1.6* ___ 10: 25PM LIPASE-77* ___ 10: 25PM ALBUMIN-3.3* ___ 10: 25PM WBC-5.0# RBC-4.29 HGB-14.3 HCT-42.6 MCV-99* MCH-33.3* MCHC-33.5 RDW-15.7* ___ 10: 25PM NEUTS-70.3* LYMPHS-16.5* MONOS-8.1 EOS-4.2* BASOS-0.8 ___ 10: 25PM PLT COUNT-71* ___ 10: 25PM ___ PTT-30.9 ___ ___ 10: 25PM ___ . CXR: No acute cardiopulmonary process. U/S: 1. Nodular appearance of the liver compatible with cirrhosis. Signs of portal hypertension including small amount of ascites and splenomegaly. 2. Cholelithiasis. 3. Patent portal veins with normal hepatopetal flow. Diagnostic para attempted in the ED, unsuccessful. On the floor, pt c/o abd distension and discomfort. <MEDICATIONS ON ADMISSION> The Preadmission Medication list is accurate and complete. 1. Furosemide 20 mg PO DAILY 2. Spironolactone 50 mg PO DAILY 3. Albuterol Inhaler 2 PUFF IH Q4H: PRN wheezing, SOB 4. Raltegravir 400 mg PO BID 5. Emtricitabine-Tenofovir (Truvada) 1 TAB PO DAILY 6. Nicotine Patch 14 mg TD DAILY 7. Ipratropium Bromide Neb 1 NEB IH Q6H SOB <DISCHARGE MEDICATIONS> 1. Albuterol Inhaler 2 PUFF IH Q4H: PRN wheezing, SOB 2. Emtricitabine-Tenofovir (Truvada) 1 TAB PO DAILY 3. Furosemide 40 mg PO DAILY RX *furosemide 40 mg 1 tablet(s) by mouth Daily Disp #*30 Tablet Refills: *3 4. Ipratropium Bromide Neb 1 NEB IH Q6H SOB 5. Nicotine Patch 14 mg TD DAILY 6. Raltegravir 400 mg PO BID 7. Spironolactone 50 mg PO DAILY 8. Acetaminophen 500 mg PO Q6H: PRN pain <DISCHARGE DISPOSITION> Home <DISCHARGE DIAGNOSIS> Ascites from Portal HTN <DISCHARGE CONDITION> Mental Status: Clear and coherent. Level of Consciousness: Alert and interactive. Activity Status: Ambulatory - Independent. <FOLLOWUP INSTRUCTIONS> ___ <DISCHARGE INSTRUCTIONS> Dear Ms. ___, It was a pleasure taking care of you! You came to us with stomach pain and worsening distension. While you were here we did a paracentesis to remove 1.5L of fluid from your belly. We also placed you on you 40 mg of Lasix and 50 mg of Aldactone to help you urinate the excess fluid still in your belly. As we discussed, everyone has a different dose of lasix required to make them urinate and it's likely that you weren't taking a high enough dose. Please take these medications daily to keep excess fluid off and eat a low salt diet. You will follow up with Dr. ___ in liver clinic and from there have your colonoscopy and EGD scheduled. Of course, we are always here if you need us. We wish you all the best! Your ___ Team. ",
    
#     "<SEX> F <SERVICE> MEDICINE <ALLERGIES> Percocet <ATTENDING> ___. <CHIEF COMPLAINT> abdominal fullness and discomfort <MAJOR SURGICAL OR INVASIVE PROCEDURE> ___ diagnostic paracentesis ___ therapeutic paracentesis <HISTORY OF PRESENT ILLNESS> ___ with HIV on HAART, COPD, HCV cirrhosis complicated by ascites and HE admitted with abdominal distention and pain. She was admitted to ___ for the same symptoms recently and had 3L fluid removed (no SBP) three days ago and felt better. Since discharge, her abdomen has become increasingly distended with pain. This feels similar to prior episodes of ascites. Her diuretics were recently decreased on ___ due to worsening hyponatremia 128 and hyperkalemia 5.1. Patient states she has been compliant with her HIV and diuretic medications but never filled out the lactulose prescription. She states she has had ___ BMs daily at home. She has had some visual hallucinations and forgetfulness. Her appetite has been poor. In the ED, initial vitals were 98.9 88 116/88 18 97% RA. CBC near baseline, INR 1.4, Na 125, Cr 0.6. AST and ALT mildly above baseline 182 and 126 and albumin 2.8. Diagnostic para with 225 WBC, 7% PMN, total protein 0.3. UA with few bact, 6 WBC, mod leuk, neg nitr, but contaminated with 6 epi. CXR clear. RUQ US with no PV thrombus, moderate ascites. She was given ondansetron 4mg IV and morphine 2.5mg IV x1 in the ED. On the floor, she is feeling improved but still has abdominal distention and discomfort. ROS: +Abdominal distention and pain. No black/bloody stools. No ___ pain or swelling. No fevers or chills. Denies chest pain, nausea, vomiting. No dysuria or frequency. <PAST MEDICAL HISTORY> 1. HCV Cirrhosis 2. No history of abnormal Pap smears. 3. She had calcification in her breast, which was removed previously and per patient not, it was benign. 4. For HIV disease, she is being followed by Dr. ___ Dr. ___. 5. COPD 6. Past history of smoking. 7. She also had a skin lesion, which was biopsied and showed skin cancer per patient report and is scheduled for a complete removal of the skin lesion in ___ of this year. 8. She also had another lesion in her forehead with purple discoloration. It was biopsied to exclude the possibility of ___'s sarcoma, the results is pending. 9. A 15 mm hypoechoic lesion on her ultrasound on ___ and is being monitored by an MRI. 10. History of dysplasia of anus in ___. 11. Bipolar affective disorder, currently manic, mild, and PTSD. 12. History of cocaine and heroin use. <SOCIAL HISTORY> ___ <FAMILY HISTORY> She a total of five siblings, but she is not talking to most of them. She only has one brother that she is in touch with and lives in ___. She is not aware of any known GI or liver disease in her family. <PHYSICAL EXAM> ADMISSION PHYSICAL EXAM: VS: T98.1 105/57 79 20 97RA 44.6kg GENERAL: Thin chronically ill appearing woman in no acute distress HEENT: Sclera anicteric, MMM, no oral lesions HEART: RRR, normal S1 S2, no murmurs LUNGS: Clear, no wheezes, rales, or rhonchi ABD: Significant distention with visible veins, bulging flanks, nontender to palpation, tympanitic on percussion, normal bowel sounds EXT: no ___ edema, 2+ DP and ___ pulses NEURO: alert and oriented, not confused, no asterixis DISCHARGE PE: VS: T 98.4 BP 95/55 (SBP ___ HR 80 RR 18 O2 95RA I/O 240/150 this am GENERAL: Thin chronically ill appearing woman in no acute distress HEENT: Sclera anicteric, MMM, no oral lesions HEART: RRR, normal S1 S2, no murmurs LUNGS: Clear, no wheezes, rales, or rhonchi ABD: Significant distention with visible veins, bulging flanks, nontender to palpation, tympanitic on percussion, normal bowel sounds EXT: no ___ edema, 2+ DP and ___ pulses NEURO: alert and oriented, not confused, no asterixis <PERTINENT RESULTS> LABS ON ADMISSION: ___ 04: 10PM BLOOD ___ ___ Plt ___ ___ 04: 10PM BLOOD ___ ___ ___ 04: 10PM BLOOD ___ ___ ___ 04: 10PM BLOOD ___ ___ ___ 04: 10PM BLOOD ___ ___ 04: 39PM BLOOD ___ LABS ON DISCHARGE: ___ 05: 10AM BLOOD ___ ___ Plt ___ ___ 05: 10AM BLOOD ___ ___ ___ 05: 10AM BLOOD ___ ___ ___ 05: 10AM BLOOD ___ ___ ___ 05: 10AM BLOOD ___ MICRO: ___ 10: 39 pm URINE Source: ___. **FINAL REPORT ___ URINE CULTURE (Final ___: MIXED BACTERIAL FLORA ( >= 3 COLONY TYPES), CONSISTENT WITH SKIN AND/OR GENITAL CONTAMINATION. ___ 7: 00 pm PERITONEAL FLUID PERITONEAL FLUID. GRAM STAIN (Final ___: 1+ (<1 per 1000X FIELD): POLYMORPHONUCLEAR LEUKOCYTES. NO MICROORGANISMS SEEN. This is a concentrated smear made by cytospin method, please refer to hematology for a quantitative white blood cell count.. FLUID CULTURE (Final ___: NO GROWTH. ANAEROBIC CULTURE (Preliminary): NO GROWTH. ___ 7: 00 pm PERITONEAL FLUID PERITONEAL FLUID. GRAM STAIN (Final ___: 1+ (<1 per 1000X FIELD): POLYMORPHONUCLEAR LEUKOCYTES. NO MICROORGANISMS SEEN. This is a concentrated smear made by cytospin method, please refer to hematology for a quantitative white blood cell count.. FLUID CULTURE (Final ___: NO GROWTH. ANAEROBIC CULTURE (Preliminary): NO GROWTH. Diagnositc Para: ___ 07: 00PM ASCITES ___ ___ ___ 07: 00PM ASCITES ___ IMAGING: ___ CXR- No acute cardiopulmonary abnormality. ___ RUQ US- 1. Extremely coarse and nodular liver echotexture consistent with a history of cirrhosis. 2. Moderate ascites. 3. Patent portal vein. <MEDICATIONS ON ADMISSION> The Preadmission Medication list is accurate and complete. 1. Albuterol Inhaler 2 PUFF IH Q6H: PRN wheezing, SOB 2. ___ (Truvada) 1 TAB PO DAILY 3. Furosemide 20 mg PO DAILY 4. Raltegravir 400 mg PO BID 5. Spironolactone 50 mg PO DAILY 6. Acetaminophen 500 mg PO Q6H: PRN pain,fever 7. Tiotropium Bromide 1 CAP IH DAILY 8. Rifaximin 550 mg PO BID 9. Calcium Carbonate 1250 mg PO BID 10. Lactulose 15 mL PO TID 11. Sulfameth/Trimethoprim DS 1 TAB PO DAILY <DISCHARGE MEDICATIONS> 1. Acetaminophen 500 mg PO Q6H: PRN pain,fever 2. Albuterol Inhaler 2 PUFF IH Q6H: PRN wheezing, SOB 3. Calcium Carbonate 1250 mg PO BID 4. ___ (Truvada) 1 TAB PO DAILY 5. Furosemide 40 mg PO DAILY 6. Lactulose 15 mL PO TID 7. Raltegravir 400 mg PO BID 8. Rifaximin 550 mg PO BID 9. Sulfameth/Trimethoprim DS 1 TAB PO DAILY 10. Tiotropium Bromide 1 CAP IH DAILY <DISCHARGE DISPOSITION> Home <DISCHARGE DIAGNOSIS> Primary: diuretic refractory ascites Secondary: HCV cirrhosis, HIV, hyponatremia, COPD <DISCHARGE CONDITION> Mental Status: Clear and coherent. Level of Consciousness: Alert and interactive. Activity Status: Ambulatory - Independent. <FOLLOWUP INSTRUCTIONS> ___ <DISCHARGE INSTRUCTIONS> Dear ___, ___ was a pleasure to take care of you at ___ ___. You were admitted with abdominal fullness and pain from your ascites. You had a diagnostic and therapeutic paracentesis with 4.3 L removed. Your spironolactone was discontinued because your potassium was high. Your lasix was increased to 40mg daily. You are scheduled for another paracentesis on ___ prior to your other appointments that day. Please call tomorrow to find out the time of the paracentesis. Please continue to follow a low sodium diet and fluid restriction. You should call your liver doctor or return to the emergency room if you have abdominal pain, fever, chills, confusion, or other concerning symptoms. Sincerely, Your ___ medical team", 
               
#     "<SEX> F <SERVICE> MEDICINE <ALLERGIES> omeprazole <ATTENDING> ___. <CHIEF COMPLAINT> dysphagia <MAJOR SURGICAL OR INVASIVE PROCEDURE> Upper endoscopy ___ <HISTORY OF PRESENT ILLNESS> ___ w/ anxiety and several years of dysphagia who p/w worsened foreign body sensation. She describes feeling as though food gets stuck in her neck when she eats. She put herself on a pureed diet to address this over the last 10 days. When she has food stuck in the throat, she almost feels as though she cannot breath, but she denies trouble breathing at any other time. She does not have any history of food allergies or skin rashes. In the ED, initial vitals: 97.6 81 148/83 16 100% RA Imaging showed: CXR showed a prominent esophagus Consults: GI was consulted. Pt underwent EGD which showed a normal appearing esophagus. Biopsies were taken. Currently, she endorses anxiety about eating. She would like to try eating here prior to leaving the hospital. <PAST MEDICAL HISTORY> - GERD - Hypercholesterolemia - Kidney stones - Mitral valve prolapse - Uterine fibroids - Osteoporosis - Migraine headaches <SOCIAL HISTORY> ___ <FAMILY HISTORY> + HTN - father + Dementia - father <PHYSICAL EXAM> - ADMISSION/DISCHARGE EXAM - VS: 97.9 PO 109 / 71 70 16 97 ra GEN: Thin anxious woman, lying in bed, no acute distress HEENT: Moist MM, anicteric sclerae, NCAT, PERRL, EOMI NECK: Supple without LAD, no JVD PULM: CTABL no w/c/r COR: RRR (+)S1/S2 no m/r/g ABD: Soft, non-tender, non-distended, +BS, no HSM EXTREM: Warm, well-perfused, no ___ edema NEURO: CN II-XII grossly intact, motor function grossly normal, sensation grossly intact <PERTINENT RESULTS> - ADMISSION LABS - ___ 08: 27AM BLOOD WBC-5.0 RBC-4.82 Hgb-14.9 Hct-44.4 MCV-92 MCH-30.9 MCHC-33.6 RDW-12.1 RDWSD-41.3 Plt ___ ___ 08: 27AM BLOOD ___ PTT-28.6 ___ ___ 08: 27AM BLOOD Glucose-85 UreaN-8 Creat-0.9 Na-142 K-3.6 Cl-104 HCO3-22 AnGap-20 ___ 08: 27AM BLOOD ALT-11 AST-16 LD(LDH)-154 AlkPhos-63 TotBili-1.0 ___ 08: 27AM BLOOD Albumin-4.8 - IMAGING - CXR ___: IMPRESSION: Prominent esophagus on lateral view, without air-fluid level. Given the patient's history and radiographic appearance, barium swallow is indicated either now or electively. NECK X-ray ___: IMPRESSION: Within the limitation of plain radiography, no evidence of prevertebral soft tissue swelling or soft tissue mass in the neck. EGD: ___ Impression: Hiatal hernia Angioectasia in the stomach Angioectasia in the duodenum (biopsy, biopsy) Otherwise normal EGD to third part of the duodenum Recommendations: - no obvious anatomic cause for the patient's symptoms - follow-up biopsy results to rule out eosinophilic esophagitis - follow-up with Dr. ___ if biopsies show eosinophilic esophagitis <MEDICATIONS ON ADMISSION> The Preadmission Medication list is accurate and complete. 1. Omeprazole 20 mg PO BID <DISCHARGE MEDICATIONS> 1. Omeprazole 20 mg PO BID <DISCHARGE DISPOSITION> Home <DISCHARGE DIAGNOSIS> PRIMARY DIAGNOSIS: -dysphagia and foreign body sensation SECONDARY DIAGNOSIS: -GERD <DISCHARGE CONDITION> Mental Status: Clear and coherent. Level of Consciousness: Alert and interactive. Activity Status: Ambulatory - Independent. <FOLLOWUP INSTRUCTIONS> ___ <DISCHARGE INSTRUCTIONS> Dear Ms. ___, You were hospitalized at ___. You came in due to difficulty swallowing. You had an endoscopy to look for any abnormalities in the esophagus. Thankfully, this was normal. They took biopsies, and you will be called with the results. You should have a test called a barium swallow as an outpatient. We wish you all the best! -Your ___ Team"]

MAX_CHUNK_SIZE = 2500  # Define the number of keys per chunk

def get_section_names(dataset):
    """
    Extracts section names from a dataset
    Removes SOCIAL HISTORY and ATTENDING sections
    Args:
        dataset (list): list of strings

    Returns:
        list: list of section names
    """
    section_names = set()
    for text in dataset:
        names = re.findall("<([\w{2,}\s]+)>", text)
        section_names.update(names)

    try:
        section_names.remove('ATTENDING')
        section_names.remove('SOCIAL HISTORY')
    except KeyError as e:
        data_logger.warning(f"Section not found for removal: {e}")
    
    section_names = list(section_names)
    section_names = [tag.upper() for tag in section_names]
    section_names.sort()
    return section_names

def segment_by_sections(text, section_names):
    """
    Segments a medical record into structured sections for easier processing and retrieval.
    """
    sections = {name: "None" for name in section_names}

    for tag in sections.keys():
        try:
            pattern = f"<{tag.upper().replace('_', ' ')}> (.+?)(?=\s*<|$)"
            match = re.search(pattern, text, re.DOTALL)
            if match:
                sections[tag] = match.group(1).strip()
        except Exception as e:
            data_logger.warning(f"Could not segment medical record {tag}: {e}")

    return sections

def remove_irrelevant_information(text):
    """
    Removes placeholders and standardizes common abbreviations.
    """
    # text = re.sub(r'<[A-Z_]+>', '', text)  # Remove placeholders like <___>
    try:
        for k, v in ABBREVIATIONS.items():
            text = text.replace(k, v)
        return text
    except Exception as e:
        data_logger.warning(f"Could not remove irrelevant information: {e}")

# def normalize_text(text):
#     """
#     Normalizes text by lowercasing and correcting basic spelling.
#     """
#     text = text.lower()
#     # Additional spelling correction logic could go here
#     return text

# # def standardize_vital_signs(text):
#     """
#     Standardizes the format of vital signs and lab values.
#     """
#     # Standardize temperature, blood pressure, etc. Example patterns:
#     text = re.sub(r'(\d+(\.\d+)?) F', r'\1°F', text)
#     text = re.sub(r'(\d{2,3})/(\d{2,3})', r'\1/\2 mmHg', text)
#     return text

def replace_blanks(text):
    # print("Replace Blanks type: ", type(text))
    # print(text)
    try:
        if text is not None:
            text = re.sub(r"_+", "", text)
            text = text.strip()
        return text
    except Exception as e:
        data_logger.warning(f"Could not remove blanks: {e}")

def numbers_to_array(text):
    reg = r"\d+\.\s"
    text = re.split(reg, text)

    # if no numbers detected retain the text
    if len(text) == 1:
        text = text[0]
        no_numbers = True
    else:
        text = text[1:]
        text = [t.strip() for t in text]
        no_numbers = False

    text = str(text) #f"{text}"

    return text, no_numbers

def ordered_list_to_string(text):
    text, no_numbers = numbers_to_array(text)
    if no_numbers:
        reg = r"\s\-\s"
        text = re.split(reg, text)
        text[0] = re.sub(r"-\s", "", text[0])
        text = str(text)
    data_logger.debug("Ordered list converted to string")
    return text


def sex(text):
    # print("Sex type: ", type(text))
    # print(text)
    if text.lower() == 'f':
        text = 'female'
    elif text.lower() == 'm':
        text = 'male'
    return text

def discharge_condition(text):
    # print("discharge_condition: ", type(text))
    # print(text)
    if text is None: return None
    reg = r"Mental Status: |Level of Consciousness: |Activity Status: "

    tmp = re.split(reg, text)

    if len(tmp) != 4:
        return text
    else:
        text = tmp[1:]
        text = dict(zip(["Mental Status", "Level of Consciousness", "Activity Status"], [t.strip() for t in text]))
        return text

def no_change(text):
    return text

def preprocess(text, section_names):
    text = remove_irrelevant_information(text)

    sections = segment_by_sections(text, section_names)

    # print("\n-------------------------------- Section --------------------------------")
    # print(sections)
    function_dict = {
        "DISCHARGE INSTRUCTIONS": [no_change],
        "PERTINENT RESULTS": [replace_blanks],
        "CHIEF COMPLAINT": [replace_blanks],
        "SERVICE": [replace_blanks],
        "MAJOR SURGICAL OR INVASIVE PROCEDURE": [replace_blanks],
        "FAMILY HISTORY": [replace_blanks],
        "MEDICATIONS ON ADMISSION": [ordered_list_to_string, replace_blanks],
        "HISTORY OF PRESENT ILLNESS": [no_change, replace_blanks],
        "PHYSICAL EXAM": [no_change, replace_blanks],
        "DISCHARGE MEDICATIONS": [replace_blanks, ordered_list_to_string],
        "FOLLOWUP INSTRUCTIONS": [replace_blanks],
        "DISCHARGE DISPOSITION": [replace_blanks],
        "DISCHARGE CONDITION": [replace_blanks, discharge_condition],
        "ALLERGIES": [replace_blanks],
        "DISCHARGE DIAGNOSIS": [replace_blanks],
        "SEX": [sex],
        "PAST MEDICAL HISTORY": [replace_blanks, ordered_list_to_string]
    }

    output_dict = {}

    for section_name, section_value in sections.items():
        try:
            # print(f"____{section_name}______")
            if section_name in function_dict:
                result = section_value
                for func in function_dict[section_name]:
                    result = func(result)
                output_dict[section_name] = result

                if section_name == "FOLLOWUP INSTRUCTIONS" and len(result)==0:
                    output_dict[section_name] = "None"
                # output_dict[section_name] = function_dict[section_name](section_value)
            else:
                output_dict[section_name] = 'Function not defined'
        except Exception as e:
            data_logger.warning(f"Could not preprocess {section_name}: {e}")

    return output_dict

def flatten_dict(d, parent_key='', sep='.'):
    """
    Flatten a nested dictionary.
    """
    items = []
    for k, v in d.items():
        try:
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        except Exception as e:
            data_logger.warning(f"Could not flatten {k}: {e}")
    return dict(items)

def chunk_json_string(flattened_data, max_chunk_size):
    """
    Chunk the flattened dictionary into JSON string chunks, each within max_chunk_size limit.
    """
    chunks = []
    current_chunk = {}
    current_chunk_size = 0

    # Go through each key-value pair in the flattened dictionary
    for key, value in flattened_data.items():
        # Prepare a tentative chunk with the new key-value pair added
        tentative_chunk = current_chunk.copy()
        tentative_chunk[key] = value
        
        # Convert tentative chunk to JSON string to check its size
        tentative_chunk_string = json.dumps(tentative_chunk)
        tentative_chunk_size = len(tentative_chunk_string)

        # Check if adding this key-value pair exceeds the max chunk size
        if tentative_chunk_size > max_chunk_size:
            # If it exceeds, finalize the current chunk and start a new one
            chunks.append(json.dumps(current_chunk))
            current_chunk = {key: value}  # Start new chunk with the current pair
            current_chunk_size = len(json.dumps(current_chunk))
        else:
            # If it doesn't exceed, update current chunk and size
            current_chunk[key] = value
            current_chunk_size = tentative_chunk_size

    # Add the final chunk
    if current_chunk:
        chunks.append(json.dumps(current_chunk))

    return chunks

def transform_text(text, section_names, chunk_size=MAX_CHUNK_SIZE):
    """
    Preprocess the text, flattens dictionary and converts it into chunks
    Args:
        text (string): Medical Input
        section_names (set): Names of tags in the input
        chunk_size (int, optional): Defaults to MAX_CHUNK_SIZE.

    Returns:
        list: List of chunks
    """
    preprocessed_text = preprocess(text, section_names)
    flattened_data = flatten_dict(preprocessed_text)

    chunks = chunk_json_string(flattened_data, chunk_size)
    return chunks

if __name__ == '__main__':

    section_names = SECTION_NAMES

    local_processed_data_path = '../datasets/'
    processed_dataset_filename = 'preprocessed_dataset.csv'
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILEPATH

    # SERVICE_KEY_FILE = "D:/Rohan/Northeastern/Courses/MLOPS/GCP Service Keys/medscript-437117-e1e48d1242ef.json"
    CREDENTIALS = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILEPATH)

    storage_client = storage.Client(credentials=CREDENTIALS, project=CREDENTIALS.project_id)

    bucket = storage_client.get_bucket(MIMIC_DATASET_BUCKET_NAME)

    download_blob = bucket.blob('raw_data/mimic4-dataset.csv')
    data = download_blob.download_as_text()

    # Load the data into a DataFrame
    data_io = StringIO(data)

    df = pd.read_csv(data_io, encoding='utf-8', engine='python', on_bad_lines='warn')
    
    print("Succcessfully read dataset from bucket")

    df.drop('target', axis='columns', inplace=True)

    # df.to_csv('datasets/original.csv', index=False)
    # df = pd.read_csv('datasets/original.csv')

    df['input'] = df['input'].apply(lambda x: transform_text(x, section_names, MAX_CHUNK_SIZE))

    print("Succcessfully transformed dataset")

    df.to_csv(local_processed_data_path+processed_dataset_filename, index=False)
    
    print("Saved transformed dataset")

    upload_blob = bucket.blob('processed_data/' + processed_dataset_filename)

    upload_blob.upload_from_filename(local_processed_data_path+processed_dataset_filename)

    print("Uploaded transformed dataset to bucket")

    os.remove(local_processed_data_path+processed_dataset_filename)
    print("Deleted transformed dataset from local system")
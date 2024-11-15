import os
from google.cloud import aiplatform
from google.oauth2 import service_account
import json
import requests
from google.auth.transport.requests import Request

# Set path to service account JSON
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sa_path = "../data_pipeline/secrets/medscript-sa.json"

def test_endpoint_raw():
    """Test endpoint using raw REST API"""
    print("\nTesting endpoint using raw REST API...")
    
    try:
        # Get credentials and token
        credentials = service_account.Credentials.from_service_account_file(
            sa_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())
        
        # API endpoint URL
        url = "https://us-east4-aiplatform.googleapis.com/v1/projects/946534278700/locations/us-east4/endpoints/205217248254623744:predict"
        
        # Headers
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        medical_case = """Given the following patient information and context, provide a diagnosis.
  Patient Information:
        Gender: female
        Medical History: ['HEPATIC CYST ABD PAIN/DIFFICULTY DEFECATING ALTERNATING CONSTIPATION AND DIARRHEA ANEMIA  ESOPHAGUS ? DIVERTICULOSIS FRANK REGURGITATION GASTROPARESIS GENERALIZED POOR GUT MOTILITY HEMORRHOIDSINT colon  HR HPV needs repeat pap  NAUSEA EGD  nl, hh only EGD  antral gastritis, also by bx NON -SPECIFIC ESOPHAGEAL DYSMOTILITY low LES.  swallows did not propagate. More acid than nl, not bile reflux.. + symptom correlation with regurg videoswallow completely nl  S/P LAPAROSCOPIC SIGMOID COLECTOMY  S/P SIGMOID RESECTION  SMALL INTESTINAL BACTERIAL OVERGROWTH DIARRHEA  stools daily ESR 31, CRP nl, nl celiac serologies DEPRESSION ANXIETY']
        Allergies: No Allergies/ADRs on File
        Chief Complaint: vertigo, left sided weakness
        History of Present Illness: (; AKA EU Critical   is a  woman with a history of rheumatoid arthritis, hypertension, hyperlipidemia, GERD, sigmoidectomy  diverticulosis, and depression who presented to OSH this morning with vertigo, nausea, and incoordination. She was in her usual state of health last night. She awoke this morning at 8AM feeling nauseated. She laid back down, then re-awoke and felt vertiginous. She attempted to walk and describes feeling like she was drunk and having difficulty coordinating all of her extremities. She also felt that she might "black out". At some point she felt that her left arm was also heavy and painful in her shoulder, with pain also radiating to her neck (serial troponins negative). She also noticed transient left parioral numbness. Her husband took her to  where non-contrast CT was negative for large territory infarction so she was given tPA at 10: 41AM for initial NIHSS of 5 at OSH (specific documantation of deficits unavailable). She was subsequently transferred to  for post-tPA monitoring.
      
  Context:
  {"HISTORY OF PRESENT ILLNESS": "years old female with history of PE (on lovenox), bladder cancer status post Robotic TAH-BSO, lap radical cystectomy with ileal loop diversion and anterior vaginectomy in  casebook (sometimes chartbook) abdominal fluid requiring placement of drainage catheters. Recent abdominal imaging noted worsening of her bilateral severe hydronephrosis and her Cr was noted to have risen from 0.8 to 1.3(outside lab value). Patient recently underwent bilateral nephrostomy tube placement by  on . She first started feeling weak during  yesterday doing the exercises. Had palpitations with ambulation. Has tightness in chest with ambulating since yesterday. Felt light headed with ambulation. SNF noticed increased hematuria with R bag darker than L bag since yesterday. Her Urostomy (placed in  also positive for hematuria. She was transferred to  ED for further management. In the ED, initial vitals were: Temp. 98.1, HR 72, BP 139/56, RR 16, 99% RA - Labs notable for: WBC 5.9, Hg 8.1, platelets 374. Na 140, K 4.3, Cl 103, biacrb 22, BUN 29, Cr 1.0 UA from bilateral nephrostomy tubes with > 100 WBC, moderate leukocytes, and large blood. - Imaging was notable for: CT abd/pelvis without contrast: Interval placement of bilateral percutaneous nephroureterostomy tubes with resolved hydroureteronephrosis. No RP hematoma. - Patient was given: LR Upon arrival to the floor, patient reports that she noticed shortness of breath today with walking in conjunction with bloody output from her ostomy tubes. She notes that the output from her nephrostomy tubes was pink tinged when she left the hospital 2 days ago. She also endorses associated chest tightness but no pain or pressure. She denies cough, fever, chills, abdominal pain, or diarrhea. She notes that she has an ostomy and nephroureterostomy without sensation of dysuria. Patient notes feeling dizzy and lightheaded previously though is currently asymptomatic.", "MAJOR SURGICAL OR INVASIVE PROCEDURE": "None", "MEDICATIONS ON ADMISSION": "['Atorvastatin 10 mg PO QPM', 'Enoxaparin Sodium 70 mg SC Q12H Start: , First Dose: Next Routine Administration Time', 'Levothyroxine Sodium 175 mcg PO DAILY', 'Multivitamins 1 TAB PO DAILY', 'Probiotic-Digestive Enzymes (L. acidophilus-dig  5)  mg oral daily']"}
{"HISTORY OF PRESENT ILLNESS": "Mrs.  is a  w/ history of stage III splenic flexure colon cancer status post resection with colonic anastamosis, HTN, DMII, CAD who presents with one episode of bright red blood per rectum this morning. She never has constipation, but some loose stools since her surgery over a decade ago. Today, she had a normal BM for her, and had some blood on top of the BM, small amount, also some red blood on toilet paper. She states she had some mild left sided abdominal pain that came and went with belching, so she thought it was gas pain. She saw her primary care physician today who noticed a small amount of bright red blood in the rectal vault, she was subsequently sent in to us for evaluation. PCP exam  few hours ago with anoscopy demonstrated hemorrhoid and stool with small amount of blood in vault. In the ED intial vitals were: 98.1 58 155/80 18 98% RA - Labs were significant for normal coags, normal CBC, normal LFTs, normal coags. UA shows few bacteria and 2 epithelial cells, otherwise normal. - Urine and blood cultures were sent. Vitals prior to transfer were: 98.4 68 121/65 17 97% RA On the floor, vitals are 98.4 158/86 84 18 100%RA. She is in good spirits, in no distress, in no pain and has had no more red blood since earlier today.", "MAJOR SURGICAL OR INVASIVE PROCEDURE": "None", "MEDICATIONS ON ADMISSION": "['Lisinopril 10 mg PO DAILY', 'Oxybutynin 5 mg PO DAILY', 'Rosuvastatin Calcium 10 mg PO DAILY', 'Aspirin 81 mg PO DAILY', 'Multivitamins 1 TAB PO DAILY', 'Calcium Carbonate 500 mg PO TID: PRN .', 'FoLIC Acid 1 mg PO DAILY', 'Fish Oil (Omega 3) 1000 mg PO BID', 'Nicotine Lozenge 2 mg PO Q8H: PRN smoking cessation']", "PAST MEDICAL HISTORY": "['-COLON CANCER -DIABETES TYPE II -HYPERCHOLESTEROLEMIA -LACTOSE INTOLERANCE -STROKE -INFERIOR MYOCARDIAL INFARCTION -HYPERTENSION -HYPERLIPIDEMIA -DIZZINESS']"}
{"HISTORY OF PRESENT ILLNESS": "Ms.  is a delightful  year old woman with prior paramedian pontine infarct () and right-sided lenticulostriate territory infarct (), hypertension, hyperlipidemia, colon cancer status post resection and chemotherapy in , and extensive tobacco use who presents with acute onset left sided weakness that started at 2200 last night with her left leg and evolved this AM to involve the left arm. As per Ms. , she returned from election campaign headquarters last night between -22: 30 and noted that her left leg was giving way under her. She needed to use her cane to walk. She had no sensory symptoms, no dysarthria, aphasia, arm or facial weakness at this time. She spoke to her daughter on the phone and then went to bed. This AM when she awoke, she noticed that her left arm was weak as well. However, her left leg weakness was much improved and she was able to walk without her cane this AM. Of note, Ms.  was admitted to  two times with above mentioned strokes and is followed by Dr.  in stroke clinic. His note from  notes that Ms.  often has vertiginous symptoms/ dizziness and has had repeated falls as a result. Moreover, her eyesight and hearing have declined. His note seems to suggest that she should be on 325mg ASA, but patient taking only 81mg. On neuro ROS, the pt denies headache, loss of vision, blurred vision, diplopia, dysarthria, dysphagia, tinnitus or hearing difficulty. Denies difficulties producing or comprehending speech. Denies numbness, parasthesiae. No bowel incontinence or retention. Has bladder incontinence at baseline she says and takes a \"blue pill\" for it. Denies difficulty with gait. On general review of systems, the pt denies recent fever or chills. No night sweats or recent weight loss or gain. Denies cough, shortness of breath.", "MAJOR SURGICAL OR INVASIVE PROCEDURE": "None", "MEDICATIONS ON ADMISSION": "['FoLIC Acid 1 mg PO DAILY', 'Oxybutynin 5 mg PO DAILY', 'Rosuvastatin Calcium 10 mg PO DAILY', 'Aspirin 81 mg PO DAILY', 'Calcium Carbonate 500 mg PO TID', 'Fish Oil (Omega 3) 1000 mg PO DAILY', 'Vitamin D 1000 UNIT PO DAILY']"}
  Required Diagnosis: Most likely diagnosis and Differential diagnoses"""




#         medical_case = """Given the following patient information, provide a detailed diagnosis and treatment plan:

# [Patient Information]
# Gender: Female
# Chief Complaint: Worsening ABD distension and pain
# History of Present Illness: HCV cirrhosis casebook with ascites, HIV on ART, history of IVDU, COPD, bipolar, PTSD. Patient presented from OSH ED with worsening abd distension over past week. Self-discontinued lasix and spironolactone. Labs show Tbili1.6, WBC 5K, platelet 77, INR 1.6.

# Past Medical History: 
# - HCV Cirrhosis
# - HIV on ART
# - COPD
# - Bipolar disorder and PTSD
# - History of cocaine and heroin use

# Current Symptoms:
# - Worsening abdominal distension and discomfort
# - Gum bleeding
# - Brief periods of confusion
# - No edema, SOB, or orthopnea

# Required Analysis:
# 1. Most likely diagnosis:
# 2. Differential diagnoses:
# 3. Recommended treatment plan:"""
        

        # Try different input formats
        payloads = [
            # # Format 1: Simple inputs
            # {
            #     "instances": [{"inputs": medical_case}]
            # },
            # # # Format 2: Text format
            # # {
            # #     "instances": [{"text": medical_case}]
            # # },
            # # # Format 3: Prompt format
            {
                "instances": [{
                    "inputs": medical_case,
                    "max_tokens": 4000,
                    "temperature": 0.7
                }]
            }
        ]
        
        # Try each payload format
        for i, payload in enumerate(payloads, 1):
            # print(f"\nTrying payload format {i}...")
            # print(f"Request Headers: {json.dumps(headers, indent=2)}")
            # print(f"Request Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, headers=headers, json=payload)
            
            print(f"\nResponse Status Code: {response.status_code}")
            # print(f"Response Headers: {dict(response.headers)}")
            print("\nResponse Body:")
            print("=" * 80)
            
            try:
                response_json = response.json()
                print(json.dumps(response_json, indent=2))
                
                # Save response if successful
                if response.status_code == 200:
                    output_file = os.path.join(current_dir, f"prediction_output_format_{i}.txt")
                    with open(output_file, "w") as f:
                        json.dump(response_json, f, indent=2)
                    print(f"\nResponse saved to: {output_file}")
                
            except json.JSONDecodeError:
                print("Raw response text:")
                print(response.text)
            
            print("=" * 80)
            
            if response.status_code == 200:
                print(f"Format {i} successful!")
                break
        
    except Exception as e:
        print(f"Error in raw endpoint test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing Vertex AI endpoint with detailed debugging...")
    test_endpoint_raw()
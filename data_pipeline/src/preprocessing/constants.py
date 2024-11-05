PROJECT_ID = "medscript-437117"
MIMIC_DATASET_BUCKET_NAME = "medscript-mimic4-dataset"
BASE_DATASET_FILENAME = "mimic4-dataset.csv"

QDRANT_INSTANCE_ZONE = "us-central1-a"
QDRANT_INSTANCE_NAME = "instance-20241101-155133"

EMBEDDING_SIZE = 768
EMBEDDING_TOKENIZER = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
EMBEDDING_MODEL = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"                   
EMBEDDING_MODEL_PATH = './models/embedding'

QDRANT_COLLECTION = "mimic_embeddings"
QDRANT_PORT = 6333

SERVICE_ACCOUNT_FILEPATH = "secrets/medscript-sa.json"

VECTORSTORE_IP = ""

SECTION_NAMES = ['ALLERGIES', 'CHIEF COMPLAINT', 'DISCHARGE CONDITION', 'DISCHARGE DIAGNOSIS', 'DISCHARGE DISPOSITION', 'DISCHARGE INSTRUCTIONS', 'DISCHARGE MEDICATIONS', 'FAMILY HISTORY', 'FOLLOWUP INSTRUCTIONS', 'HISTORY OF PRESENT ILLNESS', 'MAJOR SURGICAL OR INVASIVE PROCEDURE', 'MEDICATIONS ON ADMISSION', 'PAST MEDICAL HISTORY', 'PERTINENT RESULTS', 'PHYSICAL EXAM', 'SERVICE', 'SEX']

ABBREVIATIONS = {
    "a/p": "anterior-posterior",
    "a/w": "associated with",
    "b/l": "bilateral",
    "b/p": "blood pressure",
    "c/b": "casebook (sometimes chartbook)",
    "c/c": "chief complaint",
    "c/d": "clean and dry",
    "c/e": "clinical evaluation",
    "c/f": "comes for (follow-up)",
    "c/o": "complains of",
    "c/w": "consistent with",
    "d/c": "discontinue or discharge",
    "d/o": "disease of",
    "d/t": "due to",
    "e/o": "evidence of",
    "f/b": "followed by",
    "f/c": "fever and chills",
    "f/u": "follow-up",
    "g/r": "general rule",
    "h/h": "hand hygiene",
    "h/o": "history of",
    "i/j": "icteric jaundice",
    "i/o": "intake/output",
    "m/g": "milligrams",
    "m/r": "medical records",
    "n/a": "not applicable",
    "n/v": "nausea and vomiting",
    "p/w": "presents with",
    "r/g": "rule out",
    "r/o": "rule out",
    "r/r": "respiration rate",
    "s/p": "status post",
    "s/s": "signs and symptoms",
    "u/a": "urinalysis",
    "u/l": "upper limb",
    "u/s": "ultrasound",
    "w/c": "wheelchair",
    "w/o": "without",
    "w/r": "with respect to",
    "y/o": "years old"
}

def set_vectorstore_ip(ip):
    VECTORSTORE_IP = ip
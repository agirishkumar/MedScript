import json
import ast
import os
import sys
from pathlib import Path
current_file = Path(__file__).resolve()
project_dir = current_file.parent.parent
sys.path.append(str(project_dir))
import torch
from data_pipeline.utils.preprocess_dataset import flatten_dict
from data_pipeline.dags.query_vectorstore import VectorStore

def record_to_rag_query(record):
    data = record['patientRecord']
    '''
    Gender -> SEX
    Allergies -> ALLERGIES
    put age, weight, height, blood type in 1 list
    Detailed symptoms -> CHIEF COMPLAINT
    Existing medical conditions -> HISTORY OF PRESENT ILLNESS
    Current medications -> MEDICATIONS ON ADMISSION
    '''
    
    converted_data = {}
    converted_data['SEX'] = data['Gender'].lower()
    converted_data['ALLERGIES'] = data['Allergies']
    converted_data['DURATION'] = data['Duration of the symptoms']
    converted_data['SEVERITY'] = data['Severity']
    converted_data['AGE'] = data['Age']
    converted_data['WEIGHT'] = data['Weight']
    converted_data['HEIGHT'] = data['Height']
    converted_data['BLOOD_TYPE'] = data['Blood type']
    converted_data['CHIEF_COMPLAINT'] = data['Detailed symptoms']
    converted_data['HISTORY_OF_PRESENT_ILLNESS'] = data['Existing medical conditions']
    converted_data['MEDICATIONS_ON_ADMISSION'] = data['Current medications']
    
    return converted_data

def create_doc_dict(docs):
    doc_dict_list = []
    for doc in docs:
        doc_dict = ast.literal_eval(doc.payload['input'])
        doc_dict_list.append(doc_dict)
    return doc_dict_list

def add_context_to_query(query, vector_store, top_k=3, device='cpu'):
    rag_query = record_to_rag_query(query)
    rag_query = json.dumps(flatten_dict(rag_query))
    docs = vector_store.get_relevant_records(rag_query, top_k, device)
    doc_dict_list = create_doc_dict(docs)
    query['context'] = doc_dict_list
    return query

if __name__ == '__main__':
    vector_store = VectorStore()
    current_dir = os.getcwd()

    # print("Current directory: ", current_dir)
    json_path = os.path.join(current_dir, 'models', 'records.json')
    json_context_path = os.path.join(current_dir, 'models', 'records_with_context.json')

    with open(json_path, 'r') as f:
        records = json.load(f)

    # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # print(device)
    # print(torch.__version__)
    device = torch.device('cpu')
    new_records = []
    for record in records:
        print("Adding contexts for patient ID: ", record['patientId'])
        new_records.append(add_context_to_query(record, vector_store))
        
    # new_records = [add_context_to_query(record, vector_store, device) for record in records]

    with open(json_context_path, 'w') as file:
        json.dump(new_records, file)
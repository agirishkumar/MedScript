# data_pipeline/dags/create_embedding.py

'''
This script generates embeddings using PubMedBERT, processes them in batches, and uploads them to Google Cloud Storage,
while managing GPU memory and saving results incrementally.
'''

import ast
import gc
import pickle
import io
from google.cloud import storage
from transformers import BertTokenizer, BertModel
import torch
import os
from constants import SERVICE_ACCOUNT_FILEPATH
from tqdm import tqdm  
import pandas as pd
from logger import logger

def get_embedding(text, tokenizer, model, device):
    """Generate embedding for a single text"""
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, 
                          padding=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():  # Disable gradient computation
            outputs = model(**inputs)
        
        # Get embeddings and move to CPU
        embeddings = outputs.last_hidden_state.mean(dim=1).cpu()
        
        # Clear GPU memory
        del outputs
        torch.cuda.empty_cache()
        
        return embeddings
    
    except Exception as e:
        logger.log_error(f"Error processing text: {str(e)}")
        return None

def embed_to_str(embedding):
    """Converts a single embedding to string representation"""
    if embedding is None:
        return "[]"
    # str_emb = '[' + ','.join(map(str, embedding.flatten().numpy())) + ']'
    # return str_emb
    res = []
    for emb in embedding:
        # str_emb = '[' + ','.join(map(str, emb)) + ']'
        str_emb = str(emb.tolist())
        res.append(str_emb)

    final = '[' + ','.join(map(str, res)) + ']'

    return final

def embed(data, tokenizer, model, device, csv_filename = '', batch_size=4):
    """
    Generates embeddings for data using GPU acceleration
    Smaller batch size and more memory management for 6GB VRAM
    Appends each batch of embeddings to a CSV file for recovery if interrupted.
    """

    if isinstance(data, str):
        embedding = get_embedding(data,tokenizer, model, device)
        embedding = embedding.detach().numpy()
        return embedding
        

    total_batches = len(data) // batch_size + (1 if len(data) % batch_size != 0 else 0)
    
    try:
        for i in tqdm(range(0, len(data), batch_size), desc="Generating embeddings"):
            batch_texts = data.iloc[i:i+batch_size]['input']
            batch_embeddings = []
            
            for text in batch_texts:
                emb = get_embedding(text, tokenizer, model, device)
                if emb is not None:
                    str_emb = embed_to_str(emb)
                    batch_embeddings.append(str_emb)
                
                # Clear memory after each text
                torch.cuda.empty_cache()
            
            # Append to CSV file
            batch_df = data.iloc[i:i+batch_size].copy()
            batch_df['embedding'] = batch_embeddings
            batch_df.to_csv(csv_filename, mode='a', header=not os.path.exists(csv_filename), index=False)

            # Clear memory
            del batch_embeddings, batch_df
            gc.collect()
            torch.cuda.empty_cache()

    except Exception as e:
        logger.log_error(f"Error during embedding generation: {str(e)}")
        raise

def upload_embeddings(data, tokenizer, model, device, bucket, csv_filename = '', batch_size=4):
    """
    Uploads the embeddings to a Google Cloud Storage bucket after generating them incrementally with embed.

    Args:
        data (pd.DataFrame): The input DataFrame containing the 'input' column.
        tokenizer (transformers.BertTokenizer): The tokenizer to use for the input column.
        model (transformers.BertModel): The model to use for the input column.
        device (str): The device to use for the model.
        bucket (google.cloud.storage.Bucket): The Google Cloud Storage bucket to upload to.
        csv_filename (str, optional): The filename to save the embeddings as. Defaults to ''.
        batch_size (int, optional): The batch size to use for generating embeddings. Defaults to 4.

    Returns:
        None
    """
    try:
        data.drop(['input_tokens', 'target_tokens'], axis='columns', inplace=True)
        data['input'] = data['input'].apply(lambda x: ast.literal_eval(x))
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise
    
    # Generate and save embeddings incrementally
    print("Generating embeddings and saving incrementally...")
    embed(df, tokenizer, model, device, csv_filename=csv_filename, batch_size=batch_size)
    print("Completed embedding generation and saving")
    
    # Upload to a different path to keep full dataset separate
    upload_blob = bucket.blob('processed_data/embeddings_100/' + csv_filename)
    upload_blob.upload_from_filename(csv_filename)
    print("Uploaded embedding dataframe to bucket")
    
    # Cleanup
    os.remove(csv_filename)
    logger.info("Deleted local embedding dataframe")

if __name__ == '__main__':
    try:
        # Set up device
        # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        device = torch.device("cpu")
        print(f"Using device: {device}")
        
        if torch.cuda.is_available():
            print(f"Total GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**2:.2f} MB")
        
        # Load model
        tokenizer = BertTokenizer.from_pretrained(
            "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
        )
        model = BertModel.from_pretrained(
            "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
        ).to(device)
        model.eval()  # Set to evaluation mode
        
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILEPATH
        
        bucket_name = "medscript-mimic4-dataset"
        preprocesed_dataset_path = 'processed_data/preprocessed_dataset.csv'
        embed_df_filename = 'embed_df_10k.csv'  
        
        # GCP setup
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        download_blob = bucket.blob(preprocesed_dataset_path)
        
        print("Downloading dataset...")
        content = download_blob.download_as_text()
        csv_file = io.StringIO(content)
        
        # Read only first 100 records
        print("Loading first 100 records...")
        df = pd.read_csv(csv_file, nrows=100)
        print(f"Loaded {len(df)} records")
        upload_embeddings(df, tokenizer, model, device, bucket, csv_filename = embed_df_filename, batch_size=4)
        
    except Exception as e:
        logger.log_error(f"An error occurred: {str(e)}")
        if os.path.exists(embed_df_filename):
            os.remove(embed_df_filename)
        raise

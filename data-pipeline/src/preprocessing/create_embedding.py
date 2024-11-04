import pandas as pd
import ast
import gc
import pickle
import io
from google.cloud import storage
from transformers import BertTokenizer, BertModel
import torch
import os
from constants import SERVICE_ACCOUNT_FILEPATH
from tqdm import tqdm  # For progress bar

def get_embedding(text, tokenizer, model, device):
    """Generate embedding for a single text"""
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, 
                          padding=True, max_length=512)
        # Move inputs to GPU
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
        print(f"Error processing text: {str(e)}")
        return None

def embed_to_str(embedding):
    """Converts a single embedding to string representation"""
    if embedding is None:
        return "[]"
    str_emb = '[' + ','.join(map(str, embedding.flatten().numpy())) + ']'
    return str_emb

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
        print(f"Error during embedding generation: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        # Set up device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
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
        
        # Read only first 10000 records
        print("Loading first 10000 records...")
        df = pd.read_csv(csv_file, nrows=10000)
        print(f"Loaded {len(df)} records")
        
        # Preprocess
        df.drop(['input_tokens', 'target_tokens'], axis='columns', inplace=True)
        df['input'] = df['input'].apply(lambda x: ast.literal_eval(x))
        
        # Generate and save embeddings incrementally
        print("Generating embeddings and saving incrementally...")
        embed(df, tokenizer, model, device, csv_filename=embed_df_filename, batch_size=4)
        print("Completed embedding generation and saving")
        
        # Upload to a different path to keep full dataset separate
        upload_blob = bucket.blob('processed_data/embeddings_10k/' + embed_df_filename)
        upload_blob.upload_from_filename(embed_df_filename)
        print("Uploaded embedding dataframe to bucket")
        
        # Cleanup
        os.remove(embed_df_filename)
        print("Deleted local embedding dataframe")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if os.path.exists(embed_df_filename):
            os.remove(embed_df_filename)
        raise

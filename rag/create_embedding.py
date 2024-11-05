import pandas as pd
import ast
import gc
import pickle
# from google.colab import auth
import io
from google.cloud import storage
from transformers import BertTokenizer, BertModel
import torch
import os
from constants import SERVICE_ACCOUNT_FILEPATH

def get_embedding(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    # Get the embeddings from the last hidden layer
    embeddings = outputs.last_hidden_state.mean(dim=1)  # Average pooling
    return embeddings

def embed_to_str(embeddings):
    """
    Converts the embeddings to a string representation to avoid errors during storing as a csv

    Args:
        embeddings (list): list of embeddings

    Returns:
        list: list of embeddings in string representation
    """
    res = []
    for emb in embeddings:
        str_emb = '[' + ','.join(map(str, emb)) + ']'
        res.append(str_emb)

    final = '[' + ','.join(map(str, res)) + ']'
    return final 

def embed(data, tokenizer, model, batch_size=8):
    """
    Generates embedding for data

    Args:
        data (Dataframe, String): data to embed
        tokenizer (BertTokenizer): Tokenizer used for embedding
        model (BertModel): Model used for embedding
        batch_size (int, optional): Batch size required for generating embeddings of dataset in batches. Defaults to 8.

    Returns:
        Array: Array of embeddings
    """
    if isinstance(data, str):
        embedding = get_embedding(data, tokenizer, model)
        embedding = embedding.detach().numpy()
        return embedding

    for i in range(0, len(data), batch_size):
        batch_texts = data.iloc[i:i+batch_size]['input']
        batch_embeddings = [get_embedding(text, tokenizer, model) for text in batch_texts]
        
        del batch_texts

        with open("embeddings.pkl", "ab+") as f:
            pickle.dump(batch_embeddings, f)
        
        del batch_embeddings
        gc.collect()
    
    embeddings = []
    with open('embeddings.pkl', 'rb') as fr:
        try:
            while True:
                embeddings.extend(pickle.load(fr))
        except EOFError:
            pass
    
    os.remove('embeddings.pkl')
    gc.collect()

    return embeddings

if __name__ == '__main__':
    tokenizer = BertTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
    model = BertModel.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILEPATH

    bucket_name = "medscript-mimic4-dataset"
    preprocesed_dataset_path = 'processed_data/' + 'preprocessed_dataset.csv'
    embed_df_filename = 'embed_df.csv'

    client = storage.Client()
    bucket = client.get_bucket(bucket_name)

    download_blob = bucket.blob(preprocesed_dataset_path)

    content = download_blob.download_as_text()

    csv_file = io.StringIO(content)

    df = pd.read_csv(csv_file)    

    print("Downloaded preprocessed dataset from bucket")

    df.drop(['input_tokens', 'target_tokens'], axis='columns', inplace=True)
    df['input'] = df['input'].apply(lambda x: ast.literal_eval(x))

    embeddings = embed(df, tokenizer, model)

    print("Created embeddings")

    df['embedding'] = [e.detach().numpy() for e in embeddings]

    df['embedding'] = df['embedding'].apply(lambda x: embed_to_str(x))

    df.to_csv(embed_df_filename, index=False)

    print("Current working directory: ", os.getcwd())
    print("Files in current directory:", os.listdir())

    upload_blob = bucket.blob('processed_data/' + embed_df_filename)

    upload_blob.upload_from_filename(embed_df_filename)


    print("Uploaded embedding dataframe to bucket")

    os.remove(embed_df_filename)
    print("Deleted local embedding dataframe")
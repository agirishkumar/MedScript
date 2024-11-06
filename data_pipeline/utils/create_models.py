from transformers import BertTokenizer, BertModel

from constants import EMBEDDING_TOKENIZER, EMBEDDING_MODEL, EMBEDDING_MODEL_PATH
# Load model and tokenizer
model_name = EMBEDDING_MODEL  # or any other model name
model = BertModel.from_pretrained(model_name)
tokenizer = BertTokenizer.from_pretrained(model_name)

# Save model and tokenizer
save_directory = EMBEDDING_MODEL_PATH
model.save_pretrained(save_directory)
tokenizer.save_pretrained(save_directory)

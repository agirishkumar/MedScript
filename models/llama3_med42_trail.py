import transformers
import torch
import mlflow
import time
import os
import sys
from huggingface_hub import snapshot_download

# Set max split size to 128 MB
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'

mlflow.set_experiment("Med42 Trial Experiments with Chain of Thought")

model_name_or_path = "m42-health/Llama3-Med42-8B"

user_info = """
Age: 35
Gender: Female
Medical History: No significant past medical issues
Height: 5'6" (168 cm)
Weight: 140 lbs (63.5 kg)
Allergies: None known
Current Medications: None
"""

symptoms = """
- Severe headache for the past 3 days, primarily on the right side
- Sensitivity to light and sound
- Nausea and vomiting (twice yesterday)
- Blurred vision in the right eye, started about 24 hours ago
- Dizziness when standing up quickly
- Slight neck stiffness
"""

report_template = """
# Comprehensive Diagnostic Report

## 1. Initial Impression
[Provide a summary of key points from patient information and symptoms]

## 2. Possible Diagnoses
### Primary Diagnosis:
[State the most likely diagnosis]

### Differential Diagnoses:
[List other possible diagnoses]

## 3. Reasoning Process
[For each diagnosis, explain why it's being considered and how symptoms support or contradict it]

## 4. Recommended Tests or Examinations
[List and explain rationale for each recommended test]

## 5. Potential Treatment Options
[Suggest treatments for the most likely diagnoses and explain reasoning]

## 6. Immediate Precautions or Recommendations
[Provide urgent advice and explain its importance]

## 7. Follow-up Plan
[Suggest follow-up timeline and what to monitor]

## 8. Summary
[Provide a concise summary of likely diagnosis, key next steps, and important patient instructions]
"""

def initialize_model():
    """
    Downloads and loads a model from the Hugging Face Hub. The model is loaded onto the GPU if available, with a device map that automatically moves the model's parameters to the GPU or CPU as needed. The model is also cast to float16 precision to save memory. The offload folder is set to "offload" to avoid writing temporary files to the current working directory.

    Args:
        model_name_or_path (str): The name or path of the model on the Hugging Face Hub.

    Returns:
        tuple: A tuple of (model, tokenizer) where model is a transformers.AutoModelForCausalLM and tokenizer is a transformers.AutoTokenizer.
    """
    print("Downloading model...", flush=True)
    local_model_path = snapshot_download(model_name_or_path)
    
    print("Loading model...", flush=True)
    model = transformers.AutoModelForCausalLM.from_pretrained(
        local_model_path,
        device_map="auto",
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
        offload_folder="offload",
    )
    tokenizer = transformers.AutoTokenizer.from_pretrained(local_model_path, use_fast=True)
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    return model, tokenizer

def estimate_words_from_tokens(token_count):
    """
    A rough estimate of how many words a given number of tokens corresponds to.

    Assuming an average of 0.75 words per token, this function takes a token count
    and returns an estimated word count.

    Args:
        token_count (int): The number of tokens to estimate a word count for.

    Returns:
        int: An estimated number of words.
    """
    return int(token_count * 0.75)

def run_experiment(min_tokens, max_tokens, do_sample, temperature, top_k, top_p, repetition_penalty, length_penalty):

    """
    Runs an experiment with the given parameters, logs metrics to MLflow, and writes the generated text to a file.

    Args:
        min_tokens (int): The minimum number of tokens to generate.
        max_tokens (int): The maximum number of tokens to generate.
        do_sample (bool): Whether to use sampling or greedy decoding.
        temperature (float): The temperature to use for sampling.
        top_k (int): The number of tokens to consider for sampling.
        top_p (float): The cumulative probability to use for sampling.
        repetition_penalty (float): The penalty to use for repetition.
        length_penalty (float): The penalty to use for length.

    Returns:
        tuple: A tuple of (generated_text, inference_time) where generated_text is the generated text and inference_time is the time it took to generate the text.
    """
    if mlflow.active_run():
        mlflow.end_run()

    with mlflow.start_run():
        mlflow.log_params({
            "min_tokens": min_tokens,
            "max_new_tokens": max_tokens,
            "estimated_min_words": estimate_words_from_tokens(min_tokens),
            "estimated_max_words": estimate_words_from_tokens(max_tokens),
            "do_sample": do_sample,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "repetition_penalty": repetition_penalty,
            "length_penalty": length_penalty
        })

        print("Clearing CUDA cache...", flush=True)
        torch.cuda.empty_cache()

        try:
            print("Initializing model...", flush=True)
            start_time = time.time()
            model, tokenizer = initialize_model()
            initialization_time = time.time() - start_time
            mlflow.log_metric("initialization_time", initialization_time)
            print(f"Model initialized in {initialization_time:.2f} seconds", flush=True)

            messages = [
                {"role": "system", "content": "You are a highly skilled medical assistant. Provide detailed, accurate diagnostic reports including possible diagnoses, reasoning, recommended tests, and potential treatments. Use a step-by-step chain of thought approach to explain your reasoning."},
                {"role": "user", "content": f"""Patient Information:
{user_info}

Reported Symptoms:
{symptoms}

Please provide a comprehensive diagnostic report following these steps:

{report_template}

Please fill in each section of the report template with relevant information based on the patient's symptoms and medical history. Provide clear and detailed explanations throughout your chain of reasoning."""}
            ]

            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
            input_ids = inputs.input_ids.to(model.device)
            attention_mask = inputs.attention_mask.to(model.device)

            print("Generating text...", flush=True)
            start_time = time.time()
            
            with torch.no_grad():
                output = model.generate(
                    input_ids,
                    attention_mask=attention_mask,
                    max_new_tokens=max_tokens,
                    do_sample=do_sample,
                    temperature=temperature,
                    top_k=top_k,
                    top_p=top_p,
                    repetition_penalty=repetition_penalty,
                    length_penalty=length_penalty,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )

            inference_time = time.time() - start_time
            print(f"Text generated in {inference_time:.2f} seconds", flush=True)

            generated_text = tokenizer.decode(output[0], skip_special_tokens=True)[len(prompt):]

            with open("generated_text.txt", "w") as f:
                f.write(generated_text)
            mlflow.log_artifact("generated_text.txt")

            generated_token_count = len(tokenizer.encode(generated_text))
            estimated_word_count = estimate_words_from_tokens(generated_token_count)

            mlflow.log_metrics({
                "generated_token_count": generated_token_count,
                "estimated_word_count": estimated_word_count,
                "inference_time": inference_time
            })

            return generated_text, inference_time

        except Exception as e:
            print(f"Error during experiment: {str(e)}", flush=True)
            mlflow.log_param("error", str(e))
            return None, None
        
        finally:
            if mlflow.active_run():
                mlflow.end_run()
        
def evaluate_chain_of_thought(generated_text):
    """
    Evaluates the completeness of a generated diagnostic report based on the presence of key sections.

    Args:
        generated_text (str): The generated text to evaluate.

    Returns:
        float: A score from 0 to 1 indicating the completeness of the report.
    """
    sections = [
        "# Comprehensive Diagnostic Report",
        "## 1. Initial Impression",
        "## 2. Possible Diagnoses",
        "### Primary Diagnosis:",
        "### Differential Diagnoses:",
        "## 3. Reasoning Process",
        "## 4. Recommended Tests or Examinations",
        "## 5. Potential Treatment Options",
        "## 6. Immediate Precautions or Recommendations",
        "## 7. Follow-up Plan",
        "## 8. Summary"
    ]
    
    score = sum(1 for section in sections if section in generated_text)
    completeness = score / len(sections)
    return completeness

# Baseline parameters
baseline = {
    "min_tokens": 512,
    "max_tokens": 1024,
    "do_sample": True,
    "temperature": 0.7,
    "top_k": 50,
    "top_p": 0.95,
    "repetition_penalty": 1.1,
    "length_penalty": 1.0
}

# Experiments
experiments = [
    baseline,  # Baseline
    {**baseline, "do_sample": False},  # Greedy decoding
    {**baseline, "temperature": 0.5},  # Lower temperature
    {**baseline, "temperature": 0.9},  # Higher temperature
    {**baseline, "temperature": 1.2},  # Even higher temperature
    {**baseline, "top_k": 10},  # Lower top_k
    {**baseline, "top_k": 100},  # Higher top_k
    {**baseline, "top_p": 0.5},  # Lower top_p
    {**baseline, "top_p": 0.99},  # Higher top_p
    {**baseline, "repetition_penalty": 1.0},  # No repetition penalty
    {**baseline, "repetition_penalty": 1.3},  # Higher repetition penalty
    {**baseline, "length_penalty": 0.8},  # Encourage shorter sequences
    {**baseline, "length_penalty": 1.2},  # Encourage longer sequences
    {**baseline, "min_tokens": 256, "max_tokens": 512},  
    {**baseline, "min_tokens": 1024, "max_tokens": 2048},
]

if __name__ == "__main__":
    for i, exp in enumerate(experiments):
        print(f"Running experiment {i+1} with parameters: {exp}", flush=True)
        generated_text, inference_time = run_experiment(**exp)
        
        if generated_text is not None:
            print(f"Inference time: {inference_time:.2f} seconds", flush=True)
            
            completeness_score = evaluate_chain_of_thought(generated_text)
            print(f"Chain of Thought Completeness Score: {completeness_score:.2f}", flush=True)
            
            mlflow.log_metric("completeness_score", completeness_score)
            
            print("Generated text:", flush=True)
            print(generated_text, flush=True)
        else:
            print("Experiment failed. Check logs for details.", flush=True)
        
        print("\n" + "="*50 + "\n", flush=True)
        sys.stdout.flush()

    print("Experiments complete. View results in MLflow UI.", flush=True)
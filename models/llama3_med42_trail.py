import transformers
import torch
import mlflow
import time
import os
import sys

os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

mlflow.set_experiment("Med42 Trail Experiments")

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

def run_experiment(max_new_tokens, do_sample, temperature, top_k, top_p, repetition_penalty, length_penalty):
    with mlflow.start_run():
        # Log parameters
        mlflow.log_params({
            "max_new_tokens": max_new_tokens,
            "do_sample": do_sample,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "repetition_penalty": repetition_penalty,
            "length_penalty": length_penalty
        })

        print("Clearing CUDA cache...", flush=True)
        torch.cuda.empty_cache()

        # Initialize pipeline
        print("Initializing pipeline...", flush=True)
        start_time = time.time()
        pipeline = transformers.pipeline(
            "text-generation",
            model=model_name_or_path,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        initialization_time = time.time() - start_time
        mlflow.log_metric("initialization_time", initialization_time)
        print(f"Pipeline initialized in {initialization_time:.2f} seconds", flush=True)

        messages = [
            {"role": "system", "content": "You are a highly skilled medical assistant. Provide detailed, accurate diagnostic reports including possible diagnoses, reasoning, recommended tests, and potential treatments."},
            {"role": "user", "content": f"Patient Information:\n{user_info}\n\nReported Symptoms:\n{symptoms}\n\nPlease provide a comprehensive diagnostic report including:\n1. Possible diagnoses (primary and differential)\n2. Detailed reasoning for each potential diagnosis\n3. Recommended tests or examinations\n4. Potential treatment options\n5. Any immediate precautions or recommendations for the patient"},
        ]

        prompt = pipeline.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)

        # Generate text and measure time
        print("Generating text...", flush=True)
        start_time = time.time()
        outputs = pipeline(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
            length_penalty=length_penalty,
        )
        inference_time = time.time() - start_time
        print(f"Text generated in {inference_time:.2f} seconds", flush=True)

        generated_text = outputs[0]["generated_text"][len(prompt):]

        # Log the generated text as an artifact
        print("Logging generated text as artifact...", flush=True)
        with open("generated_text.txt", "w") as f:
            f.write(generated_text)
        mlflow.log_artifact("generated_text.txt")

        # Log metrics
        mlflow.log_metrics({
            "text_length": len(generated_text),
            "inference_time": inference_time
        })

        return generated_text, inference_time
# Baseline parameters
baseline = {
    "max_new_tokens": 1024,
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
    {**baseline, "max_new_tokens": 512},  # Shorter output
    {**baseline, "max_new_tokens": 1536},  # Longer output
    {**baseline, "max_new_tokens": 2048},  # Even longer output
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
]

for i, exp in enumerate(experiments):
    print(f"Running experiment {i+1} with parameters: {exp}", flush=True)
    try:
        generated_text, inference_time = run_experiment(**exp)
        print(f"Inference time: {inference_time:.2f} seconds", flush=True)
        print("Generated text:", flush=True)
        print(generated_text, flush=True)
    except Exception as e:
        print(f"Error in experiment {i+1}: {str(e)}", flush=True)
        mlflow.log_param(f"error_{i+1}", str(e))
    print("\n" + "="*50 + "\n", flush=True)
    sys.stdout.flush()  # Ensure all output is flushed

print("Experiments complete. View results in MLflow UI.", flush=True)
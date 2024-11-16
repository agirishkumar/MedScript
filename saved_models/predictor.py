# import json
# import torch
# from flask import Flask, request, jsonify
# from transformers import AutoModelForCausalLM, AutoTokenizer
# from accelerate import init_empty_weights, load_checkpoint_and_dispatch

# app = Flask(__name__)

# model_dir = "med42_model"

# if torch.cuda.is_available():
#     with init_empty_weights():
#         model = AutoModelForCausalLM.from_pretrained(model_dir, torch_dtype=torch.float16)
#     model = load_checkpoint_and_dispatch(model, model_dir, device_map="auto", offload_folder="offload")
# else:
#     with init_empty_weights():
#         model = AutoModelForCausalLM.from_pretrained(model_dir, torch_dtype=torch.float32)
#     model = load_checkpoint_and_dispatch(model, model_dir, device_map="auto", offload_folder="offload")

# tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)

# if tokenizer.pad_token is None:
#     tokenizer.pad_token = tokenizer.eos_token


# def generate_diagnostic_report(
#         user_info, symptoms, report_template,
#         max_tokens=512, min_tokens=256, do_sample=True,
#         temperature=0.7, top_k=50, top_p=0.9,
#         repetition_penalty=1.1, length_penalty=1.0
# ):
#     prompt = f"""
# Patient Information:
# {user_info}

# Reported Symptoms:
# {symptoms}

# Please provide a comprehensive diagnostic report following these steps:

# {report_template}
#     """

#     inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
#     input_ids = inputs.input_ids.to(model.device)
#     attention_mask = inputs.attention_mask.to(model.device)

#     with torch.no_grad():
#         output = model.generate(
#             input_ids=input_ids,
#             attention_mask=attention_mask,
#             max_new_tokens=max_tokens,
#             min_new_tokens=min_tokens,
#             do_sample=do_sample,
#             temperature=temperature,
#             top_k=top_k,
#             top_p=top_p,
#             repetition_penalty=repetition_penalty,
#             length_penalty=length_penalty,
#             pad_token_id=tokenizer.pad_token_id,
#             eos_token_id=tokenizer.eos_token_id,
#         )

#     generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
#     return generated_text


# @app.route("/predict", methods=["POST"])
# def predict():
#     data = request.get_json()
#     user_info = data.get("user_info", "")
#     symptoms = data.get("symptoms", "")
#     report_template = data.get("report_template", "")

#     report = generate_diagnostic_report(user_info, symptoms, report_template)
#     return jsonify({"report": report})


# if __name__ == "__main__":
#     app.run(host="localhost", port=8088)


import json
import torch
from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

app = Flask(__name__)

# Get the absolute path to the model directory
current_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(current_dir, "med42_model")

print(f"Loading model from: {model_dir}")
print(f"GPU Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"Initial GPU Memory: {torch.cuda.mem_get_info()[0]/1024**3:.2f} GB free")

def load_model_and_tokenizer():
    """Initialize model and tokenizer with proper error handling for sharded model"""
    try:
        # Load the model with appropriate settings for sharded files
        model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            device_map="auto",
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            offload_folder="offload"
        )
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        return model, tokenizer
        
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise

print("Initializing model and tokenizer...")
model, tokenizer = load_model_and_tokenizer()
print("Model and tokenizer loaded successfully!")

def generate_diagnostic_report(
    user_info,
    symptoms,
    report_template,
    max_tokens=512,
    min_tokens=256,
    do_sample=True,
    temperature=0.7,
    top_k=50,
    top_p=0.9,
    repetition_penalty=1.1,
    length_penalty=1.0
):
    """Generate a diagnostic report based on the input information"""
    prompt = f"""
Patient Information:
{user_info}

Reported Symptoms:
{symptoms}

Please provide a comprehensive diagnostic report following these steps:
{report_template}
    """
    
    try:
        inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
        input_ids = inputs.input_ids.to(model.device)
        attention_mask = inputs.attention_mask.to(model.device)
        
        with torch.no_grad():
            output = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=max_tokens,
                min_new_tokens=min_tokens,
                do_sample=do_sample,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                length_penalty=length_penalty,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
            
        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
        return generated_text
        
    except Exception as e:
        print(f"Error during generation: {str(e)}")
        raise

@app.route("/predict", methods=["POST"])
def predict():
    """Handle prediction requests"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400
            
        user_info = data.get("user_info", "")
        symptoms = data.get("symptoms", "")
        report_template = data.get("report_template", "")
        
        if not all([user_info, symptoms, report_template]):
            return jsonify({"error": "Missing required fields"}), 400
            
        report = generate_diagnostic_report(user_info, symptoms, report_template)
        return jsonify({"report": report})
        
    except Exception as e:
        print(f"Error in prediction endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    if torch.cuda.is_available():
        print(f"Final GPU Memory: {torch.cuda.mem_get_info()[0]/1024**3:.2f} GB free")
    app.run(host="0.0.0.0", port=8088, debug=False)
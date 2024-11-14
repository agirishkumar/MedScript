import json
import torch
from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
from accelerate import init_empty_weights, load_checkpoint_and_dispatch

app = Flask(__name__)

model_dir = "med42_model"

if torch.cuda.is_available():
    with init_empty_weights():
        model = AutoModelForCausalLM.from_pretrained(model_dir, torch_dtype=torch.float16)
    model = load_checkpoint_and_dispatch(model, model_dir, device_map="auto", offload_folder="offload")
else:
    with init_empty_weights():
        model = AutoModelForCausalLM.from_pretrained(model_dir, torch_dtype=torch.float32)
    model = load_checkpoint_and_dispatch(model, model_dir, device_map="auto", offload_folder="offload")

tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


def generate_diagnostic_report(
        user_info, symptoms, report_template,
        max_tokens=512, min_tokens=256, do_sample=True,
        temperature=0.7, top_k=50, top_p=0.9,
        repetition_penalty=1.1, length_penalty=1.0
):
    prompt = f"""
Patient Information:
{user_info}

Reported Symptoms:
{symptoms}

Please provide a comprehensive diagnostic report following these steps:

{report_template}
    """

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


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    user_info = data.get("user_info", "")
    symptoms = data.get("symptoms", "")
    report_template = data.get("report_template", "")

    report = generate_diagnostic_report(user_info, symptoms, report_template)
    return jsonify({"report": report})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)

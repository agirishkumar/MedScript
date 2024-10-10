import transformers
import torch

model_name_or_path = "m42-health/Llama3-Med42-8B"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_name_or_path,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

user_info = """
Age: 35
Gender: Female
Medical History: No significant past medical issues
"""

symptoms = """
- Severe headache for the past 3 days
- Sensitivity to light
- Nausea
- Blurred vision in the right eye
"""

messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful, respectful and honest medical radiologist. You are a second version of Med42 developed by the AI team at M42, UAE. "
            "Always answer as helpfully as possible, while being safe. "
            "Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. "
            "Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. "
            "If you don't know the answer to a question, please don't share false information."
        ),
    },
    {
        "role": "user",
        "content": f"Please provide a detailed diagnostic report for a patient with the following information:\n\nPatient Information:\n{user_info}\n\nSymptoms:\n{symptoms}\n\nInclude possible diagnoses, reasoning for each diagnosis, recommended tests or examinations, and potential treatment options."
    },
]


prompt = pipeline.tokenizer.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=False
)

stop_tokens = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>"),
]

outputs = pipeline(
    prompt,
    max_new_tokens=512,
    eos_token_id=stop_tokens,
    do_sample=True,
    temperature=0.4,
    top_k=150,
    top_p=0.75,
)

print(outputs[0]["generated_text"][len(prompt) :])

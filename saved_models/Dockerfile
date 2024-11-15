FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir flask transformers safetensors accelerate

COPY med42_model /app/med42_model
COPY predictor.py /app/predictor.py

WORKDIR /app

EXPOSE 8080

CMD ["python", "predictor.py"]

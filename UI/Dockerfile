# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the default Streamlit port
EXPOSE 8080

# Run Streamlit
CMD ["streamlit", "run", "patient_form.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.enableCORS=false"]

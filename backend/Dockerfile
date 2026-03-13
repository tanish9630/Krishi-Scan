FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required for OpenCV/PIL if needed, and curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the HuggingFace model so it's baked into the image
# This avoids downloading it every time the container starts
RUN python -c "from transformers import AutoImageProcessor, AutoModelForImageClassification; AutoImageProcessor.from_pretrained('linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification'); AutoModelForImageClassification.from_pretrained('linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification')"

COPY . .

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

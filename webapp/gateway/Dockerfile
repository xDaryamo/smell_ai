FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Run the FastAPI gateway
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

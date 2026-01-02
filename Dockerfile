FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything into container
COPY . .

# ✅ FIX: your main file is app.py (root)
ENTRYPOINT ["python", "app.py"]
CMD ["--help"]

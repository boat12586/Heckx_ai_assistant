FROM python:3.11-alpine

WORKDIR /app

# Copy requirements and install dependencies  
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8000

# Start with Python directly (simpler than gunicorn for debugging)
CMD ["python", "app_railway.py"]
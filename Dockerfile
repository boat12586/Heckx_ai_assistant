FROM python:3.11-alpine

WORKDIR /app

# Copy requirements and install dependencies  
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY music_discovery.py .
COPY google_drive_service.py .

# Expose port
EXPOSE 8000

# Start with Python directly
CMD ["python", "app.py"]
FROM python:3.11-alpine

WORKDIR /app

# Copy requirements and install dependencies  
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY app.py .
COPY ui_simple.html .

# Expose port
EXPOSE 8000

# Start with Python directly
CMD ["python", "app.py"]
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Ensure pip is upgraded
RUN pip install --upgrade pip

# Install requirements (including gunicorn)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p /app/models /app/data

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PATH="/app/.local/bin:${PATH}"

EXPOSE 5000

# Use full path to gunicorn
CMD ["/usr/local/bin/gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
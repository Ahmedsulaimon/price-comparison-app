
# # More secure base image
FROM python:3.10-slim-bullseye 

WORKDIR /

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install system dependencies first (required for some Python packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY app/ /app/
COPY main.py / 

EXPOSE 5001
#ENV PYTHONPATH=/app

# Run the application
CMD ["python", "main.py"]
#CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
# Use Gunicorn for production
#CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]
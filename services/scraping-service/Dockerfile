 # Use Python slim image
# FROM python:3.10-slim-bullseye

# WORKDIR /

# # Update package list BEFORE installing dependencies
# # Install Playwright dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libgtk-3-0 \
#     libnotify-dev \
#     libgconf-2-4 \
#     libnss3 \
#     libxss1 \
#     libasound2 \
#     && rm -rf /var/lib/apt/lists/*

# # Install Playwright
# RUN pip install playwright && playwright install

# # # Upgrade pip
#  RUN python -m pip install --upgrade pip



# # Replace Chrome installation with Firefox
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     firefox-esr \
#     wget \
#     && rm -rf /var/lib/apt/lists/*

# # Install GeckoDriver
# RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz \
#     && tar -xzf geckodriver-v0.34.0-linux64.tar.gz \
#     && mv geckodriver /usr/local/bin/ \
#     && chmod +x /usr/local/bin/geckodriver \
#     && rm geckodriver-v0.34.0-linux64.tar.gz
# # Install dependencies from requirements.txt
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy application files
# COPY app/ /app/
# COPY main.py /

# EXPOSE 5001

# # Ensure chromedriver is in PATH
# ENV PATH="/usr/local/bin:$PATH"
# #WORKDIR /

# # Run the application
# #CMD ["python", "main.py"]
# #CMD ["xvfb-run", "--server-args=-screen 0 1024x768x24", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001", "--reload-dir", "/app", "python", "main.py"]

# #ENTRYPOINT ["/usr/bin/xvfb-run", "--server-args=-screen 0 1024x768x24"]

# # Create a startup script with logging
# RUN echo '#!/bin/bash\n\
# set -x\n\
# echo "Current directory: $(pwd)"\n\
# echo "Python version: $(python --version)"\n\
# echo "Contents of /app:"\n\
# ls -la /app\n\
# echo "Contents of /app/app:"\n\
# ls -la /app/app\n\
# echo "Running application..."\n\
# xvfb-run --server-args="-screen 0 1024x768x24" python main.py 2>&1 | tee /app/startup.log\n\
# ' > /start.sh && chmod +x /start.sh

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001", "--reload-dir", "/app"]
# #CMD ["/usr/bin/xvfb-run", "--server-args=-screen 0 1024x768x24", "python", "main.py"]


# Use Python slim image
FROM python:3.10-slim-bullseye

WORKDIR /app

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Playwright dependencies
    libgtk-3-0 \
    libnotify-dev \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libasound2 \
    libdbus-glib-1-2 \
    libxt6 \
    libxrender1 \
    libxtst6 \
    # Firefox dependencies
    firefox-esr \
    wget \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install GeckoDriver (specific version for compatibility)
RUN wget -q https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz \
    && tar -xzf geckodriver-*.tar.gz \
    && mv geckodriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver \
    && rm geckodriver-*.tar.gz

# Upgrade pip and install Python dependencies
RUN python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install firefox \
    && playwright install-deps

# Copy application files
COPY . .

# Environment variables
ENV PATH="/usr/local/bin:$PATH"
ENV DISPLAY=":99"
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Startup command
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & uvicorn main:app --host 0.0.0.0 --port 5001"]
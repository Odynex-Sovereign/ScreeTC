FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose operational container routing port
EXPOSE 8080

# Explicitly invoke Gunicorn to bind to the runtime environment port
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--chdir", "src", "main_api_gateway:app"]
FROM python:3.10-slim

WORKDIR /app

# Install bare minimum compilation tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration and install libraries 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source repository structure
COPY . .

# Expose dynamic cloud routing port
EXPOSE 8080

# Execute Gunicorn by navigating into src directory natively
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--chdir", "src", "main_api_gateway:app"]

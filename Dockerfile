# -----------------------------
# Base Image
# -----------------------------
FROM python:3.12-slimdocke

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the local web server port
EXPOSE 8000

# Set environment variable for .env loading (optional)
ENV PYTHONUNBUFFERED=1

# Command to run your app
CMD ["python", "generate.py"]
# -----------------------------
# Base Image
# -----------------------------
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the local web server port
EXPOSE 8000

# Set environment variable for .env loading (optional)
ENV PYTHONUNBUFFERED=1

# Command to run your app
CMD ["python", "generate.py"]

FROM python:3.11-slim-buster

# Install system dependencies for Selenium (adjust if needed)
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy your project files into the container
COPY . ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run when the container starts
CMD ["python", "src/main.py"]
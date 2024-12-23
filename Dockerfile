FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create volume for persistent data
VOLUME /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Run the application
CMD ["python", "youtube_opportunity_finder.py"]

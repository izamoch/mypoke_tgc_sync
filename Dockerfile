# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set PYTHONPATH to include src
ENV PYTHONPATH=/app/src

# Run the sync job by default using the module entry point
CMD ["python", "-m", "mypoke_sync.main"]

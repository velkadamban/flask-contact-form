# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your application files
COPY . .

# Expose port 5000 (Flask default)
EXPOSE 5000

# Command to run your application
CMD ["python", "app.py"]
# Use Python 3.9 slim image for smaller size
FROM python:3.9-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first for better Docker caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Expose port 5000 for Flask app
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
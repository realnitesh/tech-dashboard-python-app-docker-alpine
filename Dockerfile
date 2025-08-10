# Use Alpine Linux with Python 3.9
FROM python:3.9-alpine

# Set working directory
WORKDIR /app

# Install system dependencies required for Python packages


# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY dashboard.py .
COPY assets/ ./assets/

# Expose port
EXPOSE 8050

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DASH_DEBUG=True

# Run the application
CMD ["python", "dashboard.py"]



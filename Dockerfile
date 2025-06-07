FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories for logs
RUN mkdir -p logs

# Make entrypoint script executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

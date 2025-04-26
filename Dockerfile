# Base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /natwest

# Install system dependencies
RUN apt-get update && apt-get install -y netcat-openbsd gcc libpq-dev

# Install Python dependencies
COPY requirements.txt /natwest/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy all files, including entrypoint
COPY . /natwest/

# Make entrypoint executable
RUN chmod +x /natwest/entrypoint.sh

# Expose port
EXPOSE 8000

# Entrypoint script
CMD ["sh", "/natwest/entrypoint.sh"]
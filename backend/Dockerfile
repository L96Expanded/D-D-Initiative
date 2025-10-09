FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


# Install bcrypt at a compatible version before requirements
RUN pip install --upgrade bcrypt==4.0.1

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy database and images first (these change less frequently)
COPY creature_database.json .
COPY database-images/ ./database_images/

# Copy application code (changes more frequently, so do this last for better caching)
COPY backend/ .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
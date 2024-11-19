# Use the official Python image as a base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Add wait-for-it.sh script
# Download the wait-for-it script to handle waiting for Kafka
RUN apt-get update && apt-get install -y curl && \
    curl -o /wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /wait-for-it.sh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Expose Kafka default port (not required but good practice for documentation)
EXPOSE 9092

# Command to wait for Kafka and then run the application
CMD ["/bin/sh", "-c", "/wait-for-it.sh kafka:9092 && sleep 30 && python producer.py"]

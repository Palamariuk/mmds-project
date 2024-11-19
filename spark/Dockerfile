# Use a base image with Spark
FROM bitnami/spark:latest

# Switch to root user to run privileged commands
USER root

# Set the working directory
WORKDIR /app

# Update apt and install Python
RUN apt-get clean && \
    apt-get update && \
    apt-get install -y python3-pip

# Copy requirements.txt and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

# Revert back to non-root user for security
USER 1001

# Copy your Spark application code into the container
COPY spark_job.py /app/spark_job.py

# Copy the Bloom filter state file into the container
COPY bloom_state.pkl /app/bloom_state.pkl

# Expose ports for Spark
EXPOSE 4040

# Command to run the Spark job
CMD ["sh", "-c", "sleep 30 && spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 /app/spark_job.py"]

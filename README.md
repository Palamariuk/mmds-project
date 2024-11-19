
# Wiki Article Analysis Pipeline: Bot Detection

This project implements a real-time data pipeline for reading and analyzing Wikipedia articles using the Wikipedia API, Kafka, and Apache Spark. A **Bloom filter** is employed to identify whether an edit was made by a bot or a human contributor efficiently and in real-time.

---

## Project Overview

### Key Components
1. **Wikipedia API Integration**: 
   - Fetches and processes Wikipedia articles in real-time.
   - Acts as the **producer**, sending data to Kafka.

2. **Kafka**:
   - Serves as the message broker for handling real-time data streams.
   - Receives article data from the producer and makes it available to consumers.

3. **Spark Consumer**:
   - Consumes data from Kafka.
   - Applies a **Bloom filter** to classify whether an edit was made by a bot or a human contributor.

4. **Bloom Filter**:
   - A probabilistic data structure used to check if an article has already been processed.
   - Ensures memory-efficient deduplication with minimal false positives.

---

#  Project Setup

## Prerequisites

- **Docker** installed on your machine.
- **Docker Compose** installed.

---

## Services Overview

### 1. **ZooKeeper**
Manages distributed systems and is a required component for Kafka.

- **Image**: `confluentinc/cp-zookeeper:latest`
- **Port**: `2181`
- **Environment Variables**:
  - `ZOOKEEPER_CLIENT_PORT=2181`
  - `ZOOKEEPER_TICK_TIME=2000`

---

### 2. **Kafka**
Message broker used for real-time data streaming.

- **Image**: `confluentinc/cp-kafka:latest`
- **Ports**: 
  - Exposes Kafka on `9092`.
- **Environment Variables**:
  - `KAFKA_BROKER_ID=1`
  - `KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181`
  - `KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092`
  - `KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092`
  - `KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1`
- **Volumes**:
  - Mounts a script (`create-topic.sh`) to create Kafka topics during startup.
- **Entrypoint**:
  - Starts the Kafka broker and executes the topic creation script.
- **Dependencies**:
  - Depends on **ZooKeeper** for operation.

---

### 3. **Spark Consumer**
Consumes messages from Kafka and processes them using Apache Spark.

- **Build Context**: `./spark`
- **Dockerfile**: Located in the `./spark` directory.
- **Port**: `4040` (exposes Spark's web UI).
- **Volumes**:
  - Mounts the `./spark` directory to `/app` in the container.
- **Dependencies**:
  - Depends on **Kafka**.

---

### 4. **Wiki Producer**
Produces messages to Kafka by simulating or fetching Wikipedia data streams.

- **Build Context**: `./wiki-producer`
- **Dockerfile**: Located in the `./wiki-producer` directory.
- **Volumes**:
  - Mounts the `./wiki-producer` directory to `/app` in the container.
- **Dependencies**:
  - Depends on **Kafka**.

---

## File Structure

```
.
├── docker-compose.yml      # Defines all services
├── scripts/
│   └── create-topic.sh     # Script for Kafka topic creation
├── spark/
│   ├── Dockerfile          # Dockerfile for the Spark consumer
│   └── ...                 # Spark consumer application files
├── wiki-producer/
│   ├── Dockerfile          # Dockerfile for the Wiki producer
│   └── ...                 # Wiki producer application files
```

---

## Usage

### 1. Build and Start Services
Run the following command to build and start all services:
```bash
docker-compose up --build
```

### 2. Accessing Services
- **Kafka**: Available on `localhost:9092`.
- **Spark UI**: Available on `localhost:4040`.

### 3. Stopping Services
To stop all running containers:
```bash
docker-compose down
```

---

## Customization

### Kafka Topics
Modify the `scripts/create-topic.sh` file to customize Kafka topics.

### Application Logic
- Update Spark consumer logic in the `./spark` directory.
- Modify or extend the Wiki producer in the `./wiki-producer` directory.

---

## Notes
- Ensure `create-topic.sh` contains the correct Kafka CLI commands to initialize topics as needed.
- Allow sufficient startup time for dependencies (e.g., ZooKeeper, Kafka) before running producers or consumers.

Happy Streaming! 🚀

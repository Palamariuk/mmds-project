# Wikimedia Stream URL
STREAM_URL = 'https://stream.wikimedia.org/v2/stream/recentchange'
WIKI = 'enwiki'  # Client-side filter

# Sampling Configuration
SAMPLE_RATE = 0.2  # Keep 20% of records

# Output Stream
BROKER_TYPE = 'Socket'  # or "Kafka"

# Socket Configuration (legacy)
SOCKET_HOST = 'localhost'
SOCKET_PORT = 9999

# Kafka settings
KAFKA_BROKER = "localhost:9092"  # Kafka broker address (use "kafka:9092" in Docker if services are linked)
KAFKA_TOPIC = "wiki-changes"  # Topic to which the data will be published

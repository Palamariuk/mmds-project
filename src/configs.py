# Socket Configuration (legacy)
SOCKET_HOST = 'localhost'
SOCKET_PORT = 9999

# Wikimedia Stream URL
STREAM_URL = 'https://stream.wikimedia.org/v2/stream/recentchange'
WIKI = 'enwiki'  # Client-side filter

# Sampling
NUMBER_OF_FILES = 40
RECORDS_PER_FILE = 1000

# Kafka settings
KAFKA_BROKER = "localhost:9092"  # Kafka broker address (use "kafka:9092" in Docker if services are linked)
KAFKA_TOPIC = "wiki-changes"  # Topic to which the data will be published

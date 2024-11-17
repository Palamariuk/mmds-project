import json
from kafka import KafkaProducer
from sseclient import SSEClient as EventSource

from configs import *


# Function to stream data to a Kafka topic
def stream_to_kafka():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    try:
        for event in EventSource(STREAM_URL):
            try:
                change = json.loads(event.data)
                # Filter events based on 'enwiki' and 'edit' type
                if change.get("wiki") == WIKI and change.get('type') == 'edit':
                    event_data = {
                        "id": change.get("id"),
                        "title": change.get("title"),
                        "timestamp": change.get("timestamp"),
                        "user": change.get("user"),
                        "bot": change.get("bot"),
                        "minor": change.get("minor"),
                        "change": change.get("length", {}).get("new", 0) - change.get("length", {}).get("old", 0),
                        "comment": change.get("comment"),
                    }
                    # Send the event data to the Kafka topic
                    producer.send(KAFKA_TOPIC, event_data)
                    print(f"Sent to Kafka: {event_data}")

            except json.JSONDecodeError:
                continue
    except Exception as e:
        print(f"Error: {e}")
    finally:
        producer.close()


# Run the script
if __name__ == "__main__":
    stream_to_kafka()

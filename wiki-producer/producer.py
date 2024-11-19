import json
from sseclient import SSEClient as EventSource
from confluent_kafka import Producer

# Kafka configuration
KAFKA_BROKER = 'kafka:9092'
TOPIC = 'test'

# Configure Kafka Producer
producer_conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'client.id': 'wiki-stream-producer'
}
producer = Producer(producer_conf)


def delivery_report(err, msg):
    """
    Callback for Kafka delivery reports.
    """
    if err is not None:
        print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        print(f"Record successfully produced to {msg.topic()} partition {msg.partition()} offset {msg.offset()}")


# Wikimedia event stream URL
url = 'https://stream.wikimedia.org/v2/stream/recentchange'
wiki = 'enwiki'  # Filter for English Wikipedia
maxEvents = 2000  # Number of events to capture


def produce_to_kafka():
    """
    Stream events from Wikimedia and produce them to Kafka.
    """
    event_count = 0
    print("Starting to stream events from Wikimedia...")

    for event in EventSource(url):
        try:
            # Parse the event data
            change = json.loads(event.data)

            # Filter for relevant events
            if change.get("wiki") == wiki and change.get('type') == 'edit':
                # Prepare the payload
                event_data = {
                    "id": change.get("id"),
                    "title": change.get("title"),
                    "timestamp": change.get("timestamp"),
                    "user": change.get("user"),
                    "bot": change.get("bot"),
                    "minor": change.get("minor"),
                    "patrolled": change.get("patrolled"),
                    "change": change.get("length", {}).get("new", 0) - change.get("length", {}).get("old", 0),
                    "comment": change.get("comment"),
                }

                # Convert to JSON string
                event_json = json.dumps(event_data)

                # Send to Kafka
                producer.produce(
                    topic=TOPIC,
                    value=event_json,
                    callback=delivery_report
                )

                # Increment the event counter
                event_count += 1

                # Trigger delivery report
                producer.poll(0)

                print(f"Event {event_count} produced to Kafka: {event_data['title']}")

                # Stop after reaching maxEvents
                if event_count >= maxEvents:
                    break
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error processing event: {e}")
            continue

    # Wait for all messages to be delivered
    producer.flush()
    print(f"Stream ended. {event_count} events sent to Kafka.")


if __name__ == "__main__":
    produce_to_kafka()

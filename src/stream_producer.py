import json
import socket

from kafka import KafkaProducer
from sseclient import SSEClient as EventSource

from configs import *


# Common function to stream events
def stream_events(callback):
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
                    callback(event_data)
            except json.JSONDecodeError:
                continue
    except Exception as e:
        print(f"Error: {e}")


# Function to stream data to a socket
def stream_to_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SOCKET_HOST, SOCKET_PORT))
    server_socket.listen(1)
    print(f"Server started at {SOCKET_HOST}:{SOCKET_PORT}, waiting for client...")
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr} established.")

    def send_to_socket(event_data):
        client_socket.send((json.dumps(event_data) + "\n").encode('utf-8'))
        print(f"Sent to Socket: {event_data}")

    try:
        stream_events(send_to_socket)
    finally:
        client_socket.close()
        server_socket.close()


# Function to stream data to a Kafka topic
def stream_to_kafka():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    def send_to_kafka(event_data):
        producer.send(KAFKA_TOPIC, event_data)
        print(f"Sent to Kafka: {event_data}")

    try:
        stream_events(send_to_kafka)
    finally:
        producer.close()


if __name__ == "__main__":
    if BROKER_TYPE == 'Socket':
        stream_to_socket()
    else:
        stream_to_kafka()
